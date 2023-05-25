<template>
  <div id="mhr-home-location">
    <section id="mhr-home-location-type-wrapper" class="mt-10">
      <h2>Location Type</h2>
      <p class="mt-2 mb-6">
        Indicate the type of location for the home.
      </p>

      <HomeLocationType
        :validate="validateLocationType"
        :class="{ 'border-error-left': validateLocationType }"
      />
    </section>

    <section id="mhr-home-civic-address-wrapper" class="mt-10">
      <h2>Civic Address of the Home</h2>
      <p class="mt-2">
        Enter the Street Address (Number and Name) and City of the location of the home. Street Address must be entered
        if there is one. The home must be located in B.C.
      </p>

      <HomeCivicAddress
        :value="getMhrRegistrationLocation.address"
        :validate="validateCivicAddress"
        :class="{ 'border-error-left': validateCivicAddress }"
      />
    </section>
    <section id="mhr-home-land-ownership-wrapper" class="mt-10">
      <h2>Land Details</h2>
      <p class="mt-2">
        Confirm the land lease or ownership information for the home.
      </p>
      <HomeLandOwnership />
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { HomeLocationType, HomeCivicAddress, HomeLandOwnership } from '@/components/mhrRegistration'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'HomeLocation',
  components: {
    HomeLocationType,
    HomeCivicAddress,
    HomeLandOwnership
  },
  props: {},
  setup () {
    const {
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      getSectionValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      validateLocationType: computed((): boolean => {
        return !!getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID)
      }),
      validateCivicAddress: computed((): boolean => {
        return !!getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID)
      })
    })

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
    }

    watch(() => localState, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
      getMhrRegistrationLocation,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#mhr-home-location {
  /* Set "header-counter" to 0 */
  counter-reset: header-counter;
}

h2::before {
  /* Increment "header-counter" by 1 */
  counter-increment: header-counter;
  content: counter(header-counter) '. ';
}
</style>
