<template>
  <div ref="geminiLoadingRef" class="chat-gemini-loading">
    <IconGemini class="chat-gemini-loading__icon" />
  </div>
</template>

<script setup>
import IconGemini from "@/components/icons/IconGemini.vue";
import { onMounted, defineExpose, ref } from "vue";
import { gsap } from "@/utils/gsap";
import { pxToVh } from "@/utils/shared";
const geminiLoadingRef = ref(null);

const tlIn = gsap.timeline();
const tlOut = gsap.timeline();
const animateIn = () => {
  if (!geminiLoadingRef.value) return;
  tlIn.restart();
};

const animateOut = () => {
  if (!geminiLoadingRef.value) return;
  tlIn.pause();
  tlOut.restart();
};

const animateSet = () => {
  if (!geminiLoadingRef.value) return;
  gsap.set(geminiLoadingRef.value, {
    scale: 0,
    y: pxToVh(100),
    opacity: 0,
  });
};

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});

onMounted(() => {
  tlIn
    .to(geminiLoadingRef.value, {
      scale: 1,
      duration: 0.5,
      y: 0,
      ease: "power2.out",
    })
    .to(
      geminiLoadingRef.value,
      {
        opacity: 1,
        duration: 0.5,
        delay: 0.2,
        ease: "power2.out",
      },
      "<"
    );

  tlIn.to(geminiLoadingRef.value, {
    rotate: 360,
    duration: 1.5,
    ease: "power1.inOut",
    repeat: -1,
  });

  tlIn.pause();

  tlOut
    .to(geminiLoadingRef.value, {
      opacity: 0,
      duration: 0.5,
      ease: "power1.out",
    })
    .to(
      geminiLoadingRef.value,
      {
        scale: 0,
        y: pxToVh(100),
        duration: 1,
        delay: 0.2,
        ease: "power1.out",
      },
      "<"
    );

  tlOut.pause();
});
</script>

<style lang="scss" scoped>
.chat-gemini-loading {
  transform-origin: center;
  &__icon {
    width: 100%;
    height: 100%;
  }
}
</style>
