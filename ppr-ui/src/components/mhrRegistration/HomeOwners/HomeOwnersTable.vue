<template>
  <v-card id="home-owner-table-card" flat rounded :class="{ 'border-error-left': showTableError}">
    <BaseDialog
      :setOptions="mhrDeceasedOwnerChanges"
      :setDisplay="showOwnerChangesDialog"
      @proceed="handleOwnerChangesDialogResp($event)"
    />

    <v-simple-table
      id="mh-home-owners-table-1"
      class="home-owners-table"
      :class="{ 'review-mode': isReadonlyTable }"
      item-key="groupId"
      :group-by="showGroups ? 'groupId' : null"
    >
      <thead class="simple">
        <tr>
            <th v-for="header in homeOwnersTableHeaders" :key="header.value" :class="header.class">
              {{ header.text }}
            </th>
          </tr>
      </thead>
      <tbody v-if="homeOwners.length > 0">
        <tr v-for="(group, groupIndex) in homeOwnerGroups" :key="`${group}: ${groupIndex}`">
          <td class="pa-0" colspan="4"> <!-- Start of Home Owner Group -->
            <div
                v-if="showGroups && !(disableGroupHeader(group.groupId) && (hideRemovedOwners || isReadonlyTable))"
                :colspan="4"
                class="py-1 px-7 group-header-slot"
                :class="{'spacer-header': disableGroupHeader(group.groupId),
                  'border-error-left': isInvalidOwnerGroup(group.groupId)
                }"
              >
                <TableGroupHeader
                  :groupId="group.groupId"
                  :groupNumber="getGroupNumberById(group.groupId)"
                  :owners="hasActualOwners(group.owners) ? group.owners : []"
                  :showEditActions="showEditActions && enableTransferOwnerGroupActions()"
                  :disableGroupHeader="disableGroupHeader(group.groupId)"
                  :isMhrTransfer="isMhrTransfer"
                />
              </div> <!-- End of Table Group Header -->

            <div v-for="(item, index) in group.owners" :key="`${item}: ${index}`" class="owner-row">

              <div v-if="isMhrTransfer && !hasActualOwners(group.owners) && group.owners.length > 0 &&
                hasRemovedAllHomeOwnerGroups() &&
                !isTransferToExecutorProbateWill &&
                !isTransferToExecutorUnder25Will &&
                !isTransferToAdminNoWill"
                >
                <div class="pa-6 fs-14 text-center no-owners-head-row" data-test-id="no-data-msg">
                    No owners added yet.
                </div>
              </div>

              <!-- Transfer scenario: Display error for groups that 'removed' all owners
                but they still exist in the table -->
              <div v-if="isGroupWithNoOwners(item.groupId, index) ||
                isTransferGroupInvalid(group.groupId, index)">
                <div
                  class="py-1 bottom-border"
                  :class="{ 'border-error-left': isInvalidOwnerGroup(group.groupId)}"
                  data-test-id="invalid-group-msg"
                >
                  <div
                    class="error-text my-6 text-center"
                    :data-test-id="`no-owners-msg-group-${group.owners.indexOf(item)}`"
                  >
                    <HomeOwnersGroupError :groupId="group.groupId" />
                  </div>
                </div>
              </div>

              <tr v-else-if="!isMhrTransfer && index === 0 && hasMixedOwnersInGroup(item.groupId)
                && !isReadonlyTable">
                <HomeOwnersMixedRolesError
                  :groupId="item.groupId"
                  :showBorderError ='isInvalidOwnerGroup(item.groupId)'
                  />
              </tr>

              <template v-if="isCurrentlyEditing(group.owners.indexOf(item))">
                <div class="pa-0" :colspan="homeOwnersTableHeaders.length">
                  <v-expand-transition>
                    <AddEditHomeOwner
                      :editHomeOwner="item"
                      :isHomeOwnerPerson="!item.organizationName"
                      :isMhrTransfer="isMhrTransfer"
                      :showTableError="validateTransfer && (isAddingMode || isEditingMode)"
                      @cancel="currentlyEditingHomeOwnerId = -1"
                      @remove="removeOwnerHandler(item)"
                    />
                  </v-expand-transition>
                </div>
              </template>

              <template v-else-if="item.ownerId">
                <tr
                  :key="`owner-row-key-${group.owners.indexOf(item)}`"
                  class="owner-info"
                  :data-test-id="`owner-info-${item.ownerId}`"
                >
                  <!-- Start of Name -->
                  <td
                    class="owner-name"
                    :class="[{'no-bottom-border' : hideRowBottomBorder(item),
                      'border-error-left': isInvalidOwnerGroup(item.groupId) },
                      homeOwnersTableHeaders[0].class]"
                  >
                    <div :class="{'removed-owner': isRemovedHomeOwner(item)}">
                      <div v-if="item.individualName" class="owner-icon-name">
                        <v-icon
                          class="mr-2"
                          :class="{'person-executor-icon': item.partyType !== HomeOwnerPartyTypes.OWNER_IND}"
                        >
                          {{ getHomeOwnerIcon(item.partyType) }}
                        </v-icon>
                        <div class="font-weight-bold">
                          {{ item.individualName.first }}
                          {{ item.individualName.middle }}
                          {{ item.individualName.last }}
                        </div>
                      </div>
                      <div v-else class="owner-icon-name">
                        <v-icon
                          class="mr-2"
                          :class="{'business-executor-icon': item.partyType !== HomeOwnerPartyTypes.OWNER_BUS}"
                        >
                          {{ getHomeOwnerIcon(item.partyType, true) }}
                        </v-icon>
                        <div class="font-weight-bold">
                          {{ item.organizationName }}
                        </div>
                      </div>
                      <div v-if="item.suffix" class="font-light suffix">
                        {{ item.suffix }}
                      </div>
                      <div v-else-if="item.description"
                        class="font-light description"
                      >
                        {{ item.description }}
                      </div>
                    </div>

                    <!-- Hide Chips for Review Mode -->
                    <template v-if="isMhrTransfer && (!isReadonlyTable || showChips)">
                      <InfoChip class="ml-8 mt-2" :action="mapInfoChipAction(item)" />
                    </template>
                  </td> <!-- End of Name -->

                  <td :class="[{'no-bottom-border' : hideRowBottomBorder(item)}, homeOwnersTableHeaders[1].class]">
                    <base-address
                      :schema="addressSchema"
                      :value="item.address"
                      :class="{'removed-owner': isRemovedHomeOwner(item)}"
                    />
                  </td> <!-- End of Address -->

                  <td :class="[{'no-bottom-border' : hideRowBottomBorder(item)}, homeOwnersTableHeaders[2].class]">
                    <div :class="{'removed-owner': isRemovedHomeOwner(item)}">
                      {{ toDisplayPhone(item.phoneNumber) }}
                      <span v-if="item.phoneExtension"> Ext {{ item.phoneExtension }} </span>
                    </div>
                  </td> <!-- End of Phone -->

                  <td v-if="showEditActions" class="row-actions text-right"
                    :class="[{'no-bottom-border' : hideRowBottomBorder(item)}, homeOwnersTableHeaders[3].class]">

                    <!-- New Owner Actions -->
                    <div
                      v-if="(!isMhrTransfer || isAddedHomeOwner(item)) && enableHomeOwnerChanges()"
                      class="mr-n4"
                    >
                      <v-btn
                        text
                        color="primary"
                        class="mr-n4"
                        :ripple="false"
                        :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                        @click="openForEditing(group.owners.indexOf(item))"
                        data-test-id="table-edit-btn"
                      >
                        <v-icon small>mdi-pencil</v-icon>
                        <span>Edit</span>
                        <v-divider class="ma-0 pl-3" vertical />
                      </v-btn>
                      <!-- Actions drop down menu -->
                      <v-menu offset-y left nudge-bottom="0">
                        <template v-slot:activator="{ on }">
                          <v-btn text v-on="on"
                                color="primary" class="px-0"
                                :disabled="isAddingMode || isGlobalEditingMode"
                          >
                            <v-icon>mdi-menu-down</v-icon>
                          </v-btn>
                        </template>

                        <!-- More actions drop down list -->
                        <v-list class="actions-dropdown actions__more-actions">
                          <v-list-item class="my-n2">
                            <v-list-item-subtitle class="pa-0" @click="remove(item)">
                              <v-icon small style="margin-bottom: 3px;">mdi-delete</v-icon>
                              <span class="ml-1 remove-btn-text">Remove</span>
                            </v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div> <!-- End of Owner Actions -->

                    <!-- Existing Owner Actions -->
                    <template v-else-if="enableTransferOwnerActions(item)">
                      <v-btn
                        v-if="!isRemovedHomeOwner(item) && !isChangedOwner(item) && !isDisabledForSoGChanges(item)"
                        text color="primary" class="mr-n4"
                        :ripple="false"
                        :disabled="isAddingMode || isEditingMode || isGlobalEditingMode ||
                          isDisabledForSJTChanges(item) || isDisabledForWillChanges(item)"
                        @click="markForRemoval(item)"
                        data-test-id="table-delete-btn"
                      >
                        <v-icon small>mdi-delete</v-icon>
                        <span>Delete</span>
                        <v-divider v-if="enableTransferOwnerMenuActions(item)" class="ma-0 pl-3" vertical />
                      </v-btn>

                      <v-btn
                        v-if="isRemovedHomeOwner(item) || isChangedOwner(item)"
                        text color="primary" class="mr-n4"
                        :ripple="false"
                        :disabled="isAddingMode || isEditingMode || isGlobalEditingMode ||
                          isDisabledForSJTChanges(item)"
                        @click="undo(item)"
                        data-test-id="table-undo-btn"
                      >
                        <v-icon small>mdi-undo</v-icon>
                        <span>Undo</span>
                        <v-divider
                          v-if="enableTransferOwnerMenuActions(item) && !isRemovedHomeOwner(item)"
                          class="ma-0 pl-3" vertical
                        />
                      </v-btn>

                      <!-- Menu actions drop down menu -->
                      <template v-if="enableTransferOwnerMenuActions(item) && !isRemovedHomeOwner(item)">
                        <v-menu offset-y left nudge-bottom="0">
                          <template v-slot:activator="{ on }">
                            <v-btn
                              text v-on="on"
                              color="primary"
                              class="px-0 mr-n3"
                              :disabled="isAddingMode || isGlobalEditingMode || isDisabledForSJTChanges(item)"
                            >
                              <v-icon>mdi-menu-down</v-icon>
                            </v-btn>
                          </template>

                          <!-- More actions drop down list -->
                          <v-list class="actions-dropdown actions__more-actions">
                            <!-- Menu Edit Option -->
                            <v-list-item class="my-n2">
                              <v-list-item-subtitle class="pa-0" @click="openForEditing(group.owners.indexOf(item))">
                                <v-icon small class="mb-1">mdi-pencil</v-icon>
                                <span class="ml-1 remove-btn-text">Change Details</span>
                              </v-list-item-subtitle>
                            </v-list-item>

                            <!-- Menu Delete Option -->
                            <v-list-item class="my-n2" v-if="isChangedOwner(item)">
                              <v-list-item-subtitle class="pa-0" @click="removeChangeOwnerHandler(item)">
                                <v-icon small class="mb-1">mdi-delete</v-icon>
                                <span class="ml-1 remove-btn-text">Delete</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </template>
                    </template>
                  </td>
                </tr>
              </template>

              <!-- For MHR scenarios where users can entirely remove added owners -->
              <tr v-else-if="!hideRemovedOwners && !showGroups">
                <div class="my-6 text-center" data-test-id="no-owners-mgs">
                  No owners added yet.
                </div>
              </tr>
              <tr
                v-if="isRemovedHomeOwner(item) && showDeathCertificate() && !isReadonlyTable"
                class="death-certificate-row"
              >
                <td
                  :colspan="homeOwnersTableHeaders.length"
                  class="pt-0 pl-8"
                  :class="{ 'border-error-left': isInvalidOwnerGroup(item.groupId) }"
                >
                  <v-expand-transition>
                    <DeathCertificate
                      :deceasedOwner="item"
                      :validate="validateTransfer"
                    />
                  </v-expand-transition>
                </td>
              </tr>
              <tr
                v-else-if="isRemovedHomeOwner(item) &&
                  (showDeathCertificate() || showSupportingDocuments()) &&
                  isReadonlyTable"
              >
                <td v-if="item.supportingDocument"
                  :colspan="homeOwnersTableHeaders.length" class="deceased-review-info">
                  <v-row no-gutters class="ml-8 my-n3">
                    <v-col cols="12">
                      <div v-if="item.supportingDocument === SupportingDocumentsOptions.AFFIDAVIT"
                        data-test-id="affidavit-review-note">
                        <p class="generic-label fs-14 mb-3">
                          Affidavit of Executor with Death Certificate<br>
                          <span class="font-light ml-0">
                            Note: Ensure you have the original signed Affidavit of Executor form and a
                            court certified true copy of the will.
                          </span>
                        </p>
                          <p class="generic-label fs-14">
                            Death Certificate Registration Number:
                            <span class="font-light mx-1">{{item.deathCertificateNumber}}</span>
                          </p>
                          <p class="generic-label fs-14 mt-n4">Date of Death:
                            <span class="font-light mx-1">{{yyyyMmDdToPacificDate(item.deathDateTime, true)}}</span>
                          </p>
                      </div>
                      <div
                        v-if="item.supportingDocument === SupportingDocumentsOptions.DEATH_CERT ||
                        showDeathCertificate()"
                        data-test-id="death-cert-review-note"
                      >
                        <p class="generic-label fs-14">
                          Death Certificate Registration Number:
                          <span class="font-light mx-1">{{item.deathCertificateNumber}}</span>
                        </p>
                        <p class="generic-label fs-14 mt-n4">Date of Death:
                          <span class="font-light mx-1">{{yyyyMmDdToPacificDate(item.deathDateTime, true)}}</span>
                        </p>
                      </div>
                      <div
                        v-else-if="item.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT"
                        data-test-id="grant-review-note"
                      >
                        <p class="generic-label fs-14">
                          Grant of Probate with Will<br>
                          <span class="font-light ml-0">
                            Note: Ensure you have a court certified true copy of the Grant of Probate with the
                            will attached.
                          </span>
                        </p>
                      </div>
                    </v-col>
                  </v-row>
                </td>
              </tr>

              <tr v-else-if="isRemovedHomeOwner(item) &&
                showSupportingDocuments() &&
                !isReadonlyTable &&
                isPartyTypeNotEAT(item)">
                <td
                  :colspan="homeOwnersTableHeaders.length"
                  class="pl-14"
                  :class="{ 'border-error-left': isInvalidOwnerGroup(group.groupId) }"
                >
                  <v-expand-transition>
                    <SupportingDocuments
                      :key="item.ownerId"
                      :deletedOwner="item"
                      :validate="validateTransfer"
                      :isSecondOptionDisabled="TransToExec.hasOnlyOneOwnerInGroup(item.groupId)"
                      :isSecondOptionError="TransToExec.isAllGroupOwnersWithDeathCerts(item.groupId)"
                      :hasDeathCertForFirstOption="isTransferToExecutorUnder25Will"
                      @handleDocOptionOneSelected="TransToExec.resetGrantOfProbate(group.groupId, item.ownerId)"
                    >
                      <template v-slot:deathCert>
                        <DeathCertificate
                          :deceasedOwner="item"
                          :validate="validateTransfer"
                          :isDisabled="isGlobalEditingMode"
                        />
                      </template>
                    </SupportingDocuments>
                  </v-expand-transition>
                </td>
              </tr>

            </div>
            <div v-if="group.owners.length === 0" class="my-6 text-center" data-test-id="no-data-msg">
              No owners added yet.
            </div>
          </td>
        </tr>
      </tbody>

      <!-- No Data -->
      <tbody v-else>
        <tr class="text-center">
          <td :colspan="homeOwnersTableHeaders.length"
            class="pa-4 text-center"
            data-test-id="no-data-msg">
            No owners added yet.
          </td>
        </tr>
      </tbody>
    </v-simple-table>

     <!-- start of data-table -->
     <!-- end of data-table -->

  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { homeOwnersTableHeaders, homeOwnersTableHeadersReview } from '@/resources/tableHeaders'
