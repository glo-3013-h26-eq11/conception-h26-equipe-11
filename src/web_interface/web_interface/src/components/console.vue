<script setup lang="ts">
import {ref} from "vue";

const messageList = ref([""])

async function getLoadUnsafe() {
  const res = await fetch("/api/console", {"method": "GET"})

  const data = await res.json()
  if (res.ok) {
    for (let i = 0; i < data.messages.length; i++) {
      messageList.value.push(data.messages[i])

    }
  }
}

setInterval(getLoadUnsafe, 500)
</script>

<template>
  <div>
    <v-card>
      <v-container>
        <v-virtual-scroll :items="messageList" height="25vh">
          <template v-slot:default="{ item }">
            {{ item }}
          </template>
        </v-virtual-scroll>
      </v-container>
    </v-card>
  </div>
</template>

<style scoped>

</style>