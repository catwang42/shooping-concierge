<template>
  <BackgroundBase>
    <template v-slot="{ oglState }">
      <BackgroundGradient :oglState="oglState" v-bind="bgProps" useStates />
    </template>
  </BackgroundBase>

  <div class="button-container--back">
    <VButton
      ref="backButtonRef"
      class="back-button"
      text="Back"
      variant="clear"
      icon="arrow-left"
      iconLeft
      @click="onBackButtonClick"
    ></VButton>
  </div>

  <div class="button-container--how-it-works">
    <VButton
      @click="onHowItWorksButtonClick"
      ref="howItWorksButtonRef"
      class="how-it-works-button"
      :text="copy.howitworksBtn"
      variant="clear"
    ></VButton>
  </div>
  <div class="sub-routes">
    <component
      v-for="route in activeRoutes"
      :is="route"
      ref="activeRoutesRef"
      :key="route.__name"
    />
  </div>

  <ServerLogListing />
</template>

<script setup>
import { shallowRef, onMounted, onUnmounted } from "vue";
import copy from "/public/data/copy.json";
import { useRouteManager } from "@/router/useRouteManager";
import CBSplashRoute from "@/routes/sub/splash/CBSplashRoute.vue";
import ServerLogListing from "@/components/server-logs/ServerLogListing.vue";
import CBPromptingRoute from "@/routes/sub/prompting/CBPromptingRoute.vue";
import CBMainRoute from "@/routes/sub/main/CBMainRoute.vue";
import CBCart from "@/routes/sub/cart/CBCart.vue";
import BackgroundBase from "@/components/background/BackgroundBase.vue";
import BackgroundGradient from "@/components/background/BackgroundGradient.vue";
import VButton from "@/components/VButton.vue";
import { useProductsStore } from "@/stores/products";
import { useChatStore } from "@/stores/chat";
import { gsap } from "@/utils/gsap";
import { nextTick, ref } from "vue";
import { getQueryParam } from "@/utils/get-query-param";
import { useShopSockets } from "@/services/shopsockets";

import { useAudioStore } from "@/stores/audio";
import { useSessionStore } from "@/stores/session";
import { useLogsStore } from "@/stores/logs";
const activeRoutes = shallowRef([]);
const activeRoutesRef = shallowRef([]);
const backButtonRef = shallowRef(null);
const howItWorksButtonRef = shallowRef(null);
const routes = {
  splash: CBSplashRoute,
  prompting: CBPromptingRoute,
  main: CBMainRoute,
  cart: CBCart,
};

const storeSockets = useShopSockets();

// link the sockets to the stores
const chatStore = useChatStore();
chatStore.setSockets(storeSockets);

const productsStore = useProductsStore();
productsStore.setSockets(storeSockets);

const sessionStore = useSessionStore();
sessionStore.setSockets(storeSockets);

const audioStore = useAudioStore();
audioStore.setSockets(storeSockets);

const logsStore = useLogsStore();
logsStore.setSockets(storeSockets);

const {
  registerRoutes,
  navigateTo,
  // Optional: Use this to customize how routes change behave
  // onRouteChange,
} = useRouteManager();

window.navigateTo = navigateTo;

let index = 0;

function toggleBackButton(open) {
  if (open) {
    gsap.to(backButtonRef.value.$el, {
      z: 0,
      opacity: 1,
      duration: 0.5,
      ease: "power2.out",
      delay: 1,
    });
  } else {
    gsap.to(backButtonRef.value.$el, {
      z: -100,
      opacity: 0,
      duration: 0.5,
      ease: "power2.out",
    });
  }
}

function onHowItWorksButtonClick() {
  eventBus.emit("server-log-open", true);
}

function onBackButtonClick() {
  eventBus.emit("modal:close");
}

function onModalOpen() {
  toggleBackButton(true);
}

function onModalClose() {
  toggleBackButton(false);
}

// Register routes with their animations
onMounted(async () => {
  gsap.set(howItWorksButtonRef.value.$el, {
    z: -100,
    opacity: 0,
  });

  eventBus.on("modal:open", onModalOpen);
  eventBus.on("modal:close", onModalClose);

  gsap.set(backButtonRef.value.$el, {
    z: -100,
    opacity: 0,
  });

  registerRoutes(routes, activeRoutes, activeRoutesRef);

  await nextTick();

  gsap.to(howItWorksButtonRef.value.$el, {
    z: 0,
    opacity: 1,
    ease: "power2.out",
    duration: 1,
    delay: 1,
  });

  const initialView = Object.keys(routes).find(
    (key) => getQueryParam("view", false) === key
  );
  index = Object.keys(routes).indexOf(initialView);
  index = index === -1 ? 0 : index;

  navigateTo(initialView ?? "splash");
});

onUnmounted(() => {
  eventBus.off("modal:open", onModalOpen);
  eventBus.off("modal:close", onModalClose);
});

const bgProps = {
  animate: true,
  bgColor: "#000000",
  fade: 1,
  disk1: {
    color: "#4285f4",
    center: {
      x: -0.6000000000000001,
      y: -0.30000000000000004,
    },
    radius: 0.1,
    type: "group",
  },
  disk2: {
    color: "#1f427c",
    center: {
      x: 0.7599999999999999,
      y: -0.44000000000000006,
    },
    radius: 0.31599999999999995,
    type: "group",
  },
  disk3: {
    color: "#598adb",
    center: {
      x: -0.26999999999999996,
      y: -0.13000000000000006,
    },
    radius: -0.27,
    type: "group",
  },
  disk4: {
    color: "#d1dff5",
    center: {
      x: 1.62,
      y: 0.09000000000000002,
    },
    radius: -0.06,
    type: "group",
  },
};
</script>

<style lang="scss" scoped>
.sub-routes {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;

  > * {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
}

.button-container {
  &--back {
    position: absolute;
    left: calc(25% + px-to-vh(114));
    top: px-to-vh(50);
    z-index: 999;
    perspective: px-to-vh(1000);
  }
  &--how-it-works {
    position: absolute;
    right: px-to-vh(50);
    top: px-to-vh(50);
    z-index: 9999;
    perspective: px-to-vh(1000);
  }
}
</style>
