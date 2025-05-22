<template>
  <div ref="chatContainerRef" class="chat-container">
    <TransitionGroup @leave="animateOut" name="chat-item" tag="ul">
      <li v-for="message in chatStore.messages" :key="message.id">
        <ChatUserMessage
          v-if="message.type === 'userMessage'"
          :text="message.text"
        />
        <ChatAgentMessage
          v-if="message.type === 'agentMessage'"
          :text="message.text"
        />
        <ChatInfo
          v-if="message.type === 'info'"
          :text="message.text"
          :type="message.type"
        />
        <ChatQueryResponse
          v-if="message.type === 'queryResponse'"
          :text="message.text"
          :resultCount="message.resultCount"
          :productName="message.productName"
          :groupIconID="message.groupIconID"
          :groupID="message.groupID"
        />
        <ChatImageInput
          v-if="message.type === 'imageInput'"
          :image="message.image"
        />
        <ChatImageAnalysis
          v-if="message.type === 'imageAnalysis'"
          :image="message.image"
          :text="message.text"
        />
      </li>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useChatStore } from "@/stores/chat";
const chatStore = useChatStore();
import ChatUserMessage from "./ChatUserMessage.vue";
import ChatInfo from "./ChatInfo.vue";
import ChatQueryResponse from "./ChatQueryResponse.vue";
import ChatImageInput from "./ChatImageInput.vue";
import ChatImageAnalysis from "./ChatImageAnalysis.vue";
import ChatAgentMessage from "./ChatAgentMessage.vue";
import { ref } from "vue";
import gsap from "gsap";
const chatContainerRef = ref(null);

const lastHeight = ref(0);
let tween = null;

function animateOut(el, done) {
  gsap.to(el, {
    x: -100,
    opacity: 0,
    duration: 1,
    ease: "power2.inOut",
    delay: el.dataset.index * 0.1,
    onComplete: done,
  });
}

function onAction() {
  setTimeout(() => {
    if (tween) {
      tween.kill();
    }
    // get the height of the chat container
    const heightEl = chatContainerRef.value.scrollHeight;
    if (heightEl === lastHeight.value) {
      return;
    }

    // scroll to the bottom of the chat container
    chatContainerRef.value.scrollTo({
      top: heightEl,
      behavior: "smooth",
    });
  }, 100);
}

// listen for changes in the chat store
chatStore.$onAction(({ name }) => {
  if (name === "addMessage") onAction();
});
</script>

<style scoped lang="scss">
.chat-container {
  width: 100%;
  height: 100%;
  overflow-y: scroll;
  overflow-x: visible;
  &::-webkit-scrollbar {
    display: none;
  }
}
.chat-switch {
  width: 100%;
  height: 100%;
}
.chat-item {
  padding-left: px-to-vh(30);
  padding-right: px-to-vh(30);
}
ul {
  list-style: none;
  padding: px-to-vh(24) 0;
  width: 100%;
  overflow-y: scroll;
  &::-webkit-scrollbar {
    display: none;
  }
  li {
    margin-bottom: px-to-vh(24);
    display: flex;
    width: 100%;

    &:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
