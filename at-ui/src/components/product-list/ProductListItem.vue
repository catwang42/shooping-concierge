<template>
  <div
    ref="containerRef"
    class="product-list-item"
    :class="{ 'product-list-item--loaded': imageLoaded }"
  >
    <div class="product-list-item__content">
      <div ref="imageContainerRef" class="product-list-item__image">
        <img
          ref="imageRef"
          :src="
            getImageUrl(id, index === 0 ? 500 : 400, index === 0 ? 500 : 400)
          "
          alt="product image"
        />
      </div>
      <div class="product-list-item__info">
        <div class="product-list-item__info-overlay">
          <div class="product-list-item__loading-bar"></div>
          <div class="product-list-item__loading-bar"></div>
          <div class="product-list-item__loading-bar"></div>
        </div>
        <div class="product-list-item__info-content">
          <VText
            ref="nameRef"
            forceSet
            class="product-list-item__name"
            variant="body-18"
            :text="truncated(name, index)"
          />
          <VText
            v-if="price"
            ref="priceRef"
            forceSet
            class="product-list-item__price"
            variant="medium-18"
            :text="'$' + price"
          />
          <VText
            v-if="store"
            ref="storeRef"
            forceSet
            class="product-list-item__store"
            variant="body-18"
            :text="store"
          />
        </div>
        <div class="product-list-item__cta">
          <button
            ref="ctaRef"
            @click="handleCtaClick"
            class="product-list-item__cta-button"
          >
            <IconPlus />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  onMounted,
  ref,
  defineExpose,
  reactive,
  watch,
  onUnmounted,
  nextTick,
} from "vue";
import gsap from "gsap";
import IconPlus from "@/components/icons/IconPlus.vue";
import VText from "@/components/VText.vue";
import { useProductsStore } from "@/stores/products";
import { Flip } from "@/utils/gsap";
import { eventBus } from "@/utils/event-bus";
import { waitUntil } from "@/utils/gsap";
import { getImageUrl } from "@/utils/shared";
import { pxToVh, pxToVw, truncatedTextWithEllipsis } from "../../utils/shared";
const containerRef = ref(null);
const imageRef = ref(null);
const imageContainerRef = ref(null);
const imageLoaded = ref(false);
const nameRef = ref(null);
const priceRef = ref(null);
const storeRef = ref(null);
const ctaRef = ref(null);
const mounted = ref(false);
const animateInRef = reactive({
  value: false,
});
const currentTween = ref(null);

const productsStore = useProductsStore();

const truncated = (text, index) => {
  let count = 40;
  if (index > 4) {
    count = 50;
  }
  if (index === 0) {
    count = 100;
  }
  return truncatedTextWithEllipsis(text, count);
};

const props = defineProps({
  id: {
    type: [Number, String],
    required: true,
  },
  index: {
    type: Number,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  price: {
    type: [Number, String],
    required: false,
  },
  store: {
    type: String,
    required: false,
  },
});

const animateIn = async () => {
  if (!containerRef.value) {
    return;
  }
  if (currentTween.value) {
    currentTween.value.kill();
  }
  currentTween.value = gsap.to(containerRef.value, {
    scale: 1,
    duration: 1,
    ease: "power2.inOut",
    opacity: 1,
    delay: props.index * 0.1,
    onComplete: () => {
      animateInRef.value = true;
      nameRef.value.animateIn(0.5);
      priceRef.value && priceRef.value.animateIn(0.5);
      storeRef.value && storeRef.value.animateIn(0.5);
      gsap.to(ctaRef.value, {
        scale: 1,
        duration: 1,
        delay: 1,
        ease: "power2.inOut",
      });
    },
  });
};

const animateOut = async () => {
  if (!containerRef.value) {
    return;
  }
  if (currentTween.value) {
    currentTween.value.kill();
  }
  currentTween.value = gsap.to(containerRef.value, {
    scale: 0,
    duration: 0.75,
    opacity: 0,
    ease: "power2.inOut",
  });
};

const animateSet = async () => {
  await waitUntil(() => mounted.value);
  gsap.set(containerRef.value, { scale: 0 });
  gsap.set(imageRef.value, { scale: 1.2 });

  nameRef.value.prepare();
  priceRef.value && priceRef.value.prepare();
  storeRef.value && storeRef.value.prepare();

  nameRef.value.animateSet();
  priceRef.value && priceRef.value.animateSet();
  storeRef.value && storeRef.value.animateSet();

  gsap.set(ctaRef.value, { scale: 0 });
};

const handleCtaClick = async () => {
  productsStore.setSelectedProduct(props.id);
  eventBus.emit("modal:open");
  await new Promise((resolve) => setTimeout(resolve, 100));

  const oldContainer = imageContainerRef.value;
  const newContainer = document.querySelector(".product-modal__image");

  const state = Flip.getState(imageRef.value);

  const newStyles = {
    objectFit: "cover",
    borderRadius: pxToVh(36),
    display: "block",
    width: "100%",
  };

  Object.assign(imageRef.value.style, newStyles);

  newContainer.appendChild(imageRef.value);

  const clonedImage = imageRef.value.cloneNode(true);

  Flip.from(state, {
    duration: 1,
    ease: "power2.out",
    onComplete: () => {
      oldContainer.appendChild(clonedImage);
      imageRef.value = clonedImage;
      // remove the inline style border radius
      clonedImage.style.borderRadius = "0px";
    },
  });
};

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});

