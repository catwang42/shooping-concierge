<template>
  <div ref="audioModeRef" class="audio-mode-container">
    <div v-if="audioMode === 'audio'" class="audio-mode__voice">
      <IconVoice gradient class="audio-mode__icon" />
      <div class="audio-mode__body text-medium-16 gradient">Voice</div>
    </div>
    <div v-else class="audio-mode__text">
      <IconText gradient class="audio-mode__icon" />
      <div class="audio-mode__body text-medium-16 gradient">Text</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import IconVoice from "@/components/icons/IconVoice.vue";
import IconText from "@/components/icons/IconText.vue";
import { useSessionStore } from "@/stores/session";
import { storeToRefs } from "pinia";
const sessionStore = useSessionStore();
const { mode } = storeToRefs(sessionStore);
import { gsap } from "@/utils/gsap";
const audioMode = ref("voice");
const audioModeRef = ref(null);

const animateSet = () => {
  audioMode.value = mode.value;
  gsap.set(audioModeRef.value, {
    scale: 0,
    opacity: 0,
  });
};

const animateIn = (delay = 0) => {
  gsap.to(audioModeRef.value, {
    scale: 1,
    opacity: 1,
    duration: 1,
    ease: "power2.out",
    delay: delay,
  });
};

const animateOut = () => {
  gsap.to(audioModeRef.value, {
    scale: 0,
    opacity: 0,
    duration: 21,
    ease: "power2.out",
  });
};

defineExpose({
  animateSet,
  animateIn,
  animateOut,
});
</script>

<style scoped lang="scss">
.audio-mode-container {
  position: absolute;
  top: px-to-vh(32);
  right: px-to-vh(32);
}
.audio-mode {
  &__voice,
  &__text {
    padding: px-to-vh(10) px-to-vh(20);
    background-color: rgba(255, 255, 255, 0.03);
    border-radius: px-to-vh(48);
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: px-to-vh(10);
    @include gradient-border((45deg, #639bf5, #4285f4), 1px);
    &:before {
      border-radius: px-to-vh(48);
    }
  }
  &__icon {
    width: px-to-vh(18);
    height: px-to-vh(18);
  }
}
</style>
