<template>
  <div class="cb-prompting">
    <!-- <TitleWithIcon
      ref="titleRefConsole"
      icon="gemini"
      textVariant="medium-24"
      :title="copy.mainConsoleTitle"
      class="cb-prompting__title-console"
    /> -->
    <VText
      ref="titleRef"
      animateBy="chars"
      splitType="chars, lines"
      fadeIn
      :text="copy.promptingTitle"
      variant="medium-108"
      gradient
      class="cb-prompting__title"
    />
    <div class="cb-prompting__pills">
      <VPill ref="pill1Ref" :caption="prompts[0]" />
      <VPill ref="pill2Ref" :caption="prompts[1]" />
      <VPill ref="pill3Ref" :caption="prompts[2]" />
    </div>

    <div class="cb-prompting__input-container">
      <InputGeneral
        ref="InputGeneralRef"
        :cta="copy.promptingPlaceholder"
        class="cb-prompting__input-general"
        :qrCode="qrCode"
        :imageUpload="imageUpload"
        @input-general-camera-hover="handleCameraIconHover"
        @input-general-send-click="handleSendClick"
        @input-general-mic-clicked="handleMicIconClick"
        @input-general-input="handleInput"
      />
    </div>
  </div>
</template>

<script setup>
import VText from "@/components/VText.vue";
import { onMounted, onUnmounted, ref, watch } from "vue";
import InputGeneral from "@/components/input-general/InputGeneral.vue";
import VPill from "@/components/VPill.vue";
import { useSessionStore } from "@/stores/session";
import { useChatStore } from "@/stores/chat";
import { useProductsStore } from "@/stores/products";
import { storeToRefs } from "pinia";
import { useAudioStore } from "@/stores/audio";
import copy from "/public/data/copy.json";
import { useRouteManager } from "@/router/useRouteManager";
const sessionStore = useSessionStore();
const audioStore = useAudioStore();
const chatStore = useChatStore();
const productsStore = useProductsStore();
const { qrCodeImage, imageUploads } = storeToRefs(sessionStore);
const { recording } = storeToRefs(audioStore);
const pill1Ref = ref(null);
const pill2Ref = ref(null);
const pill3Ref = ref(null);

const pills = ref([pill1Ref, pill2Ref, pill3Ref]);

const mediumSelectionRef = ref(null);
const firstAgentMessage = ref(false);
const qrCode = ref(null);
const imageUpload = ref(null);
const selectMenuHover = ref(false);
const titleRef = ref(null);
//const titleRefConsole = ref(null);
const InputGeneralRef = ref(null);
const mediumSelected = ref(false);
const navigatedAfterImageUpload = ref(false);

const prompts = ref([]);
prompts.value = getPrompt();

function getPrompt() {
  const randBase = Math.floor(Math.random() * copy.promptingPillChoices.length);
  const randValue1 = (randBase + 1) % copy.promptingPillChoices.length;
  const randValue2 = (randBase + 2) % copy.promptingPillChoices.length;
  const randValue3 = (randBase + 3) % copy.promptingPillChoices.length;
  return [
    copy.promptingPillChoices[randValue1],
    copy.promptingPillChoices[randValue2],
    copy.promptingPillChoices[randValue3],
  ];
}

watch(
  () => qrCodeImage.value,
  (newVal) => {
    const currentRoute = useRouteManager().currentRoute;
    if (newVal && currentRoute.value.id === "prompting") {
      InputGeneralRef.value.updateQRCode(newVal);
      InputGeneralRef.value.animateInQrCode();
    }
  },
  { immediate: true, deep: true }
);

// listen for latest imageUploads
watch(
  () => imageUploads.value,
  (newVal) => {
    const currentRoute = useRouteManager().currentRoute;
    if (newVal && currentRoute.value.id === "prompting") {
      // get latest imageUpload
      const latestImageUpload = newVal[newVal.length - 1];
      if (latestImageUpload) {
        InputGeneralRef.value.updateImageUpload(latestImageUpload);
      }
    }
  },
  { immediate: true, deep: true }
);

watch(recording, (isRecording) => {
  InputGeneralRef.value.setRecordingState(isRecording);
});

