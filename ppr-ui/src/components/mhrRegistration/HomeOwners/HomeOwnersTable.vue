<template>
  <v-card flat rounded :class="{ 'border-error-left': showTableError || reviewedNoOwners}">
    <v-data-table
      id="mh-home-owners-table"
      class="home-owners-table"
      :class="{ 'review-mode': isReadonlyTable }"
      :headers="homeOwnersTableHeaders"
      hide-default-footer
      :items="homeOwners"
      item-key="groupId"
      :group-by="showGroups ? 'groupId' : null"
      disable-sort
      disable-pagination
    >
      <template
        v-slot:header
        v-if="isMhrTransfer && hasRemovedAllHomeOwners(homeOwners) && addedOwnerCount === 0 && !hideRemovedOwners"
      >
        <tr class="fs-14 text-center no-owners-head-row" data-test-id="no-data-msg">
          <td class="pa-6" :colspan="homeOwnersTableHeaders.length">
            No owners added yet.
          </td>
        </tr>
      </template>

      <template v-slot:group.header="{ group, items }" class="group-header-slot">
        <td
          v-if="!(disableGroupHeader(group) && (hideRemovedOwners || isReadonlyTable))"
          :colspan="4"
          class="py-1"
          :class="{'spacer-header': disableGroupHeader(group)}"
        >
          <TableGroupHeader
            :groupId="group"
            :owners="hasActualOwners(items) ? items : []"
            :showEditActions="showEditActions"
            :disableGroupHeader="disableGroupHeader(group)"
            :isMhrTransfer="isMhrTransfer"
          />
        </td>
      </template>

      <template v-slot:item="row" v-if="homeOwners.length">
        <tr v-if="isCurrentlyEditing(homeOwners.indexOf(row.item))">
          <td class="pa-0" :colspan="homeOwnersTableHeaders.length">
            <v-expand-transition>
              <AddEditHomeOwner
                :editHomeOwner="row.item"
                :isHomeOwnerPerson="!row.item.organizationName"
                :isMhrTransfer="isMhrTransfer"
                @cancel="currentlyEditingHomeOwnerId = -1"
                @remove="remove(row.item)"
              />
            </v-expand-transition>
          </td>
        </tr>

        <tr
          v-else-if="row.item.ownerId"
          :key="row.item.ownerId"
          class="owner-info"
          :data-test-id="`owner-info-${row.item.ownerId}`"
        >
          <td class="owner-name">
            <div :class="{'removed-owner': isRemovedHomeOwner(row.item)}">
              <div v-if="row.item.individualName" class="owner-icon-name">
                <v-icon class="mr-2">mdi-account</v-icon>
                <div class="font-weight-bold">
                  {{ row.item.individualName.first }}
                  {{ row.item.individualName.middle }}
                  {{ row.item.individualName.last }}
                </div>
              </div>
              <div v-else class="owner-icon-name">
                <v-icon class="mr-2">mdi-domain</v-icon>
                <div class="font-weight-bold">
                  {{ row.item.organizationName }}
                </div>
              </div>
              <div v-if="row.item.suffix" class="suffix">
                {{ row.item.suffix }}
              </div>
            </div>

            <!-- Hide Chips for Review Mode -->
            <template v-if="!isReadonlyTable || showChips">
              <v-chip
                v-if="isMhrTransfer && isAddedHomeOwner(row.item)"
                class="badge-added ml-8 mt-2"
                color="primary"
                label x-small
                text-color="white"
                data-test-id="owner-added-badge"
              >
                <b>ADDED</b>
              </v-chip>
              <v-chip
                v-if="isMhrTransfer && isRemovedHomeOwner(row.item)"
                class="badge-delete ml-8 mt-2"
                label x-small
                color="#grey lighten-2"
                text-color="$gray9"
                data-test-id="owner-removed-badge"
              >
                <b>DELETED</b>
              </v-chip>
            </template>
          </td>
          <td>
            <base-address
              :schema="addressSchema"
              :value="row.item.address"
              :class="{'removed-owner': isRemovedHomeOwner(row.item)}"
            />
          </td>
          <td>
            <div :class="{'removed-owner': isRemovedHomeOwner(row.item)}">
              {{ toDisplayPhone(row.item.phoneNumber) }}
              <span v-if="row.item.phoneExtension"> Ext {{ row.item.phoneExtension }} </span>
            </div>
          </td>
          <td v-if="showEditActions" class="row-actions text-right">

            <!-- New Owner Actions -->
            <template v-if="!isMhrTransfer || isAddedHomeOwner(row.item)">
              <v-btn
                text
                color="primary"
                class="pr-0"
                :ripple="false"
                :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                @click="openForEditing(homeOwners.indexOf(row.item))"
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
                    <v-list-item-subtitle class="pa-0" @click="remove(row.item)">
                      <v-icon small style="margin-bottom: 3px;">mdi-delete</v-icon>
                      <span class="ml-1 remove-btn-text">Remove</span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>

            <!-- Existing Owner Actions -->
            <template v-else>
              <v-btn
                v-if="!isRemovedHomeOwner(row.item)"
                text color="primary" class="pr-0"
                :ripple="false"
                :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                @click="markForRemoval(row.item)"
                data-test-id="table-edit-btn"
              >
                <v-icon small>mdi-delete</v-icon>
                <span>Delete</span>
              </v-btn>
              <v-btn
                v-if="isRemovedHomeOwner(row.item)"
                text color="primary" class="pr-0"
                :ripple="false"
                :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
                @click="undoRemoval(row.item)"
                data-test-id="table-edit-btn"
              >
                <v-icon small>mdi-undo</v-icon>
                <span>Undo</span>
              </v-btn>
            </template>
          </td>
        </tr>
        <tr v-else-if="!hideRemovedOwners">
          <td :colspan="4" class="py-1">
            <div
              v-if="showGroups"
              class="error-text my-6 text-center"
              :data-test-id="`no-owners-msg-group-${homeOwners.indexOf(row.item)}`"
            >
              Group must contain at least one owner
            </div>
            <div v-else class="my-6 text-center" data-test-id="no-owners-mgs">
              No owners added yet
            </div>
          </td>
        </tr>
      </template>
      <template v-slot:no-data>
        <div class="pa-4 text-center" data-test-id="no-data-msg">No owners added yet.</div>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { homeOwnersTableHeaders, homeOwnersTableHeadersReview } from '@/resources/tableHeaders'
