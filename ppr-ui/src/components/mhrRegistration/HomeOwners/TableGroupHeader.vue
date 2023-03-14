<template>
  <div v-if="!disableGroupHeader" :id="'mhr-home-edit-owners-group-' + groupId" class="group-header">
    <BaseDialog
      :setDisplay="showDeleteGroupDialog"
      @proceed="cancelOrProceed($event, groupId)"
      :setOptions="{
        title: 'Delete Group',
        text:
          'Deleting a group also deletes all of the owners in the group. ' +
          'All subsequent groups will be re-numbered.' +
          '<br><br>' +
          'If there are any newly added owerns in the group that you wish to keep, move those ' +
          'owners to a different group prior to deletion.',
        acceptText: 'Delete Group',
        cancelText: 'Cancel'
      }"
    />
    <div v-if="!isEditGroupMode" class="group-header-summary">
      <div>
        <v-chip
          v-if="isMhrTransfer && isRemovedHomeOwnerGroup(group)"
          class="badge-delete mr-4"
          :class="{ 'ml-8 mr-n4': !showEditActions }"
          label x-small
          color="#grey lighten-2"
          data-test-id="owner-removed-badge"
        >
          <b>DELETED</b>
        </v-chip>
        <v-chip
          v-else-if="isMhrTransfer && isAddedHomeOwnerGroup(group)"
          class="badge-added mr-4"
          :class="{ 'ml-8 mr-n2': !showEditActions }"
          label x-small
          color="primary"
          data-test-id="owner-added-badge"
        >
          <b>ADDED</b>
        </v-chip>
        <span
          v-if="!(isMhrTransfer && isRemovedHomeOwnerGroup(group))"
          :class="{'removed-owner-group': isRemovedHomeOwnerGroup(group)}"
        >
          <span class="pr-4 font-weight-bold group-id" :class="{ 'pl-8': !showEditActions }">
            Group {{ groupNumber }}
          </span>
          |
          <span class="px-4">Owners: {{ isRemovedHomeOwnerGroup(group) ? '0' : ownersCount }}</span>
          |
          <span class="px-4" :class="{ 'ml-1': !showEditActions }">
            Group Tenancy Type: {{ isRemovedHomeOwnerGroup(group) ? 'N/A' : getGroupTenancyType(group) }}
          </span>
          |
          <span class="px-4" :class="{ 'error-text': hasUndefinedInterest && !isRemovedHomeOwnerGroup(group) }">
            Interest: {{ isRemovedHomeOwnerGroup(group) ? 'N/A' : getOwnershipInterest() }}
          </span>
        </span>
        <span
          v-else
          class="font-weight-bold removed-owner-group"
          :class="{ 'ml-3' : !showEditActions }">Previous Owner Group</span>
      </div>

      <!-- Default Actions -->
      <div v-show="showEditActions && !isMhrTransfer" class="mr-n4">
        <v-btn
          text
          color="primary"
          class="pr-0"
          :ripple="false"
          :disabled="isGlobalEditingMode"
          @click="openGroupForEditing(groupId)"
        >
          <v-icon small>mdi-pencil</v-icon>
          <span>Edit</span>
          <v-divider class="ma-0 pl-3" vertical />
        </v-btn>

        <v-menu offset-y left nudge-bottom="0" class="delete-group-menu">
          <template v-slot:activator="{ on }">
            <v-btn text v-on="on" color="primary" class="pa-0" :disabled="isGlobalEditingMode">
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>

          <!-- More actions drop down list -->
          <v-list class="actions-dropdown actions__more-actions">
            <v-list-item class="my-n2">
              <v-list-item-subtitle class="pa-0" @click="showDeleteGroupDialog = true">
                <v-icon small style="margin-bottom: 3px;">mdi-delete</v-icon>
                <span class="ml-1 remove-btn-text">Delete Group</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <!-- Mhr Transfer Actions -->
      <div v-if="showEditActions && isMhrTransfer && !isRemovedHomeOwnerGroup(group)" class="mr-n4">
        <v-btn
          text
          color="primary"
          class="pr-0"
          :ripple="false"
          :disabled="isGlobalEditingMode"
          @click="showDeleteGroupDialog = true"
        >
          <v-icon small>mdi-delete</v-icon>
          <span>Delete Group</span>
          <v-divider class="ma-0 pl-3" vertical />
        </v-btn>

        <v-menu offset-y left nudge-bottom="0" class="delete-group-menu">
          <template v-slot:activator="{ on }">
            <v-btn text v-on="on" color="primary" class="pa-0" :disabled="isGlobalEditingMode">
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>

          <!-- More actions drop down list -->
          <v-list class="actions-dropdown actions__more-actions">
            <v-list-item class="my-n2">
              <v-list-item-subtitle class="pa-0" @click="openGroupForEditing(groupId)">
                <v-icon small style="margin-bottom: 3px;">mdi-pencil</v-icon>
                <span class="ml-1 remove-btn-text">Edit Group Details</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <!-- Undo removal action -->
      <div v-else-if="showEditActions && isMhrTransfer">
        <v-btn
          text color="primary"
          class="pr-0"
          :ripple="false"
          @click="undoGroupRemoval(groupId, true)"
          :disabled="isGlobalEditingMode"
          data-test-id="group-header-undo-btn"
        >
          <v-icon small>mdi-undo</v-icon>
          <span>Undo</span>
        </v-btn>
      </div>
    </div>

    <!-- Group Edit -->
    <div v-else class="py-8">
      <v-row>
        <v-col cols="3">
          <label class="generic-label"> Edit Group </label>
        </v-col>
        <v-col cols="9">
          <label class="generic-label"> Group {{ groupId }} Details: </label>

          <v-form class="mt-5" ref="homeFractionalOwnershipForm" v-model="isHomeFractionalOwnershipValid">
            <FractionalOwnership
              :groupId="groupId"
              :fractionalData="fractionalData"
              :isMhrTransfer="isMhrTransfer"
            />
          </v-form>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <div class="form__row form__btns">
            <v-btn color="primary" class="ml-auto" :ripple="false" large @click="done()">
              Done
            </v-btn>
            <v-btn :ripple="false" large color="primary" outlined @click="cancel()">
              Cancel
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script lang="ts">
import { BaseDialog } from '@/components/dialogs'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import FractionalOwnership from './FractionalOwnership.vue'
import { find } from 'lodash'
/* eslint-disable no-unused-vars */
import { MhrRegistrationFractionalOwnershipIF, MhrHomeOwnerGroupIF } from '@/interfaces/mhr-registration-interfaces'
import { ActionTypes } from '@/enums'
import { toTitleCase } from '@/utils'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'TableGroupHeader',
  props: {
    groupId: { default: 1 },
    groupNumber: { default: 1 },
    owners: { default: [] },
    showEditActions: { type: Boolean, default: true },
    isMhrTransfer: { type: Boolean, default: false },
    disableGroupHeader: { type: Boolean, default: false }
  },
  components: {
    BaseDialog,
    FractionalOwnership
  },
  setup (props, context) {
    const {
      isGlobalEditingMode,
      setGlobalEditingMode,
      deleteGroup,
      setGroupFractionalInterest,
      markGroupForRemoval,
      undoGroupRemoval,
      hasUndefinedGroupInterest,
      getTransferOrRegistrationHomeOwnerGroups,
      getHomeTenancyType,
      getGroupTenancyType
    } = useHomeOwners(props.isMhrTransfer)

    const homeFractionalOwnershipForm = ref(null)

    const localState = reactive({
      isEditGroupMode: false,
      showDeleteGroupDialog: false,
      isHomeFractionalOwnershipValid: false,
      fractionalData: {} as MhrRegistrationFractionalOwnershipIF,
      group: computed((): MhrHomeOwnerGroupIF => {
        return find(getTransferOrRegistrationHomeOwnerGroups(), { groupId: props.groupId })
      }),
      ownersCount: computed((): number => {
        return props.owners.filter(owner => owner.action !== ActionTypes.REMOVED && !!owner.ownerId).length
      }),
      hasUndefinedInterest: computed((): boolean => {
        return hasUndefinedGroupInterest(getTransferOrRegistrationHomeOwnerGroups()) &&
          !(localState.group.interestNumerator && localState.group.interestDenominator)
      })
    })

    const openGroupForEditing = (): void => {
      localState.fractionalData = {
        type: localState.group?.type || '',
        interest: localState.group?.interest || 'Undivided',
        interestNumerator: localState.group?.interestNumerator || null,
        interestDenominator: localState.group?.interestDenominator || null
      } as MhrRegistrationFractionalOwnershipIF

      localState.isEditGroupMode = true
    }

    const getOwnershipInterest = (): string => {
      const { interest, interestNumerator, interestDenominator } = localState.group
      if (!interestNumerator || !interestDenominator) return 'N/A'

      return `${toTitleCase(interest)} ${interestNumerator}/${interestDenominator}`
    }

    const isRemovedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
      return group.action === ActionTypes.REMOVED
    }

    const isAddedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
      return group.action === ActionTypes.ADDED
    }

    const done = (): void => {
      // @ts-ignore - function exists
      context.refs.homeFractionalOwnershipForm.validate()

      if (localState.isHomeFractionalOwnershipValid) {
        localState.isEditGroupMode = false
        setGroupFractionalInterest(props.groupId, localState.fractionalData)
      }
    }

    const cancel = (): void => {
      localState.isEditGroupMode = false
    }

    watch(
      () => localState.isEditGroupMode,
      () => {
        setGlobalEditingMode(localState.isEditGroupMode)
      }
    )

    // Close Delete Group dialog or proceed to deleting a Group
    const cancelOrProceed = (proceed: boolean, groupId: number): void => {
      if (proceed) {
        if (props.isMhrTransfer && localState.group?.action !== ActionTypes.ADDED) {
          markGroupForRemoval(groupId)
        } else deleteGroup(groupId)

        localState.showDeleteGroupDialog = false
      } else {
        localState.showDeleteGroupDialog = false
      }
    }

    return {
      getOwnershipInterest,
      openGroupForEditing,
      isGlobalEditingMode,
      done,
      cancel,
      cancelOrProceed,
      homeFractionalOwnershipForm,
      isRemovedHomeOwnerGroup,
      isAddedHomeOwnerGroup,
      undoGroupRemoval,
      getHomeTenancyType,
      getGroupTenancyType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.group-header::v-deep {
  .group-header-summary {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .group-id {
      color: $gray9 !important;
    }
  }
  .theme--light.v-text-field--filled.background-white > .v-input__control > .v-input__slot {
    background: white;
  }
  .removed-owner-group {
    opacity: .4;
    color: $gray9 !important;
  }
}
</style>
