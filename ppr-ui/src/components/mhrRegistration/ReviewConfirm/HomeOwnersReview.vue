<template>
  <v-card flat id="home-owners-summary" class="mt-6">
    <header class="review-header">
      <img class="ml-1 home-owners-icon" src="@/assets/svgs/homeownersicon_reviewscreen.svg" />
      <label class="font-weight-bold pl-2">Home Owners</label>
    </header>

    <div :class="{ 'border-error-left': !getStepValidation(MhrSectVal.HOME_OWNERS_VALID) }">
      <section v-show="!getStepValidation(MhrSectVal.HOME_OWNERS_VALID)"
        :class="hasHomeOwners ? 'pt-30px px-6' : 'px-6 py-8'">
        <span>
          <v-icon color="error">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_OWNERS}` }"
          >Return to this step to complete it.</router-link>
        </span>
      </section>

      <section class="px-6 my-2" v-if="hasHomeOwners">
        <article class="border-btm py-5">
          <v-row no-gutters data-test-id="home-tenancy-type">
            <v-col cols="3"><span class="generic-label">Home Tenancy Type </span></v-col>
            <v-col class="pl-2  gray7">{{ getHomeTenancyType() }}</v-col>
          </v-row>
          <v-row no-gutters class="pt-2" v-if="showGroups" data-test-id="total-ownership">
            <v-col cols="3"><span class="generic-label">Total Ownership Allocated </span></v-col>
            <v-col class="pl-2 gray7">{{ getTotalOwnershipAllocationStatus().totalAllocation }}</v-col>
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
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { useHomeOwners, useMhrValidations } from '@/composables/mhrRegistration'

export default defineComponent({
  name: 'HomeOwnersReview',
  components: { HomeOwnersTable },
  props: {
    isMhrTransfer: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { getMhrRegistrationValidationModel } = useStore()

    const { MhrSectVal, getStepValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel))
    const {
      getHomeTenancyType,
      getTotalOwnershipAllocationStatus,
      showGroups,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups
    } = useHomeOwners(props.isMhrTransfer)

    const localState = reactive({
      homeOwners: computed(() => getTransferOrRegistrationHomeOwners()),
      hasHomeOwners: computed(() => !!getTransferOrRegistrationHomeOwners().find(owner => owner.ownerId)),
      hasGroups: computed(() => getTransferOrRegistrationHomeOwnerGroups().length > 0),
      showStepError: computed(() => !getStepValidation(MhrSectVal.HOME_OWNERS_VALID))
    })

    return {
      MhrSectVal,
      getStepValidation,
      RouteNames,
      getHomeTenancyType,
      getTotalOwnershipAllocationStatus,
      showGroups,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
