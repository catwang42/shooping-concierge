import { defineStore } from "pinia";

export const MODES = {
  TEXT: 'text',
  AUDIO: 'audio'
}

export const useSessionStore = defineStore("session", {
  state: () => ({
    sessionId: null,
    qrCodeImage: null, // prompting or chat
    imageUploads: [], // image uploads
    mode: MODES.TEXT // text or audio
  }),
  actions: {
    setSockets(sockets) {
      this.sockets = sockets;
      this.sockets.on('set-session-id', (sessionId) => {
        this.setSessionId(sessionId);
      });
      this.sockets.on('user-image', (image) => {
        console.log("user-image", image);
        this.setImageUpload(image);
      });
    },
    setSessionId(sessionId) {
      this.sessionId = sessionId;
    },
    clearSessionId() {
      this.sessionId = null;
    },
    setGeminiMode(mode) {
      this.mode = mode;
      this.sockets.setGeminiMode(mode === "audio" ? true : false);
    },
    setQRItem(qrItem) {
      this.qrCodeImage = qrItem;
    },
    setImageUpload(imageUpload) {
      this.imageUploads.push({
        src: 'data:image/jpeg;base64,' + imageUpload,
        alt: 'User Image',
      });
    },
    sendGenerateImage(productId) {
      this.sockets.generateImage(productId);
    },
    sendImageUpload(imageUpload) {
      this.sockets.send(imageUpload);
    },
    clearQRCode() {
      this.qrCodeImage = null;
    },
    resetAll() {
      this.sessionId = null;
      this.qrCodeImage = null;
      this.imageUploads = [];
    },
  },
});
