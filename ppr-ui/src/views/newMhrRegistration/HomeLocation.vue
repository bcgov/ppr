<template>
  <div
    id="mhr-home-location"
    class="increment-sections"
  >
    <!-- Correction Template when Active Transport Permit -->
    <template v-if="isMhrCorrection && hasActiveTransportPermit">
      <section id="mhr-correction-has-active-permit">
        <CautionBox
          class="mt-12"
          setImportantWord="Note"
          setMsg="A transport permit has been issued for this home. While the permit is still active, the home’s
            location on the transport permit can be amended from the Manufactured Home Information page."
        />

        <HomeLocationReview
          :hideDefaultHeader="true"
          class="mt-10"
        />
      </section>
    </template>

    <!-- Standard MHR Home Location Components -->
    <template v-else>
      <section
        id="mhr-home-location-type-wrapper"
        class="mt-10"
      >
        <h2>Location Type</h2>
        <p class="mt-2 mb-6">
          Indicate the type of location for the home.
        </p>

        <HomeLocationType
          :locationTypeInfo="getMhrRegistrationLocation"
          :validate="getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)"
          :class="{ 'border-error-left': validateLocationType }"
          :updatedBadge="isMhrCorrection ? homeLocationCorrection : null"
          @setStoreProperty="setMhrLocation($event)"
          @isValid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID, $event)"
        />
      </section>

      <section
        id="mhr-home-civic-address-wrapper"
        class="mt-10"
      >
        <h2>Civic Address of the Home</h2>
        <p class="mt-2">
          Enter the Street Address (Number and Name) and City of the location of the home. Street Address must be
          entered if there is one.
        </p>

        <HomeCivicAddress
          :value="getMhrRegistrationLocation.address"
          :schema="CivicAddressSchema"
          :validate="validateCivicAddress"
          :class="{ 'border-error-left': validateCivicAddress }"
          :updatedBadge="isMhrCorrection ? civicAddressCorrection : null"
          @setStoreProperty="setCivicAddress('mhrRegistration', $event)"
          @isValid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, $event)"
        />
      </section>

      <section
        id="mhr-home-land-ownership-wrapper"
        class="mt-10"
      >
        <h2>Land Details</h2>
        <p class="mt-2">
          Confirm the land lease or ownership information for the home.
        </p>

        <HomeLandOwnership
          :ownLand="getMhrRegistrationOwnLand"
          :validate="validateLandDetails"
          :class="{ 'border-error-left': validateLandDetails }"
          :content="{
            description: 'Is the manufactured home located on land that the homeowners own or on ' +
              'land that they have a registered lease of 3 years or more?'
          }"
          :updatedBadge="isMhrCorrection ? landDetailsCorrection : null"
          @setStoreProperty="setMhrRegistrationOwnLand($event)"
          @isValid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LAND_DETAILS_VALID, $event)"
        />
      </section>
    </template>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { HomeLocationType, HomeCivicAddress, HomeLandOwnership } from '@/components/mhrRegistration'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { HomeLocationReview } from '@/components/mhrRegistration'
import { useMhrCorrections, useTransportPermits } from '@/composables'
import { CautionBox } from '@/components/common'
import { UpdatedBadgeIF } from '@/interfaces'

export default defineComponent({
  name: 'HomeLocation',
  components: {
    CautionBox,
    HomeLocationReview,
    HomeLocationType,
    HomeCivicAddress,
    HomeLandOwnership
  },
  setup () {

    const { setMhrRegistrationOwnLand, setMhrLocation, setCivicAddress } = useStore()

    const {
      getMhrBaseline,
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel,
      getMhrRegistrationOwnLand
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      getValidation,
      getSectionValidation,
      scrollToInvalid,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { isMhrCorrection } = useMhrCorrections()
    const { hasActiveTransportPermit } = useTransportPermits()

    const localState = reactive({
      validateLocationType: computed((): boolean => {
        return !!getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID)
      }),
      validateCivicAddress: computed((): boolean => {
        return !!getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID)
      }),
      validateLandDetails: computed((): boolean => {
        return !!getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LAND_DETAILS_VALID)
      }),
      homeLocationCorrection: computed((): UpdatedBadgeIF => {
        return {
          baseline: { ...getMhrBaseline.value?.location, address: null },
          currentState: { ...getMhrRegistrationLocation.value, address: null }
        }
      }),
      civicAddressCorrection: computed((): UpdatedBadgeIF => {
        return {
          baseline: getMhrBaseline.value?.location.address,
          currentState: getMhrRegistrationLocation.value.address
        }
      }),
      landDetailsCorrection: computed((): UpdatedBadgeIF => {
        return {
          baseline: getMhrBaseline.value?.ownLand,
          currentState: getMhrRegistrationOwnLand.value
        }
      })
    })

    onMounted(() => {
      // Override validation for MhrCorrections: Active Transport Permit disables corrections and components are hidden
      if (isMhrCorrection.value && hasActiveTransportPermit.value) {
        setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID, true)
        setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, true)
        setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LAND_DETAILS_VALID, true)
      }
    })

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
    }

    watch(() => localState, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
      MhrCompVal,
      MhrSectVal,
      getValidation,
      setValidation,
      setMhrLocation,
      setCivicAddress,
      getMhrRegistrationLocation,
      getMhrRegistrationOwnLand,
      setMhrRegistrationOwnLand,
      CivicAddressSchema,
      isMhrCorrection,
      hasActiveTransportPermit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
