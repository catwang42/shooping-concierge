<template>
  <label ref="audioModeRef" class="toggle">
    <input type="checkbox" class="toggle__input" v-model="isChecked" />
    <span ref="sliderRef" class="toggle__slider"></span>
    <div class="toggle__text">
      <span
        ref="textLeftRef"
        class="toggle__text-item toggle__text-item--left text-medium-16"
        ><IconText />Text</span
      >
      <span
        ref="textRightRef"
        class="toggle__text-item toggle__text-item--right text-medium-16"
        ><IconVoice />Voice</span
      >
    </div>
    <div class="toggle__background"></div>
  </label>
</template>

<script setup>
import { ref, watch, defineEmits, defineExpose } from "vue";
import { gsap } from "@/utils/gsap";
import IconText from "@/components/icons/IconText.vue";
import IconVoice from "@/components/icons/IconVoice.vue";

const audioModeRef = ref(null);
const isChecked = ref(false);
const emit = defineEmits(["update:isChecked"]);

const sliderRef = ref(null);
const textLeftRef = ref(null);
const textRightRef = ref(null);

watch(isChecked, (newVal) => {
  emit("update:isChecked", newVal);
});

const animateSet = () => {
  gsap.set(audioModeRef.value, {
    scale: 0,
    opacity: 0,
  });

  gsap.set(sliderRef.value, {
    scale: 0,
  });

  gsap.set(textLeftRef.value, {
    opacity: 0,
  });

  gsap.set(textRightRef.value, {
    opacity: 0,
  });
};

const animateIn = (delay = 0) => {
  const tl = gsap.timeline();
  tl.to(audioModeRef.value, {
    scale: 1,
    opacity: 1,
    duration: 0.5,
    delay: delay,
    ease: "power2.out",
  })
    .to(
      sliderRef.value,
      {
        scale: 1,
        duration: 1,
        ease: "power2.out",
      },
      "<+=0.1"
    )
    .to(
      textLeftRef.value,
      {
        opacity: 1,
        duration: 0.5,
        ease: "power2.out",
      },
      "<+=0.1"
    )
    .to(
      textRightRef.value,
      {
        opacity: 1,
        duration: 0.5,
        ease: "power2.out",
      },
      "<+=0.1"
    );
};

const animateOut = () => {
  const tl = gsap.timeline();
  tl.to(audioModeRef.value, {
    scale: 0,
    opacity: 0,
    duration: 1.5,
    ease: "power2.out",
  })
    .to(sliderRef.value, {
      scale: 0,
      duration: 1.5,
      ease: "power2.out",
    })
    .to(textLeftRef.value, {
      opacity: 0,
      duration: 1.5,
      ease: "power2.out",
    })
    .to(textRightRef.value, {
      opacity: 0,
      duration: 1.5,
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
.toggle {
  position: relative;
  display: inline-block;
  width: px-to-vh(254);
  height: px-to-vh(50);
  border-radius: px-to-vh(34);
  margin-left: auto;
  cursor: pointer;

  // Input element
  &__input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
  }

  // Text container and items
  &__text {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 0 px-to-vh(10);
  }

  &__text-item {
    z-index: 10;
    font-size: 1.473vh;
    transition: all 0.4s ease-in-out;

    &--left,
    &--right {
      display: flex;
      color: #4285f4;
      opacity: 0.5;
      align-items: center;
      gap: px-to-vh(5);
      svg {
        width: px-to-vh(18);
        height: px-to-vh(18);
      }
    }

    &--right {
    }
  }

  // Background element
  &__background {
    position: absolute;
    inset: 0;
    height: 100%;
    border-radius: px-to-vh(34);
    border: 1px solid rgba(66, 133, 244, 0.1);
    background: rgba(37, 49, 75, 0.55);
    backdrop-filter: blur(10px);
    &:before {
      border-radius: px-to-vh(34);
    }
  }

  // Slider element
  &__slider {
    display: block;
    position: absolute;
    inset: 0;
    cursor: pointer;
    border-radius: px-to-vh(34);
    transform-origin: left;
    z-index: 10;

    &:before {
      content: "";
      position: absolute;
      height: px-to-vh(39);
      width: 50%;
      left: px-to-vh(8);
      bottom: 50%;
      transform: translateY(50%);
      @include gradient-bg;
      border-radius: px-to-vh(36);
      transition: 0.4s;
    }
  }

  // States
  &__input:checked {
    & + .toggle__slider:before {
      transform: translate(px-to-vh(112), 50%);
    }

    & ~ .toggle__text {
      .toggle__text-item--right {
        color: #100f14;
        opacity: 1;
      }
      .toggle__text-item--left {
        color: #fff;
      }
    }
  }

  &__input:not(:checked) ~ .toggle__text {
    .toggle__text-item--left {
      color: #100f14;
      opacity: 1;
    }
    .toggle__text-item--right {
      color: #fff;
    }
  }
}
</style>
