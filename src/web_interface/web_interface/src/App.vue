<script setup lang="ts">
import { ref } from 'vue'

const status = ref('Aucun fichier sélectionné')
const fileInput = ref<HTMLInputElement | null>(null)

function openPicker() {
  fileInput.value?.click()
}

async function onFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const files = input.files

  if (!files || files.length !== 2) { 
    status.value = 'Choisir exactement 2 fichiers CSV'
    return
  }

  const [f1, f2] = Array.from(files)

  const isCsv1 = f1.name.toLowerCase().endsWith('.csv')
  const isCsv2 = f2.name.toLowerCase().endsWith('.csv')
  if (!isCsv1 || !isCsv2) {
    status.value = 'Erreur: les deux fichiers doivent être des .csv'
    return
  }

status.value = `Ok: ${f1.name} + ${f2.name}`

try {
  status.value = 'Lecture des fichiers...'
  const text1 = await f1.text()
  const text2 = await f2.text()

  const mergedCsv = `${text1}\n---\n${text2}`
  
  status.value = 'Envoie au backend'
  console.log(mergedCsv)

  const res = await fetch('/api/csv/concat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_names: [f1.name, f2.name],
      csv_content: mergedCsv })
  })

  const data = await res.json()
  if (!res.ok) {
    status.value = `Erreur backend: ${data.detail ?? 'inconnue'}`
    return
  }
  status.value = `Succès: ${data.message}`

} catch (e) {
  status.value = 'Erreur lors de la lecture ou de l\'envoie'
} finally {
  input.value = ''
  }

}
</script>

<template>
 <main>
  <button type="button" @click="openPicker">Choisir 2 CSV</button>
  <input ref="fileInput" type="file" accept=".csv,text/csv" multiple hidden @change = "onFilesSelected">
  <p>{{ status }}</p>
 </main>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
