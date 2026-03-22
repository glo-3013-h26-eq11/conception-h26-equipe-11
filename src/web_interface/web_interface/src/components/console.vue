<script setup lang="ts">
import {ref} from "vue";
import {Ros, Topic} from "roslib";

const messageList = ref([""])

var ros = new Ros({
  url: 'ws://localhost:9999'
});

ros.on('connection', function () {
  console.log('Console connected to ROS');
});

ros.on('error', (err) => {
  console.error(err);
})

ros.on('close', function () {
  console.log('Websocket closed');
})

var console_ros = new Topic(
    {
      ros: ros,
      name: '/console',
      messageType: 'std_msgs/msg/String'
    }
)

console_ros.subscribe((message) => {
  const newLogs = JSON.parse(message.data)

  const current = messageList.value

  if (!current.length) {
    messageList.value.push(...newLogs)
    return
  }

  for (const log of newLogs) {
    if (!current.find(l => l === log)) {
      current.push(log)
    }
  }
})

</script>

<template>
  <div>
    <v-card>
      <v-container>
        <v-virtual-scroll :items="messageList" height="25vh">
          <template v-slot:default="{ item }">
            <div class="log-line">
              {{item}}
            </div>
          </template>
        </v-virtual-scroll>
      </v-container>
    </v-card>
  </div>
</template>

<style scoped>

</style>