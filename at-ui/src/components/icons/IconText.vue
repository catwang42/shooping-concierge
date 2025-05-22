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
      <linearGradient id="textGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fff" />
        <stop offset="80%" stop-color="#4285f4" />
      </linearGradient>
    </defs>
    <mask
      id="mask0_2365_12238"
      style="mask-type: alpha"
      maskUnits="userSpaceOnUse"
      x="0"
      y="0"
      width="19"
      height="18"
    >
      <rect x="0.75" width="18" height="18" fill="currentColor" />
    </mask>
    <g mask="url(#mask0_2365_12238)">
      <path
        d="M5.25 10.5H11.25V9H5.25V10.5ZM5.25 8.25H14.25V6.75H5.25V8.25ZM5.25 6H14.25V4.5H5.25V6ZM2.25 16.5V3C2.25 2.5875 2.39688 2.23438 2.69063 1.94063C2.98438 1.64688 3.3375 1.5 3.75 1.5H15.75C16.1625 1.5 16.5156 1.64688 16.8094 1.94063C17.1031 2.23438 17.25 2.5875 17.25 3V12C17.25 12.4125 17.1031 12.7656 16.8094 13.0594C16.5156 13.3531 16.1625 13.5 15.75 13.5H5.25L2.25 16.5ZM4.6125 12H15.75V3H3.75V12.8438L4.6125 12Z"
        fill="url(#textGradient)"
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
      id="mask0_2365_12238"
      style="mask-type: alpha"
      maskUnits="userSpaceOnUse"
      x="0"
      y="0"
      width="19"
      height="18"
    >
      <rect x="0.75" width="18" height="18" fill="currentColor" />
    </mask>
    <g mask="url(#mask0_2365_12238)">
      <path
        d="M5.25 10.5H11.25V9H5.25V10.5ZM5.25 8.25H14.25V6.75H5.25V8.25ZM5.25 6H14.25V4.5H5.25V6ZM2.25 16.5V3C2.25 2.5875 2.39688 2.23438 2.69063 1.94063C2.98438 1.64688 3.3375 1.5 3.75 1.5H15.75C16.1625 1.5 16.5156 1.64688 16.8094 1.94063C17.1031 2.23438 17.25 2.5875 17.25 3V12C17.25 12.4125 17.1031 12.7656 16.8094 13.0594C16.5156 13.3531 16.1625 13.5 15.75 13.5H5.25L2.25 16.5ZM4.6125 12H15.75V3H3.75V12.8438L4.6125 12Z"
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
