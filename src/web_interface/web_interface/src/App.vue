<template>
  <v-app>
    <v-main>
      <v-container fluid>
        <Configuration/>
        <DestinationStart/>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import Configuration from "@/components/configuration.vue";
import DestinationStart from "@/components/destination_start.vue";
</script>
