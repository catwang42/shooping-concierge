<template>
  <div class="iconBase" ref="iconBase">
    <component
      :class="[variant, { active: isActive }]"
      :is="currentIcon"
      v-if="currentIcon"
    />
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, shallowRef, watchEffect } from "vue";
import { defineAsyncComponent } from "vue";

const props = defineProps({
  variant: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false,
  },
});

const iconBase = shallowRef(null);
const currentIcon = shallowRef(null);
const isActive = ref(false);

watchEffect(async () => {
  try {
    currentIcon.value = defineAsyncComponent(
      () => import(`./icons/Icon${toPascalCase(props.variant)}.vue`)
    );
  } catch (error) {
    console.error(`Failed to load icon: ${props.variant}`, error);
  }
  if (props.active) {
    isActive.value = true;
  } else {
    isActive.value = false;
  }
});

function toPascalCase(str) {
  return str
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
}
</script>

<style lang="scss" scoped>
.iconBase {
  display: flex;
  align-items: center;
  justify-content: center;
  svg {
    transition: transform 0.3s ease-in-out;
  }
  &:hover svg {
    transform: scale(1.1);
  }
}
.active.mic {
  //border: 6px solid rgb(108, 113, 121);
}
.active {
  border-radius: 78px;
  background: linear-gradient(70.04deg, #ffffff -100.01%, $brandBlue 182.1%);
  color: black;
}
</style>
