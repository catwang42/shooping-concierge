<template>
  <transition @leave="animateOut">
    <div v-if="open" class="chat-info chat-item">
      <div ref="innerRef" class="chat-info__inner">
        <IconInfo class="chat-info__icon" v-if="props.type === 'info'" />
        <VText :text="props.text" variant="bold-14" />
      </div>
    </div>
  </transition>
</template>

<script setup>
import VText from "@/components/VText.vue";
import gsap from "gsap";
import IconInfo from "@/components/icons/IconInfo.vue";
import { onMounted, ref, defineExpose, onUnmounted } from "vue";
const props = defineProps({
  text: String,
  type: String, // choose icon based on type
});

const innerRef = ref(null);
const open = ref(true);

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

function animateOut(el, done) {}

onMounted(() => {
  animateSet();
  console.log(props.open);
});

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});
</script>

<style scoped lang="scss">
.chat-info {
  width: 100%;

  .VText {
    opacity: 0.5;
  }

  .chat-info__icon {
    width: px-to-vh(20);
    height: px-to-vh(20);
    color: $lightBlue;
    opacity: 0.5;
  }

  &__inner {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: px-to-vh(8);
    box-shadow: 0 px-to-vh(10) px-to-vh(19.7) 0 rgba(0, 0, 0, 0.15);
    @include chat-panel;
  }
}
</style>
