<script setup lang="ts">
import {ref} from 'vue'

const topographie = ref()
const aruco = ref()

async function uploadFile() {

  const fileTopographie = topographie.value
  const fileAruco = aruco.value

  var csvTopographie = await fileTopographie.text()
  var csvAruco = await fileAruco.text()

  const mergedCsv = `${csvTopographie}\n---\n${csvAruco}`

  const res = await fetch('/api/csv/concat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_names: [fileTopographie.name, fileAruco.name],
      csv_content: mergedCsv })
  })

  const data = await res.json()
  if (!res.ok) {
    return
  }
}
</script>

<template>
  <v-container fluid>
    <v-card title="Configuration" border="thin">
      <v-row>
        <v-col>
          <v-file-input v-model="topographie" accept=".csv,text/csv" clearable prepend-icon="mdi-train-car"
                        label="Topographie" variant="outlined"/>
        </v-col>
        <v-col>
          <v-file-input v-model="aruco" accept=".csv,text/csv" clearable prepend-icon="mdi-qrcode" label="ArUco"
                        variant="outlined"/>
        </v-col>
      </v-row>
      <v-card-actions>
        <v-btn variant="tonal" prepend-icon="mdi-upload" @click="uploadFile">Téléchargé</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<style scoped>

</style>