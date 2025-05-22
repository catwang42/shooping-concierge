<template>
  <div class="qr-code-basic-container">
    <div class="qr-code-basic" ref="qrCodeBasicRef">
      <img :src="src" alt="QR Code" />
      <VText text="Learn more" variant="bold-20" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { generateQR } from "@/utils/qr";
import VText from "./VText.vue";
import gsap from "gsap";
const qrCodeBasicRef = ref(null);

const props = defineProps({
  value: {
    type: String,
    required: true,
  },
});

const src = ref(null);

onMounted(async () => {
  src.value = await generateQR(props.value);
});

defineExpose({
  animateSet: () => {
    gsap.set(qrCodeBasicRef.value, {
      opacity: 0,
      z: -300,
    });
  },
  animateIn: (delay = 0) => {
    gsap.to(qrCodeBasicRef.value, {
      opacity: 1,
      z: 0,
      delay,
      duration: 1,
      ease: "power2.out",
    });
  },
  animateOut: (delay = 0) => {
    gsap.to(qrCodeBasicRef.value, {
      opacity: 0,
      z: -100,
      delay,
      duration: 1,
      ease: "power2.out",
    });
  },
});
</script>

<style lang="scss">
.qr-code-basic-container {
  position: absolute;
  perspective: 1000px;
}
.qr-code-basic {
  background: linear-gradient(70.04deg, #ffffff -100.01%, #4285f4 182.1%);
  border-radius: px-to-vw(32, 4k);
  width: px-to-vw(350, 4k);
  padding: px-to-vw(48, 4k);
  padding-bottom: px-to-vw(32, 4k);
  gap: px-to-vw(32, 4k);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  color: #0e0d0d;

  * {
    white-space: nowrap;
  }

  img {
    width: 100%;
  }
}
</style>
