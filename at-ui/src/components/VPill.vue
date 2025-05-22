<template>
  <div @click="handleClick" ref="pillContainer" class="pill-container">
    <div class="pill text-body-16" ref="pillDiv">
      <IconBase class="pill__icon" variant="gemini" />
      <span class="pill__caption">{{ caption }}</span>
    </div>
  </div>
</template>

<script setup>
import IconBase from "@/components/IconBase.vue";
import gsap from "gsap";
import { ref, defineExpose, onMounted } from "vue";
import { useChatStore } from "@/stores/chat";

const pillDiv = ref(null);
const chatStore = useChatStore();
const props = defineProps({
  caption: {
    type: String,
    required: true,
    default: "this is a pill",
  },
});

onMounted(() => {
  animateSet();
});

const handleClick = () => {
  chatStore.sendUserMessage(props.caption);
  navigateTo("main");
};

function animateSet() {
  gsap.set(pillDiv.value, {
    y: 135,
  });
}

function animateIn({ delay = 0 } = {}) {
  gsap.to(pillDiv.value, {
    y: 0,
    duration: 1,
    ease: "power1.out",
    delay: delay,
  });
}

function animateOut({ delay = 0 } = {}) {
  gsap.to(pillDiv.value, {
    y: 135,
    duration: 1,
    ease: "power2.inOut",
    delay: delay,
  });
}

defineExpose({
  animateSet,
  animateIn,
  animateOut,
});
</script>

<style lang="scss" scoped>
.pill-container {
  //width: 100%;
  overflow: hidden;
  display: inline-block;
  height: 110%;
  vertical-align: middle;

  transition: scale 0.4s ease-in-out;

  &:hover {
    scale: 1.05;
  }

  &:nth-child(2) {
    margin-left: 1em;
  }
  &:nth-child(3) {
    margin-left: 1em;
  }
}

.pill {
  display: flex;
  width: fit-content;
  flex-direction: row;
  align-items: center;
  color: $darkmode;
  font-size: 1.473vh !important;
  line-height: 1 !important;
  padding: 1.3em 1.9em;
  border-radius: 2.5em;
  position: relative;
  background: rgba(37, 49, 75, 0.55);
  backdrop-filter: blur(100px);
  gap: 0.6em;
  cursor: pointer;
  @include gradient-border((45deg, #639bf5, #4285f4), 1px);

  &:before {
    border-radius: 2.5em;
  }

  &__icon {
    color: $shopperBlue;
    height: 1.2em;
    width: 1.2em;
    svg {
      width: 100% !important;
      height: 100% !important;
    }
  }

  &__caption {
    padding-left: 0.5em;
  }
}
</style>
