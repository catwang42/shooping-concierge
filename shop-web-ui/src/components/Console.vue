<template>
  <div style="width: 320px; height: 90%; margin-left: 10px;">
    <v-row align-content="start" class="pl-2 pr-0 pt-4 overflow-y-auto" style="width: 335px; height: 75vh;">
      <v-col v-for="(content, i) in consoleMessages" :key="i" class="pt-1 pb-1" cols="12">
        <v-card v-if="content.command == CMD_UI.SHOW_QUERY_MSG" elevation="2">
          <v-card-text class="text-left pt-2 pb-2" v-html="'🔍 ' + JSON.stringify(content.parameter)"></v-card-text>
        </v-card>
        <v-card v-if="content.command == CMD_UI.SHOW_AGENT_MSG" elevation="2">
          <v-card-text class="text-left pt-2 pb-2">🤖 {{ content.parameter }}</v-card-text>
        </v-card>
        <v-card v-if="content.command == CMD_UI.SHOW_AGENT_THOUGHTS" elevation="2">
          <v-card-text class="text-left pt-2 pb-2" style="color:darkgrey;">🤖.oO({{ content.parameter }})</v-card-text>
        </v-card>
        <v-card v-if="content.command == CMD_UI.SHOW_USER_MSG" elevation="2">
          <v-card-text class="text-left pt-2 pb-2">👦 {{ content.parameter }}</v-card-text>
        </v-card>
        <v-card v-if="content.command == CMD_UI.SHOW_USER_IMG" elevation="2">
          <v-img :src="getImageUrl(content.parameter)"></v-img>
        </v-card>
        <v-card v-if="content.command == CMD_UI.SHOW_SYSTEM_MSG" elevation="2">
          <v-card-text class="text-left pt-2 pb-2">ℹ️ {{ content.parameter }}</v-card-text>
        </v-card>
      </v-col>
      <div id="consoleLastRow" />
    </v-row>
  </div>
</template>

<script setup>

import { ref, defineEmits } from 'vue';

// Shared consts and functions
import { CMD_UI, base64ToArray } from '../../public/shop-web-js/shared.js';

// Events
const emit = defineEmits(["imageSentToServer"]);

// Console messages
const consoleMessages = ref([]);

// Clear console
const clearConsole = () => {
  consoleMessages.value.length = 0;
};

// scroll Console to the bottom
const scrollConsoleToBottom = () => {
  const console = document.getElementById('consoleLastRow');
  if (console) {
    console.scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'nearest' });
  }
};

// Returns Image URL for the image data
const getImageUrl = (b64data) => {
  try {
    const imageData = base64ToArray(b64data);
    return URL.createObjectURL(new Blob([imageData]));
  } catch (error) {
    console.error("Error decoding base64 data:", error);
    console.debug("base64data: " + b64data);
  }
};

// Show content on console
const showContent = (content) => {

  // If the content is String
  if (typeof content.parameter === "string") {
    // skip if empty
    if (content.parameter.trim().length === 0) return;

    // skip if the same content
    if (consoleMessages.value.length > 0) {
      if (consoleMessages.value[consoleMessages.value.length - 1].parameter == content.parameter) return;
    }
  }

  // add the message as a new element
  consoleMessages.value.push(content);

  // if it's image/jpeg content, emit imageSentToServer event
  if (content.command == CMD_UI.SHOW_USER_IMG) {
    emit('imageSentToServer', null);
  }

  // scroll Console to the bottom
  setTimeout(scrollConsoleToBottom, 500);
  setTimeout(scrollConsoleToBottom, 1000);
};

defineExpose({ showContent, clearConsole })

</script>