/**
 * shop-sockets.js: provides websocket abnd audio hooks.
 */

// UI components

import mitt from 'mitt';

/**
 * WebSocket
 */



const IS_PROD = import.meta.env.MODE === 'prod';

// Host name options
const HOSTNAME_PROD = window.location.host; // default
const HOSTNAME_STAGE = "stage0327---shop-web-nhhfh7g7iq-uc.a.run.app";

// Current host name
export const HOSTNAME = IS_PROD ? HOSTNAME_PROD : HOSTNAME_STAGE;

const liveTextUrl = 'wss://' + HOSTNAME + '/live?mode=text';
const liveAudioUrl = 'wss://' + HOSTNAME + '/live?mode=audio';

// WebSocket
let websocket = null;
let sessionId = null;

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
    SHOW_SPINNER: "show_spinner",
}

// Agent commands
export const CMD_AGENT = {
    SET_USER_LOCATION: "set_user_location",
    GENERATE_IMAGE: "generate_image",
    SET_AUDIO: "set_audio",
}

// retry status
let lastConnectTime = 0;
let retryCount = 0;
const emitter = mitt(); 

// Connect with the server
export const useShopSockets = (isAudio) => {

    console.log("useShopSockets()", isAudio);


    websocket = null;

    function connect() {

        // Connect
        const wsUrl = (isAudio ? liveAudioUrl : liveTextUrl)
        websocket = new WebSocket(wsUrl);

    }

    connect();


    websocket.onopen = () => {
        // Reset the UI
        lastConnectTime = new Date();
        retryCount = 0;

        console.log("websocket: onopen");

        // sendUserMessageToServer(" "); // for the agent's greeting message
        // sendUserLocationServer();
        emitter.emit('open');
    };

    websocket.onclose = () => {
        // Retry connection immediately or after 5 secs
        const now = new Date();
        const retryNeedsDelay = (now - lastConnectTime) < 5000 || retryCount > 0;
        retryCount += 1;
        setTimeout(() => {
            connect();
        }, retryNeedsDelay ? 5000 : 100);

        emitter.emit('close');
    };

    websocket.onmessage = (event) => {
        // Parse the incoming message
        const chunk = JSON.parse(event.data);

        console.log("websocket: onmessage", chunk);

        // interruption
        if(chunk.interrupted) {
            emitter.emit('agent-message-interrupted', null);
        }

        // text message
        if (chunk.mime_type == "text/plain") {
            if(chunk.data !== 'agent message' && chunk.data !== '\n') {
                emitter.emit('agent-message', chunk.data);
            }
        }

        // play audio
        if (chunk.mime_type.startsWith("audio/pcm")) {
            emitter.emit('audio-player-message', chunk.data);
        }

        // app level commands
        if (chunk.mime_type == "application/json") {
            const command = chunk.data.command;
            const parameter = chunk.data.parameter;

            switch (command) {
                case CMD_UI.PRESENT_ITEMS:
                    emitter.emit('present-items', parameter);
                    break;
                    
                case CMD_UI.SET_SESSION_ID:
                    console.log("websocket: set session id", parameter);
                    emitter.emit('set-session-id', parameter);
                    break;

                case CMD_UI.SHOW_AGENT_MSG:
                    emitter.emit('agent-message', parameter);
                    break;

                case CMD_UI.SHOW_AGENT_THOUGHTS:
                    emitter.emit('agent-message', parameter);
                    break;

                case CMD_UI.SHOW_USER_MSG:
                    emitter.emit('user-message', parameter);
                    break;

                case CMD_UI.SHOW_USER_IMG:
                    console.log("websocket: show user image", parameter);
                    if (parameter.data) {
                        emitter.emit('user-image', parameter.data);
                        emitter.emit('image-uploaded');
                    }else {
                        emitter.emit('user-image', parameter);
                        emitter.emit('image-uploaded');
                    }
                break;

                case CMD_UI.SHOW_SPINNER:
                    emitter.emit('show-spinner', parameter);
                break;
                    
                case CMD_UI.SHOW_QUERY_MSG:
                    emitter.emit('show-query-msg', parameter);

                    // if this is a query response with results, set the product group for filtering
                    if(parameter.group_id) {
                        console.log("chunk", chunk);
                        emitter.emit('set-product-group', parameter);
                    }
                    break;
                    
                default:
                    break;
            }
        }

        websocket.onerror = (error) => {
            console.error('websocket: error:', error);
        }
    };

    websocket.onSendCallback = (data) => {
        console.log("websocket: onSendCallback", data);
    }

    function on(event, callback) {
        emitter.on(event, callback);
    }

    function off(event, callback) {
        emitter.off(event, callback);
    }

    function send(data) {
        if(websocket && websocket.readyState === WebSocket.OPEN) {
            console.log("send()", data);
            websocket.send(data);
        }
    }

    function setGeminiMode(audioMode) {
        if(websocket && websocket.readyState === WebSocket.OPEN) {
            const data = JSON.stringify({
                mime_type: "application/json",
                data: {
                    command: CMD_AGENT.SET_AUDIO,
                    parameter: audioMode,
                }
            });
            console.log("websocket: setGeminiMode", data);
            websocket.send(data);
        }
    }

    function generateImage(productId) {
        if(websocket && websocket.readyState === WebSocket.OPEN) {
            const data = JSON.stringify({
                mime_type: "application/json",
                data: {
                    command: CMD_AGENT.GENERATE_IMAGE,
                    parameter: productId,
                }
            });
            console.log("websocket: generateImage", data);
            websocket.send(data);
        }
    }

    function sendMessage(message) {        
        const messageJson = JSON.stringify({
            mime_type: "text/plain",
            data: message,
        });
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(messageJson);
        }
    }

    function close() {
        if(websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.close();
            websocket = null;
        }
    }

    return {
        on,
        off,
        send,
        close,
        sendMessage,
        setGeminiMode,
        generateImage,
        websocket
    };
}

export const closeWebSocket = () => {
    if(websocket && websocket.readyState === WebSocket.OPEN) {
        console.log("closeWebSocket()");
        websocket.close();
        websocket = null;
    }
}