<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <Configuration/>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" md="6">
            <DestinationStart/>
          </v-col>
          <v-col cols="12" md="3">
            <RoverInformation/>
          </v-col>
          <v-col cols="12" md="3">
            <LoadUnsafeDistance/>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <Console/>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import Configuration from "@/components/configuration.vue";
import DestinationStart from "@/components/destination_start.vue";
import RoverInformation from "@/components/rover_information.vue";
import LoadUnsafeDistance from "@/components/load_unsafe_distance.vue";
import Console from "@/components/console.vue";
</script>
