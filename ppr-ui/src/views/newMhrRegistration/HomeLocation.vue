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
        Enter the Street Address (Number and Name) and City for the location of the home. Must be located in B.C.
      </p>

      <HomeCivicAddress
        :validate="validateCivicAddress"
        :class="{ 'border-error-left': validateCivicAddress }"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { HomeLocationType, HomeCivicAddress } from '@/components/mhrRegistration'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'

export default defineComponent({
  name: 'HomeLocation',
  components: {
    HomeLocationType,
    HomeCivicAddress
  },
  props: {},
  setup () {
    const {
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationValidationModel'
    ])

    const {
      MhrCompVal,
      MhrSectVal,
      getSectionValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      validateLocationType: computed(() => {
        return getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LOCATION_TYPE_VALID)
      }),
      validateCivicAddress: computed(() => {
        return getSectionValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.CIVIC_ADDRESS_VALID)
      })
    })

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
    }

    watch(() => localState, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
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
