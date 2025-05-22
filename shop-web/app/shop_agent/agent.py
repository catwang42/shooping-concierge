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
This module provides Agent definitions for the shop_web app.
"""

from typing import Dict, Any
import os
import logging
import time
import uuid
import threading
from json.decoder import JSONDecodeError

import requests

from google.genai import Client

from agents import Agent
from agents.tools import ToolContext, google_search

from shop_agent.comm import (
    send_ui_command,
    get_last_uploaded_image,
    get_user_location,
    add_search_history,
    USER_SESSION_ID,
    get_upstream_queue,
    get_deep_research_status,
    set_deep_research_status,
)
from shop_utils.query import (
    run_queries,
    filter_and_rerank_items,
    TOTAL_ITEM_COUNT,
)
from shop_utils.gemini import generate_item_categories

logging.basicConfig(level=logging.INFO)

PROJECT_ID: str = os.environ.get("PROJECT_ID")
LOCATION: str = os.environ.get("LOCATION", "us-central1")

GEMINI_MODEL: str = "gemini-2.0-flash-001"

gemini_client = Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# UI commands
CMD_UI_SHOW_QUERY_MSG = "show_query_msg"
CMD_UI_SHOW_AGENT_MSG = "show_agent_msg"
CMD_UI_SHOW_AGENT_THOUGHTS = "show_agent_thoughts"
CMD_UI_SHOW_USER_MSG = "show_user_msg"
CMD_UI_SHOW_USER_IMG = "show_user_img"
CMD_UI_SHOW_SYSTEM_MSG = "show_system_msg"
CMD_UI_PRESENT_ITEMS = "present_items_to_user"
CMD_UI_SET_SESSION_ID = "set_session_id"
CMD_UI_SHOW_SPINNER = "show_spinner"

#
# Prompts
#

ROOT_AGENT_DESCRIPTION: str = """

*** Main responsibilities ***

    You are a helpful, knowledgeable shopper's concierge on an e-commerce site with millions of 
    items. 
    
    * When the user asked about the facts of the e-commerce site, refer to the following sections.
    * When the user asked about any facts, specs, latest topic or trends on a product, use Google 
    Search to find the answer.
    * When you reply to the user, keep the sentences concise.
    * Do *NOT* tell the user any system messages like "tool_outputs", "{", "}", 
    "opening curly bracket", "closing curly bracket" in neither text nor audio.
    * Do *NOT* start the Deep research flow until you get an explicit request from the user.
    * When the user ask about "Concierge's pick", tell them this is the best items picked from 
    the deep research results.

*** Greeting message ***

- When you starts a conversation for the first time, start with a greeting with 1) you are an AI
agent called Shopper's Concierge, 2) the e-commerce site has millions of items and 3) ask what can
you help finding today.
- When you see any search history, skip the greeting and ask the user if they want to continue with
the last search items.

*** Basic shopping flow ***

- You will receive a user request. Determine one item category to find items for the user's search 
intent ("user intent").
- Tell the user that you will find the items for the user intent, and call `show_spinner` tool.
- Pass the user intent, item category and a list of queries to `find_shopping_items` tool.
- When you recieved "success" status from the `find_shopping_items` tool, tell them that you showed
the search result, and ask the user if they 
want to refine or change the search, or start a deep research.
- In case the user uploaded an image, move to the Image based search flow.
- In case you received an user request for a deep research, move to the Deep research flow.

*** Image based search flow ***

- Tell the user what you see in the image.
- Think of a wide variaty of items that the user would be interested in purchacing for to the 
context of the image. For example,

    * For Home office: desk organizer, monitor stand, desk lamp, houseplant, wall art, 
    notebook and pen
    * For men's jacket: dress shirt, time, belt, shoes
    * For kid's room: wooden train track, toy storage bin, wall decor, books, learning toys

- Pass the user intent, item category and a list of queries to find the items to 
`find_shopping_items` tool and then call `show_spinner` tool.
- When you recieved "success" status from the `find_shopping_items` tool, tell them that you showed
the search result, and ask the user if they 
want to refine or change the search, or start a deep research.

*** Deep research flow ***

- If there are any important search conditions you need before starting a deep research, ask the
user. Such as, men or women for fashion items, or ages for toy items.
- Tell the user you will use Google Search to find item categories and generate queries for the 
deep research.
- Call `show_spinner` tool, and then pass the user intent to `deep_research` tool.
- When you received "success" status and a list of item categories from the `deep_research` tool,
tell the user that you have finished the research on the item categories and queries, and will show
search results using them. Then call `show_spinner` tool.