onMounted(() => {
  mounted.value = true;
  animateSet();
  // wait for image to load
  //imageRef.value.onload = () => {
  // listen for the reactive animateInRef.value to change
  watch(animateInRef, (newVal) => {
    if (newVal) {
      imageLoaded.value = true;

      gsap.to(imageRef.value, {
        scale: 1,
        duration: 1,
        ease: "power2.out",
      });
    }
  });
  //};
});

onUnmounted(() => {
  animateOut();
});
</script>

<style scoped lang="scss">
.product-list-item {
  display: flex;
  flex-direction: column;
  margin: 0;
  border-radius: px-to-vh(24);

  &__content {
    width: 100%;
    height: 100%;
  }

  &__info {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    position: relative;
    width: 100%;
    padding-left: px-to-vh(10);
    padding-right: px-to-vh(10);
  }

  &__loading-bar {
    width: 100%;
    height: 30%;
    border-radius: px-to-vh(4);
    background: linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.2) -100.01%,
      rgba(66, 133, 244, 0.4) 182.1%
    );
    z-index: 100;
    &:nth-child(1) {
      width: 70%;
    }
    &:nth-child(2) {
      width: 40%;
    }
    &:nth-child(3) {
      width: 50%;
    }
  }

  &__cta-button {
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    border-radius: 50%;
    width: px-to-vh(50);
    height: px-to-vh(50);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid $grey;
    color: white;
    cursor: pointer;
    :deep(svg) {
      transition: transform 0.3s ease-in-out;
      width: px-to-vh(18);
      height: px-to-vh(18);
    }
    &:hover {
      :deep(svg) {
        transform: rotate(90deg);
      }
    }
  }

  &__info-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: px-to-vh(10);
    z-index: 100;
    padding-left: px-to-vh(10);
    padding-right: px-to-vh(10);
    transition: opacity 1s ease-in-out;
    pointer-events: none;
  }

  &--loaded {
    .product-list-item__info-overlay {
      opacity: 0;
    }
  }

  &__name,
  &__price,
  &__cta,
  &__store {
    z-index: 0;
    opacity: 0;
    transition: opacity 1s ease-in-out 0.5s;
  }

  &__store {
    color: $grey !important;
  }

  &--loaded {
    .product-list-item__name,
    .product-list-item__price,
    .product-list-item__cta,
    .product-list-item__store {
      opacity: 1 !important;
    }
  }

  &__image {
    margin-bottom: px-to-vh(16);
    overflow: hidden;
    border-radius: px-to-vh(24);
    aspect-ratio: 1/1;
    background: linear-gradient(
      70deg,
      rgba(255, 255, 255, 0.2) -100.01%,
      rgba(66, 133, 244, 0.4) 182.1%
    );
  }

  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: opacity 1s ease-in-out;
  }

  &--loaded {
    img {
      opacity: 1;
    }
  }
}
</style>
