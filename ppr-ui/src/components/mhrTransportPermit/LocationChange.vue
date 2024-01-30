<template>
  <div class="mhr-location-change">
    <BaseDialog
      :setOptions="changeTransportPermitLocationTypeDialog"
      :setDisplay="state.showChangeTransportPermitLocationTypeDialog"
      @proceed="handleChangeTransportPermitLocationTypeResp($event)"
    />

    <FormCard
      label="Location Change Type"
      :showErrors="validate && !state.locationChangeFromValid"
      :class="{'border-error-left': validate && !state.locationChangeFromValid}"
    >
      <template #formSlot>
        <v-form
          ref="locationChangeForm"
          v-model="state.locationChangeFromValid"
        >
          <v-select
            id="location-change-select"
            ref="locationChangeSelectRef"
            v-model="state.locationChangeType"
            :items="state.roleBasedLocationChangeTypes"
            :rules="required('Select Location Change Type')"
            itemTitle="title"
            itemValue="type"
            variant="filled"
            label="Location Change Type"
            color="primary"
          >
            <template #item="{ props, item }">
              <v-list-item
                v-bind="props"
                @click="handleLocationTypeChange(item.props.value)"
              />
            </template>
          </v-select>
        </v-form>
      </template>
    </FormCard>

    <div
      v-if="state.isTransportPermitType"
      id="transport-permit-location-type"
    >
      <section
        id="transport-permit-home-location-type"
        class="mt-12"
      >
        <h2>1. Location Type</h2>
        <p class="mt-2 mb-8">
          Enter the new location type of the home.
        </p>

        <HomeLocationType
          :locationTypeInfo="getMhrTransportPermit.newLocation"
          :class="{ 'border-error-left': validate && !getInfoValidation('isHomeLocationTypeValid') }"
          :validate="validate && !getInfoValidation('isHomeLocationTypeValid')"
          @setStoreProperty="handleLocationTypeUpdate($event)"
          @isValid="setValidation('isHomeLocationTypeValid', $event)"
        />
      </section>

      <section
        id="transport-permit-home-civic-address"
        class="mt-12"
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
          ref="homeCivicAddressRef"
          :value="getMhrTransportPermit.newLocation"
          :schema="CivicAddressSchema"
          :class="{ 'border-error-left': validate && !getInfoValidation('isHomeCivicAddressValid') }"
          :validate="validate && !getInfoValidation('isHomeCivicAddressValid')"
          @isValid="setValidation('isHomeCivicAddressValid', $event)"
        />
      </section>

      <section
        id="transport-permit-home-land-ownership"
        class="mt-12"
      >
        <h2>3. New Land Details</h2>
        <p class="mt-2">
          Confirm the land lease or ownership information for the home.
        </p>

        <HomeLandOwnership
          :ownLand="getMhrTransportPermit.ownLand"
          :class="{ 'border-error-left': validate && !getInfoValidation('isHomeLandOwnershipValid') }"
          :validate="validate && !getInfoValidation('isHomeLandOwnershipValid')"
          :content="{
            description: 'Will the manufactured home be located on land that the homeowners ' +
              'own or on land that they have a registered lease of 3 years or more?'
          }"
          @setStoreProperty="setMhrTransportPermit({ key: 'ownLand', value: $event })"
          @isValid="setValidation('isHomeLandOwnershipValid', $event)"
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
          ref="taxCertificateRef"
          :expiryDate="getMhrTransportPermit.newLocation.taxExpiryDate"
          :class="{ 'border-error-left': validate && !getInfoValidation('isTaxCertificateValid') }"
          :validate="validate && !getInfoValidation('isTaxCertificateValid')"
          @setStoreProperty="handleTaxCertificateUpdate($event)"
          @isValid="setValidation('isTaxCertificateValid', $event)"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">

import { HomeLocationTypes, LocationChangeTypes } from "@/enums"
import { ContentIF, FormIF } from "@/interfaces"
import { locationChangeTypes } from "@/resources/mhr-transfers/transport-permits"
import { useStore } from "@/store/store"
import { reactive, computed, watch, ref, nextTick } from "vue"
import { FormCard } from "../common"
import { HomeCivicAddress, HomeLandOwnership, HomeLocationType } from "../mhrRegistration"
import { CivicAddressSchema } from '@/schemas/civic-address'
import { TaxCertificate } from "../mhrTransfers"
import { useInputRules } from "@/composables/useInputRules"
import { useMhrInfoValidation, useTransportPermits } from "@/composables"
import { storeToRefs } from "pinia"
import { changeTransportPermitLocationTypeDialog } from '@/resources/dialogOptions'
import { BaseDialog } from '@/components/dialogs'
import { cloneDeep } from 'lodash'

