<template>
  <v-card flat id="home-owners-summary" class="mt-6">
    <header class="review-header">
      <v-icon class="ml-2" color="darkBlue">mdi-home</v-icon>
      <label class="font-weight-bold pl-2">Home Owners</label>
    </header>

    <div v-if="hasHomeOwners">
      <HomeOwnersTable :homeOwners="homeOwners" />
    </div>
    <div v-else class="px-6 py-8" :class="{ 'border-error-left': !getStepValidation(MhrSectVal.HOME_OWNERS_VALID) }">
      <v-icon color="error">mdi-information-outline</v-icon>
      <span class="error-text mx-1">This step is unfinished.</span>
      <router-link :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_OWNERS}` }"
        >Return to this step to complete it.
      </router-link>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { useMhrValidations } from '@/composables/mhrRegistration'

export default defineComponent({
  name: 'HomeOwnersReview',
  components: { HomeOwnersTable },
  // eslint-disable-next-line
  setup() {
    const { getMhrRegistrationHomeOwners, getMhrRegistrationValidationModel } = useGetters<any>([
      'getMhrRegistrationHomeOwners',
      'getMhrRegistrationValidationModel'
    ])

    const { MhrSectVal, getStepValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      homeOwners: computed(() => getMhrRegistrationHomeOwners.value),
      hasHomeOwners: computed(() => localState.homeOwners.length > 0)
    })

    return {
      MhrSectVal,
      getStepValidation,
      RouteNames,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.review-header {
  display: flex; // to align icons
  background-color: $BCgovBlue5O;
  padding: 1.25rem;
  color: $gray9;
}
</style>