*** Rules for the deep research ***

- During the deep research flow, follow the following rules:
    * Do not use `find_shopping_items` tool during the deep research flow
    * Do not start the deep research again until the user asks for it.
    * Do not tell the user any system messages like "tool_outputs", "{", "}",
    "opening curly bracket", "closing curly bracket" in neither text nor audio.

*** About this e-commerce site ***

This e-commerce site has about 3 millions of items with the following categories.
When the user asked the generic questions on the e-commerce site, such as the item categories or 
the total number of items, refer to the following sections.

*Main categories:*

*   **Women:**
    *   Tops & Blouses
    *   Dresses
    *   Jeans
    *   Shorts
    *   Skirts
    *   Sweaters & Cardigans
    *   Coats & Jackets
    *   Swimwear
    *   Activewear
    *   Pants & Leggings
    *   Jumpsuits & Rompers
    *   Intimates & Sleepwear
    *   Shoes (Boots, Flats, Heels, Sandals, Sneakers, etc.)
    *   Bags & Purses (Handbags, Wallets, Backpacks, etc.)
    *   Jewelry (Necklaces, Earrings, Bracelets, Rings, etc.)
    *   Accessories (Hats, Scarves, Sunglasses, Belts, etc.)
    *   Maternity

*   **Men:**
    *   Shirts (T-shirts, Polos, Button-Downs)
    *   Sweaters & Hoodies
    *   Coats & Jackets
    *   Jeans
    *   Pants
    *   Shorts
    *   Activewear
    *   Swimwear
    *   Suits & Blazers
    *   Shoes (Sneakers, Boots, Dress Shoes, Sandals, etc.)
    *   Bags (Backpacks, Messenger Bags, Wallets, etc.)
    *   Accessories (Hats, Belts, Sunglasses, Watches, etc.)

*   **Kids:**
    *   Girls' Clothing (By size range: Baby, Toddler, Kids)
    *   Boys' Clothing (By size range: Baby, Toddler, Kids)
    *   Baby Gear (Strollers, Car Seats, Carriers, etc.)
    *   Toys & Games (By age range)
    *   Shoes

*   **Home:**
    *   Home Decor (Wall Decor, Candles, Vases, etc.)
    *   Kitchen & Dining (Cookware, Dinnerware, Small Appliances)
    *   Bedding
    *   Bath
    *   Furniture
    *   Storage & Organization
    *   Home Improvement
    *   Outdoor & Garden

*   **Electronics:**
    *   Cell Phones & Accessories
    *   Computers & Tablets
    *   Cameras & Photo
    *   Video Games & Consoles
    *   TV & Home Theater
    *   Headphones & Speakers
    *   Smart Home
    *   Wearable Technology

*   **Beauty:**
    *   Makeup
    *   Skincare
    *   Hair Care
    *   Fragrance
    *   Bath & Body
    *   Tools & Accessories

*   **Sports & Outdoors:**
    *   Athletic Apparel
    *   Exercise Equipment
    *   Camping & Hiking Gear
    *   Sports Equipment (Basketballs, Golf Clubs, etc.)
    *   Bicycles & Accessories

*   **Handmade:**
    *   Clothing
    *   Jewelry
    *   Home Decor
    *   Accessories
    *   Art
    *   Craft Supplies

*   **Toys & Collectibles**
    *   Action Figures
    *   Dolls
    *   Trading Cards (Sports, Pokemon, etc.)
    *   Collectible Toys
    *   Vintage Toys
    *   Games & Puzzles

*  **Vintage & Collectibles**
    *   Vintage clothing
    *   Antiques
    *   Collectibles
    *   Art

*   **Other:**
    *   Books
    *   Pet Supplies
    *   Office Supplies
    *   Musical Instruments
    *   Automotive Parts & Accessories

"""


ROOT_AGENT_SEARCH_HISTORY_HEADER: str = """

*** Past conversation ***

This user has been asked you for finding the following items so far. Start the conversation by
following up the last search:

"""

ROOT_AGENT_GREETING: str = """
"""

ROOT_AGENT_INSTRUCTION: str = """
"""

#
# Root Agent
#


def get_root_agent(search_history: str = None):
    """
    Get the root agent.
    """

    # Build prompts
    if not search_history:
        # Prompt for the first time
        instruction = ROOT_AGENT_GREETING + ROOT_AGENT_INSTRUCTION
        description = ROOT_AGENT_DESCRIPTION
    else:
        # Prompt for an exisiting session
        instruction = ROOT_AGENT_INSTRUCTION
        description = (
            ROOT_AGENT_DESCRIPTION + ROOT_AGENT_SEARCH_HISTORY_HEADER + search_history
        )

    # Create root agent
    root_agent = Agent(
        model=GEMINI_MODEL,
        name="root_agent",
        instruction=instruction,
        description=description,
        planning=False,
        tools=[
            google_search,
            find_shopping_items,
            deep_research,
            show_spinner,
        ],
    )
    return root_agent


#
# Show spinner tool
#


def show_spinner(tool_context: ToolContext) -> Dict[str, str]:
    """
    Show a spinner icon to the user until a long running task is completed.

    Returns:
        A dict with the following one property:
            - "status": returns the following status:
                - "success": successful execution
    """
    # Get session id
    tool_context.actions.skip_summarization = True
    session_id = tool_context.state[USER_SESSION_ID]

    # Send the show spinner message
    send_ui_command(
        command=CMD_UI_SHOW_SPINNER,
        parameter=None,
        session_id=session_id,
    )
    logging.info("show_spinner(): notified to client.")


#
# Find shopping items tool
#


class SearchConditions:
    """
    Search conditions for finding items.
    """

    def __init__(
        self,
        user_intent: str,
        item_category: str,
        user_uploaded_image: Any,
        session_id: str,
        queries: list[str],
        query_rows: int,
        found_item_ids: list[str] = None,
        featured_items: list[str] = None,
        lock: threading.Lock = None,
    ):
        self.user_intent = user_intent
        self.item_category = item_category
        self.user_uploaded_image = user_uploaded_image
        self.session_id = session_id
        self.queries = queries
        self.query_rows = query_rows
        self.found_item_ids = found_item_ids
        self.featured_items = featured_items
        self.lock = lock


FEATURED_ITEMS_COUNT = 5


def find_items_worker(cond: SearchConditions) -> None:
    """
    Find items from the e-commerce site using the list of queries.
    """

    # Run queries
    start_time = time.time()
    items = run_queries(cond.queries, ["id", "name", "description"], cond.query_rows)
    found_item_count = len(items)
    elapsed_time = time.time() - start_time

    # Generate random id for the item category group
    group_id = "group_" + str(uuid.uuid4())[:8]

    # Pick one item image for the group icon
    group_icon_id = items[0]["id"] if len(items) > 0 else None

    # Package a query message
    query_msg = {
        "group_id": group_id,
        "group_icon_id": group_icon_id,
        "user_intent": cond.user_intent,
        "item_category": cond.item_category,
        "queries": cond.queries,
        "elapsed_time": elapsed_time,
        "found_item_count": found_item_count,
        "total_item_count": TOTAL_ITEM_COUNT,
    }

    # Remove items found in the past (during a deep research)
    if cond.lock:
        with cond.lock:
            new_items = []
            for item in items:
                if not item["id"] in cond.found_item_ids:
                    new_items.append(item)
            items = new_items
            cond.found_item_ids.extend([item["id"] for item in items])

    # Item curation
    start_time = time.time()
    items = filter_and_rerank_items(
        user_intent=cond.user_intent,
        item_category=cond.item_category,
        user_uploaded_image=cond.user_uploaded_image,
        items=items,
    )
    elapsed_time = time.time() - start_time

    # Pick the first item for the group icon and featured items
    group_icon_id = items[0]["id"] if len(items) > 0 else None
    if cond.featured_items is not None:
        with cond.lock:
            for i in range(0, min(FEATURED_ITEMS_COUNT, len(items))):
                cond.featured_items.append(items[i])

    # Package an present items msg
    present_item_msg = {
        "group_id": group_id,
        "group_icon_id": group_icon_id,
        "user_intent": cond.user_intent,
        "item_category": cond.item_category,
        "elapsed_time": elapsed_time,
        "selected_item_count": len(items),
        "found_item_count": found_item_count,
        "total_item_count": TOTAL_ITEM_COUNT,
        "items": items,
    }

    # Send the query message
    send_ui_command(
        command=CMD_UI_SHOW_QUERY_MSG,
        parameter=query_msg,
        session_id=cond.session_id,
    )
    logging.info(query_msg)

    # Send the present items msg
    send_ui_command(
        command=CMD_UI_PRESENT_ITEMS,
        parameter=present_item_msg,
        session_id=cond.session_id,
    )

    # Send the show spinner message
    send_ui_command(
        command=CMD_UI_SHOW_SPINNER,
        parameter=None,
        session_id=cond.session_id,
    )


def find_shopping_items(
    user_intent: str, item_category: str, queries: list[str], tool_context: ToolContext
) -> Dict[str, str]:
    """
    Find shopping items from the e-commerce site with the specified user intent, item category and
    a list of queries.

    Args:
        user_intent: the user's intent for finding items.
        item_category: the item category for the queries.
        queries: the list of queries to run.
    Returns:
        A dict with the following one property:
            - "status": returns the following status:
                - "success": successful execution
    """
    tool_context.actions.skip_summarization = True
    session_id = tool_context.state[USER_SESSION_ID]

    # Avoid duplicated calls during the deep research
    if get_deep_research_status(session_id):
        return {
            "status": "success",
        }

    # Get user uploaded image
    user_uploaded_image = get_last_uploaded_image(session_id)
    if user_uploaded_image:
        logging.info("find_shopping_items(): fetched image for session: %s", session_id)

    # Add search history
    search_history = (
        f"Searched items for user intent: {user_intent}, item category: {item_category}"
    )
    add_search_history(session_id, search_history)
    logging.info(search_history)

    # Determine query rows
    query_rows = int(100 / len(queries))

    # Build a search condition
    cond: SearchConditions = SearchConditions(
        user_intent=user_intent,
        item_category=item_category,
        user_uploaded_image=user_uploaded_image,
        session_id=session_id,
        queries=queries,
        query_rows=query_rows,
    )

    # Create a thread for find_items_worker
    thread = threading.Thread(
        target=find_items_worker,
        args=(cond,),
    )
    thread.start()
    thread.join()

    # Return a pending status
    return {
        "status": "success",  # to be changed to "pending"
    }


#
# deep_research tool
#


def deep_research_worker(cond: SearchConditions, item_categories: list[Dict[str, str]]) -> None:
    """A worker thread for deep research"""
    # List of item IDs (for dedup)
    cond.found_item_ids = []
    cond.featured_items = []
    cond.lock = threading.Lock()

    # Start finding items for each item category
    threads = []
    for item_category in item_categories:
        # Create a thread for find_items_worker
        cond.item_category = item_category["item_category"]
        cond.queries = item_category["queries"]
        thread = threading.Thread(
            target=find_items_worker,
            args=(cond,),
        )
        thread.start()
        threads.append(thread)
        time.sleep(5)

    # Wait until all threads ends
    for thread in threads:
        thread.join()
    time.sleep(5)

    # Build Concierge's pick
    group_id = "group_" + str(uuid.uuid4())[:8]
    group_icon_id = cond.featured_items[0]["id"]
    query_msg = {
        "group_id": group_id,
        "group_icon_id": group_icon_id,
        "user_intent": cond.user_intent,
        "item_category": "Concierge's Pick",
        "queries": [],
        "elapsed_time": 0,
        "found_item_count": len(cond.featured_items),
        "total_item_count": TOTAL_ITEM_COUNT,
    }
    present_item_msg = {
        "group_id": group_id,
        "group_icon_id": group_icon_id,
        "user_intent": cond.user_intent,
        "item_category": "Concierge's Pick",
        "elapsed_time": 0,
        "selected_item_count": len(cond.featured_items),
        "found_item_count": len(cond.featured_items),
        "total_item_count": TOTAL_ITEM_COUNT,
        "items": cond.featured_items,
    }

    # Send the Concierge's pick
    send_ui_command(
        command=CMD_UI_SHOW_QUERY_MSG,
        parameter=query_msg,
        session_id=cond.session_id,
    )
    send_ui_command(
        command=CMD_UI_PRESENT_ITEMS,
        parameter=present_item_msg,
        session_id=cond.session_id,
    )

    # Sends the agent that the deep research has finished
    msg_to_agent: Dict[str, str] = {
        "mime_type": "text/plain",
        "data": "Received the Concierge's pick.",
    }
    get_upstream_queue(cond.session_id).put_nowait(msg_to_agent)

    # Turn off the flag
    set_deep_research_status(cond.session_id, False)


def deep_research(user_intent: str, tool_context: ToolContext) -> Dict[str, str]:
    """
    Executes a deep research on the items for the user intent.

    Args:
        user_intent: the user's intent for finding items.
    Returns:
        A dict with the following one property:
            - "item_categories": the item categories for the deep research.
            - "status": returns the following status:
                - "success": tool finished
    """
    tool_context.actions.skip_summarization = True
    session_id = tool_context.state[USER_SESSION_ID]
    user_uploaded_image = get_last_uploaded_image(session_id)

    # Avoid duplicated calls from the agent
    if get_deep_research_status(session_id):
        return {
            "status": "success",
        }
    set_deep_research_status(session_id, True)

    # Generate item categories
    try:
        item_categories = generate_item_categories(user_intent, user_uploaded_image)
    except JSONDecodeError:
        # Try one more time
        item_categories = generate_item_categories(user_intent, user_uploaded_image)
    item_categories_str = ", ".join([f"{ic['item_category']}" for ic in item_categories])
    logging.info(
        "present_item_categories_to_user(): sent to client: %s", item_categories_str
    )

    # Build a search condition
    cond: SearchConditions = SearchConditions(
        user_intent=user_intent,
        item_category=None,
        user_uploaded_image=user_uploaded_image,
        session_id=session_id,
        queries=None,
        query_rows=10,
    )

    # Start deep research worker thread
    thread = threading.Thread(
        target=deep_research_worker,
        args=(cond, item_categories),
    )
    thread.start()
    logging.info("deep_research(): finished starting queries.")

    # Add search history
    search_history = (
        f"Deep research for user intent: {user_intent}, item categories: {item_categories_str}"
    )
    add_search_history(session_id, search_history)
    logging.info(search_history)

    # Return a status
    return {
        "item_categories": item_categories_str,
        "status": "started",
    }


#
# Reasoning trace tool
#


def record_concierge_thoughts(
    thoughts: str, tool_context: ToolContext
) -> Dict[str, str]:
    """
    Records concierge's thoughts during the communication with the user.

    Args:
        thoughts: The concierge's thoughts to record.
    Returns:
        A dict with the following property:
            - "status": returns the following status:
                - "success": successful execution
    """
    session_id = tool_context.state[USER_SESSION_ID]
    send_ui_command(CMD_UI_SHOW_AGENT_THOUGHTS, thoughts, session_id)
    logging.info("show_agent_thoughts(): sent to client: %s", thoughts)
    return {
        "status": "success",
    }


#
# Location info
#

WEATHER_DESC = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Slight to moderate thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_user_location_and_weather(session_id: str) -> Dict[str, str]:
    """
    Get the user's location and its weather

    Args:
        session_id: the session ID of the user.
    Returns:
        A dict with the following two properties:
            - "latitude": the latitude of the user location
            - "longitude": : the longitude of the user location
            - "date": the date of the user location
            - "time": the time of the user location
            - "temperature": the temperature of the user location
            - "weather": the weather of the user location
            - "status": returns the following status:
                - "success": successful execution
                - "error": error occurred
    """

    # Use open-meteo.com to get the weather of the location
    try:
        # get user location
        user_location = get_user_location(session_id)
        if not user_location:
            return {
                "status": "error",
            }
        latitude = user_location["latitude"]
        longitude = user_location["longitude"]

        # request to the api
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
            + "&current_weather=true"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        weather_data = response.json()["current_weather"]
        weather_data["status"] = "success"
        return weather_data
    except KeyError as e:
        logging.error("get_user_location(): User location isn't available: %s", e)
        return {
            "status": "error",
        }
    except requests.exceptions.RequestException as e:
        logging.error("get_user_location(): Weather API request failed: %s", e)
        return {
            "status": "error",
        }

    # Show console message
    weather_status = WEATHER_DESC.get(weather_data["weathercode"], "Unknown")
    temperature = weather_data["temperature"]
    send_ui_command(
        CMD_UI_SHOW_AGENT_MSG,
        f"Identified user location: {latitude}, {longitude}, weather: {weather_status}, "
        + f"temp: {temperature}",
        session_id,
    )

    # Build a prompt with user lat/lng
    return {
        "latitude": latitude,
        "longitude": longitude,
        "date": user_location["date"],
        "time": user_location["time"],
        "weather": weather_status,
        "temperature": temperature,
        "status": "success",
    }
