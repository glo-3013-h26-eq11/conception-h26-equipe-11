<script setup lang="ts">
import {ref} from "vue";
import {Ros, Topic} from "roslib";

const loaded = ref(false);
const roverTooClose = ref(false);

var ros = new Ros({
  url: 'ws://localhost:9999'
});

ros.on('connection', function () {
  console.log('Laod and Unsafe distance connected to ROS');
});

ros.on('error', (err) => {
  console.error(err);
})

ros.on('close', function () {
  console.log('Websocket closed');
})

var is_there_merchandise = new Topic(
    {
      ros: ros,
      name: '/proximity_sensor/merchandise',
      messageType: 'std_msgs/msg/Bool'
    }
)

is_there_merchandise.subscribe(message => {
  loaded.value = message.data;
})

var unsafe_distance = new Topic(
    {ros: ros,
      name: '/car_distance/dangerous',
      messageType: 'std_msgs/msg/Bool'}
)

unsafe_distance.subscribe(message => {
  roverTooClose.value = message.data;
})
</script>

<template>
  <div>
    <v-container>
      <v-row align="center" justify="center">
        <v-col align="center" justify="center">
          <v-chip prepend-icon="mdi-package" size="x-large" :color="loaded ? 'green':'primary-variant'">Loaded</v-chip>
        </v-col>
      </v-row>
      <v-row align="center" justify="center">
        <v-col align="center" justify="center">
          <v-chip prepend-icon="mdi-alert" size="x-large" :color="roverTooClose ? 'error':'primary-variant'">Rover too
            close
          </v-chip>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped>

</style>