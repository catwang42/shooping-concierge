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
This module provides communication management between the agent and user.
"""

import os
import json
import base64
import logging
import asyncio
import uuid
import time
import traceback
import threading
import re
from typing import Any, Dict, AsyncGenerator, Optional, TypedDict

from quart import Websocket

from google.genai.types import (
    Blob,
    Content,
    Part,
)

from agents.agents import LiveRequestQueue
from agents.runners import Runner
from agents.artifacts import InMemoryArtifactService
from agents.sessions.in_memory_session_service import InMemorySessionService
from agents.events import Event
from shop_utils.gemini import generate_image
from shop_utils.query import fetch_feature_values


logging.basicConfig(level=logging.INFO)

# Agent commands
CMD_AGENT_SET_USER_LOCATION = "set_user_location"
CMD_AGENT_SET_AUDIO = "set_audio"  # "True" or "False"
CMD_AGENT_GENERATE_IMAGE = "generate_image"

# UI commands
CMD_UI_SHOW_QUERY_MSG = "show_query_msg"
CMD_UI_SHOW_SYSTEM_MSG = "show_system_msg"
CMD_UI_SET_SESSION_ID = "set_session_id"
CMD_UI_SHOW_USER_IMG = "show_user_img"


#
# Session and communication management
#

# User session objects
user_sessions: Dict[str, Dict[str, Any]] = {}
USER_SESSION: str = "session"
USER_SESSION_ID: str = "session_id"
USER_SESSION_DEEP_RESEARCH_IN_PROGRESS: str = "deep_research_in_progress"
USER_SESSION_UPSTREAM_QUEUE: str = "upstream_queue"
USER_SESSION_DOWNSTREAM_QUEUE: str = "downstream_queue"
USER_SESSION_USER_LOCATION: str = "user_location"
USER_SESSION_AF_LIVE_REQUEST_QUEUE: str = "af_live_request_queue"
USER_SESSION_LAST_UPLOADED_IMAGE: str = "last_uploaded_image"
USER_SESSION_SEARCH_HISTORY: str = "search_history"
USER_SESSION_IS_AUDIO: str = "is_audio"
MAX_RETRIES_PER_SESSION: int = 10


class MessageToUser(TypedDict, total=False):
    """Message to user"""

    mime_type: str
    data: Dict[str, Any]
    turn_complete: bool
    interrupted: bool


class MessageToAgent(TypedDict, total=False):
    """Message to agent"""

    mime_type: str
    data: Dict[str, Any]


def get_downstream_queue(session_id: str) -> asyncio.Queue:
    """Get or create downstream queue"""
    if not session_id in user_sessions:
        raise ValueError("get_downstream_queue(): session not found: " + session_id)
    if USER_SESSION_DOWNSTREAM_QUEUE in user_sessions[session_id]:
        downstream_queue = user_sessions[session_id][USER_SESSION_DOWNSTREAM_QUEUE]
    else:
        downstream_queue = asyncio.Queue()
        user_sessions[session_id][USER_SESSION_DOWNSTREAM_QUEUE] = downstream_queue
    return downstream_queue


def get_upstream_queue(session_id: str) -> asyncio.Queue:
    """Get or create upstream queue"""
    if not session_id in user_sessions:
        raise ValueError("get_upstream_queue(): session not found: " + session_id)
    if USER_SESSION_UPSTREAM_QUEUE in user_sessions[session_id]:
        upstream_queue = user_sessions[session_id][USER_SESSION_UPSTREAM_QUEUE]
    else:
        upstream_queue = asyncio.Queue()
        user_sessions[session_id][USER_SESSION_UPSTREAM_QUEUE] = upstream_queue
    return upstream_queue


def get_live_request_queue(session_id: str) -> LiveRequestQueue:
    """Get live request queue"""
    if not session_id in user_sessions:
        raise ValueError("get_live_request_queue(): session not found: " + session_id)
    if not USER_SESSION_AF_LIVE_REQUEST_QUEUE in user_sessions[session_id]:
        raise ValueError(
            "get_live_request_queue(): live_request_queue not found: " + session_id
        )
    return user_sessions[session_id][USER_SESSION_AF_LIVE_REQUEST_QUEUE]


def get_last_uploaded_image(session_id: str) -> Any:
    """Get last uploaded image"""
    if not session_id in user_sessions:
        raise ValueError("get_last_uploaded_image(): session not found: " + session_id)
    if not USER_SESSION_LAST_UPLOADED_IMAGE in user_sessions[session_id]:
        return None
    return user_sessions[session_id][USER_SESSION_LAST_UPLOADED_IMAGE]


def get_user_location(session_id: str) -> Dict[str, Any]:
    """Get user location"""
    if not session_id in user_sessions:
        raise ValueError("get_user_location(): session not found: " + session_id)
    if not USER_SESSION_USER_LOCATION in user_sessions[session_id]:
        return None
    return user_sessions[session_id][USER_SESSION_USER_LOCATION]


def send_ui_command(command: str, parameter: str, session_id: str) -> None:
    """
    Send UI commands to the client.
    """

    # Create a message
    msg: MessageToUser = {
        "mime_type": "application/json",
        "data": {
            "command": command,
            "parameter": parameter,
        },
        "turn_complete": False,
        "interrupted": False,
    }

    # Put to the queue
    downstream_queue = get_downstream_queue(session_id)
    downstream_queue.put_nowait(msg)
    logging.info("send_ui_command(): sent to client: %s", command)


def add_search_history(session_id: str, search_history: str) -> None:
    """Add search history"""
    user_sessions[session_id][USER_SESSION_SEARCH_HISTORY] += search_history + "\n"


def get_deep_research_status(session_id: str) -> bool:
    """Get deep research in progress"""
    if USER_SESSION_DEEP_RESEARCH_IN_PROGRESS in user_sessions[session_id]:
        return user_sessions[session_id][USER_SESSION_DEEP_RESEARCH_IN_PROGRESS]
    return False


def set_deep_research_status(session_id: str, status: bool) -> None:
    """Set deep research in progress"""
    user_sessions[session_id][USER_SESSION_DEEP_RESEARCH_IN_PROGRESS] = status


#
# Gemini API Keys rotation
#

gemini_api_keys: list[str] = []

# Open "keys.txt" and get a list of each line
with open("keys.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    gemini_api_keys = [line.strip() for line in lines]
    gemini_api_keys = [key for key in gemini_api_keys if len(key) > 0]


def set_gemini_api_key() -> None:
    """Pick one Gemini API key from GEMINI_API_KEYS and set it to GOOGLE_API_KEY"""
    if os.environ["GOOGLE_GENAI_USE_VERTEXAI"] == "0":
        # If it's not using Vertex AI, set Gemini API keys
        key = gemini_api_keys.pop(0)
        gemini_api_keys.append(key)
        os.environ["GOOGLE_API_KEY"] = key


#
# Image generation worker
#


def generate_image_worker(
    item_id: str, user_uploaded_image: Any, session_id: str
) -> None:
    """
    Generates an image with specified item and user uploaded image and send it back to the user
    """
    # Generate an image
    jpeg_b64 = generate_image(item_id, user_uploaded_image)

    # Send it back to the user
    if jpeg_b64:
        send_ui_command(
            command=CMD_UI_SHOW_USER_IMG, parameter=jpeg_b64, session_id=session_id
        )
        logging.info("generate_image_worker(): image generated and sent.")


#
# Agent stream management
#

# AF State keys
AF_APP_NAME: str = "shop-web"

# AF services
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


async def send_message_to_agent(
    message_to_agent: MessageToAgent, session_id: str
) -> None:
    """
    Send a message to the agent.

    Args:
        content: a dict with:
            mime_type: "text/plain", "audio/pcm", "image/jpeg" or "application/json"
            data: the content to send. Use base64 encoding for audio and image.
        session_id: the session ID of the user.
    """
    # get chunk
    mime_type: str = message_to_agent["mime_type"]
    data: str = message_to_agent["data"]
    live_request_queue = user_sessions[session_id][USER_SESSION_AF_LIVE_REQUEST_QUEUE]

    # sent the content to live_request_queue for the session
    if mime_type == "text/plain":
        # Send text to agent
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        logging.info("send_message_to_agent(): sent text to agent: %s", data)

    elif mime_type == "audio/pcm":
        # Send audio to agent
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
    #       logging.info("send_message_to_agent(): sent %s to agent: %s bytes", mime_type, len(data))

    elif mime_type == "image/jpeg":
        # Send image to agent
        live_request_queue.send_realtime(Blob(data=data, mime_type=mime_type))

        # Store the image to user session
        user_sessions[session_id][USER_SESSION_LAST_UPLOADED_IMAGE] = data

        # Send image back to the client console
        send_ui_command(
            command=CMD_UI_SHOW_USER_IMG, parameter=data, session_id=session_id
        )

        # Wait before asking about the image (otherwise Gemini talks about a previous image)
        await asyncio.sleep(1)

        # Send msg to agent to analyze the image
        img_upload_prompt = "Image uploaded."
        msg_to_agent: MessageToAgent = {
            "mime_type": "text/plain",
            "data": img_upload_prompt,
        }
        await get_upstream_queue(session_id).put(msg_to_agent)

    #        logging.info(
    #            "upstream_worker(): sent %s to agent: %s bytes", mime_type, len(data)
    #        )

    elif mime_type == "application/json":
        # Process agent command
        logging.info("upstream_worker(): received: %s", str(message_to_agent))
        if data["command"] == CMD_AGENT_SET_USER_LOCATION:
            # set user location to the state
            user_sessions[session_id][USER_SESSION_USER_LOCATION] = data["parameter"]
        elif data["command"] == CMD_AGENT_SET_AUDIO:
            user_sessions[session_id][USER_SESSION_IS_AUDIO] = data["parameter"]
            raise ValueError("Audio mode is changed to: " + str(data["parameter"]))
        elif data["command"] == CMD_AGENT_GENERATE_IMAGE:
            # Start a thread with generate_image_worker
            item_id = data["parameter"]
            user_uploaded_image = get_last_uploaded_image(session_id)
            if user_uploaded_image:
                thread = threading.Thread(
                    target=generate_image_worker,
                    args=(item_id, user_uploaded_image, session_id),
                )
                thread.start()

            # Let the agent selling the item to the user
            items = fetch_feature_values([{"id": item_id}], ["name", "description"])
            item_name_desc = \
                f"Item name: {items[0]["name"]}, Item description: {items[0]["description"]}"
            msg_to_agent: MessageToAgent = {
                "mime_type": "text/plain",
                "data": f"Can you explain this? In 30 words. {item_name_desc}",
            }
            await get_upstream_queue(session_id).put(msg_to_agent)


def create_message_to_user(event: Event) -> None:
    """Creates a MessageToUser object from an Event object."""
    # Read the Content and its first Part
    part: Part = event.content and event.content.parts and event.content.parts[0]
    if not part:
        return None

    # Build a MessageToUser
    msg_to_user: MessageToUser = {
        "turn_complete": event.turn_complete,
        "interrupted": event.interrupted,
        "mime_type": None,
        "data": None,
    }
    if event.interrupted:
        logging.info("create_message_to_user(): interrupted")

    # Check if it's audio
    is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
    if is_audio:
        audio_data: Optional[bytes] = part.inline_data and part.inline_data.data
        if audio_data:
            msg_to_user["mime_type"] = "audio/pcm"
            msg_to_user["data"] = base64.b64encode(audio_data).decode("ascii")
            return msg_to_user
    else:
        # It's text
        msg_to_user["mime_type"] = "text/plain"

    # Check if it's an interruption
    if event.interrupted:
        return msg_to_user

    # Skip if it's a partial text
    if event.partial:
        return None

    # Get the text
    text: str = event.content and event.content.parts and event.content.parts[0].text

    # Check if it's empty
    if not text:
        return None

    # Remove system words accidentally generated from Gemini (to be removed)
    for system_word in [
        r"tool_outputs",
        r"tool_code",
        r"'status': 'success'",
        r"'status': 'error'",
        r"```",
        r"\{",
        r"\}",
        r"print\(.*\)",
    ]:
        text = re.sub(system_word, "", text)

    # check if the text is empty
    text = text.strip()
    if len(text) == 0:
        text = None
    msg_to_user["data"] = text

    # Check if data is empty
    if msg_to_user["data"] is None:
        return None
    return msg_to_user


async def downstream_queue_producer(
    live_events: AsyncGenerator[Event, None], session_id: str
) -> None:
    """
    Gets messages from the agent and put it the downstream queue
    """
    while True:
        async for event in live_events:
            # Send the msg to the client
            msg_to_user: MessageToUser = create_message_to_user(event)
            if not msg_to_user:
                await asyncio.sleep(0)
                continue
            await get_downstream_queue(session_id).put(msg_to_user)
            await asyncio.sleep(0)

            # logging
            msg_log = f"{len(msg_to_user["data"])} bytes"
            logging.info("downstream_queue_producer(): sent to client: %s", msg_log)


async def upstream_queue_consumer(session_id: str) -> None:
    """
    Gets messages from the upstream_queue and send it to the agent.
    """

    last_upstream_log_time = 0
    upstream_bytes = 0

    while True:
        upstream_queue = get_upstream_queue(session_id)
        msg_to_agent: MessageToAgent = await upstream_queue.get()

        # Logging
        if msg_to_agent["mime_type"] == "audio/pcm":
            # logging audio/pcm stream bandwidth
            upstream_bytes += len(msg_to_agent["data"])
            elapsed_time = time.time() - last_upstream_log_time
            bps = upstream_bytes * 8 / elapsed_time / 1024
            bps_str = f"{bps:.2f} Kbps"
            if elapsed_time > 0.5:
                upstream_bytes = 0
                last_upstream_log_time = time.time()
                logging.info("upstream_queue_consumer(): sent to agent: %s", bps_str)
        elif msg_to_agent["mime_type"] == "text/plain":
            logging.info(
                "upstream_queue_consumer(): sent to agent: %s, %s",
                msg_to_agent["mime_type"],
                msg_to_agent["data"],
            )
        else:
            logging.info(
                "upstream_queue_consumer(): sent to agent: %s",
                msg_to_agent["mime_type"],
            )

        await send_message_to_agent(msg_to_agent, session_id)
        upstream_queue.task_done()

        await asyncio.sleep(0)


async def start_agent_session(session_id: str) -> None:
    """
    Starts agent session
    """

    # Set a Gemini API Key
    set_gemini_api_key()

    # Create AF serviece and store them to user_sessions
    live_request_queue = LiveRequestQueue()
    user_sessions[session_id][USER_SESSION_AF_LIVE_REQUEST_QUEUE] = live_request_queue

    # Get or create an AF session
    session = session_service.create_session(
        app_name=AF_APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )
    user_sessions[session_id][USER_SESSION] = session
    session.state[USER_SESSION_ID] = session_id

    # Create or get search history
    if not USER_SESSION_SEARCH_HISTORY in user_sessions[session_id]:
        user_sessions[session_id][USER_SESSION_SEARCH_HISTORY] = ""
        search_history = None
    else:
        search_history = user_sessions[session_id][USER_SESSION_SEARCH_HISTORY]
    logging.info(
        "start_agent_session(): search_history: %s",
        search_history if search_history else "None",
    )

    # Create a Runner
    from shop_agent.agent import get_root_agent

    is_audio = user_sessions[session_id][USER_SESSION_IS_AUDIO]
    response_modalities: list[str] = ["AUDIO"] if is_audio else ["TEXT"]
    runner = Runner(
        app_name=AF_APP_NAME,
        agent=get_root_agent(search_history),
        response_modalities=response_modalities,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    # Connect with AF Runner
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
    )
    logging.info(
        "start_agent_session(): connected. is_audio: %s, session_id: %s, total sessions: %s",
        str(is_audio),
        session_id,
        len(user_sessions),
    )

    # Clear queues (and the first message if needed)
    clear_queues(session_id)
    if search_history:
        initial_msg_to_agent: MessageToAgent = {
            "mime_type": "text/plain",
            "data": "Can we continue the shopping session?",
        }
        await get_upstream_queue(session_id).put(initial_msg_to_agent)
    else:
        initial_msg_to_agent: MessageToAgent = {
            "mime_type": "text/plain",
            "data": " ",
        }
        await get_upstream_queue(session_id).put(initial_msg_to_agent)

    # Send the session_id to the client
    send_ui_command(CMD_UI_SET_SESSION_ID, session_id, session_id)
    logging.info(
        "start_user_session(): connected. session_id: %s, total sessions: %s",
        session_id,
        len(user_sessions),
    )

    # Start upstream, downstream and ui_command tasks
    downstream_queue_producer_task: asyncio.Task = asyncio.create_task(
        downstream_queue_producer(live_events, session_id)
    )
    upstream_queue_consumer_task: asyncio.Task = asyncio.create_task(
        upstream_queue_consumer(session_id)
    )
    logging.info("start_agent_session(): tasks started.")

    # Wait until the tasks finishes
    tasks = [downstream_queue_producer_task, upstream_queue_consumer_task]

    # Wait until either task finishes or raises an exception
    done_tasks, pending_tasks = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_EXCEPTION,
    )
    logging.info("start_agent_session(): tasks done.")

    # Close the queue
    live_request_queue.close()

    # Cancel pending tasks
    for task in pending_tasks:
        task.cancel()

    # Log any exceptions from the done tasks
    for task in done_tasks:
        if task.exception():
            exp = task.exception()
            traceback.print_exception(type(exp), exp, exp.__traceback__)
            logging.error(
                "start_agent_session(): task raised an exception: %s", task.exception()
            )


#
# User communication management
#


async def downstream_queue_consumer(
    client_websocket: Websocket, session_id: str
) -> None:
    """
    Gets messages from the downstream queue and send it to the client websocket.
    """
    while True:
        downstream_queue = get_downstream_queue(session_id)
        msg_to_user: MessageToUser = await downstream_queue.get()
        msg_to_user_json: str = json.dumps(msg_to_user)
        await client_websocket.send(msg_to_user_json)
        downstream_queue.task_done()
        await asyncio.sleep(0)
        logging.info(
            "downstream_queue_consumer(): sent to client: %s", msg_to_user["mime_type"]
        )


async def upstream_queue_producer(client_websocket: Websocket, session_id: str) -> None:
    """
    Gets messages from the client websocket and put it to the upstream queue.
    """
    while True:
        msg_to_agent_json: str = await client_websocket.receive()
        msg_to_agent: MessageToAgent = json.loads(msg_to_agent_json)
        if msg_to_agent["mime_type"] == "text/plain":
            logging.info(
                "upstream_queue_producer(): received from client: %s",
                msg_to_agent["data"],
            )
        upstream_queue = get_upstream_queue(session_id)
        await upstream_queue.put(msg_to_agent)
        await asyncio.sleep(0)


def clear_queues(session_id: str) -> None:
    """
    Clears the queues
    """

    # Clear the downstream queue
    downstream_queue = get_downstream_queue(session_id)
    while True:
        try:
            downstream_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

    # Clear the upstream queue
    upstream_queue = get_upstream_queue(session_id)
    while True:
        try:
            upstream_queue.get_nowait()
        except asyncio.QueueEmpty:
            break


async def start_user_session(client_websocket: Websocket) -> None:
    """
    Starts user session
    """

    # Create a session
    session_id = uuid.uuid4().hex[:8]
    user_sessions[session_id] = {
        USER_SESSION_ID: session_id,
    }

    # Waits for the first set audio command
    while True:
        try:
            msg_json = await client_websocket.receive()
            msg_to_agent: MessageToAgent = json.loads(msg_json)
            if msg_to_agent["mime_type"] == "application/json":
                if msg_to_agent["data"]["command"] == CMD_AGENT_SET_AUDIO:
                    is_audio = msg_to_agent["data"]["parameter"]
                    user_sessions[session_id][USER_SESSION_IS_AUDIO] = is_audio
                    logging.info(
                        "start_user_session(): audio command received:" + str(is_audio)
                    )
                    break
        except asyncio.CancelledError:
            return

    # Start tasks
    downstream_queue_consumer_task: asyncio.Task = asyncio.create_task(
        downstream_queue_consumer(client_websocket, session_id)
    )
    upstream_queue_producer_task: asyncio.Task = asyncio.create_task(
        upstream_queue_producer(client_websocket, session_id)
    )

    # Start/restart the agent session until client websocket closed
    try:
        retry_count = 0
        while retry_count < MAX_RETRIES_PER_SESSION:
            retry_count += 1

            # Start agent session
            await start_agent_session(session_id)

            # retry
            await asyncio.sleep(1)
            logging.info(
                "start_user_session(): reconnecting. retry_count: %s", retry_count
            )

    # Catch client websocked closing
    except asyncio.CancelledError:
        downstream_queue_consumer_task.cancel()
        upstream_queue_producer_task.cancel()
        logging.info("start_user_session(): client websocket closed.")

    # Catch any other exceptions
    except Exception:
        logging.error("start_user_session(): Unexpected error:", exc_info=True)
        # Handle the exception (e.g., close the connection, log the error)

    finally:
        # Delete the user session
        del user_sessions[session_id]
        logging.info(
            "start_user_session(): user session closed. Total sessions: %s",
            len(user_sessions),
        )


def send_message_to_agent_from_http(
    msg_to_agent: MessageToAgent, session_id: str
) -> None:
    """
    Send a message to the agent by http request (mainly for image upload from the smartphone)
    """
    # send to agent
    get_upstream_queue(session_id).put_nowait(msg_to_agent)
