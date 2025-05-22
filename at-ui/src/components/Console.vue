<template>
  <v-container class="h-100">
    <v-row align-content="start">
      <v-col v-for="(msg, i) in consoleMessages" :key="i" cols="12" class="pb-0">
        <v-card elevation="2">
          <v-card-text class="text-left pt-2 pb-2" v-html="msg"></v-card-text>
        </v-card>
      </v-col>
      <div id="consoleLastRow"/>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'Console',
  props: {
    consoleMessages: {
      type: Array,
      required: true,
    },
  },
};
</script>