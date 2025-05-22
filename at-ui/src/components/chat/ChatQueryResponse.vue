<template>
  <transition @leave="animateOut">
    <div class="chat-query-response chat-item">
      <div ref="innerRef" class="chat-query-response__inner">
        <div class="chat-query-response__inner__header">
          <IconQuery class="chat-query-response__inner__header__icon" />
          <VText text="Query" variant="bold-14" />
          <VText
            v-if="resultCount"
            class="chat-query-response__inner__header__result-count"
            :text="`${resultCount} results`"
            variant="medium-14"
          />
        </div>
        <div class="chat-query-response__inner__content">
          <p
            v-html="text"
            class="text-body-18 chat-query-response__inner__content__queryname"
          ></p>
          <hr v-if="productName" />
          <button
            v-if="productName"
            class="chat-query-response__inner__content__product"
            @click="handleProductClick"
          >
            <img
              :src="getImageUrl(groupIconID, 44, 44)"
              alt="Product Icon"
              class="chat-query-response__inner__content__product__icon"
            />
            <VText :text="productName" variant="medium-18" />
            <IconArrow class="chat-query-response__inner__content__arrow" />
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import VText from "@/components/VText.vue";
import IconQuery from "@/components/icons/IconQuery.vue";
import IconArrow from "@/components/icons/IconArrow.vue";
import gsap from "gsap";
import { onMounted, ref, defineExpose } from "vue";
import { useProductsStore } from "@/stores/products";
import { getImageUrl } from "@/utils/shared";
const props = defineProps({
  text: String,
  resultCount: Number,
  productName: String,
  groupIconID: String,
  groupID: String,
});
const innerRef = ref(null);
const isLoading = ref(false);

const productsStore = useProductsStore();

function handleProductClick() {
  if (productsStore.modalOpen) return;
  productsStore.setProductGroup({
    productName: props.productName,
    group_id: props.groupID,
  });
}

function animateIn() {
  gsap.to(innerRef.value, {
    x: 0,
    opacity: 1,
    ease: "Power2.out",
  });
}

function animateSet() {
  gsap.set(innerRef.value, {
    x: -100,
    opacity: 0,
  });
  setTimeout(() => {
    animateIn();
  }, 100);
}

function animateOut(el, done) {
  gsap.to(el, {
    x: -100,
    opacity: 0,
    ease: "Power2.out",
    onComplete: done,
  });
}

onMounted(() => {
  isLoading.value = true;
  animateSet();
});

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});
</script>

<style scoped lang="scss">
.chat-query-response {
  width: 100%;

  &__inner {
    box-shadow: 0 px-to-vh(5) px-to-vh(10.7) 0 rgba(0, 0, 0, 0.25);
  }

  &__inner__header {
    display: flex;
    flex-direction: row;
    gap: px-to-vh(8);
    align-items: center;
    width: 100%;
    opacity: 0.5;
    margin-bottom: px-to-vh(24);
    &__icon {
      width: px-to-vh(24);
      height: px-to-vh(24);
      color: $lightBlue;
      opacity: 0.5;
    }
    &__result-count {
      margin-left: auto;
    }
  }

  hr {
    border: none;
    height: px-to-vh(1);
    background-color: rgba(255, 255, 255, 0.2);
    margin-bottom: px-to-vh(24);
  }

  &__inner {
    @include chat-panel;
  }

  &__inner__content {
    width: 100%;
    &__queryname {
      padding-bottom: px-to-vh(24);
      text-transform: capitalize;
    }
    &__arrow {
      display: flex;
      width: px-to-vh(20);
      height: px-to-vh(20);
      min-width: px-to-vh(20);
      min-height: px-to-vh(20);
      svg {
        width: 100%;
        height: 100%;
      }
    }
    &__product {
      border: 0;
      border-top: 1px solid rgba(255, 255, 255, 0.2);
      position: relative;
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: px-to-vh(12);
      color: white;
      max-width: 80%;
      background: linear-gradient(
        50deg,
        rgba(66, 133, 244, 0.1) -4.95%,
        rgba(217, 231, 255, 0.2) 117.88%
      );
      box-shadow: 0px 14px 59.7px 0px rgba(0, 0, 0, 0.15);
      padding: px-to-vh(8) px-to-vh(16) px-to-vh(8) px-to-vh(8);
      border-radius: px-to-vh(16);
      text-transform: capitalize;
      text-align: left;
      cursor: pointer;
      transition: scale 0.2s ease-in-out;
      &:hover {
        scale: 1.05;
      }
      &:before {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        height: calc(100% - 1px);
        border-radius: px-to-vh(16);
        border: 1.5px solid transparent;
        background: linear-gradient(45deg, #5091fa, #afdcfaf1) border-box;
        mask:
          linear-gradient(#000 0 0) padding-box,
          linear-gradient(#000 0 0);
        mask-composite: exclude;
      }
    }
    &__product__icon {
      width: px-to-vh(44);
      height: px-to-vh(44);
      border-radius: px-to-vh(12);
    }
  }
}
</style>
