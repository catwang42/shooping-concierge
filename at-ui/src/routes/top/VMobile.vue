<template>
  <div class="mobile-view">
    <BackgroundBase>
      <template v-slot="{ oglState }">
        <BackgroundGradient :oglState="oglState" v-bind="bgProps" />
      </template>
    </BackgroundBase>

    <div class="content-container">
      <div ref="webcamContainerRef" class="webcam-container">
        <video
          class="webcam"
          ref="webcamRef"
          id="webcam"
          autoplay
          playsinline
        ></video>
        <div ref="webcamInstructionsRef" class="webcam-instructions">
          <p>{{ copy.webcamInstructions }}</p>
        </div>
      </div>

      <div class="capture-container">
        <button
          @click="captureImage"
          ref="captureButtonRef"
          class="capture-container__button"
        >
          <IconCapture />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import BackgroundBase from "@/components/background/BackgroundBase.vue";
import BackgroundGradient from "@/components/background/BackgroundGradient.vue";
import IconCapture from "@/components/icons/IconCapture.vue";
import { arrayBufferToBase64 } from "@/utils/shared";
import gsap from "gsap";
import copy from "/public/data/copy.json";
import { HOSTNAME } from "../../services/shopsockets";
const bgProps = {
  animate: true,
  bgColor: "#000000",
  fade: 1,
  disk1: {
    color: "#4285f4",
    center: {
      x: -0.6000000000000001,
      y: -0.30000000000000004,
    },
    radius: 0.1,
    type: "group",
  },
  disk2: {
    color: "#1f427c",
    center: {
      x: 0.7599999999999999,
      y: -0.44000000000000006,
    },
    radius: 0.31599999999999995,
    type: "group",
  },
  disk3: {
    color: "#598adb",
    center: {
      x: -0.26999999999999996,
      y: -0.13000000000000006,
    },
    radius: -0.27,
    type: "group",
  },
  disk4: {
    color: "#d1dff5",
    center: {
      x: 1.62,
      y: 0.09000000000000002,
    },
    radius: -0.06,
    type: "group",
  },
};
const webcamRef = ref(null);
const webcamContainerRef = ref(null);
const captureButtonRef = ref(null);
const captureEnabled = ref(false);
const webcamInstructionsRef = ref(null);
const stream = ref(null);

onMounted(async () => {
  captureButtonRef.value.disabled = true;

  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then((stream) => {
      webcamRef.value.srcObject = stream;
      stream.value = stream;
      new Promise((resolve) => {
        setTimeout(() => {
          resolve();
        }, 1200);
      }).then(() => {
        animateIn();
      });
    })
    .catch((error) => {
      console.error("Error accessing webcam:", error);
    });
});

const captureImage = () => {
  if (captureEnabled.value) {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    canvas.width = webcamRef.value.videoWidth;
    canvas.height = webcamRef.value.videoHeight;
    context.drawImage(webcamRef.value, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob) {
        const reader = new FileReader();
        reader.onload = () => {
          sendUserImage(reader.result);
        };
        reader.readAsArrayBuffer(blob);
      }
    }, "image/jpeg");
  }
};

// Content upload endpoint URL

function sendUserImage(imageData) {
  const contentEndpointUrl = "https://" + HOSTNAME + "/send_content";
  console.log("sendUserImage(): Content endpoint URL: %s", contentEndpointUrl);
  captureButtonRef.value.disabled = true;

  gsap.to(captureButtonRef.value, {
    scale: 0,
    duration: 0.5,
    ease: "power1.out",
  });

  setTimeout(() => {
    gsap.to(captureButtonRef.value, {
      scale: 1,
      duration: 1,
      ease: "power1.out",
    });
  }, 3000);
  // Get session id
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const sessionId = urlParams.get("session_id");

  console.log("sendUserImage(): Session ID: %s", sessionId);

  // Encapsulate the imageData to a content JSON
  const b64data = arrayBufferToBase64(imageData);
  const requestJson = JSON.stringify({
    content: {
      mime_type: "image/jpeg",
      data: b64data,
    },
    session_id: sessionId,
  });

  console.log("sendUserImage(): Request JSON: %s", requestJson);

  // Send the image to the server
  fetch(contentEndpointUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: requestJson,
  })
    .then((response) => {
      captureButtonRef.value.disabled = false;
      // handle the response
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      console.log("sendUserImage(): Response: %s", response.json());
      return response.json();
    })
    .then((data) => {
      console.log("sendUserImage(): Sent image: %s bytes.", b64data.length);
    })
    .catch((error) => {
      console.error("sendUserImage(): Error:", error);
    });
}

const animateIn = () => {
  gsap.to(captureButtonRef.value, {
    scale: 1,
    duration: 1,
    opacity: 1,
    delay: 0.2,
    ease: "power1.out",
    onComplete: () => {
      captureButtonRef.value.disabled = false;
    },
  });
  gsap.to(webcamContainerRef.value, {
    duration: 1.5,
    opacity: 1,
    ease: "power1.out",
    onComplete: () => {
      captureEnabled.value = true;
    },
  });

  gsap.to(webcamInstructionsRef.value, {
    duration: 1.5,
    opacity: 1,
    delay: 0.3,
    ease: "power1.out",
  });
};
</script>

<style lang="scss" scoped>
.mobile-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;

  .content-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: calc(100svh);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 30px;
    margin-bottom: 30px;

    .webcam-container {
      position: relative;
      display: block;
      border-radius: 0.8em;
      overflow: hidden;
      width: calc(100% - 60px);
      box-shadow: 0 px-to-vh(14) px-to-vh(59.7) 0 rgba(0, 0, 0, 0.55);

      &:before {
        border-radius: 0.8em;
      }
      height: 100%;
      opacity: 0;
      .webcam {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }

  .webcam-instructions {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    z-index: 100;
    font-size: 18px;
    font-weight: 500;
    text-align: center;
    padding: 100px 0 24px 0;
    background: linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.8) 0%,
      rgba(0, 0, 0, 0) 100%
    );
    opacity: 0;
    p {
      max-width: 60%;
      margin: 0 auto;
    }
  }

  .capture-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: auto;
    margin-bottom: 50px;
    padding-top: 20px;
    &__button {
      scale: 0;
      background-color: transparent;
      box-shadow: none;
      outline: none;
      border: none;
      color: #fff;
      opacity: 0;
      svg {
        width: 80px;
        height: 80px;
      }
    }
  }
}
</style>
