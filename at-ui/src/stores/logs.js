import { defineStore } from 'pinia'

export const useLogsStore = defineStore('logs', {
  state: () => ({
    logs: []
  }),
  actions: {
    setSockets(sockets) {
      this.sockets = sockets;
      this.sockets.on('show-query-msg', (data) => {
          if(data.group_id) {
          this.addLog({
            type: "queryResponse",
            userIntent: data.user_intent,
            itemCategory: data.item_category,
            foundItemCount: data.found_item_count,
            totalItemCount: data.total_item_count,
            elapsedTime: data.elapsed_time,
            queries: data.queries,
          });
        }
      })
      this.sockets.on('present-items', (data) => {
        this.addLog({
          type: "presentItems",
          userIntent: data.user_intent,
          itemCategory: data.item_category,
          selectedItemCount: data.selected_item_count,
          foundItemCount: data.found_item_count,
          elapsedTime: data.elapsed_time,
        })
      })
    },
    addLog(log) {
      this.logs.push(log);
    },
    clearLogs() {
      this.logs = [];
    }
  }
})