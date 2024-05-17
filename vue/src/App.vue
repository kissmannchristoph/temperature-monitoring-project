<script setup>
import { ref, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { io } from 'socket.io-client'
import axios from 'axios'
import TempGraph from './components/TempGraph'

const theme = useTheme()
const darkMode = ref(false)

const chartRef = ref(null)

//const socketUrl = 'ws://127.0.0.1:8080/'
const dataUrl = ''

const socketConnectionState = ref(false)

const showTempGraph = ref(false)

const data = ref({
  temp: 0.0,
  rain: false
})

async function setupSocket() {
  const socket = io()

  socket.on('connect', () => {
    socketConnectionState.value = true
  })

  socket.on('disconnect', () => {
    socketConnectionState.value = false
  })

  socket.on('updateData', (response) => {
    data.value = response
  })

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  socket.on('updateChart', (response) => {
    chartRef.value?.reloadChart()
  })
}

async function retryFetch() {
  setTimeout(fetchData, 100)
}

async function fetchData() {
  axios
    .get(dataUrl)
    .then(function (response) {
      if (response.status !== 200) {
        // now we can retry the fetch
        retryFetch()
        return
      }
      data.value = response.data
    })
    .catch(function (error) {
      // log the error
      console.log(error)
      // now we can retry the fetch
      retryFetch()
    })
}

function performShowTempGraph() {
  if (showTempGraph.value) {
    showTempGraph.value = false
    return
  }
  showTempGraph.value = true
}

const toggleTheme = () => {
  darkMode.value = !darkMode.value
  theme.global.name.value = darkMode.value ? 'dark' : 'light'
}

onMounted(async () => {
  setupSocket()

  // This is useless, because we only need the socket connection,
  // but the requirements says, we need a get request
  // fetchData();
})
</script>
<template>
  <v-app>
    <v-main>
      <v-app-bar :elevation="2">
        <template v-slot:append>
          <v-btn icon="mdi-theme-light-dark" @click="toggleTheme"></v-btn>
        </template>

        <v-app-bar-title>Raumüberwachung</v-app-bar-title>
      </v-app-bar>

      <div class="d-flex justify-center ma-10 flex-wrap">
        <v-card
          @click="performShowTempGraph"
          class="pa-4 ma-2"
          style="width: 180px; user-select: none"
        >
          <v-card-title>Temperatur</v-card-title>
          <v-card-text>
            <div class="d-flex justify-space-between mt-2 px-4">
              <span>{{ data.temp }}</span>
              <v-icon icon="mdi-thermometer-low"></v-icon>
            </div>
          </v-card-text>
        </v-card>
        <v-card class="pa-4 ma-2" style="width: 180px; user-select: none">
          <v-card-title>Regen</v-card-title>
          <v-card-text>
            <div class="d-flex justify-space-between mt-2 px-4">
              <span>{{ data.rain }}</span>
              <v-icon icon="mdi-weather-pouring"></v-icon>
            </div>
          </v-card-text>
        </v-card>
      </div>

      <TempGraph ref="chartRef" />

      <v-footer style="position: absolute; bottom: 0" class="w-100">
        <div>
          Connection State:
          {{ socketConnectionState ? 'Connected' : 'Disconnected' }}
        </div></v-footer
      >
    </v-main>
  </v-app>
</template>

<style></style>
