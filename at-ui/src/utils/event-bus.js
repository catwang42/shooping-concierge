import mitt from 'mitt';
export const eventBus = mitt();

window.eventBus = eventBus;