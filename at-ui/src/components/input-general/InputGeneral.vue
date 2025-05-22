<template>
  <div class="input-general-wrapper">
    <div
      ref="containerRef"
      class="input-general"
      :class="{ 'input-general__mini': props.mini }"
    >
      <ChatGeminiLoading
        ref="geminiLoadingRef"
        class="input-general__gemini-loading"
      />
      <QRCode
        :qrCode="props.qrCode"
        :imageUpload="props.imageUpload"
        :variant="props.mini ? 'mini' : 'default'"
        class="input-general__qr"
        ref="qrCodeRef"
        :text="copy.QRCodeCta"
      />

      <div class="input-general__text">
        <p
          :data-placeholder="props.cta"
          contenteditable="true"
          ref="textRef"
          class="input-general__input text-body-20"
          :class="{ 'text-body-18': props.mini }"
          @input="handleInput"
          @click="handleInputClick"
          @keydown="handleInputKeydown"
        >
          {{ inputText }}
        </p>

        <div class="input-general__buttons">
          <IconBase
            ref="iconCameraRef"
            @click="handleClickMedia"
            @mouseenter="handleHoverMedium"
            @mouseleave="handleHoverMedium"
            class="input-general__button input-general__button--camera"
            variant="image-upload"
          >
            <MediumSelection
              class="input-general__medium-selection"
              @medium-selection-connect-phone="handleConnectPhone"
              @medium-selection-connect-webcam="handleConnectWebcam"
              @medium-selection-upload-photo="handleUploadPhoto"
              :variant="props.mini ? 'mini' : 'default'"
              ref="mediumSelectionRef"
            />
          </IconBase>
          <IconBase
            ref="iconRecordRef"
            @click="handleClickMic"
            class="input-general__button input-general__button--mic"
            variant="mic"
          />
          <IconBase
            ref="iconSendRef"
            @click="handleSendClick"
            class="input-general__button input-general__button--send"
            variant="send"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconBase from "../IconBase.vue";
import QRCode from "../QRCode.vue";
import MediumSelection from "../MediumSelection.vue";
import ChatGeminiLoading from "../chat/ChatGeminiLoading.vue";

import copy from "/public/data/copy.json";
const emit = defineEmits([
  "input-general-mic-clicked",
  "input-general-mic-result",
  "input-general-mic-end",
  "input-general-mic-start",
  "input-general-media-click",
  "input-general-send-click",
  "input-general-camera-hover",
  "input-general-input",
]);

const props = defineProps({
  cta: {
    type: String,
    default: "",
  },
  qrCode: {
    type: String,
    default: "",
  },
  imageUpload: {
    type: String,
    default: "",
  },
  language: {
    type: String,
    default: "en-US",
  },
  mini: {
    type: Boolean,
    default: false,
  },
});

import { ref, onMounted } from "vue";

import gsap from "gsap";
const currentCta = ref("");
const inputText = ref("");
const recognition = ref(null);
const recording = ref(false);
const ended = ref(false);
const containerRef = ref(null);
const qrCodeRef = ref(null);
const iconCameraRef = ref(null);
const textRef = ref(null);
const iconRecordRef = ref(null);
const iconSendRef = ref(null);
const mediumSelectionRef = ref(null);
const animatedInRef = ref(false);
const tlRef = gsap.timeline();
const geminiLoadingRef = ref(null);

const initRecorder = () => {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.error("SpeechRecognition not supported");
    return;
  }
  recognition.value = new SpeechRecognition();
  recognition.value.lang = props.language;
  recognition.value.interimResults = true;
  recognition.value.continuous = true;
};

const initRecognitionEvents = () => {
  recognition.value.onstart = () => {
    !props.mini && (inputText.value = "Listening...");
  };

  recognition.value.onend = () => {
    recognition.value.stop();
  };

  recognition.value.onresult = (event) => {
    let text = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        text = event.results[i][0].transcript;
      } else {
        text += event.results[i][0].transcript;
      }
    }
    handleOnResultMic(text);
  };
};

const handleOnResultMic = (text) => {
  inputText.value = text;
};

const handleInput = (e) => {
  inputText.value = e.target.innerText;
  emit("input-general-input", { inputText: e.target.innerText });
};

const handleInputKeydown = (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    handleSendClick();
  }
};

const handleInputClick = () => {
  console.log("input clicked");
};

