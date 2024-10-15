<template>
  <div class="mhr-location-change">
    <BaseDialog
      :setOptions="changeTransportPermitLocationTypeDialog"
      :setDisplay="state.showChangeTransportPermitLocationTypeDialog"
      @proceed="handleChangeTransportPermitLocationTypeResp($event)"
    />

    <FormCard
      v-if="!isAmendLocationActive && !isExtendChangeLocationActive && !isNewPermitActive"
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
                v-bind="isListItemDisabled(item.props.value) ? null : props"
                :title="null"
                :ripple="isListItemDisabled(item.props.value) ? false : true"
                :class="{ 'disabled-item' : isListItemDisabled(item.props.value) }"
                @click="isListItemDisabled(item.props.value) ? null : handleLocationTypeChange(item.props.value)"
              >
                <v-tooltip
                  v-if="isListItemDisabled(item.props.value)"
                  location="right"
                  contentClass="left-tooltip"
                  transition="fade-transition"
                >
                  <template #activator="{ props }">
                    <v-list-item-title
                      v-bind="props"
                      class="disabled-transport-permit-option"
                    >
                      <div class="disabled-title">
                        {{ item.title }}
                      </div>
                      <div>
                        <v-icon
                          class="mt-n1"
                          color="primary"
                        >
                          mdi-information-outline
                        </v-icon>
                      </div>
                    </v-list-item-title>
                  </template>
                  <strong>
                    Location Change Type Not Available
                  </strong>
                  <br>
                  <br>
                  The manufactured home must be located in a manufactured home park.
                </v-tooltip>
                <span v-else>
                  {{ item.title }}
                </span>
              </v-list-item>
            </template>
          </v-select>
        </v-form>
      </template>
    </FormCard>

    <div
      v-if="state.isTransportPermitType || isRegisteredLocationChange || isExtendChangeLocationActive"
      id="transport-permit-location-type"
    >
      <section
        v-if="!isExtendChangeLocationActive"
        id="transport-permit-home-location-type"
        class="mt-10"
      >
        <div
          v-if="validate && !hasAmendmentChanges"
          class="text-error mb-7"
          data-test-id="amend-permit-changes-required-msg"
        >
          A change to the Location Type, Civic Address, and/or Land Details is required
        </div>

        <h2>1. Location Type</h2>
        <p class="mt-2 mb-8">
          {{ isAmendLocationActive ? 'Amend' : 'Enter' }} the new location type of the home.
        </p>

        <HomeLocationType
          :key="getMhrTransportPermit.locationChangeType"
          :locationTypeInfo="getMhrTransportPermit.newLocation"
          :class="{ 'border-error-left': state.isLocationTypeInvalid }"
          :validate="validate"
          :updatedBadge="isAmendLocationActive ? state.amendedBadgeHomeLocationType : null"
          @setStoreProperty="handleLocationTypeUpdate($event)"
          @isValid="setValidation('isHomeLocationTypeValid', $event)"
        />
      </section>

      <section
        v-if="!isExtendChangeLocationActive"
        id="transport-permit-home-civic-address"
        class="mt-12"
      >
        <h2>2. New Civic Address of the Home</h2>
        <template v-if="state.isRoleQSorSBCAmend">
          <p
            class="mt-2"
            data-test-id="amend-street-only-info"
          >
            Amend the Street Address (Number and Name). If you need further updates contract BC Registries staff.
          </p>
        </template>
        <template v-else>
          <p class="mt-2">
            {{ isAmendLocationActive ? 'Amend' : 'Enter' }} the Street Address (Number and Name)
            and City of new location of the home. Street Address must be entered if there is one.
          </p>
          <p
            class="mt-2"
            role="alert"
          >
            <b>Note:</b> If this manufactured home is being moved to a location outside of B.C.,
            the status of the home will be exempt upon filing.
          </p>
        </template>


        <HomeCivicAddress
          ref="homeCivicAddressRef"
          :key="getMhrTransportPermit.locationChangeType"
          :value="getMhrTransportPermit.newLocation.address"
          :schema="CivicAddressSchema"
          :class="{ 'border-error-left': state.isCivicAddressInvalid }"
          :validate="state.isCivicAddressInvalid"
          :updatedBadge="isAmendLocationActive ? state.amendedBadgeCivicAddress : null"
          :hasOnlyStreetEditable="state.isRoleQSorSBCAmend"
          @setStoreProperty="handleTransportPermitAddressUpdate($event)"
          @isValid="setValidation('isHomeCivicAddressValid', $event)"
        />
      </section>

      <section
        v-if="!isExtendChangeLocationActive"
        id="transport-permit-home-land-ownership"
        class="mt-12"
      >
        <h2>3. New Land Details</h2>
        <p class="mt-2">
          Confirm the land lease or ownership information for the home.
        </p>

        <HomeLandOwnership
          :key="getMhrTransportPermit.locationChangeType"
          :ownLand="getMhrTransportPermit.ownLand"
          :class="{ 'border-error-left': state.isLandOwnershipInvalid }"
          :validate="state.isLandOwnershipInvalid"
          :content="{
            description: 'Is the manufactured home located on land that the homeowners ' +
              'own or on land that they have a registered lease of 3 years or more?'
          }"
          :updatedBadge="isAmendLocationActive ? state.amendedBadgeHomeLandOwnership : null"
          @setStoreProperty="setMhrTransportPermit({ key: 'ownLand', value: $event })"
          @isValid="setValidation('isHomeLandOwnershipValid', $event)"
        />
      </section>

      <section
        v-if="isNotManufacturersLot && !isAmendLocationActive && !isActiveHomeOutsideBc"
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
          :key="getMhrTransportPermit.locationChangeType"
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
import { HomeLocationTypes, LocationChangeTypes, MhApiStatusTypes } from '@/enums'
import { FormIF } from '@/interfaces'
import { locationChangeTypes } from '@/resources/mhr-transport-permits/transport-permits'
import { useStore } from '@/store/store'
import { reactive, computed, watch, ref, nextTick, onMounted } from 'vue'
import { FormCard } from '@/components/common'
import { HomeCivicAddress, HomeLandOwnership, HomeLocationType } from '@/components/mhrRegistration'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { TaxCertificate } from '@/components/mhrTransfers'
import { useInputRules } from '@/composables/useInputRules'
import { useMhrInfoValidation, useTransportPermits } from '@/composables'
import { storeToRefs } from "pinia"
import { changeTransportPermitLocationTypeDialog } from '@/resources/dialogOptions'
import { BaseDialog } from '@/components/dialogs'
import { cloneDeep } from 'lodash'

