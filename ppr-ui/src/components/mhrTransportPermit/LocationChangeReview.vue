<template>
  <v-card
    id="review-card"
    flat
    aria-label="location-change-review"
    class="mb-5 pt-5"
  >
    <dl>
      <v-row
        v-if="isRoleStaffReg"
        noGutters
        class="my-4 px-8 key-value-pair"
      >
        <v-col cols="3">
          <dt>Document ID</dt>
        </v-col>
        <v-col
          id="location-change-doc-id"
          cols="9"
        >
          <dd>{{ getMhrTransportPermit.documentId }}</dd>
        </v-col>
      </v-row>

      <v-row
        noGutters
        class="my-4 px-8 key-value-pair"
      >
        <v-col cols="3">
          <dt>Location Change Type</dt>
        </v-col>
        <v-col
          id="location-change-type"
          cols="9"
        >
          <dd v-if="isAmendLocationActive">
            Amend Transport Permit
          </dd>
          <dd v-else>
            {{ getUiLocationType(getMhrTransportPermit.locationChangeType) }}
          </dd>
        </v-col>
      </v-row>
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
