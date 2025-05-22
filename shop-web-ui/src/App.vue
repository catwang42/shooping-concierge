<template>
  <v-app>

    <!-- Gemini API Key dialog -->
    <v-dialog v-model="apiKeyDialogActive" width="500">
      <v-card title="Enter Gemini API Key">
        <v-card-text v-html="geminiKeyInfo">
        </v-card-text>
        <v-text-field label="Key:" v-model="apiKey" required />
        <v-btn text="Enter" variant="plain" @click="onApiKeyEntered" />
      </v-card>
    </v-dialog>

    <v-main class="d-flex" style="width: 100vw; height: 100vh;">
      <v-row>
        <v-col class="d-flex flex-column pt-10" style="min-width: fit-content; max-width: fit-content; height: 100%; ">
          <Console ref="consoleRef" id="console" @imageSentToServer="onImageSentToServer" />
          <Chat v-model:isAudio="isAudio" :sendEnabled="sendEnabled" @submitMessage="sendUserMessageToServer"
            @submitImage="sendUserImageToServer" :sessionId="sessionId" />
        </v-col>
        <v-col class="d-flex pl-0 pt-8 pr-8" style="height: 90vh;">
          <Main :items="items" />
        </v-col>
      </v-row>
    </v-main>
  </v-app>
</template>

<script setup>

/**
 * Consts and imports
 */

const geminiKeyInfo = "See <a href='https://ai.google.dev/gemini-api/docs/api-key'>this page</a> to learn how to get a key.";

// Vue
import { ref, onMounted, watchEffect, nextTick } from 'vue';

// Shared consts and functions
import { CMD_UI, CMD_AGENT, arrayBufferToBase64, base64ToArray } from '../public/shop-web-js/shared.js';
import { startAudioPlayerWorklet } from "../public/shop-web-js/audio-player.js";

// Shop web components
import Console from './components/Console.vue'
import Main from './components/Main.vue'
import Chat from './components/Chat.vue'

// Host name options
const HOSTNAME_LOCAL = window.location.host; // default
const HOSTNAME_PROD = "shop-web-761793285222.us-central1.run.app";
const HOSTNAME_STAGE = "stage---shop-web-nhhfh7g7iq-uc.a.run.app";
const HOSTNAME_DEV = "dev---shop-web-nhhfh7g7iq-uc.a.run.app";

// Current host name
const HOSTNAME = HOSTNAME_LOCAL;
//const HOSTNAME = HOSTNAME_DEV;

/**
 * Reactive variables
 */
const items = ref([]);
const isAudio = ref(false);
const sendEnabled = ref(false);
const apiKeyDialogActive = ref(false);
const apiKey = ref("");
const consoleRef = ref(null);
const sessionId = ref("");

/**
 * WebSocket
 */
const websocket = ref(null);
const liveTextUrl = 'wss://' + HOSTNAME + '/live?mode=text';
const liveAudioUrl = 'wss://' + HOSTNAME + '/live?mode=audio';
let lastConnectTime = 0;
let retryCount = 0;

// Connect with the server
const connectWebSocket = () => {
  const wsApiKeyParam = apiKey.value ? "?apiKey=" + apiKey.value : "";
  const wsUrl = (isAudio.value ? liveAudioUrl : liveTextUrl) + wsApiKeyParam;
  websocket.value = new WebSocket(wsUrl);
  console.log('Trying connect to: ' + wsUrl);

  websocket.value.onopen = () => {
    // Wait for the DOM to update and the Console component to be ready.
    nextTick(() => {
      // Reset the UI
      consoleRef.value.clearConsole();
      items.value.length = 0;
      sendEnabled.value = true;
      lastConnectTime = new Date();
      retryCount = 0;

      // Initial messages
      consoleRef.value.showContent({
        command: CMD_UI.SHOW_SYSTEM_MSG,
        parameter: 'Connection opened.'
      });
      sendUserMessageToServer(" "); // for the agent's greeting message
      sendUserLocationServer();
    });
    console.log('WebSocket connection opened.');
  };

  websocket.value.onclose = () => {
    // Disable SEND button
    sendEnabled.value = false;

    // Show connection closed message
    if (consoleRef.value) {
      consoleRef.value.showContent({
        command: CMD_UI.SHOW_SYSTEM_MSG,
        parameter: 'Connection closed.'
      });
    }

    // Retry connection immediately or after 5 secs
    const now = new Date();
    const retryNeedsDelay = (now - lastConnectTime) < 5000 || retryCount > 0;
    retryCount += 1;
    setTimeout(() => {
      connectWebSocket();
    }, retryNeedsDelay ? 5000 : 100);

    console.log('WebSocket connection closed.');
  };

  websocket.value.onmessage = (event) => {
    // Parse the incoming message
    const chunk = JSON.parse(event.data);

    // text message
    if (chunk.mime_type == "text/plain") {
      consoleRef.value.showContent({
        command: CMD_UI.SHOW_AGENT_MSG,
        parameter: chunk.data,
      });
      console.log(chunk);
    }

    // play audio
    if (chunk.mime_type.startsWith("audio/pcm") && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(chunk.data));
      //      console.log("played audio: " + chunk.data.length + " samples");
    }

    // app level commands
    if (chunk.mime_type == "application/json") {
      const command = chunk.data.command;
      const parameter = chunk.data.parameter;
      console.log(chunk);

      if (command == CMD_UI.PRESENT_ITEMS) {
        // present items
        items.value = parameter.items;

      } else if (command == CMD_UI.SET_SESSION_ID) {
        // set session id
        sessionId.value = parameter;
      } else {
        // show content on the console
        consoleRef.value.showContent({ command: command, parameter: parameter });
      }
    };

    websocket.value.onerror = (error) => {
      console.error('WebSocket error:', error);
    }
  };
}

