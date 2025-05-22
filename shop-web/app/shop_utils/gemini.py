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
This module provides Gemini multimodal capabilities.
"""

import os
from typing import Any
import logging
import json
import re

from pydantic import BaseModel

from google import genai
from google.genai.types import (
    Part,
    GenerateContentConfig,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    Tool,
    GoogleSearch,
)

from google.cloud import aiplatform
from shop_utils.image_utils import (
    load_item_image,
    generate_item_image_board,
    image_to_bytes,
    png_to_jpeg,
)

logging.basicConfig(level=logging.INFO)

#
# Vertex AI init
#

PROJECT_ID: str = os.environ.get("PROJECT_ID")
LOCATION: str = os.environ.get("LOCATION", "us-central1")

aiplatform.init(project=PROJECT_ID, location=LOCATION)


#
# Image generation
#

IMAGE_GEN_GEMINI_MODEL = "gemini-2.0-flash"


IMAGE_GEN_PROMPT = """
You are a shopper's concierge of an e-commerce site, and now one user interested in the item in the
first image and wonder if it fits well with the second image uploaded by the user. Can you
generate a new image to show how the item can be look good when it's placed in the user image? 
You must comply with the following conditions: 1) find the best area for the item in the user's 
image to avoid covering with any existing items, and 2) place the item in a very natural fit, 
sizing, lighting and perspective (by correcting the item's perspective) as if the item is 
physically placed in the user image, and 3) retaining the entire background and surrounding 
objects of the user image without adding or changing anything, and 4) avoid making it look like 
an unnatural generated image.    
"""

GEMINI_MODEL = "gemini-2.0-flash-001"
IMAGE_GEN_GEMINI_MODEL = "gemini-2.0-flash-exp"
gemini_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# TODO: Trying to allow generating people image but doesn't work yet
safety_settings = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_NONE,
    ),
]


def generate_image(item_id: str, user_uploaded_image: Any) -> str:
    """
    Generates an image by placing the specified it to the user uploaded image.
    The generated image will be returned as base64 encoded jpeg.
    """

    # Get item image
    item_image = load_item_image(item_id, 400, 400)
    if item_image is None:
        logging.error("generate_image(): Item image could not be loaded.")
        return None

    # Build prompt
    contents = [
        Part.from_bytes(data=item_image, mime_type="image/jpeg"),
        Part.from_bytes(data=user_uploaded_image, mime_type="image/jpeg"),
        IMAGE_GEN_PROMPT,
    ]

    # Generate image
    response = gemini_client.models.generate_content(
        model=IMAGE_GEN_GEMINI_MODEL,
        contents=contents,
        config=GenerateContentConfig(
            response_modalities=["Text", "Image"],
            safety_settings=safety_settings,
        ),
    )

    # Extract the png image
    candidate = response.candidates[0]
    if not candidate.content:
        logging.error("generate_image(): No content generated: %s", candidate)
        return None

    png_b64 = None
    for part in candidate.content.parts:
        if part.inline_data and part.inline_data.mime_type == "image/png":
            image_data_b64 = part.inline_data.data
            logging.info("generate_image(): image generated.")
            png_b64 = image_data_b64
    if not png_b64:
        return None

    # Convert png_data to jpeg using PIL
    jpeg_b64 = png_to_jpeg(png_b64)
    return jpeg_b64


class ItemSelectionResult(BaseModel):
    """Schema for item selection result"""

    item_numbers: list[str]


#    reasons: list[str]


def multimodal_filtering_25items(
    user_intent, item_category, items, user_uploaded_image, queue
):
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

    prompt_intro = f"""

        Preparation:

        You are a knowledgeable shopper's concierge on an e-commerce site with millions of items. 
        The user's intent is "{user_intent}", and they are searching for items in the item category
        "{item_category}".
    """

    prompt_with_image = f"""

        Question:

        The first image is the image shared by the user as a context of this item search.
        The second image is the items found on the site. The Item List below has the detail of
        each item.
        
        From the items in the second image, select items that exactly match with the user's intent,
        the item category, and the context of the first image. Return a list of the selected 
        item numbers (starting with #).
        Do not include any items irrelevant to the user intent or item category.

        Item List:
        {item_listing}
        """

    prompt_without_image = f"""

        Question:

        The image is the items found on the site. The Item List below has the detail of each
        item. From these items, select items that exactly match with both the user's intent and the
        item category. Return a list of the selected item numbers (starting with #).
        Do not include any items irrelevant to the user intent or item category.

        Item List:
        {item_listing}
        """

    # Prepare contents and prompt
    contents = [prompt_intro]
    if user_uploaded_image:
        contents.append(prompt_with_image)
        contents.append(Part.from_bytes(data=user_uploaded_image, mime_type="image/jpeg"))
    else:
        contents.append(prompt_without_image)
    contents.append(Part.from_bytes(data=item_image_board_data, mime_type="image/jpeg"))

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
#    print(item_numbers

#
# Deep Research
#


ITEM_CATEGORY_COUNT = 5
QUERY_COUNT = 20

def generate_item_categories(user_intent: str, user_uploaded_image: bytes) -> list[dict[str, str]]:
    """Generates item categories"""

    prompt = f"""
    You are a knowledgeable shopper's concierge on an e-commerce site with millions of items. 

    You will generate a list of item categories and queries for the user's intent: '{user_intent}'.

    Use the Google Search to research on what kind of items people find useful for the user intent,
    and create a list of {ITEM_CATEGORY_COUNT} diversed and interesting item categories for finding
     a wide variety of items for the user intent. Avoid listing up similar item categories. 

    Also, generate {QUERY_COUNT} diversed queries for each item category.

    Answer in a JSON format in this example:

    [
        {{
            "item_category": "Pixel 7 smartphone",
            "queries": [
                "query string1",
                "query string2",
                "query string3"
            ]
        }},
        {{
            "item_category": "Cases & Covers",
            "queries": [
                "query string1",
                "query string2",
                "query string3"
            ]
        }}
    ]

    Examples of the list of item categories:
        * For user query "Pixel 7", item categories may include: 
            * Pixel 7 smartphone
            * Cases & Covers
            * Screen Protectors & Lens Protection
            * Chargers
            * Audio and Accessories
            * Mounts & Holders
            * Photography and Videography gears
            * Fitness & Wearables
            * Gaming Accessories
        * For user query "Warm clothes for winter", item categories may include:
            * Coats & Outerwear
            * Sweaters & Knits
            * Bottoms and Footeare
            * Accessories
            * Wears for winter activities and sports
            * Handmade & artisan winter wear
            * Loungewear & cozy comfort
        * For user query "Birthday present for my son", item categories may include:
            * Creative Toys & Arts
            * Active Play & Outdoor Fun
            * Educational Toys & Games
            * Role Play & Pretend Play
            * Books & Media
            * Experiences
            * Room Decor & Furnishings
        * For user query "Organize kids' clutter", item categories may include:
            * Themed Storage
            * Multi-Functional & Space-Saving Storage
            * Clear/Transparent Storage
            * Creative Labeling & Personalization
            * Furniture Designed for Organization
            * Activity-Specific Organization
            * Educational & Game-Based Organization Tools
    """

    # Prepare contents and prompt
    contents = [
        prompt,
    ]
    if user_uploaded_image:
        contents.append("User uploaded image:")
        contents.append(
            Part.from_bytes(data=user_uploaded_image, mime_type="image/jpeg")
        )

    # Evaluate with Gemini
    google_search_tool = Tool(google_search=GoogleSearch())
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=GenerateContentConfig(
            tools=[google_search_tool],
        ),
    )

    # Extract a list of item categories
    # (as the controlled generation is not supported by the google search tool)
    match = re.search(r"(\[.*\])", response.text, re.DOTALL)
    item_categories = json.loads(match.group(0))
    return item_categories


# testing
if __name__ == "__main__":

    # test generating item categories
    user_intent = "Find birthday present for my 10 years old son"
    item_categories = generate_item_categories(user_intent, None)
    print(item_categories)