const props = defineProps<{
  validate: boolean
}>()

const emit = defineEmits(['updateLocationType'])

const { setMhrTransportPermit, setMhrTransportPermitNewLocation,
  setMhrTransportPermitNewCivicAddress, setUnsavedChanges, setMhrStatusType } = useStore()

const {
  hasUnsavedChanges,
  isRoleStaffSbc,
  isRoleQualifiedSupplier,
  getMhrTransportPermit,
  getMhrTransportPermitHomeLocation,
  getMhrOriginalTransportPermit,
  getMhrOriginalTransportPermitHomeLocation,
  getMhrInfoValidation,
  getMhrRegistrationLocation
} = storeToRefs(useStore())

const {
  isNewPermitActive,
  setLocationChangeType,
  resetTransportPermit,
  isNotManufacturersLot,
  isAmendLocationActive,
  isValueAmended,
  hasAmendmentChanges,
  isActiveHomeOutsideBc,
  isRegisteredLocationChange,
  getLandStatusConfirmation,
  isExtendChangeLocationActive
} = useTransportPermits()

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
    (isRoleQualifiedSupplier.value || isRoleStaffSbc.value)
      ? locationChangeTypes.slice(0, -3) // remove Registered Location Change and Cancel Permit and Extend from the list
      : locationChangeTypes.slice(0, -2)), // remove Cancel Permit and Extend from the list
  isTransportPermitType: computed(() =>
    getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT),
  isNotManufacturersLot: computed(() => getMhrRegistrationLocation.value.locationType !== HomeLocationTypes.LOT),
  isNotHomePark: computed(() => getMhrRegistrationLocation.value.locationType !== HomeLocationTypes.HOME_PARK),
  isLocationTypeInvalid: computed(() => (props.validate && !getInfoValidation('isHomeLocationTypeValid')) ||
    (props.validate && !isValueAmended('newLocation') && !hasAmendmentChanges.value)),
  isCivicAddressInvalid: computed(() => (props.validate && !getInfoValidation('isHomeCivicAddressValid')) ||
    (props.validate && !isValueAmended('newLocation.address') && !hasAmendmentChanges.value)),
  isLandOwnershipInvalid: computed(() => (props.validate && !getInfoValidation('isHomeLandOwnershipValid')) ||
    (props.validate && !isValueAmended('ownLand') && !hasAmendmentChanges.value)),
  isRoleQSorSBCAmend: computed(() => (isRoleQualifiedSupplier.value || isRoleStaffSbc.value) &&
    isAmendLocationActive.value),
  showChangeTransportPermitLocationTypeDialog: false,
  amendedBadgeHomeLocationType: {
    action: 'AMENDED',
    baseline: getMhrOriginalTransportPermitHomeLocation.value,
    currentState: computed(() => getMhrTransportPermitHomeLocation.value)
  },
  amendedBadgeCivicAddress: {
    action: 'AMENDED',
    baseline: getMhrOriginalTransportPermit.value?.newLocation?.address,
    currentState: computed(() => getMhrTransportPermit.value.newLocation.address)
  },
  amendedBadgeHomeLandOwnership: {
    action: 'AMENDED',
    baseline: getMhrOriginalTransportPermit.value?.ownLand,
    currentState: computed(() => getMhrTransportPermit.value.ownLand)
  },
})