const handleSendClick = () => {
  if (inputText.value.trim() === "") {
    return;
  }
  // send the data
  emit("input-general-send-click", inputText.value);
  inputText.value = "";
  if (textRef.value) {
    textRef.value.innerText = "";
  }
  ended.value = false;
};

const toggleRecordingClass = (state) => {
  if (state) {
    iconRecordRef.value.$el.classList.add("input-general__button--recording");
  } else {
    iconRecordRef.value.$el.classList.remove(
      "input-general__button--recording"
    );
  }
};

const handleClickMic = () => {
  recording.value = !recording.value;
  emit("input-general-mic-clicked", { recordingState: recording.value });
  //recording.value ? recognition.value.start() : recognition.value.stop();
};

const handleClickMedia = () => {
  emit("input-general-media-click");
};

const handleConnectPhone = () => {
  qrCodeRef.value.updateQRCode();
  qrCodeRef.value.animateIn();
  mediumSelectionRef.value.animateOut();
};

const handleConnectWebcam = () => {
  //TODO: kaz adds webcam here
  console.log("connect webcam");
};

const handleUploadPhoto = () => {
  //TODO: kaz adds image upload here
  console.log("upload photo");
};

const animateIn = ({ delay = 0 } = {}) => {
  animatedInRef.value = true;

  const tl = gsap.timeline();
  tlRef.value = tl;
  tl.to(containerRef.value, {
    opacity: 1,
    duration: 1,
    z: 0,
    ease: "power2.out",
    delay: delay,
  });
  tl.to(
    textRef.value,
    {
      opacity: 1,
      duration: 2,
    },
    "-=1"
  )
    .to(
      iconCameraRef.value.$el,
      {
        opacity: 1,
        duration: 2,
        ease: "power2.inOut",
      },
      "<"
    )
    .to(
      iconRecordRef.value.$el,
      {
        opacity: 1,
        duration: 2,
        ease: "power2.inOut",
      },
      "-=1.5"
    )
    .to(
      iconSendRef.value.$el,
      {
        opacity: 1,
        duration: 2,
        ease: "power2.inOut",
      },
      "-=1.5"
    );
};

const animateOut = () => {
  if (!animatedInRef.value) {
    return;
  }
  animatedInRef.value = false;
  if (tlRef.value) {
    tlRef.value.kill();
  }
  tlRef.value = gsap.timeline();
  tlRef.value.to(containerRef.value, {
    opacity: 0,
    duration: 1,
  });
  tlRef.value.to(textRef.value, {
    opacity: 0,
  });
};

const animateSet = () => {
  qrCodeRef.value.animateSet();
  geminiLoadingRef.value.animateSet();

  if (tlRef.value) {
    tlRef.value.kill();
  }

  gsap.set(containerRef.value, {
    opacity: 0,
    z: -100,
  });
  gsap.set(textRef.value, {
    opacity: 0,
  });
  gsap.set(iconRecordRef.value.$el, {
    opacity: 0,
  });
  gsap.set(iconCameraRef.value.$el, {
    opacity: 0,
  });
  gsap.set(iconSendRef.value.$el, {
    opacity: 0,
  });
};

const updateQRCode = (qrCode) => {
  console.log(qrCode);
  qrCodeRef.value.updateQRCode(qrCode.src);
};

const updateImageUpload = (imageUpload) => {
  qrCodeRef.value.updateImageUpload(imageUpload);
};

const animateInQrCode = () => {
  qrCodeRef.value.animateIn();
};

const animateOutQrCode = () => {
  qrCodeRef.value.animateOut();
};

const handleHoverMedium = (event) => {
  if (event.type === "mouseenter") {
    mediumSelectionRef.value.animateIn();
  } else {
    mediumSelectionRef.value.animateOut();
  }
};

const setRecordingState = (state) => {
  toggleRecordingClass(state);
  recording.value = state;
};

const setGeminiLoading = (state) => {
  if (!geminiLoadingRef) {
    return;
  }
  state
    ? geminiLoadingRef.value.animateIn()
    : geminiLoadingRef.value.animateOut();
};

defineExpose({
  animateIn,
  animateOut,
  animateSet,
  animateInQrCode,
  animateOutQrCode,
  updateQRCode,
  updateImageUpload,
  setRecordingState,
  setGeminiLoading,
});

// Initialize on component creation
onMounted(() => {
  currentCta.value = props.cta;
  initRecorder();
});
</script>

