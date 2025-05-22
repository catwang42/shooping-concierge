<template>
  <div class="cb-main">
    <CBSidebar ref="sidebarRef" />
    <div class="cb-main__content">
      <ProductList ref="productListRef" />
    </div>
    <p
      ref="imageCreditsRef"
      class="cb-main__image-credits text-body-12"
      v-html="copy.imageCredits"
    ></p>
  </div>
</template>

<script setup>
import { defineProps, onMounted, ref } from "vue";
import { useChatStore } from "@/stores/chat";
import { useProductsStore } from "@/stores/products";
import CBSidebar from "@/routes/sub/main/CBSidebar.vue";
import ProductList from "@/components/product-list/ProductList.vue";
import copy from "/public/data/copy.json";
import { gsap } from "@/utils/gsap";
const chatStore = useChatStore();
const productsStore = useProductsStore();

window.chatStore = chatStore;
window.productsStore = productsStore;

const sidebarRef = ref(null);
const productListRef = ref(null);
const productListHidden = ref(false);
const imageCreditsRef = ref(null);
const mounted = ref(false);

defineProps({});

onMounted(() => {
  sidebarRef.value.animateSet();
  mounted.value = true;
});

async function animateIn() {
  await new Promise((resolve) => setTimeout(resolve, 1000));
  eventBus.emit("animate-background", "idle");
  sidebarRef.value.animateIn();
  gsap.to(imageCreditsRef.value, {
    opacity: 1,
    duration: 1,
    ease: "power2.out",
  });
  if (productListHidden.value) {
    productListRef.value.animateInAll();
    productListHidden.value = false;
  }
}

window.animateInMain = animateIn;

async function animateOut() {
  sidebarRef.value.animateOut();
  productListRef.value.animateOutAll();
  productListHidden.value = true;
  gsap.to(imageCreditsRef.value, {
    opacity: 0,
    duration: 1,
    ease: "power2.out",
  });
  await new Promise((resolve) => setTimeout(resolve, 2000));
}

window.animateOutMain = animateOut;

function animateSet() {
  gsap.set(imageCreditsRef.value, {
    opacity: 0,
  });
  sidebarRef.value.animateSet();
}

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});
</script>

<style lang="scss" scoped>
.cb-main {
  display: flex;
  flex-direction: row;
  width: 100vw;
  height: 100vh;

  &__sidebar {
    width: 25%;
    height: 100%;
    border-radius: 0 px-to-vh(41) px-to-vh(41) 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(28, 32, 44, 0.53);
    backdrop-filter: blur(px-to-vh(30));
    color: $grey;
  }

  &__image-credits {
    position: fixed;
    bottom: px-to-vh(40);
    right: px-to-vh(50);
    color: white;
    text-shadow: 0px px-to-vh(4) px-to-vh(44) #000;
    :deep(a) {
      color: white;
      text-decoration: underline;
    }
  }

  &__content {
    width: 75%;
    height: 100%;
    padding: px-to-vh(64) px-to-vh(117) 0 px-to-vh(117);
  }
}
</style>
