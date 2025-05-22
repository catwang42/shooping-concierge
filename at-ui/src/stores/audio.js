import { defineStore } from 'pinia'
import { startAudioRecorderWorklet} from '@/utils/audio-recorder'
import { startAudioPlayerWorklet} from '@/utils/audio-player'
import { base64ToArray } from '@/utils/shared'

export const useAudioStore = defineStore('audio', {
  state: () => ({
    recording: false,
    playing: false,
    audioRecorderNode: null,
    audioRecorderContext: null,
    micStream: null,
    socketsOpen: false,
    audioPlayerNode: null,
    audioPlayerContext: null,
    audioPlayerStream: null
  }),
  actions: {
    setSockets(sockets) {
      this.sockets = sockets;
      this.sockets.on('open', (data) => {
        this.socketsOpen = true;
      })
      this.sockets.on('close', (data) => {
        this.socketsOpen = false;
      })
      this.sockets.on('audio-player-message', (data) => {
        this.audioPlayerNode.port.postMessage(base64ToArray(data));
      })
      this.sockets.on('agent-message-interrupted', (data) => {
        this.audioPlayerNode.port.postMessage({ command: "endOfAudio" });
      })
    },
    startRecording() {

      // if the audio recorder context is already created then we just resume it
      if(this.audioRecorderContext) {
        this.audioRecorderContext.resume();
        this.recording = true;
      }else {

        // first time then we create the audio recorder node, fetch the context and stream
        this.audioRecorderNode = startAudioRecorderWorklet((data) => {        
          this?.sockets?.send(data);          
        }).then(([node, ctx, stream]) => {
          this.audioRecorderNode = node;
          this.audioRecorderContext = ctx;
          this.audioRecorderContext.resume(); // somehow this is needed to start sending audio
          this.micStream = stream;
          this.recording = true;
        });
      }      
    },

    stopRecording() {
      // stop the recording and suspend the context
      this.recording = false;
      if(this.audioRecorderContext) {
        this.audioRecorderContext.suspend();
      }
    },

    startAudioPlayer() {
      if(this.audioPlayerContext) {
        this.audioPlayerContext.resume();
        this.playing = true;
      }else {
        this.audioPlayerNode = startAudioPlayerWorklet().then(([node, ctx, stream]) => {
          this.playing = true;
          this.audioPlayerNode = node;
          this.audioPlayerContext = ctx;
          this.audioPlayerStream = stream;
        });
      }
    },

    stopAudioPlayer() {
      if(this.audioPlayerContext) {
        this.audioPlayerContext.suspend();
        this.playing = false;
      }
    }

    
  }
})  