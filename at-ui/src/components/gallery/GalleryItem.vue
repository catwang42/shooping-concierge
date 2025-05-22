<template>
  <div ref="imageContainer" class="gallery-item">
    <VCaption ref="captionRef" :caption="caption" />
    <div ref="imageInner" class="gallery-item__inner">
      <img ref="image" :src="src" />
    </div>
    <svg
      class="border-svg"
      width="100%"
      height="100%"
      :viewBox="'0 0 250 200'"
      preserveAspectRatio="none"
    >
      <path
        ref="borderRect"
        class="border-rect"
        d="M25,2 
           L225,2 
           C237,2 248,13 248,25 
           L248,175 
           C248,187 237,198 225,198 
           L25,198 
           C13,198 2,187 2,175 
           L2,25 
           C2,13 13,2 25,2"
        fill="none"
        stroke="#007AFF"
        stroke-width="2"
        stroke-linejoin="round"
      />
    </svg>
  </div>
</template>

<script setup>
import gsap from "gsap";
import { onMounted, ref, defineExpose, onBeforeUnmount } from "vue";
import VCaption from "@/components/gallery/VCaption.vue";
import { pxToVh } from "@/utils/shared";

const image = ref(null);
const imageContainer = ref(null);
const imageInner = ref(null);
const captionRef = ref(null);
const tlRef = gsap.timeline();
const borderRect = ref(null);
const isAnimatingOut = ref(false);
const emit = defineEmits(["done"]);

onMounted(() => {
  // set style of image
  imageContainer.value.style.left = `${props.position.left}`;
  imageContainer.value.style.top = `${props.position.top}`;
  imageContainer.value.style.right = `${props.position.right}`;
  imageContainer.value.style.bottom = `${props.position.bottom}`;

  if (props.animate) {
    initAnimate();
  }

  // Initialize the SVG border animation
  const border = borderRect.value;
  const length = border.getTotalLength();

  gsap.set(border, {
    strokeDasharray: length,
    strokeDashoffset: length,
  });

  gsap.to(border, {
    strokeDashoffset: 0,
    duration: 2,
    delay: 2.5,
    ease: "linear",
  });
});

onBeforeUnmount(() => {
  // Clean up any animations when component is unmounted
  if (tlRef.value) {
    tlRef.value.kill();
  }
});

function animateIn() {
  if (captionRef.value) {
    captionRef.value.animateIn();
  }
}

function animateOut() {
  if (isAnimatingOut.value) return;
  isAnimatingOut.value = true;

  if (tlRef.value) {
    tlRef.value.kill();
  }

  if (!imageContainer.value) return;

  gsap.to(imageContainer.value, {
    z: imageContainer.value.style.z + 500,
    opacity: 0,
    duration: 1,
    onComplete: () => {
      emit("done", props.id);
    },
  });
  captionRef?.value?.animateOut();
}

defineExpose({
  animateIn,
  animateOut,
});

function initAnimate() {
  if (tlRef.value) {
    tlRef.value.kill();
  }

  const x =
    props.position.left === "auto" ? -Math.random() * 20 : Math.random() * 20;
  const y =
    props.position.top === "auto" ? -Math.random() * 20 : Math.random() * 20;

  const tl = gsap.timeline({
    defaults: {
      ease: "power1.out",
    },
    onComplete: () => {
      // remove this component from the parent
      emit("done", props.id);
    },
  });

  tlRef.value = tl;

  setTimeout(() => {
    captionRef.value.animateIn();
  }, 10);

  tl.set(imageContainer.value, {
    x: `${x}%`,
    y: `${y}%`,
    z: -300,
  })
    .set(imageInner.value, {
      scale: 0,
    })
    .set(image.value, {
      scale: 4,
    })
    .to(
      imageInner.value,
      {
        scale: 1,
        duration: 3,
        ease: "power1.out",
        delay: 0.5,
        onStart: () => {},
      },
      "<"
    )
    .to(
      image.value,
      {
        scale: 1,
        duration: 3,
        ease: "power1.out",
      },
      "<"
    )
    .to(
      imageContainer.value,
      {
        z: 200,
        duration: 13,
      },
      "<"
    )
    .to(
      imageContainer.value,
      {
        opacity: 0,
        duration: 1,
      },
      "<+=6"
    );
}

const props = defineProps({
  src: {
    type: String,
    required: true,
  },
  position: {
    type: Object,
    required: true,
  },
  id: {
    type: String,
    required: true,
  },
  animate: {
    type: Boolean,
    required: false,
    default: true,
  },
  caption: {
    type: String,
    required: false,
    default: "Testing",
  },
});
</script>

<style lang="scss" scoped>
.gallery-item {
  position: absolute;
  top: 0;
  left: 0;
  transform-style: preserve-3d;
  will-change: transform;

  @include fluid(
    "width",
    (
      xxl: 250px,
      fourk: 624px,
    )
  );

  @include fluid(
    "height",
    (
      xxl: 200px,
      fourk: 480px,
    )
  );

  .border-svg {
    position: absolute;
    top: 0;
    left: 0;
    width: calc(100% + 2px);
    height: calc(100% + 2px);
    transform: translate(-1px, -1px);
    pointer-events: none;
  }

  .border-rect {
    stroke: $shopperBlue;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform-origin: center;
  }

  &__inner {
    width: calc(100% - 2px);
    height: calc(100% - 2px);
    box-sizing: border-box;
    border: none;
    transform-origin: center;
    overflow: hidden;
    border-radius: px-to-vh(25);
  }
  .vcaption {
    position: absolute;
    top: 40%;
    right: 0;
    transform: translateX(50%, -50%);
    z-index: 100;
  }
}
</style>
