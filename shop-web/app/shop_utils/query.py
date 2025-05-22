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
This module provides a hybrid search with Mercari dataset.
"""

import os
from typing import Any
import logging
import threading
import queue
import time
import json

from pydantic import BaseModel
import joblib
from Levenshtein import distance as levenshtein_distance

from google import genai
from google.genai.types import (
    Part,
    GenerateContentConfig,
)

from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    HybridQuery,
)
from google.cloud.aiplatform_v1beta1 import FeatureOnlineStoreServiceClient
from google.cloud.aiplatform_v1beta1.types import (
    feature_online_store_service as feature_online_store_service_pb2,
)
from google.cloud import discoveryengine_v1 as discoveryengine

from vertexai.language_models import (
    TextEmbeddingInput,
    TextEmbeddingModel,
)
from vertexai.vision_models import (
    MultiModalEmbeddingModel,
)

from shop_utils.image_utils import generate_item_image_board, image_to_bytes

logging.basicConfig(level=logging.INFO)

#
# Vertex AI init
#

PROJECT_ID: str = os.environ.get("PROJECT_ID")
LOCATION: str = os.environ.get("LOCATION", "us-central1")

aiplatform.init(project=PROJECT_ID, location=LOCATION)

#
# Sparse embeddings with TF-IDF
#

vectorizer = joblib.load("./shop_utils/mercari3m_vectorizer.joblib")


def get_sparse_embedding(query):
    """get sparse embedding for the query text"""

    # Transform Text into TF-IDF Sparse Vector
    tfidf_vector = vectorizer.transform([query])

    # Create Sparse Embedding for the New Text
    values = []
    dims = []
    for i, tfidf_value in enumerate(tfidf_vector.data):
        values.append(float(tfidf_value))
        dims.append(int(tfidf_vector.indices[i]))
    return {"values": values, "dimensions": dims}


#
# Dense embeddings with Text Embeddings API
#

text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-005")


def get_text_embedding(query):
    """generate text embedding for the query text."""
    emb_task_type = "QUESTION_ANSWERING"
    text_emb_inputs = [TextEmbeddingInput(query, emb_task_type)]
    embeddings = text_emb_model.get_embeddings(text_emb_inputs)
    return embeddings[0].values


#
# Dense embeddings with Multimodal Embeddings API
#

MM_EMB_MODEL_NAME = "multimodalembedding"
MM_EMB_DIMENSIONALITY = 1408
mm_emb_model = MultiModalEmbeddingModel.from_pretrained(MM_EMB_MODEL_NAME)


def get_mm_embedding(query):
    """
    Generate multimodal embeddings for items.
    """
    # Get multimodal embeddings for query texts.
    emb = mm_emb_model.get_embeddings(
        contextual_text=query, dimension=MM_EMB_DIMENSIONALITY
    )
    return emb.image_embedding


#
# Vector Search
#

VVS_ENDPOINT_ID = "8807101332625293312"
VVS_DEPLOYED_INDEX_ID = "ac_mercari3m_text_retrieva_1736979746185"
VVS_DEPLOYED_INDEX_ID_MM = "ac_mercari3m_mm_01081625_d_1736326927378"
TOTAL_ITEM_COUNT = 2874425

# DENSE_DIST_THRESHOLD = 0.1
DENSE_DIST_THRESHOLD = 0.0
RRF_ALPHA_TEXT = 0.5
RRF_ALPHA_MM = 1.0  # use no sparse results for mm search

vvs_endpoint = aiplatform.MatchingEngineIndexEndpoint(VVS_ENDPOINT_ID)


def create_hybrid_query(query, is_text=True):
    """Create a HybridQuery object for the query text"""

    # generate dense and/or sparse embs
    dense_emb = None
    sparse_dims = None
    sparse_values = None
    dense_emb = get_text_embedding(query) if is_text else get_mm_embedding(query)
    sparse_emb = get_sparse_embedding(query)
    sparse_dims = sparse_emb["dimensions"]
    sparse_values = sparse_emb["values"]

    return HybridQuery(
        dense_embedding=dense_emb,
        sparse_embedding_dimensions=sparse_dims,
        sparse_embedding_values=sparse_values,
        rrf_ranking_alpha=RRF_ALPHA_TEXT if is_text else RRF_ALPHA_MM,
    )


def run_vvs_query(hybrid_query, query_rows, deployed_index_id):
    """Run vector search"""
    response = vvs_endpoint.find_neighbors(
        deployed_index_id=deployed_index_id,
        queries=[hybrid_query],
        num_neighbors=query_rows,
    )
    return response


#
# Feature Store
#

fs_data_client = FeatureOnlineStoreServiceClient(
    client_options={"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
)

FS_ONLINESTORE = "ac_01060532"
FS_FEATUREVIEW = "ac_fv_mercari_01060532"
FS_FEATUREVIEW_PATH = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/"
    + f"featureOnlineStores/{FS_ONLINESTORE}/featureViews/{FS_FEATUREVIEW}"
)


def fetch_feature_values(items, feature_names):
    """Fetches feature values"""

    # build a list of FeatureViewDataKey objects
    data_keys = [
        feature_online_store_service_pb2.FeatureViewDataKey(key=item["id"])
        for item in items
    ]

    # build a request
    request = feature_online_store_service_pb2.StreamingFetchFeatureValuesRequest(
        feature_view=FS_FEATUREVIEW_PATH,
        data_keys=data_keys,
        data_format=feature_online_store_service_pb2.FeatureViewDataFormat.KEY_VALUE,
    )

    # fetch features
    f_dict = {}
    key_values = fs_data_client.streaming_fetch_feature_values(requests=iter([request]))
    key_values = [item.data for item in key_values][0]

    for kv in key_values:
        features = {"id": kv.data_key.key}
        for f in kv.key_values.features:
            if f.name in feature_names:
                features.update({f.name: f.value.string_value})
        f_dict[features["id"]] = features

    # sort features
    items_with_features = []
    for item in items:
        try:
            item.update(f_dict[item["id"]])
            items_with_features.append(item)
        except KeyError:
            logging.warning("fetch_feature_values(): item not found: %s", item["id"])
    return items_with_features


#
# Ranking API
#


rank_client = discoveryengine.RankServiceClient()
ranking_config = rank_client.ranking_config_path(
    project=PROJECT_ID,
    location=LOCATION,
    ranking_config="default_ranking_config",
)

RANK_MODEL = "semantic-ranker-512@latest"


def get_rank_records(items):
    """
    Get rank records.
    """
    records = []
    for item in items:
        item_id = item["id"]
        name = item["name"]
        description = item["description"]
        records.append(
            discoveryengine.RankingRecord(
                id=item_id,
                title=name,
                content=description,
            )
        )
    return records[:200] # ranking api can't take over 200 rows


def text_rerank(query, items, rows):
    """
    Rerank the features.
    """
    # call ranking api
    rank_request = discoveryengine.RankRequest(
        ranking_config=ranking_config,
        model=RANK_MODEL,
        top_n=rows,
        query=query,
        records=get_rank_records(items),
        ignore_record_details_in_response=True,
    )
    response = rank_client.rank(request=rank_request)

    # rerank the features (using the original rank as secondary rank)
    items_dict = {item["id"]: item for item in items}
    reranked_items = []
    for r in response.records:
        f = {"id": r.id, "rerank_score": r.score}
        f.update(items_dict[r.id])
        reranked_items.append(f)
    return reranked_items


#
# Dedup similar items
#

DEDUP_MIN_DIST = 10


def dedup_items(items):
    """Dedup items with Levenshtein distance on the item description"""

    descs = []
    unique_items = []
    for item in items:
        desc = item["description"].replace(" ", "").lower()
        min_dist = float("inf")
        for d in descs:
            dist = levenshtein_distance(desc, d)
            min_dist = min(min_dist, dist)
        if min_dist > DEDUP_MIN_DIST:
            unique_items.append(item)
            descs.append(desc)
    return unique_items


#
# Run Query
#


def run_vector_search_thread(query: str, is_text: bool, items_queue: queue.Queue, query_rows: int):
    """
    Run vector search in a thread.
    """
    # create a HybridQuery
    hybrid_query = create_hybrid_query(query, is_text)

    # run query
    deployed_index_id = VVS_DEPLOYED_INDEX_ID if is_text else VVS_DEPLOYED_INDEX_ID_MM
    response = run_vvs_query(hybrid_query, query_rows, deployed_index_id)

    # add distances
    for _, neighbor in enumerate(response[0]):
        items_queue.put(
            {
                "id": neighbor.id,
                "dense_dist": neighbor.distance,
                "sparse_dist": neighbor.sparse_distance,
            }
        )


def run_queries(
    query_list: list[str],
    feature_names: list[str],
    query_rows: int,
) -> list[Any]:
    """Find items from the e-commerce site with the list of queries"""

    # A list for collecting all results
    items_queue = queue.Queue()
    threads = []

    for query in query_list:
        # Create a thread for text emb search
        text_thread = threading.Thread(
            target=run_vector_search_thread, args=(query, True, items_queue, query_rows)
        )
        text_thread.start()
        threads.append(text_thread)

        # Create a thread for mm emb search
        mm_thread = threading.Thread(
            target=run_vector_search_thread, args=(query, False, items_queue, query_rows)
        )
        mm_thread.start()
        threads.append(mm_thread)

    # join all thread
    for t in threads:
        t.join()

    # merge results
    id_dict = {}
    items = []
    while items_queue.qsize() > 0:
        item = items_queue.get()
        if item["id"] not in id_dict:
            items.append(item)
            id_dict[item["id"]] = item

    # filter with dist threshold if sparse_dist isn't available
    items = [
        f
        for f in items
        if f["dense_dist"] > DENSE_DIST_THRESHOLD
        or (f["sparse_dist"] and f["sparse_dist"] > 0)
    ]

    # fetch feature values
    items = fetch_feature_values(items, feature_names)

    # return the results
    return items


#
# Multimodal item evaluation
#

GEMINI_MODEL = "gemini-2.0-flash"
gemini_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)


class ItemSelectionResult(BaseModel):
    """Schema for item selection result"""

    item_numbers: list[str]
#    reasons: list[str]


def multimodal_filtering_25items(user_intent, item_category, items, user_uploaded_image, queue):
    """Multimodal filtering for 25 items"""

    # Generate image board
    items, item_image_board = generate_item_image_board(items)

    # Convert image_board to bytearray
    item_image_board_data = image_to_bytes(item_image_board)

    # Item list with item number, title and description
    item_listing = ""
    for item in items:
        item_line = "<item>"
        item_line += f"<item_number>#{item['item_number']}</item_number>"
        item_line += f"<item_name>{item['name']}</item_name>"
        item_line += (
            f"<item_description>{item['description'][0:200]}</item_description>"
        )
        item_line += "</item>"
        item_listing += f"{item_line}\n"

    # Evaluation prompt
    eval_prompt_with_user_image = f"""

        Preparation:

        A user is visiting an e-commerce site.  The user's intent is "{user_intent}", and they are
        searching for "{item_category}" that fits the first image shared by the user. Based on the
        first image, predict what kind of profile and preference the user would have.
 
        Question:

        The second image is the items found on the site. The Item List below has the detail of each
        item. From these items, select items that best match with the user's preference, the user 
        intent and item category. Return a list of the selected item numbers 
        (starting with #). 
        Do not include any items irrelevant to the user intent or item category.

        Item List:
        {item_listing}

        """
    eval_prompt_without_user_image = f"""

        Preparation:

        A user is visiting an e-commerce site.  The user's intent is "{user_intent}", and they are
        searching for "{item_category}".

        Question:

        The image is the items found on the site. The Item List below has the detail of each
        item. From these items, select items best match with the user intent and item category. 
        Return a list of the selected item numbers (starting with #).
        Do not include any items irrelevant to the user intent or item category.

        Item List:
        {item_listing}

        """

    # Prepare contents and prompt
    if user_uploaded_image:
        contents = [
            Part.from_bytes(data=user_uploaded_image, mime_type="image/jpeg"),
            eval_prompt_with_user_image,
            Part.from_bytes(data=item_image_board_data, mime_type="image/jpeg"),
        ]
    else:
        contents = [
            eval_prompt_without_user_image,
            Part.from_bytes(data=item_image_board_data, mime_type="image/jpeg"),
        ]

    # Evaluate with Gemini
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ItemSelectionResult,
        ),
    )
    decoded_response = json.loads(response.text)
    item_numbers = decoded_response["item_numbers"]
#    reasons = decoded_response["reasons"]
#    logging.info("multimodal_filtering_25items(): reasons %s", reasons)

    # Filter and rerank items
    items_by_number = {item["item_number"]: item for item in items}
    reranked_items = []
    for item_number in item_numbers:
        item_number = (
            item_number.lstrip("#") if item_number.startswith("#") else item_number
        )
        if item_number in items_by_number:
            reranked_items.append(items_by_number[item_number])
    queue.put(reranked_items)

    # for debug
    # generate file name from user intent and item category
#    filename = f"{user_intent.replace(' ', '_')}_{item_category.replace(' ', '_')}.jpg"
#    storage_client = storage.Client()
#    bucket = storage_client.bucket("gcp-samples-ic0-ac")
#    blob = bucket.blob(filename)
#    blob.upload_from_string(item_image_board_data, content_type="image/jpeg")
#    print(f"File {filename} uploaded.")
#    print(eval_prompt_with_user_image)
#    print(item_numbers)


def multimodal_filtering(user_intent, item_category, items, user_uploaded_image):
    """Multimodal filtering"""

    start_time = time.time()

    # Start a thread of multimodal_rerank_25items for 25 items each
    reranked_queue = queue.Queue()
    threads = []
    for i in range(0, len(items), 25):
        thread = threading.Thread(
            target=multimodal_filtering_25items,
            args=(
                user_intent,
                item_category,
                items[i : i + 25],
                user_uploaded_image,
                reranked_queue,
            ),
        )
        thread.start()
        threads.append(thread)

    # Wait for the threads for upto 5 secs
    for thread in threads:
        thread.join(timeout=5)

    # Collect the results
    reranked_items = []
    while not reranked_queue.empty():
        reranked_items.extend(reranked_queue.get())

    # log elapsed time
    elapsed_time = time.time() - start_time
    logging.info(
        "multimodal_filtering: incoming items: %d, reranked items: %d, elapsed: %.2f sec, ",
        len(items),
        len(reranked_items),
        elapsed_time,
    )
    return reranked_items


def filter_and_rerank_items(
    user_intent: str,
    item_category: str,
    items: list[Any],
    user_uploaded_image: Any,
) -> list[str]:
    """Filtering and Reranking on the items"""

    # remove items without product name
    items = [item for item in items if item["name"] and len(item["name"].strip()) > 0]

    # dedup items
    items = dedup_items(items)

    # multimodal filtering
    items = multimodal_filtering(user_intent, item_category, items, user_uploaded_image)

    # text rerank
    items = text_rerank(
        f"{user_intent} {item_category}",
        items,
        len(items),
    )

    # remove distances
    for item in items:
        del item["dense_dist"]
        del item["sparse_dist"]
        del item["rerank_score"]

    # return the results
    return items
