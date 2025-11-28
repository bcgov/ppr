<template>
  <v-card
    id="review-card"
    flat
    aria-label="location-change-review"
    class="mb-5 pt-5"
  >
    <v-row
      v-if="isRoleStaffReg"
      no-gutters
      class="my-4 px-8 key-value-pair"
    >
      <v-col cols="3">
        Document ID
      </v-col>
      <v-col
        id="location-change-doc-id"
        cols="9"
      >
        {{ getMhrTransportPermit.documentId || 'Generate a Document ID Number upon filing' }}
      </v-col>
    </v-row>

    <v-row
      no-gutters
      class="my-4 px-8 key-value-pair"
    >
      <v-col cols="3">
        Location Change Type
      </v-col>
      <v-col
        id="location-change-type"
        cols="9"
      >
        <span v-if="isAmendLocationActive">
          Amend Transport Permit
        </span>
        <span v-else>
          {{ getUiLocationType(getMhrTransportPermit.locationChangeType) }}
        </span>
      </v-col>
    </v-row>

    <v-divider class="mx-8 mt-7 mb-n10" />

    <HomeLocationReview
      hide-default-header
      is-transport-permit-review
      :is-cancel-transport-permit-review="isCancelChangeLocationActive"
      :is-extend-change-location-review="isExtendChangeLocationActive"
    />
  </v-card>
</template>

<script setup lang="ts">
import { useTransportPermits } from '@/composables'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { HomeLocationReview } from '../mhrRegistration/ReviewConfirm';

const { isRoleStaffReg, getMhrTransportPermit } = storeToRefs(useStore())

const {
  getUiLocationType,
  isCancelChangeLocationActive,
  isAmendLocationActive,
  isExtendChangeLocationActive
} = useTransportPermits()

</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;

h3 {
  line-height: unset;
}
</style>
