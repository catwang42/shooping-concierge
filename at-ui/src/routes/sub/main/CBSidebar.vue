<template>
  <div ref="sidebarRef" class="cb-main__sidebar">
    <TitleWithIcon
      ref="titleRef"
      icon="gemini"
      textVariant="medium-24"
      :title="copy.mainConsoleTitle"
      class="cb-main__sidebar__title"
    />
    <AudioMode ref="audioModeRef" />
    <VChat />
    <div class="cb-main__sidebar__blur-bg"></div>
    <InputGeneral
      ref="inputGeneralRef"
      :cta="copy.mainInputPlaceholder"
      mini
      @input-general-mic-clicked="handleMicClicked"
      @input-general-send-click="handleSendClick"
    />
  </div>
</template>

<script setup>
import TitleWithIcon from "@/components/TitleWithIcon.vue";
import InputGeneral from "@/components/input-general/InputGeneral.vue";
import VChat from "@/components/chat/VChat.vue";
import AudioMode from "@/components/AudioMode.vue";
import copy from "/public/data/copy.json";
import gsap from "gsap";
import { ref, defineExpose, onMounted, watch, onUnmounted } from "vue";
import { useChatStore } from "@/stores/chat";
import { useAudioStore } from "@/stores/audio";
import { storeToRefs } from "pinia";
import { useSessionStore } from "@/stores/session";
import { useRouteManager } from "@/router/useRouteManager";
const sessionStore = useSessionStore();
const chatStore = useChatStore();
const audioStore = useAudioStore();
const { qrCodeImage, imageUploads } = storeToRefs(sessionStore);
const { recording } = storeToRefs(audioStore);
const { geminiLoading } = storeToRefs(chatStore);

const titleRef = ref(null);
const inputGeneralRef = ref(null);
const sidebarRef = ref(null);
const audioModeRef = ref(null);

/* the server will send this message by itself
sessionStore.sockets.on("image-uploaded", async () => {
  await new Promise((resolve) => setTimeout(resolve, 1500));
  sessionStore.sockets.sendMessage(
    "Can you describe what you see in this image, and find relevant items?"
  );
});
*/

watch(
  () => geminiLoading.value,
  (newVal) => {
    inputGeneralRef.value.setGeminiLoading(newVal);
  }
);

watch(
  () => qrCodeImage.value,
  (newVal) => {
    const currentRoute = useRouteManager().currentRoute;
    if (newVal && currentRoute.value.id === "main") {
      console.log("newVal", newVal);
      inputGeneralRef.value.updateQRCode(newVal);
      inputGeneralRef.value.animateInQrCode();
    }
  },
  { immediate: true, deep: true }
);

watch(
  () => imageUploads.value,
  (newVal) => {
    const currentRoute = useRouteManager().currentRoute;
    if (newVal && currentRoute.value.id === "main") {
      // get latest imageUpload
      const latestImageUpload = newVal[newVal.length - 1];
      if (latestImageUpload && inputGeneralRef.value) {
        inputGeneralRef.value.updateImageUpload(latestImageUpload);
        setTimeout(() => {
          inputGeneralRef.value.animateOutQrCode();
        }, 3000);
      }
    }
  },
  { immediate: true, deep: true }
);

watch(recording, (isRecording) => {
  console.log("isRecording sidebar", isRecording);
  inputGeneralRef.value.setRecordingState(isRecording);
});

onMounted(() => {
  titleRef.value.prepare();
  titleRef.value.animateSet();
  inputGeneralRef.value.animateSet();
  audioModeRef.value.animateSet();
  if (audioStore.recording) {
    inputGeneralRef.value.setRecordingState(true);
  }
});

onUnmounted(() => {});

function handleSendClick(text) {
  chatStore.sendUserMessage(text);
}

function handleMicClicked(e) {
  if (e.recordingState) {
    audioStore.startRecording();
  } else {
    audioStore.stopRecording();
  }
}

function animateIn() {
  audioModeRef.value.animateIn(1);
  titleRef.value.animateIn({ delay: 0.5, duration: 3, stagger: 0.5 });
  inputGeneralRef.value.animateIn({ delay: 1.5 });
  gsap.to(sidebarRef.value, {
    opacity: 1,
    x: 0,
    duration: 1,
    ease: "power2.out",
  });
}

function animateOut() {
  audioModeRef.value.animateOut();
  titleRef.value.animateOut();
  inputGeneralRef.value.animateOut();
  gsap.to(sidebarRef.value, {
    opacity: 0,
    x: -100,
    duration: 1,
    ease: "power2.out",
  });
}

function animateSet() {
  gsap.set(sidebarRef.value, {
    opacity: 0,
    x: -100,
  });
}

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});
</script>

<style lang="scss" scoped>
.cb-main__sidebar {
  position: relative;
  height: 100%;
  border-radius: 0 px-to-vh(41) px-to-vh(41) 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(28, 32, 44, 0.53);
  backdrop-filter: blur(px-to-vh(30));
  color: $grey;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: px-to-vh(100);

  &__title {
    padding: px-to-vh(32) 0 px-to-vh(32) 0;
    margin-left: px-to-vh(30);
    margin-right: px-to-vh(30);
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  }

  .input-general-wrapper {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    margin-top: auto;
    padding: px-to-vh(48) px-to-vh(30) px-to-vh(48) px-to-vh(30);

    :deep(.input-general__button) {
      svg {
        width: 80%;
        height: 80%;
      }
    }

    :deep(.input-general__text) {
      padding: px-to-vh(16) px-to-vh(16) px-to-vh(16) px-to-vh(32);
    }
  }
}
</style>