import { useHomeOwners, useMhrInfoValidation, useMhrValidations, useTransferOwners } from '@/composables'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'
import { AddEditHomeOwner } from '@/components/mhrRegistration/HomeOwners'
import HomeOwnersMixedRolesError from './HomeOwnersMixedRolesError.vue'
import { DeathCertificate, SupportingDocuments, HomeOwnersGroupError } from '@/components/mhrTransfers'
import { BaseDialog } from '@/components/dialogs'
import TableGroupHeader from '@/components/mhrRegistration/HomeOwners/TableGroupHeader.vue'
import { mhrDeceasedOwnerChanges } from '@/resources/dialogOptions'
import { yyyyMmDdToPacificDate } from '@/utils/date-helper'
import { InfoChip } from '@/components/common'
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { ActionTypes, HomeOwnerPartyTypes, HomeTenancyTypes, SupportingDocumentsOptions } from '@/enums'
import { storeToRefs } from 'pinia'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeOwnersTable',
  emits: ['isValidTransferOwners', 'handleUndo'],
  props: {
    homeOwnerGroups: { default: () => [] },
    isAdding: { default: false },
    isReadonlyTable: { type: Boolean, default: false },
    isMhrTransfer: { type: Boolean, default: false },
    hideRemovedOwners: { type: Boolean, default: false },
    showChips: { type: Boolean, default: false },
    validateTransfer: { type: Boolean, default: false }
  },
  components: {
    BaseAddress,
    BaseDialog,
    AddEditHomeOwner,
    TableGroupHeader,
    SupportingDocuments,
    DeathCertificate,
    InfoChip,
    HomeOwnersGroupError,
    HomeOwnersMixedRolesError
  },
  setup (props, context) {
    const addressSchema = PartyAddressSchema
    const { setUnsavedChanges } = useStore()
    const { // Getters
      getMhrRegistrationValidationModel,
      getMhrInfoValidation,
      hasUnsavedChanges,
      getMhrRegistrationHomeOwnerGroups,
      getMhrTransferHomeOwnerGroups
    } = storeToRefs(useStore())
    const {
      showGroups,
      removeOwner,
      deleteGroup,
      isGlobalEditingMode,
      setGlobalEditingMode,
      hasMinimumGroups,
      editHomeOwner,
      getGroupById,
      undoGroupChanges,
      getGroupNumberById,
      hasMixedOwnersInAGroup,
      hasMixedOwnersInGroup,
      hasRemovedAllHomeOwners,
      hasRemovedAllHomeOwnerGroups,
      getTotalOwnershipAllocationStatus,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups
    } = useHomeOwners(props.isMhrTransfer)

    const {
      enableHomeOwnerChanges,
      enableTransferOwnerActions,
      enableTransferOwnerGroupActions,
      enableTransferOwnerMenuActions,
      showDeathCertificate,
      showSupportingDocuments,
      isDisabledForSoGChanges,
      isDisabledForSJTChanges,
      isDisabledForWillChanges,
      isCurrentOwner,
      getCurrentOwnerStateById,
      isTransferDueToSaleOrGift,
      isTransferToSurvivingJointTenant,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      groupHasRemovedAllCurrentOwners,
      moveCurrentOwnersToPreviousOwners,
      hasMinOneExecOrAdminInGroup,
      TransSaleOrGift,
      TransToExec,
      TransToAdmin,
      TransJointTenants
    } = useTransferOwners(!props.isMhrTransfer)

    const { getValidation, MhrSectVal, MhrCompVal } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { isValidDeceasedOwnerGroup } = useMhrInfoValidation(getMhrInfoValidation.value)

    const localState = reactive({
      currentlyEditingHomeOwnerId: -1,
      reviewed: false,
      showOwnerChangesDialog: false,
      ownerToDecease: null as MhrRegistrationHomeOwnerIF,
      isEditingMode: computed((): boolean => localState.currentlyEditingHomeOwnerId >= 0),
      isAddingMode: computed((): boolean => props.isAdding),
      showTableError: computed((): boolean => {
        // For certain Transfers, we only need to check for global changes and do not show table error in other cases
        if (isTransferToExecutorProbateWill.value ||
          isTransferToExecutorUnder25Will.value ||
          isTransferDueToSaleOrGift.value ||
          isTransferToAdminNoWill.value) {
          return props.validateTransfer && props.isMhrTransfer && !hasUnsavedChanges.value
        }

        return ((props.validateTransfer || (!props.isMhrTransfer && localState.reviewedOwners)) &&
          (
            !hasMinimumGroups() ||
            (props.isMhrTransfer && !hasUnsavedChanges.value) ||
            !localState.isValidAllocation ||
            localState.hasGroupsWithNoOwners ||
            (hasMixedOwnersInAGroup() && !showGroups.value)
          )
        )
      }),
      homeOwners: computed(() => props.homeOwnerGroups
        // need to have groupId to display Group Header for groups with no Owners
        .flatMap(group => group.owners.length > 0 ? group.owners : { groupId: group.groupId })),
      reviewedOwners: computed((): boolean =>
        getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)),
      showEditActions: computed((): boolean => !props.isReadonlyTable),
      homeOwnersTableHeaders: props.isReadonlyTable ? homeOwnersTableHeadersReview : homeOwnersTableHeaders,
      addedOwnerCount: computed((): number => {
        return getTransferOrRegistrationHomeOwners().filter(owner => owner.action === ActionTypes.ADDED).length
      }),
      addedGroupCount: computed((): number => {
        return getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action === ActionTypes.ADDED).length
      }),
      hasGroupsWithNoOwners: computed((): boolean => {
        const groups = getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)
        return groups.some(group => group.owners.filter(owner => owner.action !== ActionTypes.REMOVED).length === 0)
      }),
      isValidAllocation: computed((): boolean => {
        return !showGroups.value || !getTotalOwnershipAllocationStatus().hasTotalAllocationError
      })
    })

    const isInvalidRegistrationOwnerGroup = (groupId: number) =>
      hasMixedOwnersInGroup(groupId) && localState.reviewedOwners &&
      !localState.showTableError && !props.isReadonlyTable

    const isInvalidTransferOwnerGroup = (groupId: number, hasExecOrAdminInGroup: boolean) => {
      if (props.validateTransfer &&
        (!hasUnsavedChanges.value || hasMinOneExecOrAdminInGroup(groupId)) &&
        TransToExec.hasAllCurrentOwnersRemoved(groupId)
      ) return false

      const hasRemovedOwners = TransToExec.hasSomeOwnersRemoved(groupId)
      // groups that are not edited are valid
      if (!hasRemovedOwners && !hasExecOrAdminInGroup) return false

      const hasRemovedAllOwners = TransToExec.hasAllCurrentOwnersRemoved(groupId)
      const hasValidDocs = TransToExec.hasOwnersWithValidSupportDocs(groupId)
      const hasOwnersWithoutDeathCert = !TransToExec.isAllGroupOwnersWithDeathCerts(groupId)

      return !(hasRemovedAllOwners && hasValidDocs && hasOwnersWithoutDeathCert && hasExecOrAdminInGroup)
    }

    // check if Owner Group that has deceased Owners is valid
    const isInvalidOwnerGroup = (groupId: number): boolean => {
      if (!props.isMhrTransfer) return isInvalidRegistrationOwnerGroup(groupId)
      if (!props.validateTransfer) return false
      if (isTransferDueToSaleOrGift.value) return TransSaleOrGift.hasMixedOwnersInGroup(groupId)

      if ((isTransferToExecutorProbateWill.value ||
          isTransferToExecutorUnder25Will.value ||
          isTransferToAdminNoWill.value)) {
        const hasExecOrAdminInGroup = isTransferToAdminNoWill.value
          ? TransToAdmin.hasAddedAdministratorsInGroup(groupId)
          : TransToExec.hasAddedExecutorsInGroup(groupId)

        return isInvalidTransferOwnerGroup(groupId, hasExecOrAdminInGroup)
      }

      return !isValidDeceasedOwnerGroup(groupId) && !localState.showTableError
    }

    const remove = (item): void => {
      localState.currentlyEditingHomeOwnerId = -1
      setUnsavedChanges(true)
      removeOwner(item)
    }

    const markForRemoval = (item: MhrRegistrationHomeOwnerIF): void => {
      localState.currentlyEditingHomeOwnerId = -1
      editHomeOwner(
        { ...item, action: ActionTypes.REMOVED },
        item.groupId
      )

      // When base ownership is SO/JT and all current owners have been removed: Move them to a previous owners group.
      if (groupHasRemovedAllCurrentOwners(getGroupById(item.groupId)) && showGroups.value) {
        moveCurrentOwnersToPreviousOwners(getGroupById(item.groupId))
      }
    }

    const undo = async (item: MhrRegistrationHomeOwnerIF): Promise<void> => {
      await editHomeOwner(
        { ...getCurrentOwnerStateById(item.ownerId), action: null },
        item.groupId
      )
      const isRemovedGroup = getGroupById(item.groupId).action === ActionTypes.REMOVED
      isRemovedGroup && undoGroupChanges(item.groupId)
      context.emit('handleUndo', item)
    }

    const openForEditing = (index: number) => {
      localState.currentlyEditingHomeOwnerId = index
    }

    const isCurrentlyEditing = (index: number): boolean => {
      return index === localState.currentlyEditingHomeOwnerId
    }

    const mapInfoChipAction = (item: MhrRegistrationHomeOwnerIF): string => {
      return item.action === ActionTypes.REMOVED &&
       isPartyTypeNotEAT(item) &&
        (showDeathCertificate() ||
          isTransferToExecutorProbateWill.value ||
          isTransferToExecutorUnder25Will.value ||
          isTransferToAdminNoWill.value)
        ? 'DECEASED'
        : item.action
    }

    // To render Group table header the owners array must not be empty
    // check for at least one owner with an id
    // This util function will help to show Owners: 0 in the table header
    const hasActualOwners = (owners: MhrRegistrationHomeOwnerIF[]): boolean => {
      const activeOwners = owners.filter(owner => owner.action !== ActionTypes.REMOVED)
      return activeOwners.length > 0 && activeOwners.some(owner => owner.ownerId !== undefined)
    }

    const isAddedHomeOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.ADDED
    }

    const isAddedHomeOwnerGroup = (groupId: number): boolean => {
      return getGroupById(groupId)?.action === ActionTypes.ADDED
    }

    const isChangedOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.CHANGED
    }

    const isRemovedHomeOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.REMOVED
    }

    const isPartyTypeNotEAT = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return ![HomeOwnerPartyTypes.EXECUTOR, HomeOwnerPartyTypes.ADMINISTRATOR, HomeOwnerPartyTypes.TRUSTEE]
        .includes(item.partyType)
    }

    const hasNoGroupInterest = (groupId: number): boolean => {
      const group = getGroupById(groupId)
      return !group.interestNumerator && !group.interestDenominator
    }

    const disableGroupHeader = (groupId: number): boolean => {
      const currentOwners = localState.homeOwners.filter(owner => owner.action !== ActionTypes.ADDED)

      return hasRemovedAllHomeOwners(currentOwners) &&
        isAddedHomeOwnerGroup(groupId) &&
        hasNoGroupInterest(groupId) &&
        localState.addedGroupCount <= 1
    }

    const isGroupWithNoOwners = (groupId: number, index: number): boolean => {
      const group = getGroupById(groupId)

      const hasNoOwners = group.action !== ActionTypes.REMOVED && group.interestNumerator &&
        group.interestDenominator && group.owners.filter(owner => owner.action !== ActionTypes.REMOVED).length === 0

      return hasNoOwners && index === 0
    }

    // validate group for different Transfers types
    const isTransferGroupInvalid = (groupId: number, index) => {
      if (index !== 0 || !hasUnsavedChanges.value) return false
      if (isTransferToExecutorProbateWill.value ||
          isTransferToExecutorUnder25Will.value ||
          isTransferToAdminNoWill.value) {
        const hasAddedRoleInGroup = isTransferToAdminNoWill.value
          ? TransToAdmin.hasAddedAdministratorsInGroup(groupId)
          : TransToExec.hasAddedExecutorsInGroup(groupId)

        return (
          (TransToExec.hasSomeOwnersRemoved(groupId) || hasAddedRoleInGroup) &&
          !(hasAddedRoleInGroup &&
          TransToExec.hasAllCurrentOwnersRemoved(groupId) &&
          !TransToExec.isAllGroupOwnersWithDeathCerts(groupId))
        )
      }

      if (isTransferDueToSaleOrGift.value) return TransSaleOrGift.hasMixedOwnersInGroup(groupId)
    }

    const removeOwnerHandler = (owner: MhrRegistrationHomeOwnerIF): void => {
      isCurrentOwner(owner)
        ? isChangedOwner(owner) ? removeChangeOwnerHandler(owner) : markForRemoval(owner)
        : remove(owner)
    }

    const removeChangeOwnerHandler = (owner: MhrRegistrationHomeOwnerIF): void => {
      localState.ownerToDecease = { ...getCurrentOwnerStateById(owner.ownerId), groupId: owner.groupId }
      localState.showOwnerChangesDialog = true
    }

    const handleOwnerChangesDialogResp = async (val: boolean): Promise<void> => {
      if (!val) {
        localState.showOwnerChangesDialog = false
        return
      }

      await markForRemoval(localState.ownerToDecease)
      localState.showOwnerChangesDialog = false
      localState.ownerToDecease = null
    }

    // Hide bottom border for the owner's row that requires additional input (Death Certificate etc.)
    const hideRowBottomBorder = (rowItem: MhrRegistrationHomeOwnerIF): boolean => {
      return isRemovedHomeOwner(rowItem) &&
      isPartyTypeNotEAT(rowItem) && // show the bottom border line for Execs, Admins and Trustees
      (showDeathCertificate() || showSupportingDocuments())
    }

    const getHomeOwnerIcon = (partyType: HomeOwnerPartyTypes, isBusiness = false): string => {
      const uniqueRoleIcon = isBusiness
        ? '$vuetify.icons.values.ExecutorBusinessIcon'
        : '$vuetify.icons.values.ExecutorPersonIcon'
      const ownerIcon = isBusiness
        ? 'mdi-domain'
        : 'mdi-account'

      switch (partyType) {
        case HomeOwnerPartyTypes.EXECUTOR:
        case HomeOwnerPartyTypes.ADMINISTRATOR:
        case HomeOwnerPartyTypes.TRUSTEE:
          return uniqueRoleIcon
        case HomeOwnerPartyTypes.OWNER_IND:
        case HomeOwnerPartyTypes.OWNER_BUS:
          return ownerIcon
      }
    }

    watch(() => localState.currentlyEditingHomeOwnerId, () => {
      setGlobalEditingMode(localState.isEditingMode)
    })

    // When a change is made to homeOwners, check if any actions have changed, if so set flag
    watch(() => localState.homeOwners, (val) => {
      setUnsavedChanges(val.some(owner => !!owner.action || !owner.ownerId))

      context.emit('isValidTransferOwners',
        hasMinimumGroups() &&
        localState.isValidAllocation &&
        !localState.hasGroupsWithNoOwners &&
        (isTransferDueToSaleOrGift.value ? !TransSaleOrGift.hasMixedOwners.value : true) &&
        (isTransferToSurvivingJointTenant.value ? TransJointTenants.isValidTransfer.value : true) &&
        ((isTransferToExecutorProbateWill.value || isTransferToExecutorUnder25Will.value)
          ? TransToExec.isValidTransfer.value : true)
      )
    }, { immediate: true, deep: true })

    watch(
      () => enableTransferOwnerGroupActions(),
      () => {
        localState.currentlyEditingHomeOwnerId = -1
      }
    )

    return {
      getMhrRegistrationHomeOwnerGroups,
      ActionTypes,
      addressSchema,
      toDisplayPhone,
      openForEditing,
      isCurrentlyEditing,
      showGroups,
      hasActualOwners,
      remove,
      deleteGroup,
      isGlobalEditingMode,
      hasMinimumGroups,
      isAddedHomeOwner,
      isChangedOwner,
      isRemovedHomeOwner,
      markForRemoval,
      undo,
      mapInfoChipAction,
      hasMixedOwnersInGroup,
      hasRemovedAllHomeOwners,
      hasRemovedAllHomeOwnerGroups,
      isAddedHomeOwnerGroup,
      disableGroupHeader,
      isGroupWithNoOwners,
      getGroupNumberById,
      getMhrTransferHomeOwnerGroups,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups,
      enableHomeOwnerChanges,
      enableTransferOwnerActions,
      enableTransferOwnerGroupActions,
      enableTransferOwnerMenuActions,
      showDeathCertificate,
      showSupportingDocuments,
      isDisabledForSoGChanges,
      isDisabledForSJTChanges,
      isDisabledForWillChanges,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      isCurrentOwner,
      mhrDeceasedOwnerChanges,
      removeOwnerHandler,
      removeChangeOwnerHandler,
      handleOwnerChangesDialogResp,
      hideRowBottomBorder,
      yyyyMmDdToPacificDate,
      isInvalidOwnerGroup,
      HomeOwnerPartyTypes,
      SupportingDocumentsOptions,
      HomeOwnersGroupError,
      TransSaleOrGift,
      TransToExec,
      TransToAdmin,
      getMhrInfoValidation,
      isTransferGroupInvalid,
      getHomeOwnerIcon,
      isPartyTypeNotEAT,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.home-owners-table ::v-deep {
  .person-executor-icon {
    margin-top: -3px !important;
    height: 22px !important;
    width: 22px !important;
  }
  .business-executor-icon {
    margin-top: -8px !important;
    margin-left: -4px !important;
    height: 29px !important;
    width: 28px !important;
  }
  .spacer-header {
    border-color: $gray1 !important;
    background-color: $gray1 !important;
  }

  .no-bottom-border {
    border-bottom: none !important;
  }

  .death-certificate-row {
    border-bottom: thin solid rgba(0, 0, 0, 0.12) !important;
  }

  .group-header-slot,
  tr.v-row-group__header,
  tbody tr.v-row-group__header:hover {
    background-color: $app-lt-blue;
  }

  .no-owners-head-row {
    color: $gray7;
  }

  .owner-name,
  .owner-name i {
    color: $gray9 !important;
  }

  .owner-name .suffix-error {
    color: $error;
  }

  .removed-owner {
    opacity: .4;
  }

  table {
    thead.simple {
      display:table-header-group;
      table-layout: fixed;

      th {
        padding: 0 12px;
      }
      th:first-child,
      td:first-child {
        padding-left: 30px;
      }
    }

    tbody > tr > td > div > tr > td,
    tbody > tr > td {
      padding: 20px 12px;
      // border-bottom: 1px solid red;
      border-radius: 0 !important;
    }

    .owner-row:not(:last-child) tr > td,
    .bottom-border {
      border-bottom: thin solid rgba(0, 0, 0, 0.12);
    }

    th:first-child,
    td:first-child {
      padding-left: 30px;
    }
    td:last-child {
      padding-right: 30px;
      padding-top: 8px;
    }
    tbody > tr.v-row-group__header,
    tbody > tr.v-row-group__header:hover {
      background: $app-lt-blue !important;
    }

    .no-owners-error {
      text-align: center;
      color: $error;
    }

    .owner-info {
      td {
        white-space: normal;
        vertical-align: top;
      }
    }
  }

  .owner-icon-name {
    display: flex;
    align-items: flex-start;
    div {
      word-break: break-word;
    }
    i {
      margin-top: -3px;
    }
  }

  .v-data-table thead,
  .v-data-table-header th {
    padding: 0 12px;
  }

  .font-light {
    color: $gray7;
    font-size: 14px;
    line-height: 22px;
    margin-left: 32px;
    font-weight: normal;
  }
  .theme--light.v-btn.v-btn--disabled {
    color: #1669bb !important;
    opacity: 0.4 !important;
  }
}

.v-menu__content {
  cursor: pointer;
}
.review-mode ::v-deep {
  table {
    th:first-child,
    td:first-child {
      padding-left: 0 !important;
    }
  }
  tbody > tr.v-row-group__header {
    margin-left: 20px !important;
    padding-left: 20px !important;
  }
}
</style>
