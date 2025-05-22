<template>
  <div class="vcaption text-bold-40" ref="captionDiv">
    <IconBase ref="icon" class="vcaption__icon" variant="gemini" />
    <span class="vcaption__text">{{ caption }}</span>
  </div>
</template>

<script setup>
import IconBase from "@/components/IconBase.vue";
import gsap from "gsap";
import { onMounted, ref, defineExpose, nextTick } from "vue";
import { waitUntil } from "../../utils/gsap";

const captionDiv = ref(null);
const targetWidth = ref(0);
const icon = ref(null);
const tlRef = ref(null);
const hasMounted = ref(false);
const props = defineProps({
  caption: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    required: false,
    default: "default",
  },
  centered: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const animateIn = async (delay = 0) => {
  // await mounted
  await waitUntil(() => hasMounted.value);

  if (tlRef.value) {
    tlRef.value.kill();
  }

  const tl = gsap.timeline();

  tlRef.value = tl;

  gsap.set(captionDiv.value, {
    visibility: "visible",
  });

  tl.to(captionDiv.value, {
    x: props.centered ? "-50%" : "50%",
    scale: 1,
    duration: 1,
    delay: delay,
    ease: "power2.out",
  })
    .to(icon.value.$el, {
      rotate: 360,
      duration: 1,
      ease: "power2.inOut",
    })
    .to(captionDiv.value, {
      width: targetWidth.value,
      duration: 1,
      ease: "power2.inOut",
      onStart: () => {
        captionDiv.value?.classList?.add("active");
      },
    });
};

const animateOut = () => {
  if (tlRef.value) {
    tlRef.value.kill();
  }
};

const animateSet = () => {};

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});

onMounted(async () => {
  await new Promise((resolve) => setTimeout(resolve, 100));
  targetWidth.value = captionDiv.value.offsetWidth;
  captionDiv.value.style.width = window.innerWidth > 1920 ? "130px" : "40px";
  captionDiv.value.classList.add("init");
  captionDiv.value.classList.add(`variant-${props.variant}`);
  captionDiv.value.classList.add("hidden");
  hasMounted.value = true;
});
</script>

<style lang="scss">
.vcaption {
  visibility: hidden;
  overflow: hidden;
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  color: $darkmode;
  line-height: 1 !important;
  border-radius: 2.5em;
  position: relative;
  background: #0f2f1850;
  backdrop-filter: blur(25px);
  gap: 0.6em;
  transform-origin: left center;
  padding: 11px 30px;
  height: 60px;
  font-size: 16px !important;
  scale: 0;

  @include larger(xxxl) {
    font-size: 40px !important;
    padding: 26px 50px;
    height: 130px;
  }

  &.hidden {
    .vcaption__text {
      padding-left: 0;
    }
  }

  &__text {
    transition:
      opacity 1s ease-out 0.5s,
      padding-left 1s ease-out;
    opacity: 0;
    white-space: nowrap;
    padding-left: 30px;
    @include larger(xxxl) {
      padding-left: 90px;
    }
  }

  &__icon {
    position: absolute;
    color: $shopperBlue;
    height: 20px;
    width: 20px;
    @include larger(xxxl) {
      height: 60px;
      width: 60px;
    }
    left: auto;
    svg {
      width: 100% !important;
      height: 100% !important;
    }
  }

  &.active {
    .vcaption__icon {
      left: 20px;
      @include larger(xxxl) {
        left: 35px;
      }
    }

    .vcaption__text {
      opacity: 1;
      padding-left: 10px;
      @include larger(xxxl) {
        padding-left: 40px;
      }
    }
  }

  @include gradient-border((45deg, #639bf5, #4285f4), 1px);

  &:before {
    border-radius: 2.5em;
  }
}

.shopping {
  .vcaption {
    border-radius: 1em;
    color: $grey;
    background: #0f192f50;
    @include gradient-border((45deg, #639bf5, #4285f4), 1px);
    &:before {
      border-radius: 1em;
    }
    // &__icon {
    //   display: none !important;
    // }
  }
}
</style>
