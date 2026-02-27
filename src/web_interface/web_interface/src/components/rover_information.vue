<script setup lang="ts">
import {ref} from "vue";

const direction = ref("none")

async function getDirection() {
  const res = await fetch("/api/direction", {"method": "GET"})

  const data = await res.json()
  if (res.ok) {
    direction.value = data.direction
  }
}

setInterval(getDirection, 500)
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