<style lang="scss" scoped>
.input-general-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  perspective: px-to-vh(1000);
  transform-style: preserve-3d;
}

.input-general__medium-selection {
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -111%);
  backdrop-filter: blur(px-to-vh(20));
  z-index: 999;
}

.input-general__gemini-loading {
  position: absolute;
  top: 50%;
  right: px-to-vh(110);
  transform: translate(-50%, -50%);
  width: px-to-vh(20);
  height: px-to-vh(20);
  z-index: 11;
  z-index: 999;
}

.input-general {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  transform-style: preserve-3d;
  box-shadow: 0px 14px 59.7px 0px rgba(0, 0, 0, 0.35);

  border-radius: px-to-vh(60);
  position: relative;
  background: rgba(230, 244, 234, 0.1);
  backdrop-filter: blur(px-to-vh(10));

  &__qr {
    width: px-to-vh(362);
    margin-bottom: px-to-vh(18);
    margin: px-to-vh(32) px-to-vh(40) 0px px-to-vh(40);
  }

  &:before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: calc(100% - px-to-vh(1));
    border-radius: px-to-vh(60);
    border: px-to-vh(1) solid transparent;
    background: linear-gradient(45deg, #485771, #89a6d7) border-box;
    mask:
      linear-gradient(#000 0 0) padding-box,
      linear-gradient(#000 0 0);
    mask-composite: exclude;
  }

  &__input {
    position: relative;
    width: 100%;
    border: none;
    outline: none;
    background: transparent;
    z-index: 999;
    // /color: white;
    cursor: text;

    &[data-placeholder]:empty:before {
      content: attr(data-placeholder);
      color: rgba(190, 190, 190, 0.6);
    }
  }

  &__buttons {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: px-to-vh(6);
    padding-right: px-to-vh(40);
  }

  &__button {
    width: px-to-vh(40);
    height: px-to-vh(40);
    color: white;
    position: relative;
    &--recording {
      animation: pulseRecording 2s infinite ease-in-out;
    }
    &::before {
      content: "";
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: linear-gradient(70deg, #fff -100.01%, #4285f4 182.1%);
      border-radius: px-to-vh(78);
      width: 0;
      height: 0;
      z-index: -1;
      transition: all 0.5s ease-in-out;
    }
    &::after {
      content: "";
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 0;
      height: 0;
      z-index: -2;
      background: rgb(118, 116, 149);
      border-radius: px-to-vh(78);
      transition: all 0.6s ease-in-out;
    }

    :deep(svg) {
      width: px-to-vh(24);
      height: px-to-vh(24);
    }
  }

  &__button--recording {
    color: black;
    &::before {
      width: px-to-vh(40);
      height: px-to-vh(40);
    }
    &::after {
      width: px-to-vh(50);
      height: px-to-vh(50);
    }
  }

  &__mini {
    border-radius: px-to-vh(10);

    &::before {
      background: rgba(67, 74, 96, 0.6);
      backdrop-filter: blur(30px);
      border-radius: px-to-vh(10);
    }
    .input-general__text {
      padding: 0;
      color: white;
    }

    .input-general__buttons {
      padding-right: 0px;
      gap: px-to-vh(12);
    }

    .input-general__button {
      width: px-to-vh(22);
      height: px-to-vh(22);
      &--recording {
        &::before {
          width: px-to-vh(30);
          height: px-to-vh(30);
        }
        &::after {
          width: px-to-vh(40);
          height: px-to-vh(40);
        }
        animation: pulseRecording 2s infinite ease-in-out;
      }
    }

    .input-general__input {
      padding: 0 px-to-vh(30) 0 0;

      &[data-placeholder]:empty:before {
        content: attr(data-placeholder);
        color: rgba(190, 190, 190, 1);
      }
    }
  }

  &__button {
    cursor: pointer;
    &--camera {
      position: relative;
    }
    &--mic {
    }
    &--send {
    }
  }

  &__gemini {
    flex-shrink: 0;
    margin-right: px-to-vh(16);
  }

  &__text {
    display: flex;
    flex-direction: row;
    align-items: center;
    font-size: px-to-vh(32);
    width: 100%;
    p {
      padding: px-to-vh(32) px-to-vh(32) px-to-vh(32) px-to-vh(40);
    }
  }

  @keyframes pulseRecording {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(0.9);
    }
    100% {
      transform: scale(1);
    }
  }
}
</style>
