<template>
  <div id="mhr-home-owners-list">
    <BaseDialog
      :setDisplay="showDeleteAllGroupsDialog"
      @proceed="cancelOrProceed($event)"
      :setOptions="{
        title: 'Delete All Owners/Groups',
        text:
          'Deleting all owners/groups will delete all previous owners and remove any newly added owners.',
        acceptText: 'Delete All Owners/Groups',
        cancelText: 'Cancel'
      }"
    />
    <section id="mhr-owners" class="mt-10">
      <template v-if="!isMhrTransfer">
        <h2>1. Owners</h2>
        <p class="mt-2 mb-0">
          Add a person or an organization as the owner of the home. You can add
          multiple owners to form joint tenancy or tenants in common ownership.
          Note: Tenants in common ownership requires more than one group of
          owners.
        </p>

        <SimpleHelpToggle toggleButtonTitle="Help with Owners" class="my-6">
          <h3 class="text-center mb-2">Help with Owners</h3>
          <h4>Sole Owner</h4>
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
            v-if="hasHomeOwners"
            color="green darken-2"
            data-test-id="reg-owner-checkmark"
          >
            mdi-check
          </v-icon>
          <v-icon v-else color="black">mdi-circle-small</v-icon>
          <span class="ml-1">At least one owner</span>
        </div>
      </template>

      <!-- Add/Remove Owner Actions -->
      <v-row no-gutters v-if="!isReadonlyTable && enableAddHomeOwners()">
        <v-col cols="12">
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

          <span class="mx-2"></span>

          <v-btn
            v-if="isMhrTransfer"
            outlined
            color="primary"
            :ripple="false"
            :disabled="isGlobalEditingMode"
            class="float-right"
            @click="removeAllOwnersHandler()"
            data-test-id="remove-all-owners-btn"
          >
            <v-icon class="pr-1">mdi-delete</v-icon>
            Delete All Owners/Groups
          </v-btn>
        </v-col>
        <v-col cols="9" class="mb-n6 pa-0"></v-col> <!-- Column Spacer -->
        <v-col cols="3" class="mb-n6 pa-0">
          <v-fade-transition>
            <span v-show="showRemovedAllOwnersMsg" class="error-text fs-12 ml-5">Nothing to delete</span>
          </v-fade-transition>
        </v-col>
      </v-row>

      <v-row v-if="!isReadonlyTable" class="my-6" no-gutters>
        <v-col cols="12">
          <span class="generic-label">Home Tenancy Type: </span>
          <span data-test-id="home-owner-tenancy-type">{{ homeTenancyType }}</span>
          <span
            v-show="showTenancyTypeError"
            class="error-text fs-14 ml-3"
          >
            Must include more than one group of owners
          </span>
          <span
            v-if="hasRemovedOwners && !showTotalOwnership"
            class="float-right hide-show-owners fs-14"
            @click="hideShowRemovedOwners()"
          >
            <v-icon v-if="hideRemovedOwners" class="hide-show-owners-icon pr-1" color="primary">mdi-eye</v-icon>
            <v-icon v-else class="hide-show-owners-icon pr-1" color="primary">mdi-eye-off</v-icon>
            {{ hideShowRemovedOwnersLabel }} Deleted Owners
          </span>
        </v-col>
        <v-col
          v-show="showTotalOwnership"
          cols="12"
        >
          <!-- Ownership Allocation Information -->
          <span class="generic-label">Total Ownership Allocated:</span> {{ ownershipTotalAllocation }}
          <span v-if="hasUndefinedGroups" class="error-text fs-14 ml-2">
              No ownership allocated
            </span>
          <span v-else-if="ownershipAllocation.hasTotalAllocationError" class="error-text fs-14 ml-2">
              {{ ownershipAllocation.allocationErrorMsg }}
            </span>
          <!-- Success when allocation is whole -->
          <span v-else><v-icon color="success" class="mt-n2">mdi-check</v-icon></span>

          <!-- Toggle removed owners -->
          <span
            v-if="isMhrTransfer && hasRemovedOwners"
            class="float-right hide-show-owners fs-14"
            @click="hideShowRemovedOwners()"
          >
            <v-icon v-if="hideRemovedOwners" class="hide-show-owners-icon pr-1" color="primary">mdi-eye</v-icon>
            <v-icon v-else class="hide-show-owners-icon pr-1" color="primary">mdi-eye-off</v-icon>
            {{ hideShowRemovedOwnersLabel }} Deleted Owners
          </span>
        </v-col>
        <v-col v-if="changesRequired" class="mt-3">
          <span class="error-text fs-14">Change of ownership is required</span>
        </v-col>
      </v-row>

      <!-- Read Only Template -->
      <v-card v-else class="review-table" flat id="read-only-owners">

        <!-- Transfer Type Review -->
        <template v-if="isMhrTransfer">
          <v-row id="transfer-type-review" class="mt-6 px-7 pt-8" no-gutters>
            <v-col cols="3">
              <label class="generic-label">Transfer Type</label>
            </v-col>
            <v-col cols="9" class="gray7" id="transfer-type-display">{{ getUiTransferType() }}</v-col>
          </v-row>
          <v-row class="my-4 px-7" no-gutters>
            <v-col cols="3">
              <label class="generic-label">Declared Value of Home</label>
            </v-col>
            <v-col cols="9" class="gray7" id="declared-value-display">${{ getMhrTransferDeclaredValue }}.00</v-col>
          </v-row>
          <v-divider class="my-6 mx-7" />
        </template>

        <v-row class="my-4 px-7" no-gutters>
          <v-col cols="12">
            <span class="generic-label">Home Owners </span>
            <span
              v-if="isMhrTransfer && hasRemovedOwners"
              class="float-right hide-show-owners fs-14"
              @click="hideShowRemovedOwners()"
            >
            <v-icon class="hide-show-owners-icon pr-1" color="primary">
              {{ hideRemovedOwners ? 'mdi-eye' : 'mdi-eye-off' }}
            </v-icon>
              {{ hideShowRemovedOwnersLabel }} Deleted Owners
            </span>
          </v-col>
        </v-row>
        <v-row class="my-4 px-7" no-gutters>
          <v-col cols="3">
            <span class="generic-label">Home Tenancy Type</span>
          </v-col>
          <v-col cols="9">
            <span data-test-id="home-owner-tenancy-type">{{ homeTenancyType }}</span>
          </v-col>
        </v-row>
        <HomeOwnersTable
          class="px-7"
          showChips
          :homeOwners="hideRemovedOwners ? filteredHomeOwners : getHomeOwners"
          :isAdding="disableAddHomeOwnerBtn"
          :isMhrTransfer="isMhrTransfer"
          :isReadonlyTable="isReadonlyTable"
          :hideRemovedOwners="hideRemovedOwners"
        />
      </v-card>
    </section>

    <v-expand-transition>
      <AddEditHomeOwner
        v-if="showAddPersonSection"
        :isHomeOwnerPerson="true"
        :isMhrTransfer="isMhrTransfer"
        :showTableError="validateTransfer && isGlobalEditingMode"
        @cancel="showAddPersonSection = false"
      />
    </v-expand-transition>

    <v-expand-transition>
      <AddEditHomeOwner
        v-if="showAddPersonOrganizationSection"
        :isMhrTransfer="isMhrTransfer"
        :showTableError="validateTransfer && isGlobalEditingMode"
        @cancel="showAddPersonOrganizationSection = false"
      />
    </v-expand-transition>

    <div v-if="!isReadonlyTable">
      <v-fade-transition>
        <HomeOwnersTable
          :homeOwners="hideRemovedOwners ? filteredHomeOwners : getHomeOwners"
          :isAdding="disableAddHomeOwnerBtn"
          :isMhrTransfer="isMhrTransfer"
          :hideRemovedOwners="hideRemovedOwners"
          :validateTransfer="validateTransfer"
          @isValidTransferOwners="isValidTransferOwners($event)"
        />
      </v-fade-transition>
    </div>
  </div>
