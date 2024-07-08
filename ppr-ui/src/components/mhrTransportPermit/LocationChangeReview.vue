<template>
  <v-card
    id="review-card"
    flat
    aria-label="location-change-review"
    class="mb-5 pt-5"
  >
    <dl
      v-if="isRoleStaffReg"
      class="flex-3-9 key-value-pair my-4 px-8"
    >
      <dt>Document ID</dt>
      <dd id="location-change-doc-id">
        {{ getMhrTransportPermit.documentId }}
      </dd>
    </dl>

    <dl class="flex-3-9 key-value-pair my-4 px-8">
      <dt>Location Change Type</dt>
      <dd id="location-change-type">
        <template v-if="isAmendLocationActive">
          Amend Transport Permit
        </template>
        <template v-else>
          {{ getUiLocationType(getMhrTransportPermit.locationChangeType) }}
        </template>
      </dd>
    </dl>

    <v-divider class="mx-8 mt-7 mb-n10" />

    <HomeLocationReview
      hideDefaultHeader
      isTransportPermitReview
      :isCancelTransportPermitReview="isCancelChangeLocationActive"
    />
  </v-card>
</template>

<script setup lang="ts">
import { useTransportPermits } from '@/composables'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { HomeLocationReview } from '../mhrRegistration/ReviewConfirm';

const { isRoleStaffReg, getMhrTransportPermit } = storeToRefs(useStore())

const { getUiLocationType, isCancelChangeLocationActive, isAmendLocationActive } = useTransportPermits()

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

h3 {
  line-height: unset;
}
</style>
