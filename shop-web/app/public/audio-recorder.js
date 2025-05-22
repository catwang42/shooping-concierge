/**
 * Audio Recorder Worklet
 */

export async function startAudioRecorderWorklet(audioRecorderHandler) {

  // Attempt to create an AudioContext with a sample rate of 16000 Hz.
  const audioContext = new AudioContext({ sampleRate: 16000 });
  console.log("AudioContext sample rate:", audioContext.sampleRate); // Expect 16000 if supported

  // Load the AudioWorklet module.
  await audioContext.audioWorklet.addModule("/public/pcm-recorder-processor.js");

  // Request access to the microphone.
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const source = audioContext.createMediaStreamSource(stream);

  // Create an AudioWorkletNode that uses the PCMProcessor.
  const workletNode = new AudioWorkletNode(
    audioContext,
    "pcm-recorder-processor"
  );

  // Connect the microphone source to the worklet.
  source.connect(workletNode);
  // Optionally, connect to the destination to monitor audio:
  // workletNode.connect(audioContext.destination);

  workletNode.port.onmessage = (event) => {
    const inputData = event.data; // This is a Float32Array.
    // Convert the Float32 samples to 16-bit PCM using the simple conversion.
    const pcmData = convertFloat32ToPCM(inputData);

    // Send the PCM data.
    audioRecorderHandler(pcmData);
  };
}

/**
 * Simplified conversion function: Converts a Float32Array (assumed values in [-1, 1])
 * to a 16-bit PCM ArrayBuffer in little-endian format.
 */
function convertFloat32ToPCM(inputData) {
  // Create an Int16Array of the same length.
  const pcm16 = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    // Multiply by 0x7fff (32767) to scale the float value to 16-bit PCM range.
    pcm16[i] = inputData[i] * 0x7fff;
  }
  // Return the underlying ArrayBuffer.
  return pcm16.buffer;
}

/**
 * Converts the data to Base64
 */
function arrayToBase64(data) {
  let binary = "";
  const bytes = new Uint8Array(data);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}
