/**
 * Shared consts and functions.
 */

/**
 * Constants
 */

// UI commands
export const CMD_UI = {
    SHOW_QUERY_MSG: "show_query_msg",
    SHOW_AGENT_MSG: "show_agent_msg",
    SHOW_AGENT_THOUGHTS: "show_agent_thoughts",
    SHOW_USER_MSG: "show_user_msg",
    SHOW_USER_IMG: "show_user_img",
    SHOW_SYSTEM_MSG: "show_system_msg",
    PRESENT_ITEMS: "present_items_to_user",
    SET_SESSION_ID: "set_session_id",
}

// Agent commands
export const CMD_AGENT = {
    SET_USER_LOCATION: "set_user_location",
    SET_AUDIO: "set_audio",
}

/**s
 * Functions
 */

export function base64ToArray(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

export function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
  

  export const getImageUrl = (id, width, height) => {
    return `https://u-mercari-images.mercdn.net/photos/${id}_1.jpg?w=${width}&h=${height}&fitcrop&sharpen`;
  };


  export const pxToVh = (px) => {
    return `${px / 1080 * 100}vh`;
  };

  export const pxToVw = (px) => {
    return `${px / 1920 * 100}vw`;
  };


  export const truncatedTextWithEllipsis = (text, count) => {
    if(!text) return "";
    const formattedText = text.replace(/\n|\r/g, "");
    const truncatedText = formattedText.slice(0, count);
    if (truncatedText.length < formattedText.length) {
      return truncatedText + "...";
    }
    return truncatedText;
  };