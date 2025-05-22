// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Connect the server with a WebSocket connection
const ws_url = "wss://" + window.location.host + "/live";
let ws = new WebSocket(ws_url);

/**
 * Load Audio Player Worklet
 */

let audioPlayerNode;
import { startAudioPlayerWorklet } from "/public/audio-player.js";

/**
 * Start Audio Recorder Worklet
 */

function audioRecorderHandler(data) {
  if (ws.readyState !== WebSocket.OPEN) {
    return;
  }
  const messageJson = JSON.stringify({
    mime_type: "audio/pcm",
    data: arrayToBase64(data)
  });
  ws.send(messageJson);
}

import { startAudioRecorderWorklet } from "/public/audio-recorder.js";

function arrayToBase64(data) {
  let binary = '';
  const bytes = new Uint8Array(data);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

function base64ToArray(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}


/**
 * UI handlers
 */

// Get DOM elements
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const startAudioButton = document.getElementById("startAudioButton");
let currentMessageId = null;

// On submit
messageForm.onsubmit = function (e) {
  e.preventDefault();
  const message = messageInput.value;
  if (message) {
    const p = document.createElement("p");
    p.textContent = "> " + message;
    messagesDiv.appendChild(p);
    const messageJson = JSON.stringify({
      mime_type: "text/plain",
      data: message,
    });
    ws.send(messageJson);
    messageInput.value = "";
    console.log("onsubmit: sent: " + message)
  }
  return false;
};

// On start audio
startAudioButton.onclick = function (e) {
  // Start Audio Player Worklet
  startAudioPlayerWorklet().then((node) => {
    audioPlayerNode = node;
  });

  // Start Audio Recorder Worklet
  startAudioRecorderWorklet(audioRecorderHandler);

  // Disable button
  startAudioButton.disabled = true;
  console.log("Audio Player and Recorder started.");
  return false;
};

/**
 * WebSocket handlers
 */

// WebSocket handlers
function addWebSocketHandlers() {

  ws.onopen = function () {
    console.log("WebSocket connection opened.");
    sendButton.disabled = false;
    messagesDiv.textContent = "Connection opened";
  };

  ws.onmessage = function (event) {
    // Parse the incoming message
    const chunk = JSON.parse(event.data);
    console.log(chunk);

    // Check if the turn is complete or interrupted
    if (chunk.turn_complete || chunk.interrupted) {
      currentMessageId = null;
      if (chunk.interrupted) {
        audioPlayerNode.port.postMessage({ command: "endOfAudio" });
      }
      return;
    }

    // add a new message for a new turn
    if (currentMessageId == null) {
      currentMessageId = Math.random().toString(36).substring(7);
      const message = document.createElement("p");
      message.id = currentMessageId;
      // Append the message element to the messagesDiv
      messagesDiv.appendChild(message);
    }

    // play audio
    if (chunk.mime_type.startsWith("audio/pcm") && audioPlayerNode) {
      const int16Samples = new Int16Array(base64ToArray(chunk.data));
      audioPlayerNode.port.postMessage(int16Samples);
      console.log("played audio: " + int16Samples.length + " samples");
    }

    // Add message text to the existing message element
    const message = document.getElementById(currentMessageId);
    if (message && chunk.mime_type == "text/plain" && chunk.data) {
      message.textContent += chunk.data;
    }

    // Scroll down to the bottom of the messagesDiv
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  };

  // When the connection is closed, try reconnecting
  ws.onclose = function () {
    console.log("WebSocket connection closed.");

    // stop audio
    if (audioPlayerNode) {
      audioPlayerNode.port.postMessage({ command: "endOfAudio" });
    }

    // update UI
    sendButton.disabled = true;
    messagesDiv.textContent = "Connection closed";

    // reconnecting
    setTimeout(function () {
      console.log("Reconnecting...");
      ws = new WebSocket(ws_url);
      addWebSocketHandlers();
    }, 5000);
  };

  ws.onerror = function (e) {
    console.log("WebSocket error: ", e);
  };
}
addWebSocketHandlers();
