# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module provides a batch processing for generating text/multimodal
embeddings with the Mercari dataset
"""

import os
import json
import queue
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Callable

from tqdm import tqdm

from google.cloud import bigquery, storage
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

PROJECT_ID = "gcp-samples-ic0"
LOCATION = "us-central1"

# generate an unique id for this session

UID = datetime.now().strftime("%m%d%H%M%S")
print(f"Unique ID for this session is: {UID}")

# load the BQ Table into a Pandas DataFrame
print("loading dataset...")
bq_client = bigquery.Client(project=PROJECT_ID)
QUERY = """
SELECT
  id,
  CONCAT(name, ' ', description) AS text
FROM
  `gcp-samples-ic0.mercari202502.mercari_items_202502`
WHERE
  MOD(CAST(SUBSTR(id, 12) AS INT64), 2) = 1
""" # using MOD for splitting data into several parts

query_job = bq_client.query(QUERY)
rows = query_job.result()
df = rows.to_dataframe()
items = df.to_dict("records")

TEXT_EMB_MODEL_NAME = "text-embedding-005"
TEXT_EMB_TASK_TYPE = "RETRIEVAL_DOCUMENT"
TEXT_EMB_DIMENSIONALITY = 768

vertexai.init(project=PROJECT_ID, location=LOCATION)
text_emb_model = TextEmbeddingModel.from_pretrained(TEXT_EMB_MODEL_NAME)


def generate_text_embeddings(items: List[Dict[str, Any]]) -> List[List[float]]:
    """
    Generate text embeddings for items.
    """

    # Combine name and description for embedding input.

    # Prepare inputs for the text embedding model.
    inputs: List[TextEmbeddingInput] = [
        TextEmbeddingInput(item["text"], TEXT_EMB_TASK_TYPE) for item in items
    ]
    kwargs = {"output_dimensionality": TEXT_EMB_DIMENSIONALITY}

    # Get embeddings from the model.
    return [emb.values for emb in text_emb_model.get_embeddings(inputs, **kwargs)]


def run_worker_thread(
    generation_func: Callable[[List[Dict[str, Any]], "queue.Queue"], None],
    items: List[Dict[str, Any]],
    emb_queue: "queue.Queue",
    err_queue: "queue.Queue",
) -> None:
    """
    Runs a worker thread that generates embeddings with a single API call and handles
    potential errors.

    Args:
        generation_func: A function that takes a list of items and returns their embeddings.
        items: The list of items to process. Each item should be a dictionary.
        emb_queue: The queue to put the generated embeddings into.
        err_queue: The queue to put any encountered errors into.
    """
    try:
        embs = generation_func(items)
        for i in range(0, len(items)):
            emb_queue.put({"id": items[i]["id"], "embedding": embs[i]})
    except Exception as e:
        err_queue.put(str(e))



GCS_BUCKET = f"{PROJECT_ID}-embs-{UID}"
GCS_TEXT_EMB_PATH = "text_embs"

# create a bucket
storage_client = storage.Client()
storage_bucket = storage_client.bucket(GCS_BUCKET)
storage_bucket = storage_client.create_bucket(storage_bucket, location="us-central1")

# create a folder for storing text embeddings
empty_blob = storage_bucket.blob(GCS_TEXT_EMB_PATH + "/")
empty_blob.upload_from_string("")
print(f"\nCreated text embedding folder: gs://{GCS_BUCKET}/{GCS_TEXT_EMB_PATH}")

QUEUE_FLUSH_THRESHOLD = 10000
ERR_FILE_NAME = f"err_{UID}.log"

is_queue_manager_enabled: bool = True


def flush_emb_queue(emb_queue: queue.Queue, gcs_path: str, count: int) -> None:
    """
    Flushes the embedding queue to Cloud Storage.

    Args:
    emb_queue: The queue containing embedding dictionaries.
    gcs_path: The destination path in Cloud Storage.
    count: The number of embeddings to flush from the queue.
    """
    timestamp: str = datetime.now().strftime("%m%d%H%M-%S%f")
    embs: str = ""
    for _ in range(0, count):
        emb: Dict = emb_queue.get()
        embs += json.dumps(emb) + "\n"
    gcs_file = storage_bucket.blob(f"{gcs_path}/{timestamp}_embs.json")
    gcs_file.upload_from_string(embs, content_type="application/json")
    print(f"Uploaded {count} embeddings to {gcs_file.name}")


def flush_err_queue(err_queue: queue.Queue) -> None:
    """Flushes the error queue to the error log file."""
    with open(ERR_FILE_NAME, "a", encoding="utf-8") as file:
        while not err_queue.empty():
            error = err_queue.get()
            file.write(f"Error {error}\n")
            print(f"Error {error}")


def run_queue_manager_thread(
    emb_queue: queue.Queue, err_queue: queue.Queue, gcs_path: str
) -> None:
    """Runs the queue manager thread, which monitors and flushes the embedding and error queues.

    Args:
        emb_queue: The queue for storing embeddings.
        err_queue: The queue for storing errors.
        gcs_path: The path to Cloud Storage where embeddings will be stored.
    """

    # Continue managing the queues while enabled
    while is_queue_manager_enabled:
        time.sleep(0.1)

        # Flush the embedding queue if it exceeds the threshold
        if emb_queue.qsize() > QUEUE_FLUSH_THRESHOLD:
            flush_emb_queue(emb_queue, gcs_path, QUEUE_FLUSH_THRESHOLD)

        # Flush the error queue if it contains any errors
        if err_queue.qsize() > 0:
            flush_err_queue(err_queue)

    # Perform a final flush of both queues when the queue manager is disabled
    flush_emb_queue(emb_queue, gcs_path, emb_queue.qsize())
    flush_err_queue(err_queue)


def generate_embeddings(
    generation_func: Callable[[List[Dict[str, Any]], "queue.Queue"], None],
    reqs_per_min_quota: int,
    items_per_req: int,
    gcs_path: str,
    items: List[Dict[str, Any]],
) -> None:
    """
    Generates embeddings with throttling and error handling.

    Args:
        generation_func: The function used to generate the embeddings.
        reqs_per_min_quota: The maximum number of requests allowed per minute for the model.
        items_per_req: The number of items to include in each request.
        items: The dataset we'll be working with.
    """

    # All threads.
    threads: List[threading.Thread] = []

    # Throttling interval.
    req_interval: float = 1.0 / (reqs_per_min_quota / 60)

    # Start queue manager thread.
    global is_queue_manager_enabled
    is_queue_manager_enabled = True
    emb_queue: "queue.Queue" = queue.Queue()
    err_queue: "queue.Queue" = queue.Queue()
    queue_manager_thread: threading.Thread = threading.Thread(
        target=run_queue_manager_thread, args=(emb_queue, err_queue, gcs_path)
    )
    queue_manager_thread.start()

    # Generate embeddings.
    for i in tqdm(range(0, len(items), items_per_req)):

        # Throttle requests.
        time.sleep(req_interval)

        # Start a worker thread.
        items_slice: List[Dict[str, Any]] = items[i : i + items_per_req]
        worker_thread: threading.Thread = threading.Thread(
            target=run_worker_thread,
            args=(generation_func, items_slice, emb_queue, err_queue),
        )
        worker_thread.start()
        threads.append(worker_thread)

    # Wait for all worker threads to finish.
    print(f"Waiting for {len(threads)} threads to finish...")
    for i in tqdm(range(0, len(threads), 1)):
        threads[i].join()

    # Wait for the queue manager to stop.
    print("Waiting for the queue manager to finish...")
    is_queue_manager_enabled = False
    queue_manager_thread.join()

    # Print error count.
    if os.path.exists(ERR_FILE_NAME):
        with open(ERR_FILE_NAME, "r", encoding="utf-8") as f:
            error_count: int = len(f.readlines())
        print(f"{error_count} errors recorded in {ERR_FILE_NAME}")
    else:
        print("No errors recorded")
    print("Done!")

# Start generating text embeddings
print("start generating")
generate_embeddings(
    generation_func=generate_text_embeddings,
    reqs_per_min_quota=1500,
    items_per_req=20,
    gcs_path=GCS_TEXT_EMB_PATH,
    items=items,
)

print(f"\nCreated text embeddings on folder: gs://{GCS_BUCKET}/{GCS_TEXT_EMB_PATH}")
