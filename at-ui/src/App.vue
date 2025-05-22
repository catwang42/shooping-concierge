<template>
  <div class="routes shopping">
    <component :is="currentRoute" ref="currentRouteRef" />
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import VChromebook from "./routes/top/VChromebook.vue";
import VMobile from "./routes/top/VMobile.vue";
import V404 from "./routes/top/V404.vue";

import "./styles/global.scss";

const routes = {
  "/": VChromebook,
  "/chromebook": VChromebook,
  "/mobile": VMobile,
};

const currentPath = ref(window.location.hash);

window.addEventListener("hashchange", () => {
  currentPath.value = window.location.hash;
});

const currentRoute = computed(() => {
  return routes[currentPath.value.slice(1) || "/"] || V404;
});
</script>

<style lang="scss">
.routes {
}
</style>
