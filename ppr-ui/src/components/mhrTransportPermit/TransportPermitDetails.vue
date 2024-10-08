<template>
  <article
    id="transport-permit-details"
    class="px-8 pt-6"
    :class="[
      { 'cancelled-transport-permit-details': isCancelledLocation },
      { 'void-transport-permit-details': isVoidPermit }
    ]"
  >
    <v-row noGutters>
      <v-col
        class="transport-details-header"
      >
        <InfoChip
          v-if="isVoidPermit"
          class="ml-2"
          action="VOID"
          style="float: left; margin-left: 0 !important;"
          data-test-id="void-transport-permit-badge"
        />
        <h4 class="fs-16 lh-24">
          Transport Permit Details
        </h4>
        <InfoChip
          v-if="isCancelledLocation"
          class="ml-2"
          action="CANCELLED"
        />
      </v-col>
    </v-row>

    <v-row
      v-if="infoText"
      class="mt-0"
      data-test-id="permit-details-info-text"
    >
      <v-col>
        {{ infoText }}
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="pt-4 key-value-pair"
    >
      <v-col cols="3 tp-header">
        Transport Permit<br> Number
      </v-col>
      <v-col cols="9 tp-label">
        {{ getMhrInformation.permitRegistrationNumber }}
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="pt-2 key-value-pair"
    >
      <v-col cols="3 tp-header">
        Date and Time of Issue
      </v-col>
      <v-col cols="9 tp-label">
        {{ pacificDate(getMhrInformation.permitDateTime, true) }}
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="pt-2 pb-1 key-value-pair"
    >
      <v-col cols="3 tp-header">
        Date of Expiry
        <UpdatedBadge
          v-if="isExtendChangeLocationActive"
          action="EXTENDED"
          :baseline="getMhrInformation.permitDateTime"
          :currentState="addDaysToDate(convertDate(new Date(), false, false), 30)"
        />
      </v-col>
      <v-col cols="9 tp-label">
        {{ isExtendChangeLocationActive
          ? shortPacificDate(addDaysToDate(convertDate(new Date(), false, false), 30))
          : shortPacificDate(getMhrInformation.permitExpiryDateTime)
        }}
      </v-col>
    </v-row>
    <v-divider class="transport-permit-divider my-6" />
  </article>
</template>

<script setup lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { convertDate } from '@/utils'
import { addDaysToDate, pacificDate, shortPacificDate } from '@/utils/date-helper'
import { InfoChip, UpdatedBadge } from '@/components/common'
import { useTransportPermits } from '@/composables'
const { getMhrInformation } = storeToRefs(useStore())

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  isCancelledLocation?: boolean,
  isVoidPermit?: boolean,
  infoText?: string
}>(), {
  isCancelledLocation: false,
  isVoidPermit: false,
  infoText: ''
})

const { isExtendChangeLocationActive } = useTransportPermits()

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
  dd, dt, .transport-details-header h3 {
    opacity: 0.4;
  }
}

.void-transport-permit-details {
  background-color: #FAFAFA;
  margin-top: 0px !important;
  padding-top: 40px !important;

  border-bottom: 1px solid $gray3;
  margin-bottom: 28px;
  padding-bottom: 31px;

  .transport-permit-divider {
    display: none;
  }
}
</style>