const props = defineProps<{
  validate: boolean,
  content?: ContentIF
}>()

const emit = defineEmits(['updateLocationType'])

const { isRoleQualifiedSupplier, getMhrRegistrationLocation,
  setMhrTransportPermit, setMhrTransportPermitNewLocation } = useStore()

const { hasUnsavedChanges, getMhrTransportPermit, getMhrInfoValidation } = storeToRefs(useStore())

const { setLocationChangeType, resetTransportPermit } = useTransportPermits()

const {
  setValidation,
  getInfoValidation,
  resetValidationState
} = useMhrInfoValidation(getMhrInfoValidation.value)

const { required } = useInputRules()

const locationChangeForm = ref(null) as FormIF
const locationChangeSelectRef = ref(null) as FormIF

const homeCivicAddressRef = ref(null)
const taxCertificateRef = ref(null)

const state = reactive({
  locationChangeType: getMhrTransportPermit.value.locationChangeType,
  prevLocationChangeType: null,
  locationChangeFromValid: false,
  roleBasedLocationChangeTypes: computed(() =>
    isRoleQualifiedSupplier
      ? locationChangeTypes.slice(0, -1) // qualified supplier does not have the third option in menu
      : locationChangeTypes),
  isTransportPermitType: computed(() =>
    getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT),
  isNotManufacturersLot: computed(() => getMhrRegistrationLocation.locationType !== HomeLocationTypes.LOT),
  showChangeTransportPermitLocationTypeDialog: false
})

const handleTaxCertificateUpdate = (date: string) => {
  setMhrTransportPermitNewLocation({ key: 'taxExpiryDate', value: date })
  setMhrTransportPermitNewLocation({ key: 'taxCertificate', value: !!date })
}

const handleLocationTypeUpdate = (newLocation: { key, value }) => {
  setMhrTransportPermitNewLocation(newLocation)
}

watch(() => state.locationChangeType, val => {
  setValidation('isLocationChangeTypeValid', !!val)
})

// if Tax Certificate is hidden set the validation for it to true
watch(() => state.isNotManufacturersLot, val => {
  !val && setValidation('isTaxCertificateValid', true)
})

watch(() => props.validate, () => {
  locationChangeSelectRef.value?.validate()
})


watch(() => state.isTransportPermitType, async (isTransportPermitType) => {
  // if Transport Permit form open and page validation was triggered - validate the components
  if (isTransportPermitType && props.validate) {
    nextTick(() => {
      homeCivicAddressRef.value.$refs.addressForm.validate()
      taxCertificateRef.value.$refs.expiryDatePickerRef.validate()
    })
  }
})


const selectLocationType = (item: LocationChangeTypes): void => {
  state.locationChangeType = cloneDeep(item)
  setLocationChangeType(item)
  locationChangeSelectRef.value?.blur()
}

const handleLocationTypeChange = (locationType: LocationChangeTypes) => {
  // initially there would be no type selected so we do not show the dialog
  const hasTypeSelected = !!getMhrTransportPermit.value?.locationChangeType

  if (locationType !== state.prevLocationChangeType && hasUnsavedChanges.value && hasTypeSelected) {
    state.showChangeTransportPermitLocationTypeDialog = true
  } else {
    state.prevLocationChangeType = cloneDeep(locationType)
    selectLocationType(locationType)
  }
}

const handleChangeTransportPermitLocationTypeResp = (proceed: boolean) => {
  if (proceed) {
    // change transfer type and reset transport permit
    resetTransportPermit()
    resetValidationState()
    selectLocationType(cloneDeep(state.locationChangeType))
    // when changing Location Type update the validation for it after reset
    setValidation('isLocationChangeTypeValid', true)
    // emit location change to reset page validations
    emit('updateLocationType')
  } else {
    selectLocationType(cloneDeep(state.prevLocationChangeType))
  }
  state.showChangeTransportPermitLocationTypeDialog = false
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
