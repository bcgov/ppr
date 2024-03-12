<template>
  <v-card
    id="home-owners-summary"
    flat
    class="mt-10"
  >
    <header class="review-header">
      <img
        class="ml-1 home-owners-icon"
        alt="home-owners-review-icon"
        src="@/assets/svgs/homeownersicon_reviewscreen.svg"
      >
      <label class="font-weight-bold pl-2">Home Owners</label>
    </header>

    <div :class="{ 'border-error-left': showStepError }">
      <section
        v-show="showStepError"
        class="pa-6"
      >
        <span>
          <v-icon color="error mt-n1">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_OWNERS}` }"
          ><span>Return to this step to complete it.</span></router-link>
        </span>
      </section>

      <section
        v-if="hasHomeOwners"
        class="px-8 my-2"
      >
        <article class="border-btm py-5">
          <v-row
            noGutters
            data-test-id="home-tenancy-type"
          >
            <v-col cols="3">
              <span class="generic-label">Home Tenancy Type </span>
            </v-col>
            <v-col class="pl-1  gray7">
              {{ getHomeTenancyType() }}
            </v-col>
            <v-col>
              <span
                v-if="isMhrCorrection && hasRemovedOwners"
                class="float-right hide-show-owners fs-14"
                @click="hideShowRemovedOwners()"
              >
                <v-icon
                  class="hide-show-owners-icon pr-1"
                  color="primary"
                >
                  {{ hideRemovedOwners ? 'mdi-eye' : 'mdi-eye-off' }}
                </v-icon>
                {{ hideRemovedOwners ? 'Show' : 'Hide' }} Deleted Owners
              </span>
            </v-col>
          </v-row>
          <v-row
            v-if="showGroups && ![HomeTenancyTypes.SOLE, HomeTenancyTypes.JOINT].includes(getHomeTenancyType())"
            noGutters
            class="pt-2"
            data-test-id="total-ownership"
          >
            <v-col cols="3">
              <span class="generic-label">Total Ownership Allocated </span>
            </v-col>
            <v-col class="pl-1 gray7">
              {{ getTotalOwnershipAllocationStatus.totalAllocation }}
            </v-col>
          </v-row>
        </article>

        <HomeOwnersTable
          isReadonlyTable
          :showChips="isMhrCorrection"
          :isMhrTransfer="isMhrTransfer"
          :homeOwnerGroups="hideRemovedOwners ? filteredHomeOwnersGroups : getHomeOwnerGroups"
          class="readonly-home-owners-table px-0 py-3"
        />
      </section>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { ActionTypes, HomeTenancyTypes, RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { useHomeOwners, useMhrCorrections, useMhrValidations } from '@/composables/mhrRegistration'
import { storeToRefs } from 'pinia'

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
    const { getMhrRegistrationValidationModel, isMhrManufacturerRegistration } = storeToRefs(useStore())
    const { isMhrCorrection } = useMhrCorrections()
    const { MhrSectVal, getStepValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const {
      getHomeTenancyType,
      getTotalOwnershipAllocationStatus,
      showGroups,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups
    } = useHomeOwners(props.isMhrTransfer, isMhrCorrection.value)

    const localState = reactive({
      hideRemovedOwners: false,
      filteredHomeOwnersGroups: [],
      getHomeOwnerGroups: computed(() => getTransferOrRegistrationHomeOwnerGroups()),
      hasHomeOwners: computed(() => !!getTransferOrRegistrationHomeOwners().find(owner => owner.ownerId)),
      hasGroups: computed(() => getTransferOrRegistrationHomeOwnerGroups().length > 0),
      showStepError: computed(() => {
        return !props.isMhrTransfer && !isMhrManufacturerRegistration.value &&
          !getStepValidation(MhrSectVal.HOME_OWNERS_VALID)
      }),
      hasRemovedOwners: computed(() => {
        return localState.getHomeOwnerGroups?.some(group => group.action === ActionTypes.REMOVED)
      }),
    })

    const hideShowRemovedOwners = (): void => {
      localState.hideRemovedOwners = !localState.hideRemovedOwners
      if (localState.hideRemovedOwners) filterDisplayedHomeOwners()
    }

    const filterDisplayedHomeOwners = (): void => {
      localState.filteredHomeOwnersGroups = []
      localState.getHomeOwnerGroups?.forEach(ownerGroup => {
        if (ownerGroup.action !== ActionTypes.REMOVED) {
          const owners = ownerGroup.owners
            .map(owner => {
              if (owner.action === ActionTypes.REMOVED) return { groupId: ownerGroup.groupId }
              else return { ...owner, groupId: ownerGroup.groupId }
            })
          localState.filteredHomeOwnersGroups.push({ ...ownerGroup, owners })
        }
      })
    }

    return {
      MhrSectVal,
      getStepValidation,
      RouteNames,
      getHomeTenancyType,
      isMhrCorrection,
      getTotalOwnershipAllocationStatus,
      showGroups,
      hideShowRemovedOwners,
      ...toRefs(localState)
    }
  },
  computed: {
    HomeTenancyTypes () {
      return HomeTenancyTypes
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.hide-show-owners {
  color: $primary-blue !important;
  &:hover {
    cursor: pointer;
  }
  .hide-show-owners-icon {
    font-size: 20px;
  }
}
</style>
