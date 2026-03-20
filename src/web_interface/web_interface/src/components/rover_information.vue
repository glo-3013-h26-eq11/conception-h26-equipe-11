<script setup lang="ts">
import {ref} from "vue";
import {Ros, Topic} from "roslib";

const direction = ref("none")

var ros = new Ros({
  url: 'ws://localhost:9999'
});

ros.on('connection', function () {
  console.log('Direction connected to ROS');
});

ros.on('error', (err) => {
  console.error(err);
})

ros.on('close', function () {
  console.log('Websocket closed');
})

var directionTopic = new Topic(
    {
      ros: ros,
      name: '/route_plan/directions',
      messageType: 'std_msgs/msg/String'
    }
)

directionTopic.subscribe(message => {
  direction.value = message.data
})
</script>

<template>
  <div>
    <v-container>
      <v-row>
        <v-col align="center" cols="4">
          <v-icon size="x-large" icon="mdi-arrow-left-top" v-show="direction == 'left'"/>
          <v-spacer v-show="direction != 'left'"/>
        </v-col>
        <v-col align="center" cols="4">
          <v-icon size="x-large" icon="mdi-arrow-up" v-show="direction == 'forward'"/>
          <v-spacer v-show="direction != 'forward'"/>
        </v-col>
        <v-col align="center" cols="4">
          <v-icon size="x-large" icon="mdi-arrow-right-top" v-show="direction == 'right'"/>
          <v-spacer v-show="direction != 'right'"/>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" align="center">
          <v-img src="../assets/rover.png" width="100" height="100"/>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped>

</style>