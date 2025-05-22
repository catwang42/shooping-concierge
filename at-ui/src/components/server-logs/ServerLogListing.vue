<template>
  <div ref="outerRef" class="server-log-listing">
    <IconCross class="server-log-listing-close" @click="onCloseClick" />
    <VText
      class="server-log-listing-title"
      :text="copy.serverLogTitle"
      variant="bold-24"
    />
    <div ref="containerRef" class="server-log-listing-container">
      <div v-for="log in logsStore.logs" :key="log.id">
        <ServerLogSearch v-if="log.type === 'queryResponse'" :log="log" />
        <ServerLogCuration v-if="log.type === 'presentItems'" :log="log" />
      </div>
    </div>
  </div>
</template>

<script setup>
import copy from "/public/data/copy.json";
import { useLogsStore } from "@/stores/logs";
import { watch, ref, onMounted } from "vue";
import ServerLogSearch from "./ServerLogSearch.vue";
import ServerLogCuration from "./ServerLogCuration.vue";
import VText from "@/components/VText.vue";
import IconCross from "@/components/icons/IconCross.vue";
import { eventBus } from "@/utils/event-bus";
import { gsap } from "@/utils/gsap";
const logsStore = useLogsStore();
const outerRef = ref(null);
const containerRef = ref(null);
const lastHeight = ref(0);
watch(logsStore.logs, (newLogs) => {
  setTimeout(() => {
    // get the height of the chat container
    const heightEl = containerRef.value.scrollHeight;
    if (heightEl === lastHeight.value) {
      return;
    }

    // scroll to the bottom of the chat container
    containerRef.value.scrollTo({
      top: heightEl,
      behavior: "smooth",
    });
  }, 100);
});

const animateIn = () => {
  gsap.to(outerRef.value, {
    opacity: 1,
    x: 0,
    duration: 1,
    ease: "power2.out",
  });
};

const animateOut = () => {
  gsap.to(outerRef.value, {
    opacity: 0,
    x: "120%",
    duration: 1,
    ease: "power2.out",
  });
};

const animateSet = () => {
  gsap.set(outerRef.value, {
    opacity: 0,
    x: "120%",
  });
};

const onCloseClick = () => {
  animateOut();
};
onMounted(() => {
  animateSet();
  eventBus.on("server-log-open", (open) => {
    if (open) {
      animateIn();
    } else {
      animateOut();
    }
  });
});
</script>

<style lang="scss" scoped>
.server-log-listing {
  //display: flex;
  position: fixed;
  top: px-to-vh(50);
  right: px-to-vw(50);
  z-index: 9999;
  width: 28%;
  padding: px-to-vw(48);
  background: rgba(18, 20, 33, 0.8);
  backdrop-filter: blur(30px);
  border-radius: px-to-vw(24);
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: calc(100% - px-to-vh(96));
}
.server-log-listing-title {
  margin-bottom: px-to-vh(48);
}
.server-log-listing-close {
  position: absolute;
  top: px-to-vh(34);
  right: px-to-vh(29);
  cursor: pointer;
}
.server-log-listing-container {
  position: relative;
  overflow-y: scroll;
  overflow-x: visible;
  height: calc(100% - px-to-vh(96));
  width: 100%;
  > div:first-child {
    > div {
      margin-top: 0 !important;
    }
  }
  &::-webkit-scrollbar {
    display: none;
  }
}
</style>