onMounted(async () => {
  await nextTick()
  // reset unsaved flag after data pre-fill of all the components for Amend Location Change
  isAmendLocationActive.value && setUnsavedChanges(false)
})

const handleTaxCertificateUpdate = (date: string) => {
  setMhrTransportPermitNewLocation({ key: 'taxExpiryDate', value: date })
  setMhrTransportPermitNewLocation({ key: 'taxCertificate', value: !!date })
}

const handleLocationTypeUpdate = (newLocation: { key, value }) => {
  if (newLocation.key === 'locationType') {
    const landStatus = getLandStatusConfirmation(newLocation.value)

    setMhrTransportPermit({ key: 'landStatusConfirmation', value: landStatus })
  }

  setMhrTransportPermitNewLocation(newLocation)
}

// disable Location Change Type dropdown list item for certain conditions
const isListItemDisabled = (itemValue: LocationChangeTypes): boolean => {
  return state.isNotHomePark && itemValue === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
}

watch(() => state.locationChangeType, val => {
  setValidation('isLocationChangeTypeValid', !!val)
})

// if Tax Certificate is hidden set the validation for it to true
watch(() => isNotManufacturersLot, val => {
  !val && setValidation('isTaxCertificateValid', true)
}, { immediate: true })

watch(() => props.validate, () => {
  locationChangeSelectRef.value?.validate()
})


const selectLocationType = (item: LocationChangeTypes): void => {
  state.locationChangeType = cloneDeep(item)
  setLocationChangeType(item)
  locationChangeSelectRef.value?.blur()
}

const handleLocationTypeChange = (locationType: LocationChangeTypes) => {
  const currentLocationChangeType = getMhrTransportPermit.value?.locationChangeType

  // if newly selected type is same a current, return and to nothing
  if (currentLocationChangeType === locationType) return

  // check if a Location Type is already selected
  const hasTypeSelected: boolean = !!currentLocationChangeType

  // show dialog if there are unsaved changes
  if (hasUnsavedChanges.value && hasTypeSelected) {
    state.showChangeTransportPermitLocationTypeDialog = true
    return
  }

  // reset permit and validation if changing from a selected type
  // prevents reset for the very first time Location Change dropdown is selected
  if (currentLocationChangeType !== null) {
    resetTransportPermit()
    state.prevLocationChangeType = cloneDeep(currentLocationChangeType ?? null)
    resetValidationState()
  }

  selectLocationType(locationType)
  emit('updateLocationType')
}

const handleChangeTransportPermitLocationTypeResp = (proceed: boolean) => {
  if (proceed) {
    proceedWithLocationTypeChange()
  } else {
    revertToPreviousLocationType()
  }
  // close confirm dialog
  state.showChangeTransportPermitLocationTypeDialog = false
}

const proceedWithLocationTypeChange = () => {
  // change transfer type and reset transport permit
  resetTransportPermit()
  resetValidationState()
  // update location type to new selection
  selectLocationType(cloneDeep(state.locationChangeType))
  // set previous location
  state.prevLocationChangeType = cloneDeep(getMhrTransportPermit.value?.locationChangeType)
  // when changing Location Type update the validation for it after reset
  setValidation('isLocationChangeTypeValid', true)
  // emit location change to reset page validations
  emit('updateLocationType')
}

const revertToPreviousLocationType = () => {
  const previousLocationType = state.prevLocationChangeType || getMhrTransportPermit.value?.locationChangeType
  selectLocationType(previousLocationType);
}

const handleTransportPermitAddressUpdate = (addressField: { key, value }) => {
  // when amending a permit, check if home is leaving BC and update the registration status
  if (isAmendLocationActive.value &&
    addressField.key === 'region' &&
    addressField.value !== '') {
      setMhrStatusType( addressField.value === 'BC' ? MhApiStatusTypes.ACTIVE : MhApiStatusTypes.EXEMPT)
  }
  setMhrTransportPermitNewCivicAddress(addressField)
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.v-overlay {
  .v-list-item {
    line-height: 3em;
  }
  .v-list-item.disabled-item:hover {
    color: unset;
    background-color: $gray1;
  }

  .v-list-item-title.disabled-transport-permit-option {
    font-size: 16px;
    line-height: 3em;
    letter-spacing: 0;
    color: $gray7;
    display: flex;
    justify-content: space-between;

    .disabled-title {
      opacity: 0.6;
    }
  }
}
</style>
