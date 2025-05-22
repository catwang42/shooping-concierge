<template>
  <div class="medium-selection" :class="{ 'mini': variant === 'mini' }" ref="mediumSelectionRef">
    <div class="medium-selection__container">
      <div class="medium-selection__container__item">
        <div class="medium-selection__container__item__button" @click="handleConnectPhone">
            <IconPhone class="medium-selection__container__item__button__icon" />
            <VText :variant="variant === 'mini' ? 'body-16' : 'bold-18'" text="Connect to phone"></VText>
        </div class="">
      </div>
      <div class="medium-selection__container__item">
        <div class="medium-selection__container__item__button" @click="handleConnectWebcam">
            <IconComputer class="medium-selection__container__item__button__icon" />
            <VText :variant="variant === 'mini' ? 'body-16' : 'bold-18'" text="Computer webcam"></VText>
        </div class="">
      </div>
      <div class="medium-selection__container__item">
        <label for="file-upload" class="medium-selection__container__item__button">
          <input type="file" id="file-upload" class="medium-selection__container__item__button__input" @change="handleUploadImage" />
          <IconUpload class="medium-selection__container__item__button__icon" />
          <VText :variant="variant === 'mini' ? 'body-16' : 'bold-18'" text="Upload photo"></VText>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import VText from "@/components/VText.vue";
import IconPhone from "@/components/icons/IconPhone.vue";
import IconComputer from "@/components/icons/IconComputer.vue";
import IconUpload from "@/components/icons/IconUpload.vue";
import gsap from "gsap";
import { onMounted, ref, defineEmits, defineProps, defineExpose } from "vue";
import { useSessionStore } from "@/stores/session";
import { arrayBufferToBase64 } from "@/utils/shared";
const sessionStore = useSessionStore();
const emit = defineEmits(["medium-selection-connect-phone", "medium-selection-connect-webcam", "medium-selection-upload-photo"]);

const mediumSelectionRef = ref(null);
const currentTween = ref(null);

function handleConnectPhone () {
  emit("medium-selection-connect-phone");
};

function handleConnectWebcam () {
  emit("medium-selection-connect-webcam");
};

async function handleUploadImage (event) {
  const base64data = await event.target.files[0].arrayBuffer();
  const b64data = arrayBufferToBase64(base64data);
  const mimeType = event.target.files[0].type;
  const requestJson = JSON.stringify({
      mime_type: mimeType,
      data: b64data,
  });
  sessionStore.sendImageUpload(requestJson);
  emit("medium-selection-upload-photo", requestJson);
};

function handleConnectPhoneHover () {
  console.log("connect phone hover");
};  

const animateSet = () => {
  gsap.set(mediumSelectionRef.value, {
    "--clip-animation": '100%',
  });
};

const animateOut = () => {
  if(currentTween.value) {
    currentTween.value.kill();
  }
  currentTween.value = gsap.to(mediumSelectionRef.value, {
    "--clip-animation": '100%',
    duration: 0.25,
    ease: "power2.inOut",
  });
};

const animateIn = () => {
  if(currentTween.value) {
    currentTween.value.kill();
  }
  currentTween.value = gsap.to(mediumSelectionRef.value, {
    "--clip-animation": '0%',
    duration: 0.5,
    ease: "power2.inOut",
  });
};

defineProps({
  variant: {
    type: String,
    default: "default",
  },
});

defineExpose({
  animateSet,
  animateOut,
  animateIn,
});

onMounted(() => {
  animateSet();
});
</script>

<style lang="scss" scoped>
.medium-selection {
  border-radius: px-to-vh(20);
  border: 1px solid rgba(66, 133, 244, 0.1);
  background: rgba(37, 49, 75, 1);
  box-shadow: 0px 14px 59.7px 0px rgba(0, 0, 0, 0.15);
  width: px-to-vh(300);

  input[type="file"] {
    display: none;
}

  --clip-animation: 0;

  clip-path: inset(
    var(--clip-animation) 0px 0px 0px round px-to-vh(24)
  );

  &__container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    &__item {

        width: 100%;
        
        &__button {
            display: flex;
            width: 100%;
            padding: px-to-vh(12) px-to-vh(32);
            cursor: pointer;
            color: inherit;
            align-items: center;
            justify-content: flex-start;
            gap: px-to-vh(12);
        }


        &:first-child {
            .medium-selection__container__item__button {
                padding-top: px-to-vh(32);
                display: flex;
            }
        }
        &:last-child {
            .medium-selection__container__item__button {
                padding-bottom: px-to-vh(32);
            }
        }
    }
  }
  &.mini {
    width: px-to-vh(220);
    .medium-selection__container__item__button {
      padding: px-to-vh(4) px-to-vh(16);
      .medium-selection__container__item__button__icon {
        width: px-to-vh(24);
        height: px-to-vh(24);
      }
    }
    .medium-selection__container__item {
      &:first-child {
        .medium-selection__container__item__button {
          padding-top: px-to-vh(16);
        }
      }
      &:last-child {
        .medium-selection__container__item__button {
          padding-bottom: px-to-vh(16);
        }
      }
    }
  }
}
</style>
