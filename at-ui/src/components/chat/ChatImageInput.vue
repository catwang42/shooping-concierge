<template>
  <div class="chat-image-input chat-item">
    <div ref="innerRef" class="chat-image-input__inner">
      <img :src="image" alt="Image" />
    </div>
  </div>
</template>

<script setup>
import gsap from "gsap";

import { onMounted, ref, defineExpose } from "vue";
const props = defineProps({
  image: String,
});

const innerRef = ref(null);

function animateIn() {
  gsap.to(innerRef.value, {
    x: 0,
    opacity: 1,
    ease: "Power2.out",
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
.chat-image-input {
  height: 100%;
  width: 100%;
  margin-left: auto;
  margin-top: px-to-vh(-12);
  box-shadow: 0 px-to-vh(14) px-to-vh(59.7) 0 rgba(0, 0, 0, 0.15);
  &__inner {
    position: relative;
    height: 100%;
    width: 100%;
    border-radius: px-to-vh(16);
    img {
      display: block;
      border: 1px solid rgba(255, 255, 255, 0.2);
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: px-to-vh(16);
    }
  }
}
</style>
