<template>
  <div
    id="mhr-home-location"
    class="increment-sections"
  >
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
        :validate="validateLocationType"
        :class="{ 'border-error-left': validateLocationType }"
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
        Enter the Street Address (Number and Name) and City of the location of the home. Street Address must be entered
        if there is one.
      </p>

      <HomeCivicAddress
        :value="getMhrRegistrationLocation.address"
        :schema="CivicAddressSchema"
        :validate="validateCivicAddress"
        :class="{ 'border-error-left': validateCivicAddress }"
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
        @setStoreProperty="setMhrRegistrationOwnLand($event)"
        @isValid="setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LAND_DETAILS_VALID, $event)"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { HomeLocationType, HomeCivicAddress, HomeLandOwnership } from '@/components/mhrRegistration'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'

export default defineComponent({
  name: 'HomeLocation',
  components: {
    HomeLocationType,
    HomeCivicAddress,
    HomeLandOwnership
  },
  setup () {

    const { setMhrRegistrationOwnLand } = useStore()

    const {
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel,
      getMhrRegistrationOwnLand
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      getSectionValidation,
      scrollToInvalid,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

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

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
    }

    watch(() => localState, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      setMhrLocation,
      getMhrRegistrationLocation,
      getMhrRegistrationOwnLand,
      setMhrRegistrationOwnLand,
      CivicAddressSchema,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