// Disconnect with the server
const disconnectWebsocket = () => {
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    websocket.value.close();
  }
};

/**
 * Audio Recorder and Player
 */

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;

import { startAudioRecorderWorklet, stopMicrophone } from "../public/shop-web-js/audio-recorder.js";

// Audio recorder handler
function audioRecorderHandler(data) {
  if (websocket.value.readyState == WebSocket.OPEN) {
    websocket.value.send(data);
    //    console.log("audioRecorderHandler(): sent %s bytes", data.length);
  }
}

// Watch on switching audio mode
watchEffect(() => {

  // Switch audio mode
  if (isAudio.value) {
    setAudioMode(true);
  } else {
    setAudioMode(false);
  }

  // Send agent command to change the audio mode
  const messageJson = JSON.stringify({
    mime_type: "application/json",
    data: {
      command: CMD_AGENT.SET_AUDIO,
      parameter: isAudio.value,
    }
  });

  // Send to the server
  if (websocket.value.readyState == WebSocket.OPEN) {
    websocket.value.send(messageJson);
    console.log("Sent CMD_AGENT.SET_AUDIO: " + isAudio.value);
  }
});

// Switch audio
function setAudioMode(audioMode) {
  if (audioMode) {
    // Turn on audio
    startAudioPlayerWorklet().then(([node, ctx]) => {
      audioPlayerNode = node;
      audioPlayerContext = ctx;
    });
    startAudioRecorderWorklet(audioRecorderHandler).then(([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
    });
    console.log("Audio Player and Recorder started.");
  } else {
    // Turn off audio
    if (audioPlayerContext) {
      audioPlayerNode.disconnect();
      audioPlayerContext.close();
      audioPlayerContext = null;
      console.log("Audio Player stopped.");
    }
    if (audioRecorderContext && micStream) {
      stopMicrophone(micStream);
      audioRecorderNode.disconnect();
      audioRecorderContext.close();
      audioRecorderContext = null;
      console.log("Audio Recorder stopped.");
    }
  }
}

/**
 * UI event handlers
 */

// Init
onMounted(() => {

  // Ask for Gemini API Key if it's on the prod
  if (window.location.host == HOSTNAME_PROD) {
    apiKeyDialogActive.value = false; // prod (not using at this time)
  } else {
    apiKeyDialogActive.value = false; // dev
  }

  // If key is not needed, connect WebSocket with the server immediately
  if (apiKeyDialogActive.value == false) {
    connectWebSocket();
  }
});

// Send Gemini API Key to the server
function onApiKeyEntered() {
  apiKeyDialogActive.value = false;
  console.log("onApiKeyEntered: API Key entered: " + apiKey.value);
  connectWebSocket();
}

// Send message to server
function sendUserMessageToServer(message) {
  const messageJson = JSON.stringify({
    mime_type: "text/plain",
    data: message,
  });
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    websocket.value.send(messageJson);
    consoleRef.value.showContent({ command: CMD_UI.SHOW_USER_MSG, parameter: message });
    console.log("sendUserMessageToServer(): Sent: " + messageJson);
  }
}

// Send image (and an empty text message) to server
function sendUserImageToServer(imageData) {
  const b64data = arrayBufferToBase64(imageData);
  const imageJson = JSON.stringify({
    mime_type: "image/jpeg",
    data: b64data,
  });
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    websocket.value.send(imageJson);
    console.log("sendUserImageToServer(): Sent image: %s bytes.", b64data.length);
  }
}

// Send a request for an image analytics after image posting 
function onImageSentToServer() {
  setTimeout(
    () => {
      sendUserMessageToServer("Can you describe what you see in this image in detail?");
    },
    3000);
};

/**
 * User location
 */

// Send user location to the server
function sendUserLocationServer() {
  // Check if Geolocation is supported
  if (!navigator.geolocation) {
    console.error('sendUserLocationServer(): Geolocation is not supported by this browser.');
    return;
  }

  // Get current location
  navigator.geolocation.getCurrentPosition(
    (position) => {
      // Build a JSON with current location
      const { latitude, longitude } = position.coords;
      const messageJson = JSON.stringify({
        mime_type: "application/json",
        data: {
          command: CMD_AGENT.SET_USER_LOCATION,
          parameter: {
            latitude: latitude,
            longitude: longitude,
            date: new Date().toLocaleDateString('en-US'),
            time: new Date().toLocaleTimeString('en-US'),
          }
        }
      });

      // Send to the server
      if (websocket.value.readyState == WebSocket.OPEN) {
        websocket.value.send(messageJson);
        console.log('sendUserLocationServer(): Use location: Lat:', latitude, 'Long:', longitude);
      }
    },
    (error) => {
      console.error('sendUserLocationServer(): Error getting location:', error);
    }
  );
}

</script>
