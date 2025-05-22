<template>
  <!-- Webcam dialog -->
  <v-dialog v-model="isWebcamActive" width="500">

    <v-card title="Take an image">
      <div class="webcam-container">
        <video id="webcam-video" width="400" height="300">
        </video>
      </div>
      <v-row class="d-flex">
        <v-col class="d-flex justify-center align-center">
          <v-btn text="📷 Send" variant="outlined" @click="onShootClick" class="w-50 h-30" />
        </v-col>
        <v-col v-if="qrcodeImage" class="d-flex pa-8 justify-center align-center">
          <v-card-text>Remote camera link:</v-card-text>
          <v-img :src="qrcodeImage" width="100" height="100"></v-img>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>

  <v-container style="width: 320px; height: 150px; margin-left: 10px;">
    <v-form @submit.prevent>
      <v-row>
        <v-col cols="12" class="pb-0">
          <v-text-field v-model="chatMessage" id="chatMessage" label="Enter message" variant="outlined" single-line
            clearable @keydown.enter="submitChatMessage"></v-text-field>
        </v-col>
        <v-col cols="12" class="d-flex pt-0 pb-8 ga-3 align-center">
          <v-btn id="sendButton" @click="submitChatMessage" color="primary" :disabled="!sendEnabled"
            class="d-flex">Send</v-btn>
          Text
          <v-switch v-model="isAudio" density="compact" class="d-flex" />
          Audio
          <v-btn id="webcam-button" class="webcam-button" @click="openWebcamDialog">📷</v-btn>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script setup>
import * as QRCode from 'qrcode'

import { nextTick, ref, watchEffect } from 'vue'

const chatMessage = ref("");
const qrcodeImage = ref(""); // for showing QR code for remote camera
const isAudio = ref(false); // true if audio
const isWebcamActive = ref(false);

const emit = defineEmits(["submitMessage", "update:isAudio", "submitImage"]);

const props = defineProps({
  sendEnabled: {
    type: Boolean,
    default: false,
  },
  isAudio: {
    type: Boolean,
    default: false,
  },
  sessionId: {
    type: String,
    default: null,
  },
});

// Watch for changes in isAudio
watchEffect(
  () => {
    emit('update:isAudio', isAudio.value);
  }
);

// Close webcam if the dialog is closed
watchEffect(
  () => {
    if (!isWebcamActive.value) {
      // Close webcam if the dialog is closed
      const video = document.getElementById('webcam-video');
      if (video && video.srcObject) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
      }

    }
  }
);

// Send chat message
const submitChatMessage = () => {
  emit('submitMessage', chatMessage.value);
  chatMessage.value = '';
};

// Open webcam dialog
const openWebcamDialog = async () => {

  // Generate a QR code for the remote camera
  const url = `https://${window.location.host}/remotecam.html?session_id=${props.sessionId}`;

  // Generate QR code
  QRCode.toDataURL(url)
    .then(qrCodeData => {
      qrcodeImage.value = qrCodeData;
    })
    .catch(err => {
      console.error("Error generating QR code:", err);
    });

  // Open the dialog
  isWebcamActive.value = true;
  await nextTick(); // Wait for the dialog open

  // Open webcam
  const video = document.getElementById('webcam-video');
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (video) {
          video.srcObject = stream;
          video.style.objectFit = "cover";
          video.play();
        }
      })
      .catch((error) => {
        console.error('Error accessing webcam:', error);
      });
  }
};

// Take a photo
const onShootClick = () => {

  // Take a photo
  const video = document.getElementById('webcam-video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  // Convert the canvas content to JPEG blob (not base64)
  canvas.toBlob((blob) => {
    if (blob) {
      const reader = new FileReader();
      reader.onload = () => {
        const imageData = reader.result;
        emit('submitImage', imageData);
        console.log("onShootClick: imageTaken: length=" + imageData.byteLength + " bytes");
      };
      reader.readAsArrayBuffer(blob); // Read as ArrayBuffer
    }
  }, 'image/jpeg');


  // Close the dialog
  isWebcamActive.value = false;

};


</script>


<style scoped>
.button-container {
  display: flex;
  gap: 12px;
  margin: 12px;
  align-items: center;
}

.webcam-container {
  display: flex;
  justify-content: center;
  /* Horizontally center the video */
  align-items: center;
  /* Vertically center the video */
  width: 100%;
  /* Ensure the container takes full width */
}

#webcam-video {
  margin: auto;
  /* Center the video horizontally */
  display: block;
  /* Make it a block element for margin auto to work */
}

#webcam-button {
  font-size: 24px;
  border: none;
}
</style>