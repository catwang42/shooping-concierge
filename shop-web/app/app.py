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
This module provides a Quart web application that acts as a proxy
for the Gemini API, handling WebSocket connections for text and audio.
"""

import logging
import os

from quart import Quart, websocket, send_from_directory, Response, request, redirect
from quart_cors import cors

from shop_agent.comm import start_user_session, send_message_to_agent_from_http

logging.basicConfig(level=logging.INFO)

QUART_DEBUG_MODE: bool = os.environ.get("QUART_DEBUG_MODE") == "True"
RESOURCES_URL: str = "https://cloud.google.com/vertex-ai/docs/vector-search/overview"


#
# Quart
#

app: Quart = Quart(__name__, static_folder="./dist", static_url_path="/")

# for allowing dev access
app = cors(app, allow_origin="*")


@app.route("/")
async def index() -> Response:
    """
    Serves index.html
    """
    return await send_from_directory("dist", "index.html")


@app.route("/resources")
async def resources() -> Response:
    """
    Redirects to a resources page.
    """
    return redirect(RESOURCES_URL)


@app.route("/send_content", methods=["POST"])
async def send_content() -> Response:
    """
    Send a content to the agent.

    Args:
        request: a JSON encoded string with:
            content: a dict with:
                mime_type: "text/plain", "audio/pcm", "image/jpeg" or "application/json"
                data: the content to send. Use base64 encoding for audio and image.
            session_id: the session ID of the user.
    """
    # get params
    req_params = await request.get_json()
    msg_to_agent = req_params["content"]
    session_id = req_params["session_id"]
    logging.info(
        "send_content(): received content: mime_type: %s, session_id: %s",
        msg_to_agent["mime_type"],
        session_id,
    )

    # Send the message to the agent
    send_message_to_agent_from_http(msg_to_agent, session_id)

    # Respond with empty response
    return Response()


@app.websocket("/live")
async def live() -> None:
    """
    WebSocket endpoint for live text/audio modality with Gemini.
    """
    await start_user_session(client_websocket=websocket)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=QUART_DEBUG_MODE)