onMounted(async () => {
  if (audioStore.recording) {
    console.log("audioStore.recording", audioStore.recording);
    InputGeneralRef.value.setRecordingState(true);
  }
  titleRef.value.prepare().then(() => {
    titleRef.value.animateSet();
  });

  // titleRefConsole.value.prepare().then(() => {
  //   titleRefConsole.value.animateSet();
  // });

  sessionStore.sockets.on("show-query-msg", onQueryMessage);
  // when an image is uploaded, navigate to the main route and send a message to the agent
  sessionStore.sockets.on("image-uploaded", onSendImage);
});
onUnmounted(() => {
  sessionStore.sockets.off("image-uploaded", onSendImage);
  sessionStore.sockets.off("show-query-msg", onQueryMessage);
});

function onQueryMessage(message) {
  if (!firstAgentMessage.value) {
    firstAgentMessage.value = true;
    navigateTo("main");
  }
}

async function onSendImage() {
  if (navigatedAfterImageUpload.value) {
    return;
  }
  await new Promise((resolve) => setTimeout(resolve, 2500));
  navigateTo("main");
  navigatedAfterImageUpload.value = true;
  await new Promise((resolve) => setTimeout(resolve, 1500));
  /* the server will send this message by itself
  sessionStore.sockets.sendMessage(
    "Can you describe what you see in this image, and find relevant items?"
  );
  */
}

function handleMicIconClick(e) {
  if (e.recordingState) {
    audioStore.startRecording();
  } else {
    audioStore.stopRecording();
  }
}

function handleInput(e) {}

async function handleSendClick(text) {
  navigateTo("main");
  await new Promise((resolve) => setTimeout(resolve, 1500));
  chatStore.sendUserMessage(text);
}

async function animateIn() {
  chatStore.resetAll();
  productsStore.resetAll();
  eventBus.emit("animate-background", "edge");
  navigatedAfterImageUpload.value = false;
  await new Promise((resolve) => setTimeout(resolve, 2000));

  const baseDelay = 0.5;
  setTimeout(() => {
    pills.value.forEach((pill, index) => {
      pill.value.animateIn({
        delay: baseDelay + index * 0.2,
      });
    });
    InputGeneralRef.value.animateIn({
      delay: baseDelay + 0.8,
    });
  }, 100);

  setTimeout(() => {
    // titleRefConsole.value.animateIn({
    //   delay: 0.5,
    //   duration: 1.5,
    //   stagger: 0.04,
    // });
    titleRef.value.animateIn(0, {
      duration: 1.5,
      stagger: 0.04,
    });
  }, 500);
}

async function animateOut() {
  titleRef.value.animateOut(0, {
    duration: 1,
    stagger: 0.03,
  });
  pills.value.forEach((pill, index) => {
    pill.value.animateOut({
      delay: index * 0.1,
    });
  });
  InputGeneralRef.value.animateOut();
  //titleRefConsole.value.animateOut();
  return new Promise((resolve) => setTimeout(resolve, 2000));
}

function animateSet() {
  InputGeneralRef.value.animateSet();
  titleRef.value.animateSet();
}

function handleCameraIconHover(event) {
  if (mediumSelected.value) {
    return;
  }
  if (event.type === "mouseenter") {
    mediumSelectionRef.value.animateIn();
  } else if (event.type === "mouseleave") {
    setTimeout(() => {
      if (!selectMenuHover.value) {
        mediumSelectionRef.value.animateOut();
      }
    }, 300);
  }
}

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});
</script>

<style lang="scss" scoped>
.cb-prompting {
  width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  &__title-console {
    position: absolute;
    top: 0;
    left: 0;
    padding: px-to-vh(32) 0 px-to-vh(32) 0;
    margin-left: px-to-vh(30);
    margin-right: px-to-vh(30);
  }
  &__title {
    margin: 0 auto 8.39vh auto;
    text-align: center;
    white-space: pre-line;
  }
  &__pills {
    //display: flex;
    //flex-direction: row;
    //align-items: center;
    justify-content: space-around;
    margin-bottom: 3.39vh;
    gap: 1vh;
  }
  &__input-container {
    width: 70%;
    margin: 0 auto;
    position: relative;
    display: flex;
    flex-direction: column;
  }
  &__medium-selection {
    position: absolute;
    top: 0;
    transform: translateY(-90%);
    right: 0;
    z-index: 100;
  }
}
</style>
