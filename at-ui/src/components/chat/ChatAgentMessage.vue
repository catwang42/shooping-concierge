<template>
  <div class="chat-agent-message chat-item">
    <div ref="innerRef" class="chat-agent-message__inner">
      <IconGemini class="chat-agent-message__icon" />
      <VText
        class="chat-agent-message__text"
        :text="text"
        variant="medium-18"
      />
    </div>
  </div>
</template>

<script setup>
import VText from "@/components/VText.vue";
import gsap from "gsap";
import IconGemini from "@/components/icons/IconGemini.vue";
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
.chat-agent-message {
  width: fit-content;
  max-width: calc(100% - px-to-vh(20));
  margin-right: auto;
  &__inner {
    display: flex;
    align-items: flex-start;
    width: 100%;
    border-radius: px-to-vh(16);

    //@include gradient-bg-agent;
    color: white;
    gap: px-to-vh(10);
  }
  &__icon {
    flex-shrink: 0;
    width: px-to-vh(18);
    height: px-to-vh(18);
  }
}
</style>
