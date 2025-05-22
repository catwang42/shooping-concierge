<template>
  <div
    ref="containerRef"
    class="qr-code"
    :class="{ mini: props.variant === 'mini' }"
  >
    <div class="qr-code__bg"></div>
    <div class="qr-code__container">
      <div class="qr-code__container__image">
        <img
          class="qr-code__container__image__qr"
          ref="qrImageRef"
          alt="QR Code"
        />
      </div>
      <VText
        ref="textRef"
        :text="displayText"
        :variant="props.variant === 'mini' ? 'bold-16' : 'bold-20'"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineExpose, ref, onMounted } from "vue";
import VText from "./VText.vue";
import QRCode from "qrcode";
import { useSessionStore } from "@/stores/session";
import gsap from "gsap";
import { pxToVh } from "../utils/shared";
import { HOSTNAME } from "../services/shopsockets";

const containerRef = ref(null);
const qrImageRef = ref(null);
const textRef = ref(null);
const heightRef = ref(0);
const displayText = ref("Scan to connect to phone camera");
const isOpen = ref(false);

const sessionStore = useSessionStore();

const props = defineProps({
  qrCode: {
    type: String,
    default: "",
  },
  imageUpload: {
    type: String,
    default: "",
  },
  text: {
    type: String,
    default: "",
  },
  variant: {
    type: String,
    default: "default",
  },
});

const animateIn = () => {
  isOpen.value = true;
  const tl = gsap.timeline();
  tl.to(containerRef.value, {
    height: heightRef.value,
    padding: props.variant === "mini" ? pxToVh(8) : pxToVh(16),
    margin: `${pxToVh(32)} ${pxToVh(40)} 0px ${pxToVh(40)}`,
    duration: 1,
    ease: "power2.inOut",
  }).to(
    containerRef.value,
    {
      "--clip-animation": "0%",
      duration: 1,
      ease: "power2.inOut",
      onComplete: () => {
        tl.kill();
      },
    },
    "-=0.5"
  );
};

window.animateInQR = animateIn;

const animateOut = () => {
  console.log("animateOut(): isOpen: %s", isOpen.value);
  if (!isOpen.value) {
    return;
  }
  const tl = gsap.timeline();
  tl.to(containerRef.value, {
    "--clip-animation": "100%",
    duration: 1,
    height: "auto",
    ease: "power2.inOut",
  }).to(
    containerRef.value,
    {
      height: 0,
      padding: 0,
      margin: 0,
      duration: 1,
      ease: "power2.inOut",
      onComplete: () => {
        isOpen.value = false;
        tl.kill();
      },
    },
    "-=0.5"
  );
};

window.animateOutQR = animateOut;

const animateSet = async () => {
  heightRef.value = containerRef.value.getBoundingClientRect().height;

  gsap.set(containerRef.value, {
    "--clip-animation": "100%",
  });
  gsap.set(containerRef.value, {
    height: 0,
    padding: 0,
    margin: 0,
  });
  gsap.set(qrImageRef.value, {
    opacity: 0,
  });
};

const updateQRCode = () => {
  //const url = `https://${HOSTNAME}/remotecam.html?session_id=${sessionStore.sessionId}`;
  //const url = `https://${window.location.host}/remotecam.html?session_id=${sessionStore.sessionId}`;
  const url = `https://${HOSTNAME}/?session_id=${sessionStore.sessionId}#/mobile`;

  gsap.set(qrImageRef.value, {
    borderRadius: "0",
  });

  QRCode.toDataURL(url, {
    errorCorrectionLevel: "M",
    margin: 0,
    color: {
      light: "#0000",
    },
  })
    .then((url) => {
      gsap.to(qrImageRef.value, {
        opacity: 1,
        duration: 1,
        ease: "power2.inOut",
        delay: 0.1,
      });
      qrImageRef.value.src = url;
    })
    .catch((err) => {
      console.error(err);
    });
};

const updateImageUpload = (imageUpload) => {
  const tl = gsap.timeline({
    onComplete: () => {
      tl.kill();
    },
  });
  tl.to(qrImageRef.value, {
    opacity: 0,
    onComplete: () => {
      qrImageRef.value.src = imageUpload.src;
      gsap.set(qrImageRef.value, {
        borderRadius: "0.8em",
      });
    },
  })
    .to(textRef.value.$el, {
      opacity: 0,
      onComplete: () => {
        displayText.value = "Image received from phone";
      },
    })
    .to(qrImageRef.value, {
      opacity: 1,
      delay: 0.5,
    })
    .to(
      textRef.value.$el,
      {
        opacity: 1,
      },
      "<"
    );
};

onMounted(() => {});

defineExpose({
  animateIn,
  animateOut,
  animateSet,
  updateQRCode,
  updateImageUpload,
});
</script>

<style scoped lang="scss">
.qr-code {
  color: black;
  padding: px-to-vh(16);
  position: relative;
  --clip-animation: 0;

  clip-path: inset(
    var(--clip-animation) var(--clip-animation) 0px 0px round px-to-vh(24)
  );

  &__bg {
    border-radius: px-to-vh(24);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(70deg, #fff -100.01%, #4285f4 182.1%);
  }
  &__container {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    height: 100%;
    gap: px-to-vh(16);
    &__image {
      width: 50%;
      aspect-ratio: 1/1;
      z-index: 1;
      img {
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
      }
    }
    &__image__upload {
      border-radius: px-to-vh(24);
    }
  }

  &.mini {
    clip-path: inset(
      var(--clip-animation) var(--clip-animation) 0px 0px round 0.8em
    );
    .qr-code__bg {
      border-radius: 0.8em !important;
    }
  }
  &.mini {
    display: flex;
    align-items: center;
    width: calc(100% - px-to-vh(48));
    margin-left: px-to-vh(24) !important;
    padding: px-to-vh(8);
    text-align: center;
    .qr-code__container {
      width: 100%;
      height: 50%;
      gap: px-to-vh(8);
      &__image {
        width: 40%;
        padding: px-to-vh(8);
        aspect-ratio: 1/1;
        overflow: hidden;
        &__qr {
          //border-radius: 0.8em;
        }
      }
    }
  }
}
</style>
