<script setup lang="ts">
import {ref} from "vue";

const roverStarted = ref(false)
const destination = ref("")

async function startRover() {
  const res = await fetch("/api/start", {"method": "GET"})

  if (res.ok) {
    roverStarted.value = true;
  }
}

async function stopRover() {
  const res = await fetch("/api/stop", {"method": "GET"})

  if (res.ok) {
    roverStarted.value = false;
  }
}

async function getDestination()
{
  const res = await fetch("/api/destination", {"method": "GET"})

  const data = await res.json()
  if (res.ok) {
    destination.value = data.destination
  }
}

setInterval(getDestination, 500)
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