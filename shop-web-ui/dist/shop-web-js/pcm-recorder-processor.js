class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
  }

  process(inputs, outputs, parameters) {
    if (inputs.length > 0 && inputs[0].length > 0) {
      // Use the first channel.
      const inputChannel = inputs[0][0];
      // Copy the buffer to avoid issues with recycled memory.
      const inputCopy = new Float32Array(inputChannel);

      // Downsampling to 1/2
//      const randomInt = Math.floor(Math.random() * 100);
//      if (randomInt % 2 === 0) {
        // Send the audio data to the main thread.
        this.port.postMessage(inputCopy);
//      }


    }
    return true;
  }
}

registerProcessor('pcm-recorder-processor', PCMProcessor);
