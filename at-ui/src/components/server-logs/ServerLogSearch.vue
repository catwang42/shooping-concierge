<template>
  <div ref="logRef" class="server-log-search">
    <h4 class="text-medium-21">
      <span class="icon-mag-container"> <IconMag class="icon-mag" /></span>
      Executed multimodal search:
    </h4>
    <p class="text-medium-18">
      User Intent:
      <span class="gradient user-intent">{{ log.userIntent }}</span>
    </p>
    <p class="text-medium-18">
      Item Category:
      <span class="gradient item-category">{{ log.itemCategory }}</span>
    </p>
    <br />
    <p class="text-medium-18">
      Found
      <span class="gradient found-item-count">{{ log.foundItemCount }}</span>
      Items from
      <span class="gradient total-item-count">{{ log.totalItemCount }}</span>
      Total items in
      <span class="gradient elapsed-time">{{
        log.elapsedTime.toFixed(2)
      }}</span>
      seconds
    </p>
    <br />
    <p class="text-medium-18">
      With
      <span class="gradient generated-queries">{{ log.queries.length }}</span>
      Generated queries
    </p>
    <p class="text-medium-18">
      <span
        class="generated-query gradient"
        v-for="query in log.queries"
        :key="query"
      >
        {{ query }}
      </span>
    </p>
  </div>
</template>

<script setup>
import { defineProps, onMounted, ref } from "vue";
import { gsap } from "@/utils/gsap";
import IconMag from "@/components/icons/IconMag.vue";
const logRef = ref(null);
const props = defineProps({
  log: {
    type: Object,
    required: true,
  },
});

onMounted(() => {
  gsap.to(logRef.value, {
    opacity: 1,
    x: 0,
    duration: 1,
    ease: "power2.out",
  });
});
</script>

<style lang="scss" scoped>
.server-log-search {
  margin-top: px-to-vh(48);
  opacity: 0;
  transform: translateX(120%);

  .capitalize {
    text-transform: capitalize;
  }
  h4 {
    padding-bottom: px-to-vh(28);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: px-to-vh(35);
    display: flex;
    align-items: center;
    gap: px-to-vw(10);
    .icon-mag-container {
      display: flex;
      align-items: center;
      gap: px-to-vw(10);
      background: rgba(232, 240, 254, 0.2);
      border-radius: 50%;
      padding: px-to-vh(2);
      .icon-mag {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: px-to-vh(8);
        width: 100%;
        height: 100%;
        position: relative;
      }
    }
  }
  p {
    line-height: 1.8;
    text-align: balance;
  }
  span {
    display: inline-block;
  }
  .generated-query {
    display: block;
  }
}
</style>
