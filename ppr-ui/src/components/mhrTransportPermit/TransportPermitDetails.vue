<template>
  <article
    id="transport-permit-details"
    class="px-8"
    :class="{ 'cancelled-transport-permit-details': isCancelledLocation }"
  >
    <v-row noGutters>
      <v-col
        cols="3"
        class="transport-details-header"
      >
        <h3>Transport Permit Details</h3>
        <InfoChip
          v-if="isCancelledLocation"
          class="ml-2"
          action="CANCELLED"
        />
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
import { InfoChip } from '@/components/common'
const { getMhrInformation } = storeToRefs(useStore())

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  isCancelledLocation?: boolean
}>(), {
  isCancelledLocation: false
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
h3 {
  line-height: unset;
}

.cancelled-transport-permit-details  {
  // below is to grey out transport details but not the InfoChip
  .transport-details-header {
    display: contents;
  }
  .v-row:not(:first-child), .transport-details-header h3 {
    opacity: 0.4;
  }
}
</style>
