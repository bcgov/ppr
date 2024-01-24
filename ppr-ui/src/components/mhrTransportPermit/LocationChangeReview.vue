<template>
  <v-card
    id="review-card"
    flat
    aria-label="location-change-review"
    class="mb-5"
  >
    <v-row
      class="my-4 px-7"
      noGutters
    >
      <v-col cols="3">
        <label class="generic-label">Document Id</label>
      </v-col>
      <v-col
        id="location-change-type"
        cols="9"
        class="gray7"
      >
        {{ getMhrTransportPermit.documentId }}
      </v-col>
    </v-row>

    <v-row
      class="my-4 px-7"
      noGutters
    >
      <v-col cols="3">
        <label class="generic-label">Location Change Type</label>
      </v-col>
      <v-col
        id="location-change-type"
        cols="9"
        class="gray7"
      >
        {{ getUiLocationType(getMhrTransportPermit.locationChangeType) }}
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
import { useTransportPermits } from '@/composables'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

const { getMhrTransportPermit } = storeToRefs(useStore())

const { getUiLocationType } = useTransportPermits()

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
