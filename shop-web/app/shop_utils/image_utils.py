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
""" Provides utils for image processing """

import io
import threading
import queue
import base64
from io import BytesIO
from typing import Dict, Any
import logging

from PIL import Image, ImageDraw, ImageFont
import requests

logging.basicConfig(level=logging.INFO)

# Load mono space font
font = ImageFont.truetype("./shop_utils/FreeMonoBold.ttf", 32)  # Make sure this path is correct
IMAGE_LOADING_TIMEOUT = 2

def load_item_image(id: str, width: int, height: int) -> bytes:
    """Load item image from Mercari"""
    try:
        # Download the item image
        image_url = f"https://u-mercari-images.mercdn.net/photos/{id}_1.jpg?w={width}&h={height}&fitcrop"
        response = requests.get(image_url, stream=True, timeout=IMAGE_LOADING_TIMEOUT)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.info("generate_item_tile(): Image download failed: %s", str(e))
        return None
    except Exception:
        logging.error(
            "generate_item_tile(): Image processing failed: %s", exc_info=True
        )
        return None


def generate_item_tile(item):
    """Generate an item tile"""
    # Load the item image
    item_image_bytes = load_item_image(item["id"], 200, 200)
    if not item_image_bytes:
        return None
    item_image = Image.open(io.BytesIO(item_image_bytes))

    # Paste a white background for the label at top left
    label_bg = Image.new("RGB", (60, 40), (230, 230, 230))
    item_image.paste(label_bg, (0, 0))

    # Paste an item number label at 0, 200 of item_image
    draw = ImageDraw.Draw(item_image)
    label_text = f"#{item['item_number']}"
    draw.text((0, 0), label_text, font=font, fill=(0, 0, 0))

    return item_image



def generate_item_image_board(items: list[Dict[str, Any]]):
    """Generate item image board for 5 x 5 = 25 items"""

    # Start download threads
    image_tiles = []
    image_queue = queue.Queue()
    threads = []
    item_number = 0
    for item in items:
        item.update({"item_number": str(item_number)})
        item_number += 1
        thread = threading.Thread(
            target=lambda q, item: q.put(generate_item_tile(item)),
            args=(image_queue, item),
        )
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect images from the queue
    while not image_queue.empty():
        img = image_queue.get()
        if img is not None:
            image_tiles.append(img)

    # Create a background image for 1000 x 1000
    image_board = Image.new("RGB", (1000, 1000), (255, 255, 255))

    # Paste the image tiles to bg_image with 5 tiles x 5 rows
    for y in range(0, 5):
        for x in range(0, 5):
            if len(image_tiles) > 0:
                img = image_tiles.pop(0)
                image_board.paste(img, (x * 200, y * 200))
    return items, image_board


def image_to_bytes(image: Image) -> bytes:
    """Convert PIL Image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()


def png_to_jpeg(png_b64: str) -> str:
    """ Converts image/png;base64 to image/jpeg;base64 """
    image = Image.open(BytesIO(png_b64))
    image = image.convert("RGB")
    jpeg_data = BytesIO()
    image.save(jpeg_data, "JPEG")
    jpeg_b64 = base64.b64encode(jpeg_data.getvalue()).decode("utf-8")
    return jpeg_b64
