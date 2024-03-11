<template>
  <div id="mhr-home-owners-list">
    <BaseDialog
      :setDisplay="showDeleteAllGroupsDialog"
      :setOptions="{
        title: 'Delete All Owners/Groups',
        text:
          'Deleting all owners/groups will delete all previous owners and remove any newly added owners.',
        acceptText: 'Delete All Owners/Groups',
        cancelText: 'Cancel'
      }"
      @proceed="cancelOrProceed($event)"
    />
    <section
      id="mhr-owners"
      :class="{'mt-10': !isReadonlyTable && !isMhrTransfer}"
    >
      <template v-if="!isMhrTransfer">
        <h2>1. Owners</h2>
        <p class="mt-2 mb-0">
          Add a person or an organization as the owner of the home. You can add
          multiple owners to form joint tenancy or tenants in common ownership.
          <strong>Note:</strong> Tenants in common ownership requires more than one group of
          owners.
        </p>

        <SimpleHelpToggle
          toggleButtonTitle="Help with Owners"
          :defaultHideText="false"
          class="my-6 help-with-owners"
        >
          <template #content>
            <h3 class="text-center mb-7">
              Help with Owners
            </h3>
            <h4>
              Sole Ownership
            </h4>
            <p>This applies when the home is owned by a single individual or organization.</p>
            <h4>Joint Tenancy</h4>
            <p>
              This applies when the home is owned by two or more individuals and/or organizations jointly, with rights
              of survivorship. In joint tenancy, if one joint tenant dies (or for an organization, if it ceases to
              exist) their
              ownership share in the home passes to the surviving joint owner(s).
            </p>
            <h4>Tenants in Common</h4>
            <p>
              This applies when the home is owned by two or more individuals and/or organizations that owns an undivided
              share in the home. Ownership will be displayed in groups of owners with their undivided portion. Each
              owner has the right to dispose of their share independently of the other owners, and in the case of the
              death of an individual,
              their share will belong to the estate of the individual, or through the legal process for dissolution of
              assets, in the case of an organization.
            </p>
            <h4>Definition for Groups</h4>
            <p>
              A group is one or more owners of the home that have an equal undivided share of the home. Tenants in
              common are
              recorded in the Manufactured Home Registry in groups. The relationship between groups will always be as
              tenants in
              common. The relationship between owners within each group is a joint tenancy. There may be multiple groups
              with
              joint tenants.
            </p>
            <h4>Recording Ownership for Multiple Groups</h4>
            <p>
              Each group’s ownership share must be recorded as a portion of the total number of equal shares in the
              home. For
              example, if the home is owned by two groups, and each owns half of the home, this is recorded as each
              group
              holding 1 of 2 shares. If the home is owned by two groups but one group holds two-thirds and one group
              holds
              one-third, this is recorded as the first group holding 2 of 3 shares and the second group holding 1 of 3
              shares.
            </p>
            <p>
              When adding groups of owners, you must enter the total number of shares in the home (Total Available) and
              the
              number of shares owned by each group (Amount Owned by the Group). All groups should use the same
              denominator as is
              used for Total Available, preferably using the lowest common denominator for all groups.
            </p>
          </template>
        </SimpleHelpToggle>

        <label class="generic-label">
          Your registration must include the following:
        </label>
        <div class="mt-5 mb-11 reg-owners-check">
          <v-icon
            v-if="hasHomeOwners"
            color="green-darken-2"
            data-test-id="reg-owner-checkmark"
          >
            mdi-check
          </v-icon>
          <v-icon
            v-else
            color="black"
          >
            mdi-circle-small
          </v-icon>
          <span class="ml-1">At least one owner</span>
        </div>
      </template>

      <!-- Add/Remove Owner Actions -->
      <v-row
        v-if="!isReadonlyTable && enableAddHomeOwners() && !isFrozenMhrDueToUnitNote"
        noGutters
      >
        <v-col cols="12">
          <v-btn
            variant="outlined"
            color="primary"
            :ripple="false"
            :disabled="isGlobalEditingMode"
            data-test-id="add-person-btn"
            @click="hasHomeOwnersTableErrors ? showError = true : (showAddPersonSection = true, showError = false)"
          >
            <v-icon class="pr-1">
              mdi-account-plus
            </v-icon> Add a Person
          </v-btn>

          <span class="mx-2" />

          <v-btn
            variant="outlined"
            color="primary"
            :ripple="false"
            :disabled="isGlobalEditingMode"
            data-test-id="add-org-btn"
            @click="hasHomeOwnersTableErrors
              ? showError = true
              : (showAddPersonOrganizationSection = true, showError = false)"
          >
            <v-icon class="pr-1">
              mdi-domain-plus
            </v-icon>
            Add a Business or Organization
          </v-btn>

          <span class="mx-2" />

          <v-btn
            v-if="isMhrTransfer && enableDeleteAllGroupsActions()"
            variant="outlined"
            color="primary"
            :ripple="false"
            :disabled="isGlobalEditingMode"
            class="float-right"
            data-test-id="remove-all-owners-btn"
            @click="removeAllOwnersHandler()"
          >
            <v-icon class="pr-1">
              mdi-delete
            </v-icon>
            Delete All Owners/Groups
          </v-btn>
        </v-col>
        <v-col
          cols="9"
          class="mb-n6 pa-0"
        /> <!-- Column Spacer -->
        <v-col
          cols="3"
          class="mb-n6 pa-0"
        >
          <v-fade-transition>
            <span
              v-if="showRemovedAllOwnersMsg"
              class="error-text fs-12 ml-5"
            >Nothing to delete</span>
          </v-fade-transition>
        </v-col>
      </v-row>

      <v-row v-if="!isFrozenMhrDueToUnitNote">
        <v-col
          class="transfer-table-error"
        >
          <div
            v-if="showError && hasHomeOwnersTableErrors"
            class="error-text fs-12"
            data-test-id="transfer-table-error"
          >
            {{ transfersErrors.noSupportingDocSelected[getMhrTransferType.transferType] }}
          </div>
        </v-col>
      </v-row>

      <v-row
        v-if="!isReadonlyTable"
        class="mb-6"
        noGutters
      >
        <v-col cols="12">
          <span class="generic-label">Home Tenancy Type: </span>
          <span data-test-id="home-owner-tenancy-type">{{ homeTenancyType }}</span>
          <span
            v-if="showTenancyTypeError"
            class="error-text fs-14 ml-3"
          >
            Must include more than one group of owners
          </span>
          <span
            v-if="hasRemovedOwners && !showTotalOwnership"
            class="float-right hide-show-owners fs-14"
            @click="hideShowRemovedOwners()"
          >
            <v-icon
              v-if="hideRemovedOwners"
              class="hide-show-owners-icon pr-1"
              color="primary"
            >mdi-eye</v-icon>
            <v-icon
              v-else
              class="hide-show-owners-icon pr-1"
              color="primary"
            >mdi-eye-off</v-icon>
            {{ hideShowRemovedOwnersLabel }} Deleted Owners
          </span>
        </v-col>
        <v-col
          v-show="showTotalOwnership"
          cols="12"
          data-test-id="ownership-allocation"
        >
          <!-- Ownership Allocation Information -->
          <span class="generic-label">Total Ownership Allocated:</span> {{ ownershipTotalAllocation }}
          <span
            v-if="hasUndefinedGroups"
            class="error-text fs-14 ml-2"
          >
            No ownership allocated
          </span>
          <span
            v-else-if="getTotalOwnershipAllocationStatus.hasTotalAllocationError"
            class="error-text fs-14 ml-2"
          >
            {{ getTotalOwnershipAllocationStatus.allocationErrorMsg }}
          </span>
          <!-- Success when allocation is whole -->
          <span v-else><v-icon
            color="success"
            class="mt-n2"
          >mdi-check</v-icon></span>

          <!-- Toggle removed owners -->
          <span
            v-if="isMhrTransfer && hasRemovedOwners"
            class="float-right hide-show-owners fs-14"
            @click="hideShowRemovedOwners()"
          >
            <v-icon
              v-if="hideRemovedOwners"
              class="hide-show-owners-icon pr-1"
              color="primary"
            >mdi-eye</v-icon>
            <v-icon
              v-else
              class="hide-show-owners-icon pr-1"
              color="primary"
            >mdi-eye-off</v-icon>
            {{ hideShowRemovedOwnersLabel }} Deleted Owners
          </span>
        </v-col>
        <v-col
          v-if="changesRequired"
          class="mt-3"
        >
          <span
            class="error-text fs-14"
            data-test-id="structure-change-required"
          >
            Change of the ownership structure is required
          </span>
        </v-col>
      </v-row>

      <!-- Read Only Template -->
      <v-card
        v-else
        id="read-only-owners"
        class="review-table"
        flat
      >
        <!-- Transfer Type Review -->
        <template v-if="isMhrTransfer">
          <v-row
            v-if="isRoleStaff"
            id="document-id-review"
            class="mt-6 px-7 pt-8"
            noGutters
          >
            <v-col cols="3">
              <label class="generic-label">Document ID</label>
            </v-col>
            <v-col
              id="transfer-doc-id-display"
              cols="9"
              class="gray7"
            >
              {{ getMhrTransferDocumentId }}
            </v-col>
          </v-row>
          <v-row
            id="transfer-type-review"
            :class="isRoleStaff ? 'mt-4 px-7' : 'mt-6 pt-8 px-7'"
            noGutters
          >
            <v-col cols="3">
              <label class="generic-label">Transfer Type</label>
            </v-col>
            <v-col
              id="transfer-type-display"
              cols="9"
              class="gray7"
            >
              {{ getUiTransferType() }}
            </v-col>
          </v-row>
          <v-row
            class="my-4 px-7"
            noGutters
          >
            <v-col cols="3">
              <label class="generic-label">Declared Value of Home</label>
            </v-col>
            <v-col
              id="declared-value-display"
              cols="9"
              class="gray7"
            >
              {{ formatCurrency(getMhrTransferDeclaredValue) }}
            </v-col>
          </v-row>
          <v-divider class="my-6 mx-7" />
        </template>

        <v-row
          class="my-4 px-7"
          noGutters
        >
          <v-col cols="12">
            <span class="generic-label">Home Owners </span>
            <span
              v-if="isMhrTransfer && hasRemovedOwners"
              class="float-right hide-show-owners fs-14"
              @click="hideShowRemovedOwners()"
            >
              <v-icon
                class="hide-show-owners-icon pr-1"
                color="primary"
              >
                {{ hideRemovedOwners ? 'mdi-eye' : 'mdi-eye-off' }}
              </v-icon>
              {{ hideShowRemovedOwnersLabel }} Deleted Owners
            </span>
          </v-col>
        </v-row>
        <v-row
          class="my-4 px-7"
          noGutters
        >
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
          :homeOwnerGroups="hideRemovedOwners ? filteredHomeOwnersGroups : getHomeOwnerGroups"
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
          :homeOwnerGroups="hideRemovedOwners ? filteredHomeOwnersGroups : getHomeOwnerGroups"
          :isAdding="disableAddHomeOwnerBtn"
          :isMhrTransfer="isMhrTransfer"
          :hideRemovedOwners="hideRemovedOwners"
          :validateTransfer="validateTransfer"
          @isValidTransferOwners="isValidTransferOwners($event)"
          @handleUndo="handleUndo"
        />
      </v-fade-transition>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { AddEditHomeOwner, HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { BaseDialog } from '@/components/dialogs'
import { SimpleHelpToggle } from '@/components/common'
import { useHomeOwners, useMhrValidations, useMhrInformation, useTransferOwners } from '@/composables'

import { MhrRegistrationHomeOwnerGroupIF } from '@/interfaces'
import { ActionTypes } from '@/enums'

import { transfersErrors } from '@/resources'
import { formatCurrency } from '@/utils'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'HomeOwners',
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
  emits: ['isValidTransferOwners'],
  setup (props, context) {
    const {
      isRoleStaff,
      getMhrTransferHomeOwnerGroups,
      getMhrTransferCurrentHomeOwnerGroups,
      getMhrRegistrationValidationModel,
      hasUnsavedChanges,
      getMhrTransferDocumentId,
      getMhrTransferType,
      getMhrTransferDeclaredValue
    } = storeToRefs(useStore())

    const {
      getUiTransferType,
      isFrozenMhrDueToUnitNote
    } = useMhrInformation()

    const {
      enableHomeOwnerChanges,
      enableAddHomeOwners,
      enableDeleteAllGroupsActions,
      isTransferDueToDeath,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      TransToExec
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
      filteredHomeOwnersGroups: [] as MhrRegistrationHomeOwnerGroupIF[],
      disableAddHomeOwnerBtn: computed(
        () => localState.showAddPersonOrganizationSection || localState.showAddPersonSection
      ),
      // capture different errors in the table to turn off Add Owner buttons and show error
      hasHomeOwnersTableErrors: computed(
        () => {
          return (isTransferToExecutorProbateWill.value ||
          isTransferToExecutorUnder25Will.value ||
          isTransferToAdminNoWill.value)
            ? !TransToExec.hasDeletedOwnersWithProbateGrantOrAffidavit()
            : false
        }
      ),
      showError: false,
      ownershipTotalAllocation: computed((): string => {
        return localState.hasUndefinedGroups ? 'N/A' : getTotalOwnershipAllocationStatus.value.totalAllocation
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
      getHomeOwnerGroups: computed(() => { return getTransferOrRegistrationHomeOwnerGroups() }),
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
          (showGroups && getTotalOwnershipAllocationStatus.value.hasMinimumGroupsError && localState.showTotalOwnership)
      }),
      changesRequired: computed((): boolean => {
        return props.validateTransfer && !hasUnsavedChanges.value
      })
    })

    const hideShowRemovedOwners = (forceShow: boolean = false): void => {
      // Override Toggle to force show
      if (forceShow) localState.hideRemovedOwners = true

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
      localState.filteredHomeOwnersGroups = []
      getTransferOrRegistrationHomeOwnerGroups().forEach(ownerGroup => {
        // isTransferToExecutorProbateWill condition here due to new owners being added to removed groups in WILL flow
        if (ownerGroup.action !== ActionTypes.REMOVED || isTransferToExecutorProbateWill.value) {
          const owners = ownerGroup.owners
            .map(owner => {
              if (owner.action === ActionTypes.REMOVED) return { groupId: ownerGroup.groupId }
              else return { ...owner, groupId: ownerGroup.groupId }
            })
          localState.filteredHomeOwnersGroups.push({ ...ownerGroup, owners })
        }
      })
    }

    const isValidTransferOwners = (isValid: boolean): void => {
      context.emit('isValidTransferOwners', isValid)
    }

    const handleUndo = (): void => {
      // reset all necessary flags/props
      localState.showError = false
    }

    // Enable editing mode whenever adding Person or Business
    // This would disable all Edit buttons
    watch(
      () => localState.disableAddHomeOwnerBtn,
      (isAdding: boolean) => {
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
      isRoleStaff,
      getTotalOwnershipAllocationStatus,
      getMhrTransferCurrentHomeOwnerGroups,
      getMhrTransferHomeOwnerGroups, // expose this for easier unit testing
      isGlobalEditingMode,
      getHomeTenancyType,
      showGroups,
      setShowGroups, // expose this for easier unit testing
      setGlobalEditingMode,
      cancelOrProceed,
      removeAllOwnersHandler,
      hideShowRemovedOwners,
      isValidTransferOwners,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      hasUnsavedChanges,
      getMhrTransferType,
      transfersErrors,
      getMhrTransferDocumentId,
      getUiTransferType,
      enableAddHomeOwners,
      enableHomeOwnerChanges,
      enableDeleteAllGroupsActions,
      getMhrTransferDeclaredValue,
      handleUndo,
      isFrozenMhrDueToUnitNote,
      formatCurrency,
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

.help-with-owners {
  h4 {
  font-size: 16px;
  line-height: normal
  }

  p {
    line-height: 24px;
    margin-bottom: 24px;
    color: gray7;
  }
}

.transfer-table-error {
  padding: 5px 12px 10px !important;
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

.reg-owners-check:deep() {
  i {
    vertical-align: baseline;
  }
  span {
    vertical-align: text-bottom;
  }
}

.review-table {
  margin-top: -40px !important;
  padding-top: 0 !important;
  border-radius: unset;
}
</style>
