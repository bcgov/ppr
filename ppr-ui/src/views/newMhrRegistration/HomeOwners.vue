<template>
  <div id="mhr-home-owners-list">
    <section id="mhr-owners" class="mt-10">
      <h2>1. Owners</h2>
      <p class="mt-2 mb-0">
        Add a person or an organization as the owner of the home. You can add
        multiple owners to form joint tenancy or tenants in common ownership.
        Note: Tenants in common ownership requires more than one group of
        owners.
      </p>

      <SimpleHelpToggle toggleButtonTitle="Help with Owners" class="my-6">
        <h3 class="text-center mb-2">Help with Owners</h3>
        <h4>Sole Ownership</h4>
        <p>
          This applies when the home is owned by a single individual or
          organization.
        </p>
        <h4>Joint Tenancy</h4>
        <p>
          This applies when the home is jointly owned by a number of individuals
          or organizations or some combination of the two.
        </p>
        <h4>Tenants in Common</h4>
        <p>
          This applies when the home is owned by a number of groups or
          individuals or organizations or some combination of the two (where a
          group could consist of a single owner) and each group of owners has
          the right to dispose of their share independent of the other owner
          groups and will be disposed of as part of the estate in the case of a
          death.
        </p>
        <p>
          Each group will hold a certain share of the home. To record this it is
          necessary to express this as some number of a total number of equal
          shares. For example if the home is owned by two owner groups each of
          whom owns half of the home this can be seen as each group holding 1 of
          2 shares. If the home is owned by two groups but one holds two thirds
          and one holds the other third this can be expressed as the first
          holding 2 of 3 shares and the second holding 1 of 3 shares.
        </p>
        <p>
          The total number of shares in a home must be entered when the number
          of owner groups is entered. Then the number of shares each group owns
          can be entered when the details of each group are gathered.
        </p>
        <p>
          If your tenancy structure cannot be accommodated by the online system
          please contact the Manufactured Home Registry.
        </p>
      </SimpleHelpToggle>

      <label class="generic-label">
        Your registration must include the following:
      </label>
      <div class="mt-5 mb-11 reg-owners-check">
        <v-icon
          v-if="getMhrRegistrationHomeOwners.length > 0"
          color="green darken-2"
        >
          mdi-check
        </v-icon>
        <v-icon v-else color="black">mdi-circle-small</v-icon>
        <span class="ml-1">At least one owner</span>
      </div>
      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="isGlobalEditingMode"
        @click="showAddPersonSection = true"
        data-test-id="add-person-btn"
      >
        <v-icon class="pr-1">mdi-account-plus</v-icon> Add a Person
      </v-btn>

      <span class="mx-2"></span>

      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="isGlobalEditingMode"
        @click="showAddPersonOrganizationSection = true"
        data-test-id="add-org-btn"
      >
        <v-icon class="pr-1">mdi-domain-plus</v-icon>
        Add a Business or Organization
      </v-btn>
      <div class="my-6">
        <div><span class="generic-label">Home Tenancy Type: </span>{{ homeTenancyType }}
          <span v-show="showGroups">
              <span v-show="ownershipAllocation.hasMinimumGroupsError" class="error-text fs-14 ml-3"
              >Must include more than one group of owners
              </span>
          </span>
        </div>
        <div v-show="showGroups">
          <span class="generic-label">Total Ownership Allocated:</span><span> {{ interestType }} </span>{{ ownershipAllocation.totalAllocation }}
          <span v-show="ownershipAllocation.hasTotalAllocationError" class="error-text fs-14 ml-3"
            >Total ownership must equal 1/1</span
          >
        </div>
      </div>
    </section>

    <v-expand-transition>
      <AddEditHomeOwner
        v-if="showAddPersonSection"
        :isHomeOwnerPerson="true"
        @done="addHomeOwner($event)"
        @cancel="showAddPersonSection = false"
      />
    </v-expand-transition>

    <v-expand-transition>
      <AddEditHomeOwner
        v-if="showAddPersonOrganizationSection"
        @done="addHomeOwner($event)"
        @cancel="showAddPersonOrganizationSection = false"
      />
    </v-expand-transition>

    <div>
      <HomeOwnersTable
        :homeOwners="getMhrRegistrationHomeOwners"
        :isAdding="disableAddHomeOwnerBtn"
        @edit="editHomeOwner($event)"
        @remove="removeHomeOwner($event)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { useActions, useGetters } from 'vuex-composition-helpers'
import {
  AddEditHomeOwner,
  HomeOwnersTable
} from '@/components/mhrRegistration/HomeOwners'

import { SimpleHelpToggle } from '@/components/common'
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useHomeOwners } from '@/composables/mhrRegistration'
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnersIF, MhrRegistrationTotalOwnershipAllocationIF } from '@/interfaces'
import { HomeTenancyTypes } from '@/enums'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeOwners',
  components: {
    SimpleHelpToggle,
    AddEditHomeOwner,
    HomeOwnersTable
  },
  setup () {
    const { getMhrRegistrationHomeOwners } = useGetters<any>([
      'getMhrRegistrationHomeOwners'
    ])

    const { setMhrRegistrationHomeOwners } = useActions<any>([
      'setMhrRegistrationHomeOwners'
    ])

    const {
      getHomeTenancyType,
      setGlobalEditingMode,
      isGlobalEditingMode,
      showGroups,
      getTotalOwnershipAllocationStatus,
      hasMinimumGroups,
      getInterestString
    } = useHomeOwners()

    const localState = reactive({
      showAddPersonSection: false,
      showAddPersonOrganizationSection: false,
      disableAddHomeOwnerBtn: computed(() => {
        return localState.showAddPersonOrganizationSection || localState.showAddPersonSection
      }),
      ownershipAllocation: computed(
        () => getTotalOwnershipAllocationStatus() as MhrRegistrationTotalOwnershipAllocationIF
      ),
      isValidGroups: computed(() => { return hasMinimumGroups() }),
      homeTenancyType: computed(() => { return getHomeTenancyType() }),
      interestType: computed(() => { return getInterestString() })
    })

    // Enable editing mode whenever adding Person or Business
    // This would disabled all Edit buttons
    watch(
      () => localState.disableAddHomeOwnerBtn,
      (isAdding: Boolean) => {
        setGlobalEditingMode(isAdding)
      }
    )

    const addHomeOwner = (owner: MhrRegistrationHomeOwnersIF) => {
      const homeOwners = [...getMhrRegistrationHomeOwners.value]
      homeOwners.push(owner)
      setMhrRegistrationHomeOwners(homeOwners)
    }

    const editHomeOwner = (owner: MhrRegistrationHomeOwnersIF) => {
      const homeOwners = [...getMhrRegistrationHomeOwners.value]
      const { id, ...editedOwner } = owner
      homeOwners[owner.id] = editedOwner
      setMhrRegistrationHomeOwners(homeOwners)
    }

    const removeHomeOwner = (owner: MhrRegistrationHomeOwnersIF) => {
      const homeOwners = [...getMhrRegistrationHomeOwners.value]
      homeOwners.splice(homeOwners.indexOf(owner), 1)
      setMhrRegistrationHomeOwners(homeOwners)
    }

    return {
      getMhrRegistrationHomeOwners,
      isGlobalEditingMode,
      addHomeOwner,
      editHomeOwner,
      removeHomeOwner,
      getHomeTenancyType,
      getInterestString,
      showGroups,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.reg-owners-check::v-deep {
  i {
    vertical-align: baseline;
  }
  span {
    vertical-align: text-bottom;
  }
}
</style>