import { useMhrValidations } from '@/composables'
import { BaseAddress } from '@/composables/address'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'
import { AddEditHomeOwner } from '@/components/mhrRegistration/HomeOwners'
import TableGroupHeader from '@/components/mhrRegistration/HomeOwners/TableGroupHeader.vue'
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { ActionTypes, RouteNames } from '@/enums'
/* eslint-enable no-unused-vars */
import { useActions, useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'HomeOwnersTable',
  props: {
    homeOwners: { default: () => [] },
    isAdding: { default: false },
    isReadonlyTable: { type: Boolean, default: false },
    isMhrTransfer: { type: Boolean, default: false },
    hideRemovedOwners: { type: Boolean, default: false },
    showChips: { type: Boolean, default: false }
  },
  components: {
    BaseAddress,
    AddEditHomeOwner,
    TableGroupHeader
  },
  setup (props, context) {
    const addressSchema = PartyAddressSchema

    const {
      showGroups,
      removeOwner,
      deleteGroup,
      isGlobalEditingMode,
      setGlobalEditingMode,
      hasEmptyGroup,
      hasMinimumGroups,
      editHomeOwner,
      getGroupForOwner,
      undoGroupRemoval,
      hasRemovedAllHomeOwners,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups
    } = useHomeOwners(props.isMhrTransfer)

    const { setUnsavedChanges } = useActions<any>(['setUnsavedChanges'])

    const { getMhrRegistrationValidationModel } = useGetters<any>(['getMhrRegistrationValidationModel'])

    const { getValidation, MhrSectVal, MhrCompVal } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      currentlyEditingHomeOwnerId: -1,
      reviewed: false,
      isEditingMode: computed((): boolean => localState.currentlyEditingHomeOwnerId >= 0),
      isAddingMode: computed((): boolean => props.isAdding),
      showTableError: computed((): boolean => showGroups.value && (hasMinimumGroups() || hasEmptyGroup.value)),
      reviewedNoOwners: computed((): boolean => !hasActualOwners(props.homeOwners) &&
      getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS)),
      showEditActions: computed((): boolean => !props.isReadonlyTable),
      homeOwnersTableHeaders: props.isReadonlyTable ? homeOwnersTableHeadersReview : homeOwnersTableHeaders,
      addedOwnerCount: computed((): number => {
        return getTransferOrRegistrationHomeOwners().filter(owner => owner.action === ActionTypes.ADDED).length
      }),
      addedGroupCount: computed((): number => {
        return getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action === ActionTypes.ADDED).length
      })
    })

    const remove = (item): void => {
      localState.currentlyEditingHomeOwnerId = -1
      setUnsavedChanges(true)

      const group = getGroupForOwner(item.groupId)
      removeOwner(item)

      // Remove the Group if it was Added, and we are removing the last Owner
      if (group?.owners.length === 0 && group?.action === ActionTypes.ADDED) {
        deleteGroup(item.groupId)
      }
    }

    const markForRemoval = (item: MhrRegistrationHomeOwnerIF): void => {
      editHomeOwner(
        { ...item, action: ActionTypes.REMOVED },
        item.groupId
      )
    }

    const undoRemoval = async (item): Promise<void> => {
      await editHomeOwner(
        { ...item, action: null },
        item.groupId
      )
      await undoGroupRemoval(item.groupId)
    }

    const openForEditing = (index: number) => {
      localState.currentlyEditingHomeOwnerId = index
    }

    const isCurrentlyEditing = (index: number): boolean => {
      return index === localState.currentlyEditingHomeOwnerId
    }

    // To render Group table header the owners array must not be empty
    // check for at least one owner with an id
    // This util function will help to show Owners: 0 in the table header
    const hasActualOwners = (owners: MhrRegistrationHomeOwnerIF[]): boolean => {
      return owners.length > 0 && owners[0]?.ownerId !== undefined
    }

    const isAddedHomeOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.ADDED
    }

    const isAddedHomeOwnerGroup = (groupId: number): boolean => {
      return getTransferOrRegistrationHomeOwnerGroups()
        .find(group => group.groupId === groupId)?.action === ActionTypes.ADDED
    }

    const isRemovedHomeOwner = (item: MhrRegistrationHomeOwnerIF): boolean => {
      return item.action === ActionTypes.REMOVED
    }

    const hasNoGroupInterest = (groupId: number): boolean => {
      const group = getTransferOrRegistrationHomeOwnerGroups().find(group => group.groupId === groupId)
      return !group.interestNumerator && !group.interestDenominator
    }

    const disableGroupHeader = (groupId: number): boolean => {
      return hasRemovedAllHomeOwners(props.homeOwners) &&
        isAddedHomeOwnerGroup(groupId) &&
        hasNoGroupInterest(groupId) &&
        localState.addedGroupCount <= 1
    }

    watch(
      () => localState.currentlyEditingHomeOwnerId,
      () => {
        setGlobalEditingMode(localState.isEditingMode)
      }
    )

    // When a change is made to homeOwners, check if any actions have changed, if so set flag
    watch(() => props.homeOwners, () => {
      setUnsavedChanges(props.homeOwners.some(owner => !!owner.action))
    })

    return {
      ActionTypes,
      addressSchema,
      toDisplayPhone,
      openForEditing,
      isCurrentlyEditing,
      showGroups,
      hasEmptyGroup,
      hasActualOwners,
      remove,
      deleteGroup,
      isGlobalEditingMode,
      hasMinimumGroups,
      isAddedHomeOwner,
      isRemovedHomeOwner,
      markForRemoval,
      undoRemoval,
      hasRemovedAllHomeOwners,
      isAddedHomeOwnerGroup,
      disableGroupHeader,
      getTransferOrRegistrationHomeOwners,
      getTransferOrRegistrationHomeOwnerGroups,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.home-owners-table ::v-deep {
  .spacer-header {
    border-color: $gray1 !important;
    background-color: $gray1 !important;
  }

  tr.v-row-group__header,
  tbody tr.v-row-group__header:hover {
    background-color: #e2e8ee;
  }

  .no-owners-head-row {
    color: $gray7;
  }

  .owner-name,
  .owner-name i {
    color: $gray9 !important;
  }

  .removed-owner {
    opacity: .4;
  }

  table {
    tbody > tr > td {
      padding: 20px 12px;
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
      background: #e2e8ee !important;
    }

    .no-owners-error {
      text-align: center;
      color: $error;
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
  .owner-info {
    td {
      white-space: normal;
      vertical-align: top;
    }
  }

  .v-data-table-header th {
    padding: 0 12px;
  }

  .suffix {
    color: $gray7;
    font-size: 14px;
    line-height: 22px;
    margin-left: 32px;
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
