<script setup lang="ts">
import {ref} from "vue";
import {Ros, Topic} from "roslib";

const roverStarted = ref(false)
const destination = ref("")

var ros = new Ros({
  url: 'ws://localhost:9999'
});

ros.on('connection', function () {
  console.log('Destination and Start connected to ROS');
});

ros.on('error', (err) => {
  console.error(err);
})

ros.on('close', function () {
  console.log('Websocket closed');
})

var destinationTopic = new Topic(
    {
      ros: ros,
      name: '/route_plan/nodes',
      messageType: 'std_msgs/msg/String'
    }
)

destinationTopic.subscribe(message => {
  destination.value = (JSON.parse(message.data) || []).at(-1);
});

var startTopic = new Topic(
    {
      ros: ros,
      name: '/rover/start',
      messageType: 'std_msgs/msg/Bool'
    }
)

async function startRover() {
  let message = {data: true}
  startTopic.publish(message)
  roverStarted.value = true
}

async function stopRover() {
  let message = {data: false}
  startTopic.publish(message)
  roverStarted.value = false
}
</script>

<template>
  <div>
    <v-container>
      <v-row align="center" justify="center">
        <v-col justify="center" align="center" cols="12">
          <v-text-field label="Destination" variant="outlined" v-model="destination" readonly/>
        </v-col>
      </v-row>
      <v-row align="center" justify="center">
        <v-col justify="center" align="center" cols="12">
          <v-btn prepend-icon="mdi-car" @click="startRover" v-show="!roverStarted">Démarrer le Rover</v-btn>
          <v-btn prepend-icon="mdi-car-off" @click="stopRover" v-show="roverStarted">Arreter le Rover</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped>

</style>