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

console_ros.subscribe(message => {
  messageList.value.push(message.data)
})
</script>

<template>
  <div>
    <v-card>
      <v-container>
        <v-virtual-scroll :items="messageList" height="25vh">
          <template v-slot:default="{ item }">
            {{ item }}
          </template>
        </v-virtual-scroll>
      </v-container>
    </v-card>
  </div>
</template>

<style scoped>

</style>