<template>
  <div class="gallery-container">
    <div v-if="title" class="gallery-title">
      <VText
        ref="titleRef"
        :text="title"
        animateBy="chars"
        splitType="chars, lines"
        variant="bold-128"
        class="title"
        gradient
      />
      <VText
        ref="subTitleRef"
        :text="subTitle"
        variant="bold-32"
        class="sub-title"
        gradient
      />
      <VText
        ref="ctaRef"
        :text="cta"
        variant="medium-18"
        class="cta"
        gradient
      />
    </div>
    <div class="gallery">
      <GalleryItem
        v-for="(image, index) in images"
        ref="galleryItemsRef"
        :key="image.uniqueId"
        :src="image.src"
        :alt="image.alt"
        :position="image.position"
        :caption="image.caption"
        :id="image.id"
        @done="handleItemDone"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import GalleryItem from "./GalleryItem.vue";
import VText from "@/components/VText.vue";
import { positions } from "./positions";
import { imageContent } from "./imagecontent";
const images = ref([]);
const imagesMap = ref(new Map());
const count = ref(0);
const intervalId = ref(null);
const isVisible = ref(true);
const titleRef = ref(null);
const subTitleRef = ref(null);
const ctaRef = ref(null);
const galleryItemsRef = ref([]);

const maxImagesDisplayed = ref(12);
const uniqueIdCounter = ref(0);
const props = defineProps({
  title: {
    type: String,
    required: false,
  },
  subTitle: {
    type: String,
    required: false,
    default: "",
  },
  cta: {
    type: String,
    required: false,
    default: "",
  },
  wide: {
    type: Boolean,
    required: false,
    default: false,
  },
  imageContent: {
    type: Array,
    required: false,
    default: () => imageContent,
  },
});

const SPAWN_DELAY = 1500;

const imageContentRef = computed(() => props.imageContent);

async function spawnImage() {
  //console.log("spawnImage", count.value);

  if (count.value >= imageContentRef.value.length) {
    count.value = 0;
  }

  if (imagesMap.value.size >= maxImagesDisplayed.value) {
    return;
  }

  const uniqueId = uniqueIdCounter.value++;
  const imageId = `img-${Date.now()}-${count.value}`;
  const pos = positions[props.wide ? "wide" : "narrow"][count.value];

  const obj = {
    src: imageContentRef.value[count.value].src,
    position: positions[props.wide ? "wide" : "narrow"][count.value],
    id: imageId,
    uniqueId: uniqueId,
    caption: imageContentRef.value[count.value].caption,
  };
  images.value = [...images.value, obj];
  imagesMap.value.set(imageId, obj);
  count.value++;
}

async function startInterval(delay = 0) {
  await new Promise((resolve) => setTimeout(resolve, delay * 1000));
  if (!intervalId.value) {
    spawnImage();
    intervalId.value = setInterval(spawnImage, SPAWN_DELAY);
  }
}

function stopInterval() {
  if (intervalId.value) {
    clearInterval(intervalId.value);
    intervalId.value = null;
  }
}

function handleVisibilityChange() {
  if (document.hidden) {
    isVisible.value = false;
    stopInterval();
  } else {
    isVisible.value = true;
    startInterval();
  }
}

function handleItemDone(id) {
  if (imagesMap.value.has(id)) {
    imagesMap.value.delete(id);
    images.value = images.value.filter((image) => image.id !== id);
  }
}

async function animateIn() {
  await new Promise((resolve) => setTimeout(resolve, 100));
  titleRef.value &&
    titleRef.value.animateIn(1, {
      duration: 2,
      stagger: 0.03,
    });
  subTitleRef.value &&
    subTitleRef.value.animateIn(2, {
      duration: 1.5,
      stagger: 0.03,
    });
  ctaRef.value &&
    ctaRef.value.animateIn(3, {
      duration: 1,
      stagger: 0.03,
    });
  startInterval(1);
  document.addEventListener("visibilitychange", handleVisibilityChange);
}

async function animateOut() {
  titleRef.value &&
    titleRef.value.animateOut(0, {
      duration: 1,
      stagger: 0.03,
    });
  subTitleRef.value &&
    subTitleRef.value.animateOut(0, {
      duration: 1,
      stagger: 0.03,
    });
  ctaRef.value &&
    ctaRef.value.animateOut(0, {
      duration: 1,
      stagger: 0.03,
    });

  galleryItemsRef.value.forEach((item) => {
    item.animateOut();
  });
  stopInterval();

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, 2000);
  });
}

const animateSet = async () => {
  console.log("animateSet gallery");
  imageContentRef.value = props.imageContent;
  ctaRef.value.animateSet();
  titleRef.value.animateSet();
  subTitleRef.value.animateSet();
};

defineExpose({
  animateIn,
  animateOut,
  animateSet,
});

onMounted(async () => {
  if (titleRef.value) {
    titleRef.value.prepare();
  }
  if (subTitleRef.value) {
    subTitleRef.value.prepare();
  }
  if (ctaRef.value) {
    ctaRef.value.prepare();
  }
});

onUnmounted(() => {
  stopInterval();
  images.value = [];
  imagesMap.value.clear();
  document.removeEventListener("visibilitychange", handleVisibilityChange);
});
</script>

<style lang="scss" scoped>
.gallery-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1000;
}
.gallery {
  position: relative;
  width: 100vw;
  height: 100vh;
  perspective: 600px;
}
.gallery-title {
  position: absolute;
  width: 100vw;
  height: 100vh;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  .title,
  .sub-title {
  }
  .sub-title {
    margin-top: 0.5vw;
  }
  .cta {
    margin-top: 3vw;
  }
}
</style>
