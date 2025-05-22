<template>
  <div class="input-equalizer">
    <div class="input-equalizer__bars">
      <div v-for="n in 21" :key="n" class="input-equalizer__bar"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const bars = ref([]);
</script>

<style lang="scss" scoped>
.input-equalizer {
  width: 100%;
  height: 100%;
  &__bars {
    display: flex;
    justify-content: center;
    gap: 4px;
    height: 20px;
    margin-left: 12px;
    align-items: center;
  }

  &__bar {
    width: 3px;
    background: $darkmode;
    border-radius: 3px;
    animation: equalize 1s infinite;
    background: $shopperBlue;

    @for $i from 1 through 20 {
      &:nth-child(#{$i}) {
        animation-delay: #{$i * 0.01}s;
        animation-duration: #{random(4)}s;
        animation-timing-function: ease-in-out;
        height: #{random(40)}px;
      }
    }
  }
}

@keyframes equalize {
  0% {
    height: 5px;
  }
  20% {
    height: #{random(15)}px;
  }
  40% {
    height: #{random(30)}px;
  }
  60% {
    height: #{random(12)}px;
  }
  80% {
    height: #{random(30)}px;
  }
  100% {
    height: 5px;
  }
}
</style>
