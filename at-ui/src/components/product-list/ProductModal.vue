<template>
  <div ref="containerRef" class="product-modal">
    <div class="product-modal__inner">
      <div ref="imageRef" class="product-modal__image">
        <!-- gsap flip image goes here-->
      </div>
      <div class="product-modal__info">
        <VText
          ref="nameRef"
          animateBy="lines"
          class="product-modal__info-name"
          :text="formatText(product?.name || 'Product Name')"
          variant="bold-40"
        />
        <VText
          animateBy="lines"
          ref="descriptionRef"
          class="product-modal__info-description"
          :text="formatText(product?.description || 'Product Description')"
          variant="body-24"
        />
        <VText
          v-if="product?.store"
          ref="storeRef"
          animateBy="lines"
          class="product-modal__info-store"
          :text="product?.store || 'Product Store'"
          variant="body-16"
        />
        <VText
          v-if="product?.price"
          ref="priceRef"
          animateBy="lines"
          class="product-modal__info-price"
          :text="'$' + (product?.price || '0.00')"
          variant="body-24"
        />
        <div class="product-modal__info-cta-wrapper">
          <VButton
            @click="handleCTAClick"
            ref="ctaRef"
            variant="primary"
            :text="copy.productModalCTA"
          />
          <VButton
            @click="handleFindSimilarClick"
            ref="findSimilarRef"
            variant="clear"
            :text="copy.productSimilarCTA"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import VButton from "@/components/VButton.vue";
import VText from "@/components/VText.vue";
import { onMounted, ref, defineExpose, onUnmounted } from "vue";
import { gsap } from "@/utils/gsap";
import { useProductsStore } from "@/stores/products";
import { useSessionStore } from "@/stores/session";
import { useChatStore } from "@/stores/chat";
import { eventBus } from "@/utils/event-bus";
import { waitUntil } from "../../utils/gsap";
import copy from "/public/data/copy.json";
const productsStore = useProductsStore();
const sessionStore = useSessionStore();
const chatStore = useChatStore();
window.mockProducts = productsStore.mockHydrate;

const mounted = ref(false);

const nameRef = ref(null);
const descriptionRef = ref(null);
const storeRef = ref(null);
const priceRef = ref(null);
const ctaRef = ref(null);
const findSimilarRef = ref(null);
const imageRef = ref(null);
const containerRef = ref(null);

function formatText(text) {
  // remove \n and \r from text
  const formattedText = text.replace(/\n|\r/g, "");

  const truncatedTextWithEllipsis = formattedText.slice(0, 100) + "...";
  // remove any html tags
  return truncatedTextWithEllipsis.replace(/<[^>]*>?/g, "");
}

const handleCTAClick = () => {
  console.log("handleCTAClick", productsStore.selectedProductID);
  productsStore.setCartOpen(true, productsStore.selectedProductID);
  eventBus.emit("modal:close");
  navigateTo("cart");
};

const handleFindSimilarClick = () => {
  eventBus.emit("modal:close");
  chatStore.sendUserMessage("Find me similar products");
};

const animateIn = async () => {
  sessionStore.sendGenerateImage(productsStore.selectedProductID);
  await waitUntil(() => mounted.value);
  gsap.set(containerRef.value, { pointerEvents: "auto" });
  gsap.set(imageRef.value, { opacity: 1, z: 0 });
  await new Promise((resolve) => setTimeout(resolve, 100));
  await Promise.all([
    nameRef.value.prepare(),
    descriptionRef.value.prepare(),
    storeRef.value && storeRef.value.prepare(),
    priceRef.value && priceRef.value.prepare(),
  ]);
  nameRef.value.animateIn(0.25, { duration: 1 });
  descriptionRef.value.animateIn(0.25, { duration: 1 });
  storeRef.value && storeRef.value.animateIn(0.4, { duration: 1 });
  priceRef.value && priceRef.value.animateIn(0.6, { duration: 1 });
  gsap.to(ctaRef.value.$el, {
    z: 0,
    opacity: 1,
    duration: 1,
    delay: 0.7,
    ease: "power2.out",
  });
  gsap.to(findSimilarRef.value.$el, {
    z: 0,
    opacity: 1,
    duration: 1,
    delay: 1,
    ease: "power2.out",
  });
};

const animateOut = async () => {
  productsStore.setModalOpen(false);
  await waitUntil(() => mounted.value);
  gsap.set(containerRef.value, { pointerEvents: "none" });
  nameRef.value.animateOut();
  descriptionRef.value.animateOut();
  storeRef.value && storeRef.value.animateOut();
  priceRef.value && priceRef.value.animateOut();
  gsap.to(imageRef.value, {
    z: -100,
    opacity: 0,
    duration: 1,
    ease: "power2.inOut",
    onComplete: () => {
      while (imageRef.value.firstChild) {
        imageRef.value.removeChild(imageRef.value.firstChild);
      }
    },
  });
  gsap.to(ctaRef.value.$el, {
    z: -100,
    opacity: 0,
    duration: 1,
    ease: "power2.out",
  });
  gsap.to(findSimilarRef.value.$el, {
    z: -100,
    opacity: 0,
    duration: 1,
    delay: 0.2,
    ease: "power2.out",
  });
};

defineExpose({
  animateOut,
  animateIn,
});

onMounted(async () => {
  gsap.set(containerRef.value, { pointerEvents: "none" });
  await Promise.all([
    nameRef.value.prepare(),
    descriptionRef.value.prepare(),
    storeRef.value && storeRef.value.prepare(),
    priceRef.value && priceRef.value.prepare(),
  ]);

  gsap.set(ctaRef.value.$el, { z: -100, opacity: 0 });
  gsap.set(findSimilarRef.value.$el, { z: -100, opacity: 0 });
  eventBus.on("modal:open", animateIn);
  eventBus.on("modal:close", animateOut);

  mounted.value = true;
});

onUnmounted(() => {
  eventBus.off("modal:open", animateIn);
  eventBus.off("modal:close", animateOut);
});

defineProps({
  product: {
    type: Object,
    required: false,
  },
});
</script>

<style lang="scss" scoped>
.product-modal {
  position: fixed;
  top: 50%;
  left: calc(25% + 117px);
  transform: translate(0, -50%);
  width: 58%;
  z-index: 1000;

  // :deep(.VText) {
  //   text-wrap: unset;
  // }

  &__info {
    perspective: 1000px;
  }

  &__info-name {
    margin-bottom: 24px;
  }

  &__info-description {
    margin-bottom: 31px;
    width: 100%;
  }

  &__info-price {
    margin-bottom: 31px;
    width: 100%;
  }

  &__info-store {
    margin-bottom: 8px;
    color: $darkGrey;
    width: 100%;
  }

  &__info-cta-wrapper {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: px-to-vh(16);
    perspective: 1000px;
  }

  &__inner {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    perspective: 1000px;
  }
  &__image {
    width: 50%;
    height: 100%;
    margin-right: 64px;
    flex-shrink: 0;
    img {
      display: none;
      object-fit: cover;
      border-radius: 36px;
      width: 100%;
    }
  }
}
</style>
