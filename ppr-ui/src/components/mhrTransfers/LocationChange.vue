<template>
  <div class="mhr-location-change">
    <FormCard
      :label="content.sideLabel"
      :showErrors="false"
      :class="{'border-error-left': false}"
    >
      <template #formSlot>
        <v-select
          id="location-change-select"
          v-model="state.locationChangeType"
          :items="state.roleBasedLocationChangeTypes"
          itemTitle="title"
          itemValue="type"
          variant="filled"
          label="Location Change Type"
          color="primary"
        />
      </template>
    </FormCard>

    <div
      v-if="state.isTransportPermitType"
      id="transport-permit-location-type"
    >
      <section
        id="transport-permit-home-location-type"
        class="mt-15"
      >
        <h2>1. Location Type</h2>
        <p class="mt-2 mb-8">
          Enter the new location type of the home.
        </p>

        <HomeLocationType
          :validate="false"
          :class="{ 'border-error-left': false }"
        />
      </section>

      <section
        id="transport-permit-home-civic-address"
        class="mt-15"
      >
        <h2>2. New Civic Address of the Home</h2>
        <p class="mt-2">
          Enter the Street Address (Number and Name) and City of new location of the home.
          Street Address must be entered if there is one.
        </p>
        <p class="mt-2">
          <b>Note:</b> If this manufactured home is being moved to a location outside of B.C.,
          the status of the home will be exempt upon filing.
        </p>

        <HomeCivicAddress
          :schema="CivicAddressSchema"
          :validate="false"
          :class="{ 'border-error-left': false }"
          @isValid="() => {}"
        />
      </section>

      <section
        v-if="state.isNotManufacturersLot"
        id="transport-permit-home-land-ownership"
        class="mt-15"
      >
        <h2>3. New Land Details</h2>
        <p class="mt-2">
          Confirm the land lease or ownership information for the home.
        </p>

        <HomeLandOwnership
          :validate="false"
          :class="{ 'border-error-left': false }"
          :content="{
            description: 'Will the manufactured home be located on land that the homeowners ' +
              'own or on land that they have a registered lease of 3 years or more?'
          }"
        />
      </section>

      <section
        v-if="state.isNotManufacturersLot"
        id="transport-permit-tax-certificate-date"
        class="mt-10"
      >
        <h2>4. Confirm Tax Certificate </h2>
        <p class="mt-2">
          A valid tax certificate is required; it must be issued from the tax
          authority with jurisdiction of the home, and must show that all local taxes have
          been paid for the current tax year. To confirm your tax certificate, enter the expiry date below.
        </p>

        <TaxCertificate
          @updateTaxCertificate="handleTaxCertificateUpdate($event)"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">

import { HomeLocationTypes, LocationChangeTypes } from "@/enums"
import { ContentIF } from "@/interfaces"
import { locationChangeTypes } from "@/resources/mhr-transfers/transport-permits"
import { useStore } from "@/store/store"
import { toRefs, reactive, computed, watch } from "vue"
import { FormCard } from "../common"
import { HomeCivicAddress, HomeLandOwnership, HomeLocationType } from "../mhrRegistration"
import { CivicAddressSchema } from '@/schemas/civic-address'
import { TaxCertificate } from "."

defineProps<{
  content?: ContentIF
}>()

const emit = defineEmits(['updateLocationType'])

const {  } = toRefs(useStore())

const { isRoleQualifiedSupplier, setMhrLocation, getMhrRegistrationLocation } = useStore()

const state = reactive({
  locationChangeType: null,
  roleBasedLocationChangeTypes: computed(() =>
    isRoleQualifiedSupplier
      ? locationChangeTypes.slice(0, -1) // qualified supplier does not have the third option in menu
      : locationChangeTypes),
  isTransportPermitType: computed(() => state.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT),
  isNotManufacturersLot: computed(() => getMhrRegistrationLocation.locationType !== HomeLocationTypes.LOT)
})

const handleTaxCertificateUpdate = (date: string) => {
  setMhrLocation({ key: 'taxExpiryDate', value: date })
  setMhrLocation({ key: 'taxCertificate', value: !!date })
}

watch(() => state.locationChangeType, val => {
  emit('updateLocationType', val)
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
