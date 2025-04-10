<template>
  <div
    id="mhr-home-location"
    class="increment-sections"
  >
    <!-- Correction or Re-Registration Template when Active Transport Permit -->
    <template v-if="(isMhrCorrection || isMhrReRegistration) && hasActiveTransportPermit">
      <section id="mhr-correction-has-active-permit">
        <CautionBox
          class="mt-12"
          set-important-word="Note"
          set-msg="A transport permit has been issued for this home. While the permit is still active, the home’s
            location on the transport permit can be amended from the Manufactured Home Information page."
        />

        <HomeLocationReview
          :hide-default-header="true"
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
          :location-type-info="getMhrRegistrationLocation"
          :validate="getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)"
          :class="{ 'border-error-left': validateLocationType }"
          :updated-badge="(isMhrCorrection || isMhrReRegistration) ? correctionState.location : null"
          @set-store-property="setMhrLocation($event)"
          @is-valid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID, $event)"
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
          :updated-badge="(isMhrCorrection || isMhrReRegistration) ? correctionState.civicAddress : null"
          @set-store-property="setCivicAddress('mhrRegistration', $event)"
          @is-valid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID, $event)"
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
          :own-land="getMhrRegistrationOwnLand"
          :validate="validateLandDetails"
          :class="{ 'border-error-left': validateLandDetails }"
          :content="{
            description: 'Is the manufactured home located on land that the homeowners own or on ' +
              'land that they have a registered lease of 3 years or more?'
          }"
          :updated-badge="(isMhrCorrection || isMhrReRegistration) ? correctionState.landDetails : null"
          @set-store-property="setMhrRegistrationOwnLand($event)"
          @is-valid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LAND_DETAILS_VALID, $event)"
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
import {
  HomeLocationType,
  HomeCivicAddress,
  HomeLandOwnership ,
  HomeLocationReview
} from '@/components/mhrRegistration'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { useMhrCorrections, useTransportPermits } from '@/composables'
import { CautionBox } from '@/components/common'

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
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel,
      getMhrRegistrationOwnLand,
      isMhrReRegistration
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      getValidation,
      getSectionValidation,
      scrollToInvalid,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { correctionState, isMhrCorrection } = useMhrCorrections()
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
      })
    })

    onMounted(() => {
      // Override validation for MhrCorrections: Active Transport Permit disables corrections and components are hidden
      if ((isMhrCorrection.value || isMhrReRegistration.value) && hasActiveTransportPermit.value) {
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
      correctionState,
      isMhrCorrection,
      isMhrReRegistration,
      hasActiveTransportPermit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
