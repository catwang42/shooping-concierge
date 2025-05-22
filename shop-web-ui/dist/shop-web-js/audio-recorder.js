/**
 * Audio Recorder Worklet
 */

import { arrayBufferToBase64 } from './shared.js';

let stream;
let isSilence = true;
let lastTimeVoiceActivated = 0;
let sentSamples = 0;
const SILENCE_PERIOD = 2000;

export async function startAudioRecorderWorklet(audioRecorderHandler) {

  // Attempt to create an AudioContext with a sample rate of 16000 Hz.
  const audioRecorderContext = new AudioContext({ sampleRate: 16000 });
  console.log("AudioContext sample rate:", audioRecorderContext.sampleRate); // Expect 16000 if supported

  // Load the AudioWorklet module.
  const workletURL = new URL('./pcm-recorder-processor.js', import.meta.url);
  await audioRecorderContext.audioWorklet.addModule(workletURL);

  // Request access to the microphone.
  stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } });
  const source = audioRecorderContext.createMediaStreamSource(stream);

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

    // Send the JSON message to the handler.
    audioRecorderHandler(messageJson);

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
 * Downsamples a buffer from the input sample rate to the output sample rate.
 * It uses simple averaging to reduce aliasing.
 *
 * @param {Float32Array} buffer - The original audio samples.
 * @param {number} inputRate - The original sample rate (e.g. 44100).
 * @param {number} outputRate - The target sample rate (e.g. 16000).
 * @returns {Float32Array} - The downsampled audio samples.
 */
function downsampleBuffer(buffer, inputRate, outputRate) {
  if (outputRate >= inputRate) {
    throw new Error("Output sample rate must be lower than input sample rate.");
  }
  const sampleRateRatio = inputRate / outputRate;
  const newLength = Math.floor(buffer.length / sampleRateRatio);
  const result = new Float32Array(newLength);
  let offsetResult = 0;
  let offsetBuffer = 0;

  while (offsetResult < newLength) {
    const nextOffsetBuffer = Math.floor((offsetResult + 1) * sampleRateRatio);
    let accum = 0;
    let count = 0;
    // Average the samples in the current block
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
      accum += buffer[i];
      count++;
    }
    result[offsetResult] = accum / count;
    offsetResult++;
    offsetBuffer = nextOffsetBuffer;
  }
  return result;
}

/**
 * Stop the microphone.
 */
export function stopMicrophone(micStream) {
  stream.getTracks().forEach(track => track.stop());
  console.log("stopMicrophone(): Microphone stopped.");
}
