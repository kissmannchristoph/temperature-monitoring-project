<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const dataUrl = '/graph'

const value = ref([])
const water = ref([])

function reloadChart() {
  axios
    .get(dataUrl)
    .then(function (response) {
      if (response.status !== 200) {
        // now we can retry the fetch
        return
      }
      const arr = response.data
      for (const item of arr) {
        value.value.push(item.temp)
        water.value.push(item.water === 0)
      }
      console.log(value.value)
    })
    .catch(function (error) {
      // log the error
      console.log(error)
    })
}

onMounted(() => {
  reloadChart()
})

defineExpose({ reloadChart })
</script>

<template>
  <v-card class="mx-auto text-center" max-width="600" dark>
    <v-card-text>
      <v-card-title>Temperaturverlauf</v-card-title>
      <v-sheet>
        <v-sparkline :model-value="value" height="100" padding="24" stroke-linecap="round" smooth>
          <template v-slot:label="item">
            {{ item.value }}
          </template>
        </v-sparkline>
      </v-sheet>
    </v-card-text>

    <!--<v-card-text>
      <div class="text-h4 font-weight-thin">
        Sales Last 24h
      </div>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions class="justify-center">
      <v-btn
        variant="text"
        block
      >
        Go to Report 
      </v-btn>
    </v-card-actions>-->
  </v-card>
  <v-card class="mx-auto text-center my-2" max-width="600" dark>
    <v-card-text>
      <v-card-title>Wasserverlauf</v-card-title>
      <v-sheet>
        <v-sparkline :model-value="water" height="100" padding="24" stroke-linecap="round" smooth>
          <template v-slot:label="item">
            {{ item.value }}
          </template>
        </v-sparkline>
      </v-sheet>
    </v-card-text>

    <!--<v-card-text>
      <div class="text-h4 font-weight-thin">
        Sales Last 24h
      </div>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions class="justify-center">
      <v-btn
        variant="text"
        block
      >
        Go to Report 
      </v-btn>
    </v-card-actions>-->
  </v-card>
</template>
