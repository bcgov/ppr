<template>
  <v-card flat id="home-owners-summary" class="mt-6">
    <header class="review-header">
      <v-icon class="ml-1" color="darkBlue">mdi-home</v-icon>
      <label class="font-weight-bold pl-2">Home Owners</label>
    </header>

    <div :class="{ 'border-error-left': !getStepValidation(MhrSectVal.HOME_OWNERS_VALID) }">
      <div v-show="!getStepValidation(MhrSectVal.HOME_OWNERS_VALID)" class="px-6 py-8">
        <v-icon color="error">mdi-information-outline</v-icon>
        <span class="error-text mx-1">This step is unfinished.</span>
        <router-link :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_OWNERS}` }"
          >Return to this step to complete it.
        </router-link>
      </div>
      <section class="px-6 my-2" v-if="hasHomeOwners">
        <article class="border-btm py-5">
          <v-row no-gutters>
            <v-col cols="3"><span class="generic-label">Home Tenancy Type </span></v-col>
            <v-col class="pl-2">{{ getHomeTenancyType() || 'N/A' }}</v-col>
          </v-row>
          <v-row no-gutters class="pt-2">
            <v-col cols="3"><span class="generic-label">Total Ownership <br>Allocated </span></v-col>
            <v-col class="pl-2">{{ getTotalOwnershipAllocationStatus().totalAllocation || 'N/A' }}</v-col>
          </v-row>
        </article>

        <HomeOwnersTable
          :homeOwners="homeOwners"
          isReadonlyTable
          class="readonly-home-owners-table px-0 py-3"
        />
      </section>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { useHomeOwners, useMhrValidations } from '@/composables/mhrRegistration'

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
    const {
      getHomeTenancyType,
      getTotalOwnershipAllocationStatus
    } = useHomeOwners()

    const localState = reactive({
      homeOwners: computed(() => getMhrRegistrationHomeOwners.value),
      hasHomeOwners: computed(() => localState.homeOwners.length > 0),
      showStepError: computed(() => !getStepValidation(MhrSectVal.HOME_OWNERS_VALID))
    })

    return {
      MhrSectVal,
      getStepValidation,
      RouteNames,
      getHomeTenancyType,
      getTotalOwnershipAllocationStatus,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
