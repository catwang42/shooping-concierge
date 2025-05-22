import { defineStore } from 'pinia'
import { eventBus } from '../utils/event-bus';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    count: 0,
    geminiLoading: false,
  }),
  actions: {
    setSockets(sockets) {
      this.sockets = sockets;
      this.sockets.on('open', (data) => {
        this.addMessage({
          type: "info",
          text: "Connection opened",
        });
      })
      this.sockets.on('close', (data) => {
        resetChatTimeout(() => {
          this.geminiLoading = false;
        });
        this.addMessage({
          type: "info",
          text: "Connection closed",
        });
      })
      this.sockets.on('show-spinner', (data) => {
        this.geminiLoading = true;
      })
      this.sockets.on('agent-message', (data) => {
        resetChatTimeout(() => {
          this.geminiLoading = false;
        });
        this.addMessage({
          type: "agentMessage",
          text: data,
        });
      })
      this.sockets.on('user-message', (data) => {
        this.addMessage({
          type: "userMessage",
          text: data,
        });
      })
      this.sockets.on('user-image', (base64) => {
        startChatTimeout(() => {
          this.geminiLoading = true;
        });
        this.addMessage({
          type: "imageInput",
          image: 'data:image/jpeg;base64,' + base64,
        });
        setTimeout(() => {
          this.addMessage({
            type: "imageAnalysis",
            image: 'data:image/jpeg;base64,' + base64,
            text: "Image analysis complete",
          });
        }, 500);
      })
      this.sockets.on('show-query-msg', (data) => {
        resetChatTimeout(() => {
          this.geminiLoading = false;
        });
        if(data.group_id) {
          this.addMessage({
            type: "queryResponse",
            text: data.user_intent,
            groupID: data.group_id,
            groupIconID: data.group_icon_id,
            productName: data.item_category,
            resultCount: data.found_item_count,
          });
        } else {
          this.addMessage({
            type: "queryResponse",
            text: data,
          });
        }
      })

      eventBus.on('audio-recorder-message', () => {
        startChatTimeout(() => {
          this.geminiLoading = true;
        });
      })
    },
    addMessage(message) {
      message.id = this.count
      this.messages.push(message)
      this.count++
    },
    sendUserMessage(message) {
      startChatTimeout(() => {
        this.geminiLoading = true;
      });
      this.sockets.sendMessage(message);
      this.addMessage({
        type: "userMessage",
        text: message,
      });
    },
    clearMessages() {
      this.messages = []
      this.count = 0
      resetChatTimeout(() => {
        this.geminiLoading = false;
      });
    },
    setGeminiLoading(value) {
      this.geminiLoading = value;
    },
    mockMessages(count = 10) {
      for(let i = 0; i < count; i++) {
        const type = Math.random() > 0.5 ? "userMessage" : "agentMessage";
        const text = Math.random() > 0.5 ? "Hello, how are you?" : "I'm fine, thank you!";
        this.addMessage({
          type: type,
          text: text,
        });
      }
    },
    updateQueryCount(groupID, count) {
      const queryMessages = this.messages.filter(message => message.type === "queryResponse");
      const queryMessage = queryMessages.find(message => message.groupID === groupID);
      if(queryMessage) {
        queryMessage.resultCount = count;
      }
    },
    resetAll() {
      this.clearMessages();
      resetChatTimeout(() => {
        this.geminiLoading = false;
      });
    }
  },
})

let chatTime = 0;
const maxWaitTime = 1;
let chatTimeout = null;
let timerCreated = false;

function resetChatTimeout(callback) {
  chatTime = 0;
  clearInterval(chatTimeout);
  timerCreated = false;
  callback();
}
function startChatTimeout(callback) {
  if(timerCreated) return;
  console.log("startChatTimeout");
  timerCreated = true;
  chatTimeout = setInterval(() => {
    chatTime++;
      if(chatTime >= maxWaitTime) {
        callback();
      }
  }, 1000);
}

/**
 * @typedef {Object} BaseMessage
 * @property {string} [id] - Optional message ID
 * @property {('info'|'userMessage'|'queryResponse'|'imageInput'|'imageAnalysis')} type - Message type
 */

/**
 * @typedef {Object} InfoMessage
 * @extends BaseMessage
 * @property {'info'} type
 * @property {string} text
 */

/**
 * @typedef {Object} UserMessage
 * @extends BaseMessage
 * @property {'userMessage'} type
 * @property {string} text
 */

/**
 * @typedef {Object} QueryResponse
 * @extends BaseMessage
 * @property {'queryResponse'} type
 * @property {string} text
 * @property {number} resultCount
 * @property {string} itemCategory
 * @property {number} groupID
 * @property {string} image
 */

/**
 * @typedef {Object} ImageInput
 * @extends BaseMessage
 * @property {'imageInput'} type
 * @property {string} image
 */

/**
 * @typedef {Object} ImageAnalysis
 * @extends BaseMessage
 * @property {'imageAnalysis'} type
 * @property {string} image
 * @property {string} text
 */

/**
 * @typedef {InfoMessage|UserMessage|QueryResponse|ImageInput|ImageAnalysis} ChatMessage
 */