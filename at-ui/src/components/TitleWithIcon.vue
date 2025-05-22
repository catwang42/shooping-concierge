<template>
  <div class="title-with-icon">
    <IconBase v-if="icon" :variant="icon" ref="iconRef" />
    <VText ref="textRef" :text="title" :variant="textVariant" />
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: null,
  },
  title: {
    type: String,
    default: null,
  },
  textVariant: {
    type: String,
    default: "text-bold-24",
  },
});

import { onMounted, ref } from "vue";
import IconBase from "./IconBase.vue";
import VText from "./VText.vue";

const textRef = ref(null);
const iconRef = ref(null);
const animateIn = (settings) => {
  textRef.value.animateIn(settings);
  setTimeout(() => {
    iconRef.value.$el.classList.remove("hidden");
  }, settings.delay * 1000);
};

const animateOut = () => {
  textRef.value.animateOut();
  iconRef.value.$el.classList.add("hidden");
};

const animateSet = () => {
  textRef.value.animateSet();
  iconRef.value.$el.classList.add("hidden");
};

const prepare = () => {
  return textRef.value.prepare();
};

onMounted(() => {
  iconRef.value.$el.classList.add("hidden");
});

defineExpose({
  animateIn,
  animateOut,
  animateSet,
  prepare,
});
</script>

<style lang="scss" scoped>
.title-with-icon {
  display: flex;
  align-items: center;
  gap: px-to-vh(10);
}

.iconBase {
  transition: transform 0.3s ease-in-out;

  :deep(svg) {
    width: px-to-vh(24);
    height: px-to-vh(24);
  }
}

.iconBase.hidden {
  transform: scale(0);
}
</style>
