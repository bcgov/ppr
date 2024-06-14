<template>
  <div
    v-if="!disableGroupHeader"
    :id="'mhr-home-edit-owners-group-' + groupId"
    class="group-header"
  >
    <BaseDialog
      setAttach="#mhr-home-owners-list"
      :setDisplay="showDeleteGroupDialog"
      :setOptions="{
        title: 'Delete Group',
        text:
          'Deleting a group also deletes all of the owners in the group. ' +
          'All subsequent groups will be re-numbered.' +
          '<br><br>' +
          'If there are any newly added owners in the group that you wish to keep, move those ' +
          'owners to a different group prior to deletion.',
        acceptText: 'Delete Group',
        cancelText: 'Cancel'
      }"
      @proceed="cancelOrProceed($event, groupId)"
    />
    <div
      v-if="!isEditGroupMode"
      class="group-header-summary"
    >
      <!-- Group Information -->
      <div>
        <!-- Show Information Chips for MHR Transfers -->
        <template v-if="isMhrTransfer || isMhrCorrection">
          <InfoChip
            :action="group.action"
            :class="{ 'ml-8 mr-n2': !showEditActions }"
          />
        </template>

        <span
          v-if="!((isMhrTransfer || isMhrCorrection) && isRemovedHomeOwnerGroup(group))"
          :class="{'removed-owner-group': isRemovedHomeOwnerGroup(group)}"
        >
          <span
            class="pr-4 font-weight-bold group-id"
            :class="{ 'pl-8': !showEditActions }"
          >
            Group {{ groupNumber }}
          </span>
          |
          <span class="px-4">Owners: {{ isRemovedHomeOwnerGroup(group) ? '0' : ownersCount }}</span>
          |
          <span
            class="px-4"
            :class="{ 'ml-1': !showEditActions }"
          >
            Group Tenancy Type: {{ isRemovedHomeOwnerGroup(group) ? 'N/A' : getGroupTenancyType(group) }}
          </span>
          |
          <span
            class="px-4"
            :class="{ 'error-text': hasUndefinedInterest && !isRemovedHomeOwnerGroup(group) }"
          >
            Interest: {{ isRemovedHomeOwnerGroup(group) ? 'N/A' : getOwnershipInterest() }}
          </span>
        </span>
        <span
          v-else
          class="font-weight-bold removed-owner-group"
          :class="{ 'ml-3' : !showEditActions }"
        >{{ previousOwnersLabel }}</span>
      </div>

      <!-- MhRegistration Actions -->
      <div v-show="showEditActions && !isMhrTransfer && !group.action">
        <v-btn
          variant="plain"
          color="primary"
          class="pr-0"
          :ripple="false"
          :disabled="isGlobalEditingMode"
          @click="openGroupForEditing()"
        >
          <v-icon size="small">
            mdi-pencil
          </v-icon>
          <span v-if="isMhrCorrection">{{ correctAmendLabel }} Group Details</span>
          <span v-else>Edit</span>
          <v-divider
            class="ma-0 pl-3"
            vertical
          />
        </v-btn>

        <v-menu
          location="bottom right"
          class="delete-group-menu"
        >
          <template #activator="{ props }">
            <v-btn
              variant="plain"
              color="primary"
              class="pa-0"
              :disabled="isGlobalEditingMode"
              v-bind="props"
            >
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>

          <!-- More actions drop down list -->
          <v-list class="actions-dropdown actions__more-actions">
            <v-list-item class="my-n2">
              <v-list-item-subtitle
                class="pa-0"
                @click="showDeleteGroupDialog = true"
              >
                <v-icon
                  size="small"
                  class="mb-1"
                >
                  mdi-delete
                </v-icon>
                <span class="ml-1 remove-btn-text">Delete Group</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <!-- Mhr Correction Actions -->
      <div
        v-if="showEditActions && isMhrCorrection && isAddedHomeOwnerGroup(group) &&
          !isRemovedHomeOwnerGroup(group) && !isChangedOwnerGroup(group)"
      >
        <v-btn
          variant="plain"
          color="primary"
          class="pr-0"
          :ripple="false"
          :disabled="isGlobalEditingMode"
          data-test-id="group-edit-btn"
          @click="openGroupForEditing()"
        >
          <v-icon size="small">
            mdi-pencil
          </v-icon>
          <span>Edit Group Details</span>
          <v-divider
            class="ma-0 pl-3"
            vertical
          />
        </v-btn>

        <v-menu
          location="bottom right"
          class="delete-group-menu"
        >
          <template #activator="{ props }">
            <v-btn
              variant="plain"
              color="primary"
              class="pa-0"
              :disabled="isGlobalEditingMode"
              v-bind="props"
            >
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>

          <!-- More actions drop down list -->
          <v-list class="actions-dropdown actions__more-actions">
            <v-list-item class="my-n2">
              <v-list-item-subtitle
                class="pa-0"
                @click="showDeleteGroupDialog = true"
              >
                <v-icon
                  size="small"
                  style="margin-bottom: 3px;"
                >
                  mdi-delete
                </v-icon>
                <span class="ml-1 remove-btn-text">Delete Group</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <!-- Mhr Transfer Actions -->
      <div
        v-else-if="showEditActions && isMhrTransfer &&
          !isRemovedHomeOwnerGroup(group) && !isChangedOwnerGroup(group)"
      >
        <v-btn
          variant="plain"
          color="primary"
          class="pr-0"
          :ripple="false"
          :disabled="isGlobalEditingMode"
          data-test-id="group-delete-btn"
          @click="showDeleteGroupDialog = true"
        >
          <v-icon size="small">
            mdi-delete
          </v-icon>
          <span>Delete Group</span>
          <v-divider
            class="ma-0 pl-3"
            vertical
          />
        </v-btn>

        <v-menu
          location="bottom right"
          class="delete-group-menu"
        >
          <template #activator="{ props }">
            <v-btn
              variant="plain"
              color="primary"
              class="pa-0"
              :disabled="isGlobalEditingMode"
              v-bind="props"
            >
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>

          <!-- More actions drop down list -->
          <v-list class="actions-dropdown actions__more-actions">
            <v-list-item class="my-n2">
              <v-list-item-subtitle
                class="pa-0"
                @click="openGroupForEditing()"
              >
                <v-icon
                  size="small"
                  style="margin-bottom: 3px;"
                >
                  mdi-pencil
                </v-icon>
                <span class="ml-1 remove-btn-text">Edit Group Details</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <!-- Group Actions -->
      <div v-else-if="showEditActions && (isMhrTransfer || (isMhrCorrection && !!group.action))">
        <!-- Additional actions for changed/corrected owner group -->
        <template v-if="isChangedOwnerGroup(group) || isCorrectedOwnerGroup(group)">
          <v-btn
            variant="plain"
            color="primary"
            :ripple="false"
            :disabled="isGlobalEditingMode"
            data-test-id="group-header-undo-btn"
            @click="undoGroupChanges(groupId)"
          >
            <v-icon size="small">
              mdi-undo
            </v-icon>
            <span>Undo</span>
            <v-divider
              class="ma-0 pl-3 mr-n4"
              vertical
            />
          </v-btn>

          <v-menu
            location="bottom right"
            class="delete-group-menu"
          >
            <template #activator="{ props }">
              <v-btn
                variant="plain"
                color="primary"
                class="pa-0"
                :disabled="isGlobalEditingMode"
                v-bind="props"
              >
                <v-icon>mdi-menu-down</v-icon>
              </v-btn>
            </template>

            <!-- More actions drop down list -->
            <v-list class="actions-dropdown actions__more-actions">
              <v-list-item class="my-n2">
                <v-list-item-subtitle
                  class="pa-0"
                  @click="openGroupForEditing()"
                >
                  <v-icon
                    size="small"
                    style="margin-bottom: 3px;"
                  >
                    mdi-pencil
                  </v-icon>
                  <span
                    v-if="isMhrCorrection"
                    class="ml-1 remove-btn-text"
                  >{{ correctAmendLabel }} Group Details</span>
                  <span
                    v-else
                    class="ml-1 remove-btn-text"
                  >Edit Group Details</span>
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="my-n2">
                <v-list-item-subtitle
                  class="pa-0"
                  @click="showDeleteGroupDialog = true"
                >
                  <v-icon
                    size="small"
                    style="margin-bottom: 3px;"
                  >
                    mdi-delete
                  </v-icon>
                  <span class="ml-1 remove-btn-text">Delete Group</span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>

        <!-- Undo removal actions-->
        <v-btn
          v-else
          variant="plain"
          color="primary"
          class="mr-2"
          :ripple="false"
          :disabled="isGlobalEditingMode"
          data-test-id="group-header-undo-btn"
          @click="undoGroupChanges(groupId, true)"
        >
          <v-icon size="small">
            mdi-undo
          </v-icon>
          <span>Undo</span>
        </v-btn>
      </div>
    </div>

    <!-- Group Edit -->
    <div
      v-else
      class="py-8"
    >
      <v-row>
        <v-col cols="3">
          <label class="generic-label"> Edit Group </label>
        </v-col>
        <v-col cols="9">
          <label class="generic-label"> Group {{ groupId }} Details: </label>

          <v-form
            ref="homeFractionalOwnershipForm"
            v-model="isHomeFractionalOwnershipValid"
            class="mt-5"
          >
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
          <div class="form__row form__btns float-right">
            <v-btn
              color="primary"
              class="ml-auto mx-2"
              :ripple="false"
              size="large"
              @click="done()"
            >
              Done
            </v-btn>
            <v-btn
              :ripple="false"
              size="large"
              color="primary"
              variant="outlined"
              @click="cancel()"
            >
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
import { InfoChip } from '@/components/common'
import { useHomeOwners, useMhrCorrections, useTransferOwners } from '@/composables'
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import FractionalOwnership from './FractionalOwnership.vue'
import { find } from 'lodash'
import {
  FormIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  MhrRegistrationHomeOwnerGroupIF
} from '@/interfaces/'
import { ActionTypes } from '@/enums'
import { toTitleCase } from '@/utils'

