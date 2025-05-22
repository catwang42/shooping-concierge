<template>
  <div class="product-list" ref="productListRef">
    <VText
      class="product-list__title"
      ref="productTitleRef"
      variant="bold-64 gradient"
    />
    <TransitionGroup
      @leave="animateOutItem"
      @enter="animateInItem"
      name="product-list"
      tag="div"
      class="product-list__inner--top"
    >
      <ProductListItem
        v-for="(product, index) in displayedProducts.slice(0, 5)"
        :index="index"
        :key="product.id"
        :id="product.id"
        :name="product.name"
        :price="product.price"
        :image="product.image"
        :store="product.store"
        :data-index="index"
        ref="productListItems"
      />
    </TransitionGroup>
    <TransitionGroup
      @leave="animateOutItem"
      @enter="animateInItem"
      name="product-list"
      tag="div"
      class="product-list__inner--bottom"
    >
      <ProductListItem
        v-for="(product, index) in displayedProducts.slice(4)"
        :index="index + 5"
        :key="product.id"
        :id="product.id"
        :name="product.name"
        :price="product.price"
        :image="product.image"
        :store="product.store"
        :data-index="index + 5"
        ref="productListItems"
      />
    </TransitionGroup>
    <ProductModal :product="selectedProduct" />
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  onUnmounted,
  ref,
  defineExpose,
  watch,
  nextTick,
} from "vue";
import ProductListItem from "@/components/product-list/ProductListItem.vue";
import ProductModal from "@/components/product-list/ProductModal.vue";
import { useProductsStore } from "@/stores/products";
import { useRouteManager } from "@/router/useRouteManager";
import VText from "@/components/VText.vue";
import gsap from "gsap";
import { storeToRefs } from "pinia";
import { eventBus } from "@/utils/event-bus";
import { useChatStore } from "@/stores/chat";
const productTitleRef = ref(null);
const productListItems = ref([]);
const productsStore = useProductsStore();
const displayedProducts = ref([]);
const productListRef = ref(null);
const prepared = ref(false);
const {
  products,
  currentProductName,
  currentProductGroupID,
  selectedProductID,
  modalOpen,
} = storeToRefs(productsStore);

const chatStore = useChatStore();

const { previousRoute } = useRouteManager();

// the product that is currently selected
const selectedProduct = computed(() => {
  const value = products.value.find(
    (product) => product.id === selectedProductID.value
  );
  return value;
});

// the group of products that are currently being displayed
const filteredProducts = computed(() => {
  if (!currentProductGroupID.value) {
    return products.value;
  }
  const filteredProducts = products.value.filter(
    (product) => product.groupID === currentProductGroupID.value
  );
  return filteredProducts;
});

watch(filteredProducts, async (newVal) => {
  chatStore.updateQueryCount(currentProductGroupID.value, newVal.length + 1);

  animateOutAll();
  await new Promise((resolve) => setTimeout(resolve, 1000));
  productListRef.value.scrollTo({
    top: 0,
    behavior: "smooth",
  });
  displayedProducts.value = newVal;

  if (newVal.length > 0 && modalOpen.value) {
    eventBus.emit("modal:close");
  }
});

watch(currentProductName, async (newVal) => {
  await productTitleRef.value?.animateOut();
  await productTitleRef.value?.setText(newVal);
  productTitleRef.value?.animateIn(0, {
    duration: 1.5,
  });
});

onMounted(async () => {
  if (previousRoute.value?.id === "cart") {
    // reset the product list and the product title
    displayedProducts.value = filteredProducts.value;
    setTimeout(() => {
      animateInAll(1);
    }, 1000);
  }

  await productTitleRef.value?.prepare();
  productTitleRef.value?.animateSet();

  window.productTitle = productTitleRef.value;

  prepared.value = true;

  eventBus.on("modal:open", onModalOpen);
  eventBus.on("modal:close", onModalClose);
});

async function onModalClose() {
  productListRef.value.scrollTo({
    top: 0,
  });
  if (!productsStore.cartOpen) {
    productTitleRef.value?.animateIn(0, {
      duration: 1.5,
    });
    animateInAll(1);
  }
}

async function onModalOpen() {
  productTitleRef.value?.animateOut();
  animateOutAll(1);
}

async function animateInItem(el, done) {
  setTimeout(async () => {
    productListItems.value.forEach((item) => {
      item.animateIn();
    });
  }, 1000);
}

// animate out a single product list item when it is removed from the list
function animateOutItem(el, done) {
  gsap.to(el, {
    scale: 0,
    duration: 0.75,
    opacity: 0,
    ease: "power2.inOut",
    onComplete: done,
  });
}
// animate out all product list items temporarily
function animateOutAll(delay = 0) {
  productListItems.value.forEach((item) => {
    item.animateOut();
  });
  //productTitleRef.value?.animateOut();
}

// animate in all product list items that are currently hidden
async function animateInAll(delay = 0) {
  console.log("animateInAll");
  //productTitleRef.value?.animateIn();
  productListItems.value.forEach((item) => {
    item.animateIn();
  });
}

onUnmounted(() => {
  eventBus.off("modal:open", animateOutAll);
  eventBus.off("modal:close", animateInAll);
});

defineExpose({
  animateOutAll,
  animateInAll,
});
</script>

<style scoped lang="scss">
.product-list {
  width: 100%;
  height: 100%;
  overflow-y: scroll;
  position: relative;

  &__title {
    //display: none;
    text-transform: capitalize;
  }
  &::-webkit-scrollbar {
    display: none;
  }
  &__inner {
    &--top {
      display: grid;
      grid-template-columns: 1.2fr 1.2fr 0.9fr 0.9fr;
      grid-auto-rows: auto;
      gap: px-to-vh(10);
      height: fit-content;
      padding-top: px-to-vh(64);
      padding-bottom: px-to-vh(64);
      width: 100%;

      grid-template-areas:
        "featured featured item2 item3"
        "featured featured item4 item5";

      grid-auto-rows: 1fr;

      .product-list-item {
        &:nth-child(1) {
          grid-area: featured;
          :deep(.product-list-item__image) {
            display: block;
            border-radius: px-to-vh(40);
          }
          :deep(.product-list-item__content) {
            padding-right: px-to-vh(40);
          }
        }
        &:nth-child(2) {
          grid-area: item2;
          margin-bottom: px-to-vh(50);
        }
        &:nth-child(3) {
          grid-area: item3;
        }
        &:nth-child(4) {
          grid-area: item4;
        }
        &:nth-child(5) {
          grid-area: item5;
        }
      }
    }

    &--bottom {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      grid-auto-rows: auto;
      row-gap: px-to-vh(104);
      column-gap: px-to-vh(10);
      height: fit-content;
      padding-bottom: px-to-vh(64);
      width: 100%;
    }
  }
}
</style>
