/**
 * Audio Recorder Worklet
 */

import { arrayBufferToBase64 } from './shared.js';
import { eventBus } from './event-bus.js';
let stream;
let isSilence = true;
let lastTimeVoiceActivated = 0;
let sentSamples = 0;
const SILENCE_PERIOD = 2000;

// Attempt to create an AudioContext with a sample rate of 16000 Hz.
const audioRecorderContext = new AudioContext({ sampleRate: 16000 });

// Find RODE Wireless GO II device id (if present)
let rode_device_id = null;

navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    devices.forEach(device => {
      console.log(`${device.kind}: ${device.label} id = ${device.deviceId}`);
      if (device.kind === 'audioinput' && device.label.includes('Wireless GO II') && device.deviceId !== 'default') {
        rode_device_id = device.deviceId;
        console.log("Found RODE Wireless GO II device id:", rode_device_id);
      }
    });
  })
  .catch(err => {
    console.error('Error enumerating devices:', err);
  });

export async function startAudioRecorderWorklet(audioRecorderHandler) {


  // Load the AudioWorklet module.
  const workletURL = new URL('./pcm-recorder-processor.js', import.meta.url);

  await audioRecorderContext.audioWorklet.addModule(workletURL);

  // Request access to the microphone.
  const media_stream_constraints = { audio: { channelCount: 1 } };
  if (rode_device_id) {
    media_stream_constraints.audio.deviceId = { exact: rode_device_id };
  }
  stream = await navigator.mediaDevices.getUserMedia(media_stream_constraints);
  const source = audioRecorderContext.createMediaStreamSource(stream);
  console.log("audioRecorderContext created", workletURL);

  // Create an AudioWorkletNode that uses the PCMProcessor.
  const audioRecorderNode = new AudioWorkletNode(
    audioRecorderContext,
    "pcm-recorder-processor"
  );

  // Connect the microphone source to the worklet.
  source.connect(audioRecorderNode);
  audioRecorderNode.port.onmessage = (event) => {

    // Send voice only when it's not silence
    if (isSilence) return;

    // Then convert to 16-bit PCM
    const inputData = event.data;
    const pcmData = convertFloat32ToPCM(inputData);

    // Wrap the pcm data with a JSON message with base64. 
    const messageJson = JSON.stringify({
      mime_type: "audio/pcm",
      data: arrayBufferToBase64(pcmData),
    });

    eventBus.emit('audio-recorder-message');

    // Send the JSON message to the handler.
    audioRecorderHandler(messageJson); ``

  };

  // Load the VAD processor module
  const vadWorkletURL = new URL('./vad-processor.js', import.meta.url);
  audioRecorderContext.audioWorklet.addModule(vadWorkletURL).then(() => {
    // Create an instance of the AudioWorkletNode using your processor
    const vadNode = new AudioWorkletNode(audioRecorderContext, 'vad-processor');

    // Listen for messages from the processor (voice detected or not)
    vadNode.port.onmessage = event => {
      const { voice, rms } = event.data;
      if (voice) {
        if (isSilence) console.log("Voice detected.");
        isSilence = false;
        lastTimeVoiceActivated = new Date();
        sentSamples = 0;
      } else {
        if (new Date() - lastTimeVoiceActivated > SILENCE_PERIOD) {
          const samplesPerSec = sentSamples / ((new Date() - lastTimeVoiceActivated) / 1000);
          if (!isSilence) console.log("Voice stopped. " + samplesPerSec.toFixed(2) + " samples/s");
          isSilence = true;
        }
      }
    };
    // Connect the microphone source to the VAD processor
    source.connect(vadNode);
  });

  return [audioRecorderNode, audioRecorderContext, stream];
}

// Convert Float32 samples to 16-bit PCM.
function convertFloat32ToPCM(inputData) {
  // Create an Int16Array of the same length.
  const pcm16 = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    // Multiply by 0x7fff (32767) to scale the float value to 16-bit PCM range.
    pcm16[i] = inputData[i] * 0x7fff;
  }
  sentSamples += inputData.length;
  // Return the underlying ArrayBuffer.
  return pcm16.buffer;
}

/**
 * Stop the microphone.
 */
export function stopMicrophone(micStream) {
  stream.getTracks().forEach(track => track.stop());
  console.log("stopMicrophone(): Microphone stopped.");
}