export default defineComponent({
  name: 'TableGroupHeader',
  components: {
    BaseDialog,
    FractionalOwnership,
    InfoChip
  },
  props: {
    groupId: {
      type: Number,
      default: 1
    },
    groupNumber: {
      type: Number,
      default: 1
    },
    owners: {
      type: Array as () => MhrRegistrationHomeOwnerIF[],
      default: () => []
    },
    ownerGroups: {
      type: Array as () => MhrRegistrationHomeOwnerGroupIF[],
      default: () => []
    },
    showEditActions: {
      type: Boolean,
      default: true
    },
    isMhrTransfer: {
      type: Boolean,
      default: false
    },
    disableGroupHeader: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const {
      isMhrCorrection,
      isStaffCorrection,
      isClientCorrection,
      correctAmendLabel
    } = useMhrCorrections()
    const {
      isGlobalEditingMode,
      setGlobalEditingMode,
      deleteGroup,
      setGroupFractionalInterest,
      markGroupForRemoval,
      undoGroupChanges,
      hasUndefinedGroupInterest,
      getHomeTenancyType,
      getGroupTenancyType,
      getCurrentGroupById,
      isCorrectedOwnerGroup
    } = useHomeOwners(props.isMhrTransfer, (isStaffCorrection.value || isClientCorrection.value))
    const {
      isSOorJT,
      groupHasAllAddedOwners,
      hasCurrentGroupChanges,
      isAddedHomeOwnerGroup,
      isRemovedHomeOwnerGroup,
      isChangedOwnerGroup
    } = useTransferOwners()

    const homeFractionalOwnershipForm = ref(null) as FormIF

    const localState = reactive({
      isEditGroupMode: false,
      showDeleteGroupDialog: false,
      isHomeFractionalOwnershipValid: false,
      fractionalData: {} as MhrRegistrationFractionalOwnershipIF,
      group: computed((): MhrHomeOwnerGroupIF => {
        return find(props.ownerGroups, { groupId: props.groupId })
      }),
      ownersCount: computed((): number => {
        return props.owners.filter(owner => owner.action !== ActionTypes.REMOVED && !!owner.ownerId).length
      }),
      hasUndefinedInterest: computed((): boolean => {
        return hasUndefinedGroupInterest(props.ownerGroups) &&
          !(localState.group.interestNumerator && localState.group.interestDenominator)
      }),
      previousOwnersLabel: computed((): string => {
        return isSOorJT.value ? 'Previous Owners' : 'Previous Owner Group'
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
      const interestText = toTitleCase(interest) || 'Undivided'

      return `${interestText} ${interestNumerator}/${interestDenominator}`
    }

    const done = (): void => {
      homeFractionalOwnershipForm.value?.validate()

      if (localState.isHomeFractionalOwnershipValid) {
        localState.isEditGroupMode = false
        setGroupFractionalInterest(
          props.groupId,
          localState.fractionalData,
          hasCurrentGroupChanges(getCurrentGroupById(props.groupId), localState.fractionalData)
        )
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
        // Delete the group entirely if it contained ONLY newly added owners
        if ((props.isMhrTransfer || isMhrCorrection.value) &&
          (localState.group?.action !== ActionTypes.ADDED && !groupHasAllAddedOwners(localState.group))
        ) {
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
      isMhrCorrection,
      correctAmendLabel,
      isCorrectedOwnerGroup,
      isGlobalEditingMode,
      done,
      cancel,
      cancelOrProceed,
      homeFractionalOwnershipForm,
      undoGroupChanges,
      getHomeTenancyType,
      getGroupTenancyType,
      isChangedOwnerGroup,
      isAddedHomeOwnerGroup,
      isRemovedHomeOwnerGroup,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

:deep(.group-header-summary) {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .group-id {
    color: $gray9 !important;
  }
}

:deep(.theme--light.v-text-field--filled.background-white > .v-input__control > .v-input__slot) {
  background: white;
}

:deep(.removed-owner-group) {
  opacity: .4;
  color: $gray9 !important;
}
</style>
