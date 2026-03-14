<script setup lang="ts">
import {ref} from 'vue'
import {Ros, Topic} from "roslib";

const topographie = ref()
const aruco = ref()

var ros = new Ros({
  url: 'ws://localhost:9999'
});

ros.on('connection', function () {
  console.log('Configuration connected to ROS');
});

ros.on('error', (err) => {
  console.error(err);
})

ros.on('close', function () {
  console.log('Websocket closed');
})

var mapPublisher = new Topic({
      ros: ros,
      name: '/map_manager/raw_map_topic',
      messageType: 'std_msgs/msg/String'
    })

async function uploadFile() {

  const fileTopographie = topographie.value
  const fileAruco = aruco.value

  var csvTopographie = await fileTopographie.text()
  var csvAruco = await fileAruco.text()

  const mergedCsv = `${csvTopographie}\n---\n${csvAruco}`

  let message = {data: mergedCsv}

  mapPublisher.publish(message)
}
</script>

<template>
  <div>
    <v-container>
    <v-card title="Configuration" border="thin" >
      <v-row>
        <v-col cols="12" md="6">
          <v-file-input  v-model="topographie" accept=".csv,text/csv" clearable prepend-icon="mdi-train-car"
                        label="Topographie" variant="outlined"/>
        </v-col>
        <v-col cols="12" md="6">
          <v-file-input v-model="aruco" accept=".csv,text/csv" clearable prepend-icon="mdi-qrcode" label="ArUco"
                        variant="outlined"/>
        </v-col>
      </v-row>
      <v-card-actions>
        <v-btn variant="tonal" prepend-icon="mdi-upload" @click="uploadFile">Téléchargé</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
  </div>
</template>

<style scoped>

</style>