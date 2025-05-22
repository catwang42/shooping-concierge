<template>
  <div class="cart-container">
    <QRCodeBasic
      ref="qrCodeBasicRef"
      :value="qrCodeUrl"
      class="cart-container__qr-code"
    />
    <Gallery
      ref="galleryRef"
      wide
      :subTitle="copy.cartTitle"
      :imageContent="imageContent"
    />
    <div class="cart-container__content">
      <div ref="cartProductRef" class="cart-product">
        <div class="cart-product__caption-wrapper">
          <VCaption
            centered
            class="cart-product__caption"
            ref="captionRef"
            :caption="truncatedTextWithEllipsis(selectedProduct.name, 50)"
          />
        </div>
        <div class="cart-product__image">
          <img
            ref="cartProductImageRef"
            :src="getImageUrl(selectedProduct.imageID, 1000, 1000)"
            alt="Product Image"
          />
        </div>
      </div>
      <div class="cart-product__message">
        <VText
          class="cart-product__message-text"
          ref="cartProductMessageRef"
          :text="copy.cartMessage"
          variant="medium-80"
          gradient
        />
      </div>
      <div class="cart-product__buttons">
        <VButton
          @click="handleAddAnotherClick"
          ref="cartProductButtonRef"
          class="cart-product__button"
          :text="copy.cartAddAnother"
          variant="clear"
        />
        <VButton
          @click="handleResetClick"
          ref="cartResetButtonRef"
          class="cart-reset__button"
          :text="copy.cartRestartExperience"
          variant="clear"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import Gallery from "@/components/gallery/Gallery.vue";
import VCaption from "@/components/gallery/VCaption.vue";
import VButton from "@/components/VButton.vue";
import VText from "@/components/VText.vue";
import { useChatStore } from "@/stores/chat";
import { useAudioStore } from "@/stores/audio";
import { useProductsStore } from "@/stores/products";
import { useSessionStore } from "@/stores/session";
import gsap from "gsap";
import { onMounted, ref, defineExpose, computed } from "vue";
import { waitUntil } from "../../../utils/gsap";
import { getImageUrl } from "@/utils/shared";
import { eventBus } from "@/utils/event-bus";
import copy from "/public/data/copy.json";
import QRCodeBasic from "@/components/QRCodeBasic.vue";
import { truncatedTextWithEllipsis } from "@/utils/shared";
const galleryRef = ref(null);
const captionRef = ref(null);
const cartProductRef = ref(null);
const cartProductImageRef = ref(null);
const cartProductMessageRef = ref(null);
const cartResetButtonRef = ref(null);
const cartProductButtonRef = ref(null);
const imageLoaded = ref(false);
const qrCodeBasicRef = ref(null);
const productsStore = useProductsStore();
const chatStore = useChatStore();
const sessionStore = useSessionStore();
const audioStore = useAudioStore();
const selectedProduct = computed(() => {
  const product = productsStore.getSelectedProduct();
  if (product) {
    return product;
  } else {
    console.error("no product");
  }
  return "";
});
const qrCodeUrl = computed(() => {
  return `https://${window.location.host}/resources`;
});

onMounted(() => {
  captionRef.value.animateSet();
  cartProductImageRef.value.onload = () => {
    imageLoaded.value = true;
  };
});

