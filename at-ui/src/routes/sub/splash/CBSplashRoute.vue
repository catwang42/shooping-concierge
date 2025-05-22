<template>
  <div class="cb-splash-container">
    <AudioCheck
      ref="audioCheckRef"
      @update:isChecked="handleGeminiMode"
      class="cb-splash__audio-mode"
    />
    <QRCodeBasic
      ref="qrCodeBasicRef"
      :value="qrCodeUrl"
      class="cb-splash__qr-code"
    />
    <div @click="handleClick" class="splash-inner">
      <Gallery
        ref="galleryRef"
        :title="copy.landingTitle"
        :subTitle="copy.landingSubtitle"
        :cta="copy.landingCTA"
        :imageContent="imageContent"
      />
    </div>
  </div>
</template>

<script setup>
import Gallery from "@/components/gallery/Gallery.vue";
import copy from "/public/data/copy.json";
import { ref, defineExpose, computed } from "vue";
import { useAudioStore } from "@/stores/audio";
import { useSessionStore } from "@/stores/session";
import AudioCheck from "@/components/AudioCheck.vue";
import QRCodeBasic from "@/components/QRCodeBasic.vue";
const sessionStore = useSessionStore();
const audioStore = useAudioStore();
const qrCodeBasicRef = ref(null);
const galleryRef = ref(null);
const audioCheckRef = ref(null);
const isGeminiAudioMode = ref(false);
const qrCodeUrl = computed(() => {
  return `https://${window.location.host}/resources`;
});

defineExpose({
  animateSet: () => {
    galleryRef.value.animateSet();
    audioCheckRef.value.animateSet();
    qrCodeBasicRef.value.animateSet();
  },
  animateIn: () => {
    galleryRef.value.animateIn();
    eventBus.emit("animate-background", "idle");
    audioCheckRef.value.animateIn(3);
    qrCodeBasicRef.value.animateIn(3);
    audioStore.stopAudioPlayer();
  },
  animateOut: async () => {
    audioCheckRef.value.animateOut();
    qrCodeBasicRef.value.animateOut();
    await galleryRef.value.animateOut();
  },
});

const handleClick = (e) => {
  if (!e.target.closest(".cb-splash__audio-mode")) {
    navigateTo("prompting");
    sessionStore.setGeminiMode(isGeminiAudioMode.value ? "audio" : "text"); //
    if (isGeminiAudioMode.value) {
      audioStore.startAudioPlayer();
      audioStore.startRecording();
    }
  }
};

const handleGeminiMode = (isAudioMode) => {
  eventBus.emit("audio-mode-set", isAudioMode);
  isGeminiAudioMode.value = isAudioMode;
};

const imageContent = [
  {
    src: "https://u-mercari-images.mercdn.net/photos/m88011178233_1.jpg?w=400&h=400&fitcrop&sharpen",
    alt: "Knit mini skirt",
    caption: "Knit mini skirt",
  },
  {
    src: "https://u-mercari-images.mercdn.net/photos/m71743451992_1.jpg?w=400&h=400&fitcrop&sharpen",
    alt: "Pixel Watch",
    caption: "Pixel Watch",
  },
  {
    src: "https://u-mercari-images.mercdn.net/photos/m10508654058_1.jpg?w=500&h=500&fitcrop&sharpen",
    alt: "Marvel patterned fabric",
    caption: "Marvel patterned fabric",
  },
  {
    src: "https://u-mercari-images.mercdn.net/photos/m10472626759_1.jpg?w=400&h=400&fitcrop&sharpen",
    alt: "Tile Brush",
    caption: "Tile Brush",
  },
  {
    src: "https://u-mercari-images.mercdn.net/photos/m67934957912_1.jpg?w=400&h=400&fitcrop&sharpen",
    alt: "Brickyard Building Blocks",
    caption: "Brickyard Building Blocks",
  },
  {
    src: "https://u-mercari-images.mercdn.net/photos/m83458553698_1.jpg?w=400&h=400&fitcrop&sharpen",
    alt: "Turquoise Jewelry Set",
    caption: "Turquoise Jewelry Set",
  },
];
</script>

<style lang="scss" scoped>
.splash-inner {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.cb-splash-container {
  position: relative;
  width: 100vw;
  height: 100vh;
}
.cb-splash__audio-mode {
  position: absolute;
  top: px-to-vh(50);
  left: px-to-vh(50);
  z-index: 9999;
}
.cb-splash__qr-code {
  position: absolute;
  bottom: px-to-vh(50);
  right: px-to-vh(50);
  z-index: 9999;
}
</style>
