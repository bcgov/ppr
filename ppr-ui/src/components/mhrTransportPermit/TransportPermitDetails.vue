<template>
  <article
    id="transport-permit-details"
    class="px-8"
  >
    <v-row noGutters>
      <v-col cols="3">
        <h3>Transport Permit Details</h3>
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="pt-4"
    >
      <v-col cols="3">
        <h3>Transport Permit<br> Number</h3>
      </v-col>
      <v-col cols="9">
        <p>{{ getMhrInformation.permitRegistrationNumber }}</p>
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="pt-2"
    >
      <v-col cols="3">
        <h3>Date and Time of Issue</h3>
      </v-col>
      <v-col cols="9">
        <p>{{ pacificDate(getMhrInformation.permitDateTime, true) }}</p>
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="pt-2 pb-1"
    >
      <v-col cols="3">
        <h3>Date of Expiry</h3>
      </v-col>
      <v-col cols="9">
        <p>{{ shortPacificDate(getMhrInformation.permitExpiryDateTime) }}</p>
      </v-col>
    </v-row>
    <v-divider class="my-6" />
  </article>
</template>

<script setup lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { pacificDate, shortPacificDate } from '@/utils/date-helper'
const { getMhrInformation } = storeToRefs(useStore())
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
h3 {
  line-height: unset;
}
</style>
