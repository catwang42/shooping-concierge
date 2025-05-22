<template>
  <div class="chat-user-message chat-item">
    <div ref="innerRef" class="chat-user-message__inner">
      <VText class="chat-user-message__text" :text="text" variant="medium-18" />
    </div>
  </div>
</template>

<script setup>
import VText from "@/components/VText.vue";
import gsap from "gsap";

import { onMounted, ref, defineExpose } from "vue";
const props = defineProps({
  text: String,
});

const innerRef = ref(null);

function animateIn() {
  gsap.to(innerRef.value, {
    x: 0,
    opacity: 1,
    ease: "Power4.out",
    duration: 0.5,
  });
}

function animateSet() {
  gsap.set(innerRef.value, {
    x: 100,
    opacity: 0,
  });
  setTimeout(() => {
    animateIn();
  }, 100);
}

function animateOut() {}

onMounted(() => {
  animateSet();
});

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});
</script>

<style scoped lang="scss">
.chat-user-message {
  width: fit-content;
  max-width: 60%;
  margin-left: auto;
  &__inner {
    box-shadow: 0 px-to-vh(10) px-to-vh(19.7) 0 rgba(0, 0, 0, 0.15);
    padding: px-to-vh(20);
    width: 100%;
    border-radius: px-to-vh(16);
    @include gradient-bg;
    color: $charcoal;
    text-align: right;
  }
}
</style>
