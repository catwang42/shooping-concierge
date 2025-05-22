<template>
  <svg
    v-if="gradient"
    xmlns="http://www.w3.org/2000/svg"
    width="19"
    height="18"
    viewBox="0 0 19 18"
    fill="none"
  >
    <defs>
      <linearGradient id="voiceGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fff" />
        <stop offset="80%" stop-color="#4285f4" />
      </linearGradient>
    </defs>
    <mask
      id="mask0_2365_12229"
      style="mask-type: alpha"
      maskUnits="userSpaceOnUse"
      x="0"
      y="0"
      width="19"
      height="18"
    >
      <rect x="0.75" width="18" height="18" fill="currentColor" />
    </mask>
    <g mask="url(#mask0_2365_12229)">
      <path
        d="M6 13.5V4.5H7.5V13.5H6ZM9 16.5V1.5H10.5V16.5H9ZM3 10.5V7.5H4.5V10.5H3ZM12 13.5V4.5H13.5V13.5H12ZM15 10.5V7.5H16.5V10.5H15Z"
        fill="url(#voiceGradient)"
      />
    </g>
  </svg>
  <svg
    v-else
    xmlns="http://www.w3.org/2000/svg"
    width="19"
    height="18"
    viewBox="0 0 19 18"
    fill="none"
  >
    <mask
      id="mask0_2365_12229"
      style="mask-type: alpha"
      maskUnits="userSpaceOnUse"
      x="0"
      y="0"
      width="19"
      height="18"
    >
      <rect x="0.75" width="18" height="18" fill="currentColor" />
    </mask>
    <g mask="url(#mask0_2365_12229)">
      <path
        d="M6 13.5V4.5H7.5V13.5H6ZM9 16.5V1.5H10.5V16.5H9ZM3 10.5V7.5H4.5V10.5H3ZM12 13.5V4.5H13.5V13.5H12ZM15 10.5V7.5H16.5V10.5H15Z"
        fill="currentColor"
      />
    </g>
  </svg>
</template>

<script setup>
import { defineProps } from "vue";
const props = defineProps({
  gradient: {
    type: Boolean,
    default: false,
  },
});
</script>
