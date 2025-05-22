<template>

  <v-dialog v-model="isItemDetailsDialogActive" max-width="600">
    <v-card>
      <v-card-title class="headline">
        {{ selectedItem?.name }}
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="10">
            <v-img :src="getImageUrl(selectedItem?.id, 400, 400)" :alt="selectedItem?.name"></v-img>
          </v-col>
          <v-col cols="12" md="10">
            <div class="text-body-1">
              {{ selectedItem?.description }}
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="isItemDetailsDialogActive = false">
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-row dense class="pt-2 pr-4 overflow-y-auto">
    <v-col v-for="(item, i) in (items)" :key="i" cols="4" md="2">
      <v-card class="mx-auto" color="surface-variant" max-width="200" elevation="2"
        @click="onItemClicked(item)">
        <v-img :src="getImageUrl(item['id'], 200, 200)" :alt="item['name']"></v-img>
        <v-card-text class="text-body-2 pt-2 pl-2 pr-2 pb-0">{{ item['name'] }}</v-card-text>
        <v-card-text class="text-caption pa-2">
          {{ item['description'].split(' ').slice(0, 10).join(' ') }}
          <span v-if="item['description'].split(' ').length > 10">
            ...
          </span>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>

export default {
  name: 'Main',
  data: () => ({
    isItemDetailsDialogActive: false,
    selectedItem: null,
  }),

  props: {
    items: {
      type: Array,
      required: true,
    },
  },
  methods: {
    onItemClicked(item) {
      this.selectedItem = item;
      this.isItemDetailsDialogActive = true;
    },
    getImageUrl(id, width, height) {
      return `https://u-mercari-images.mercdn.net/photos/${id}_1.jpg?w=${width}&h=${height}&fitcrop&sharpen`;
    }
  },
};
</script>

