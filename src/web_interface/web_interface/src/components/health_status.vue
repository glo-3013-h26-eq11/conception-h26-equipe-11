<script setup lang="ts">
import {ref} from "vue";
import {Ros, Topic} from "roslib";

const host = "10.241.146.61"
const status = ref({})
var ros = new Ros({
  url: `ws://${host}:9999`
});


ros.on('connection', function () {
  console.log('System Health connected to ROS');
});

ros.on('error', (err) => {
  console.error(err);
})

ros.on('close', function () {
  console.log('Websocket closed');
})

var status_ros = new Topic(
    {
      ros: ros,
      name: '/health_status',
      messageType: 'std_msgs/msg/String'
    }
)

status_ros.subscribe((message) => {
    const newStatus = JSON.parse(message.data)
    status.value = newStatus

    console.log(newStatus)
})

</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="pa-3 mb-4">
          <v-card-title>
            <strong>System Health</strong>
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col
        v-for="(nodes, system) in status"
        :key="system"
        cols="12"
        md="6"
      >
        <v-card class="pa-3 mb-4">
          <v-card-title>
            <strong>{{ system }}</strong>
          </v-card-title>
          <v-card-text>
            <v-list dense>
              <v-list-item
                v-for="(state, node) in nodes"
                :key="node"
              >
                <v-list-item-content>
                  <span>{{ node }}</span>
                </v-list-item-content>
                <v-list-item-action>
                  <span :class="['status', state.toLowerCase()]">{{ state }}</span>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.status {
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
  min-width: 60px;
  text-align: center;
}

.status.loading {
  background-color: #f5c542;
  color: #000;
}

.status.active {
  background-color: #42f554;
  color: #000;
}

.status.crashed {
  background-color: #f54242;
  color: #fff;
}
</style>
           