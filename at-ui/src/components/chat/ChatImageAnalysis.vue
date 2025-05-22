<template>
  <div class="chat-image-analysis chat-item">
    <div ref="innerRef" class="chat-image-analysis__inner">
      <div class="chat-image-analysis__inner__header">
        <IconImageAnalysis class="chat-image-analysis__inner__header__icon" />
        <VText text="Image Analysis" variant="bold-14" />
      </div>
      <div class="chat-image-analysis__inner__content">
        <img :src="image" alt="Image" />
        <VText
          class="chat-query-response__inner__content__text"
          :text="text"
          variant="medium-18"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import VText from "@/components/VText.vue";
import gsap from "gsap";
import IconImageAnalysis from "@/components/icons/iconImageAnalysis.vue";
import { onMounted, ref, defineExpose } from "vue";
const props = defineProps({
  image: String,
  text: String,
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
    x: -100,
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
.chat-image-analysis {
  width: 100%;

  &__inner {
    @include chat-panel;
    &__header {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: px-to-vh(8);
      width: 100%;
      opacity: 0.5;
      margin-bottom: px-to-vh(24);
      &__icon {
        width: px-to-vh(24);
        height: px-to-vh(24);
        color: $lightBlue;
        opacity: 0.5;
      }
    }
    &__content {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: flex-start;
      width: 100%;
      img {
        display: block;
        width: px-to-vh(56);
        height: px-to-vh(56);
        margin-right: px-to-vh(16);
        border-radius: px-to-vh(8);
        border: 1px solid #ffffff1a;
        object-fit: cover;
      }
    }
  }
}
</style>