</template>

<script lang="ts">
import { useGetters } from 'vuex-composition-helpers'
import { AddEditHomeOwner, HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { BaseDialog } from '@/components/dialogs'
import { SimpleHelpToggle } from '@/components/common'
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from '@vue/composition-api'
import { useHomeOwners, useMhrValidations, useMhrInformation, useTransferOwners } from '@/composables'
/* eslint-disable no-unused-vars */
import { MhrRegistrationTotalOwnershipAllocationIF } from '@/interfaces'
import { ActionTypes } from '@/enums'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeOwners',
  emits: ['isValidTransferOwners'],
  components: {
    AddEditHomeOwner,
    BaseDialog,
    HomeOwnersTable,
    SimpleHelpToggle
  },
  props: {
    isMhrTransfer: {
      type: Boolean,
      default: false
    },
    isReadonlyTable: {
      type: Boolean,
      default: false
    },
    validateTransfer: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getMhrRegistrationHomeOwners,
      getMhrTransferCurrentHomeOwnerGroups,
      getMhrRegistrationValidationModel,
      hasUnsavedChanges,
      getMhrTransferDeclaredValue
    } = useGetters<any>([
      'getMhrRegistrationHomeOwners',
      'getMhrTransferCurrentHomeOwnerGroups',
      'getMhrRegistrationValidationModel',
      'hasUnsavedChanges',
      'getMhrTransferDeclaredValue'
    ])

    const {
      getUiTransferType
    } = useMhrInformation()

    const {
      enableHomeOwnerChanges,
      enableAddHomeOwners,
      isTransferDueToDeath
    } = useTransferOwners(!props.isMhrTransfer)

    const {
      getValidation,
      MhrSectVal,
      MhrCompVal
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const {
      getHomeTenancyType,
      setGlobalEditingMode,
      isGlobalEditingMode,
      showGroups,
      getTotalOwnershipAllocationStatus,
      hasMinimumGroups,
      setShowGroups,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups,
      markGroupForRemoval,
      hasRemovedAllHomeOwners,
      hasUndefinedGroupInterest
    } = useHomeOwners(props.isMhrTransfer)

    const localState = reactive({
      showAddPersonSection: false,
      showAddPersonOrganizationSection: false,
      showDeleteAllGroupsDialog: false,
      showRemovedAllOwnersMsg: false,
      hideRemovedOwners: false,
      filteredHomeOwners: [],
      disableAddHomeOwnerBtn: computed(
        () => localState.showAddPersonOrganizationSection || localState.showAddPersonSection
      ),
      ownershipAllocation: computed((): MhrRegistrationTotalOwnershipAllocationIF => {
        return getTotalOwnershipAllocationStatus()
      }),
      ownershipTotalAllocation: computed((): string => {
        return localState.hasUndefinedGroups ? 'N/A' : localState.ownershipAllocation.totalAllocation
      }),
      showTotalOwnership: computed(() => {
        return showGroups.value &&
          (
            !hasRemovedAllHomeOwners(localState.getHomeOwners.filter(owner => owner.action !== ActionTypes.ADDED)) ||
            localState.hasMultipleAddedGroups ||
            localState.hasSingleInvalidGroup
          )
      }),
      hasHomeOwners: computed(() => !!getTransferOrRegistrationHomeOwners().find(owner => owner.ownerId)),
      hasReviewedOwners: computed((): boolean =>
        getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)),
      isValidGroups: computed(() => { return hasMinimumGroups() }),
      homeTenancyType: computed(() => { return getHomeTenancyType() }),
      getHomeOwners: computed(() => { return getTransferOrRegistrationHomeOwners() }),
      hasRemovedOwners: computed(() => {
        return localState.getHomeOwners.filter(ownerGroup => ownerGroup.action === ActionTypes.REMOVED).length > 0
      }),
      hasRemovedAllOwners: computed(() => { return hasRemovedAllHomeOwners(localState.getHomeOwners) }),
      hideShowRemovedOwnersLabel: computed(() => { return localState.hideRemovedOwners ? 'Show' : 'Hide' }),
      hasMultipleAddedGroups: computed(() => {
        return getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action === ActionTypes.ADDED).length > 1
      }),
      hasSingleInvalidGroup: computed(() => {
        const group = getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)
        return !!group[0]?.interestNumerator && !!group[0]?.interestDenominator
      }),
      showHideOwnersBtn: computed(() => {
        return props.isMhrTransfer &&
          localState.hasRemovedOwners &&
          (!showGroups || localState.hasRemovedAllOwners) &&
          !localState.hasMultipleAddedGroups &&
          !localState.hasSingleInvalidGroup
      }),
      hasUndefinedGroups: computed((): boolean => {
        return hasUndefinedGroupInterest(getTransferOrRegistrationHomeOwnerGroups()) &&
          getTransferOrRegistrationHomeOwnerGroups().filter(group =>
            group.action !== ActionTypes.REMOVED && !!group.interestNumerator && !!group.interestNumerator).length === 0
      }),
      showTenancyTypeError: computed((): boolean => {
        return (localState.hasReviewedOwners || props.validateTransfer) &&
          (showGroups && localState.ownershipAllocation.hasMinimumGroupsError && localState.showTotalOwnership)
      }),
      changesRequired: computed((): boolean => {
        return props.validateTransfer && !hasUnsavedChanges.value
      })
    })

    const hideShowRemovedOwners = (): void => {
      localState.hideRemovedOwners = !localState.hideRemovedOwners
      if (localState.hideRemovedOwners) filterDisplayedHomeOwners()
    }

    const removeAllOwnersHandler = (): void => {
      if (localState.hasRemovedAllOwners) {
        localState.showRemovedAllOwnersMsg = true
        setTimeout(() => { localState.showRemovedAllOwnersMsg = false }, 3000)
      } else localState.showDeleteAllGroupsDialog = true
    }

    // Close delete all groups dialog or proceed to deleting all groups
    const cancelOrProceed = (proceed: boolean): void => {
      if (proceed) {
        markGroupForRemoval(null, true)
        localState.showDeleteAllGroupsDialog = false
      } else {
        localState.showDeleteAllGroupsDialog = false
      }
    }

    const filterDisplayedHomeOwners = (): void => {
      localState.filteredHomeOwners = []
      getTransferOrRegistrationHomeOwnerGroups().forEach(ownerGroup => {
        if (ownerGroup.action !== ActionTypes.REMOVED) {
          const owners = ownerGroup.owners
            .map(owner => {
              if (owner.action === ActionTypes.REMOVED) return { groupId: ownerGroup.groupId }
              else return { ...owner, groupId: ownerGroup.groupId }
            })
          localState.filteredHomeOwners.push(...owners)
        }
      })
    }

    const isValidTransferOwners = (isValid: boolean): void => {
      context.emit('isValidTransferOwners', isValid)
    }

    // Enable editing mode whenever adding Person or Business
    // This would disable all Edit buttons
    watch(
      () => localState.disableAddHomeOwnerBtn,
      (isAdding: Boolean) => {
        setGlobalEditingMode(isAdding)
      }
    )

    watch(
      () => localState.getHomeOwners,
      () => {
        if (localState.hideRemovedOwners) filterDisplayedHomeOwners()
      }
    )

    watch(
      () => enableHomeOwnerChanges(),
      (val: boolean) => {
        if (!val) {
          localState.showAddPersonSection = val
          localState.showAddPersonOrganizationSection = val
        }
      }
    )

    onBeforeMount(() => {
      // before mounted in review mode, deleted owners hidden as per default
      // Display Deceased owners by default for Transfer Due to Death scenarios
      if (props.isReadonlyTable && !isTransferDueToDeath.value) {
        hideShowRemovedOwners()
      }
    })

    return {
      getMhrRegistrationHomeOwners,
      getMhrTransferCurrentHomeOwnerGroups,
      isGlobalEditingMode,
      getHomeTenancyType,
      showGroups,
      setShowGroups, // expose this for easier unit testing
      setGlobalEditingMode,
      cancelOrProceed,
      removeAllOwnersHandler,
      hideShowRemovedOwners,
      isValidTransferOwners,
      hasUnsavedChanges,
      getUiTransferType,
      enableAddHomeOwners,
      enableHomeOwnerChanges,
      getMhrTransferDeclaredValue,
      ...toRefs(localState)
    }
  },
  mounted () {
    this.setGlobalEditingMode(false)
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
span:not(.generic-label)  {
  color: $gray7
}

.hide-show-owners {
  color: $primary-blue !important;
  &:hover {
    cursor: pointer;
  }
  .hide-show-owners-icon {
    font-size: 20px;
  }
}

.reg-owners-check::v-deep {
  i {
    vertical-align: baseline;
  }
  span {
    vertical-align: text-bottom;
  }
}

.review-table{
  margin-top: -40px !important;
  padding-top: 0 !important;
}
</style>
