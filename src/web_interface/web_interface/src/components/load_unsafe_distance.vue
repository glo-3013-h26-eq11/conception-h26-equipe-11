<script setup lang="ts">
import {ref} from "vue";

const loaded = ref(false);
const roverTooClose = ref(false);

async function getLoadUnsafe(){
  const res = await fetch("/api/loadunsafe", {"method": "GET"})

  const data = await res.json()
  if (res.ok) {
    loaded.value = data.loaded
    roverTooClose.value = data.unsafe
  }
}

setInterval(getLoadUnsafe, 500)
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
          <v-chip prepend-icon="mdi-alert" size="x-large" :color="roverTooClose ? 'error':'primary-variant'">Rover too close
          </v-chip>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped>

</style>