defineExpose({
  animateIn: async () => {
    eventBus.emit("animate-background", "edge");
    if (imageLoaded.value) {
      await waitUntil(() => imageLoaded.value);
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
    galleryRef.value.animateIn(2);
    captionRef.value.animateIn(1);
    qrCodeBasicRef.value.animateIn(1);
    cartProductMessageRef.value.animateIn(0.5);
    gsap.to(cartProductRef.value, {
      transform: "translateZ(0px)",
      opacity: 1,
      duration: 2,
      ease: "power2.out",
    });
    gsap.to(cartProductImageRef.value, {
      scale: 1,
      duration: 2,
      ease: "power2.out",
    });
    gsap.to(cartProductButtonRef.value.$el, {
      z: 0,
      opacity: 1,
      duration: 1,
      delay: 2,
      ease: "power2.out",
    });
    gsap.to(cartResetButtonRef.value.$el, {
      z: 0,
      opacity: 1,
      duration: 1,
      delay: 2,
      ease: "power2.out",
    });
  },
  animateOut: async () => {
    galleryRef.value.animateOut();
    captionRef.value.animateOut();
    cartProductMessageRef.value.animateOut();
    gsap.to(cartProductRef.value, {
      transform: "translateZ(-200px)",
      opacity: 0,
      duration: 1,
      ease: "power2.out",
    });
    gsap.to(cartProductImageRef.value, {
      scale: 1.5,
      duration: 1,
      ease: "power2.out",
    });
    gsap.to(cartProductButtonRef.value.$el, {
      z: -100,
      opacity: 0,
      duration: 1,
      ease: "power2.out",
    });
    gsap.to(cartResetButtonRef.value.$el, {
      z: -100,
      opacity: 0,
      duration: 1,
      ease: "power2.out",
    });
    qrCodeBasicRef.value.animateOut();
    await new Promise((resolve) => setTimeout(resolve, 2000));
  },
  animateSet: async () => {
    qrCodeBasicRef.value.animateSet();
    await cartProductMessageRef.value.prepare();
    cartProductMessageRef.value.animateSet();
    gsap.set(cartProductImageRef.value, {
      scale: 1.5,
    });
    gsap.set(cartProductRef.value, {
      transform: "translateZ(-200px)",
      opacity: 0,
    });
    gsap.set(cartProductButtonRef.value.$el, {
      z: -100,
      opacity: 0,
    });
    gsap.set(cartResetButtonRef.value.$el, {
      z: -100,
      opacity: 0,
    });
  },
});

const handleAddAnotherClick = () => {
  navigateTo("main");
  productsStore.setCartOpen(false);
  eventBus.emit("cart:close");
};

const handleResetClick = () => {
  chatStore.resetAll();
  productsStore.resetAll();
  sessionStore.resetAll();
  sessionStore.setGeminiMode("text");
  productsStore.setCartOpen(false);
  eventBus.emit("cart:close");
  navigateTo("splash");
  audioStore.stopRecording();
  audioStore.stopAudioPlayer();
};

const imageContent = [
  {
    src: "https://fastly.picsum.photos/id/813/300/300.jpg?hmac=P1QaCX9HgZK2OE_XcRiYdFI9wkhiSmgYKor-9yDp00c",
    alt: "Image 1",
    caption: "Caption 1",
    position: {
      left: "0%",
      top: "0%",
      right: "auto",
      bottom: "auto",
    },
  },
  {
    src: "https://fastly.picsum.photos/id/960/300/300.jpg?hmac=33HCKWbjLrPghX-xdgDHytx4nbiWfmdQdI-Fwsgj_00",
    alt: "Image 2",
    caption: "Caption 2",
    position: {
      left: "auto",
      top: "0%",
      right: "0%",
      bottom: "auto",
    },
  },
  {
    src: "https://fastly.picsum.photos/id/813/300/300.jpg?hmac=P1QaCX9HgZK2OE_XcRiYdFI9wkhiSmgYKor-9yDp00c",
    alt: "Image 3",
    caption: "Caption 3 testing long caption",
    position: {
      left: "0%",
      right: "auto",
      top: "auto",
      bottom: "0%",
    },
  },
  {
    src: "https://fastly.picsum.photos/id/960/300/300.jpg?hmac=33HCKWbjLrPghX-xdgDHytx4nbiWfmdQdI-Fwsgj_00",
    alt: "Image 4",
    caption: "Caption 4",
    position: {
      left: "auto",
      top: "auto",
      right: "0%",
      bottom: "0%",
    },
  },
  {
    src: "https://fastly.picsum.photos/id/813/300/300.jpg?hmac=P1QaCX9HgZK2OE_XcRiYdFI9wkhiSmgYKor-9yDp00c",
    alt: "Image 5",
    caption: "Caption 5",
    position: {
      left: "auto",
      top: "auto",
      right: "20%",
      bottom: "0%",
    },
  },
  {
    src: "https://fastly.picsum.photos/id/960/300/300.jpg?hmac=33HCKWbjLrPghX-xdgDHytx4nbiWfmdQdI-Fwsgj_00",
    alt: "Image 6",
    caption: "Caption 6",
    position: {
      top: "0%",
      left: "20%",
      right: "auto",
      bottom: "auto",
    },
  },
];
</script>

<style lang="scss" scoped>
.cart-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  &__qr-code {
    position: absolute;
    bottom: px-to-vh(50);
    right: px-to-vh(50);
    z-index: 1001;
  }

  &__content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    perspective: 1000px;
    z-index: 1001;
    width: 100%;
  }

  .cart-product__buttons {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin-top: 58px;
  }

  .cart-product {
    margin-bottom: 53px;
    position: relative;

    &__message {
      margin: 0 auto;
      text-align: center;
      max-width: 60%;
    }
    &__message-text {
      margin: 0 auto;
    }

    &__caption-wrapper {
      position: absolute;
      left: 50%;
      top: -7%;
    }

    &__button {
      z-index: 999;
    }

    &__caption {
      //left: 50%;
      margin-bottom: 20px;
      visibility: hidden;
      z-index: 1;
    }

    &__image {
      width: 400px;
      height: 400px;
      border-radius: 36px;
      overflow: hidden;
      z-index: 0;
      img {
        z-index: 0;
        display: block;
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 36px;
      }
    }
  }
}
</style>
