<template>
  <div :id="'mhr-home-edit-owners-group-' + groupId" class="group-header">
    <BaseDialog
      :setDisplay="showDeleteGroupDialog"
      @proceed="cancelOrProceed($event, groupId)"
      :setOptions="{
        title: 'Delete Group',
        text:
          'Deleting a group also deletes all of the owners in the group and cannot be undone. ' +
          'All subsequent groups will be re-numbered.' +
          '<br><br>' +
          'If you wish to keep the owners of this group move the ' +
          'owners to a different group prior to deletion.',
        acceptText: 'Delete Group',
        cancelText: 'Cancel'
      }"
    />
    <div v-if="!isEditingGroupMode" class="group-header-summary">
      <div>
        <span class="mr-2 font-weight-bold">Group {{ groupId }}</span>
        |
        <span class="ma-2">Owners: {{ owners.length }} </span>
        |
        <span class="ma-2">Group Tenancy Type: </span>
        |
        <span class="ma-2">
          {{ getOwnershipInterest(Number(groupId) - 1) }}
        </span>
      </div>

      <div>
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
            <v-btn
              text
              v-on="on"
              color="primary"
              class="pa-0"
              :disabled="isGlobalEditingMode"
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
                <v-icon small>mdi-delete</v-icon>
                <span class="ml-1 remove-btn-text">Delete Group</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>
    <div v-else>
      <v-row>
        <v-col cols="3">
          <label class="generic-label"> Edit Group </label>
        </v-col>
        <v-col cols="9">
          <label class="generic-label"> Group {{ groupId }} Details </label>
          <div>
            Fractional Ownership Placeholder
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <div class="form__row form__btns">
            <v-btn
              color="primary"
              class="ml-auto"
              :ripple="false"
              large
              @click="done()"
            >
              Done
            </v-btn>
            <v-btn
              :ripple="false"
              large
              color="primary"
              outlined
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
import { useHomeOwners } from '@/composables/mhrRegistration'
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'

export default defineComponent({
  name: 'TableGroupHeader',
  props: {
    groupId: { default: '' },
    owners: { default: [] }
  },
  components: {
    BaseDialog
  },
  setup () {
    const {
      isGlobalEditingMode,
      setGlobalEditingMode,
      deleteGroup
    } = useHomeOwners()

    const localState = reactive({
      isEditingGroupMode: computed(
        (): boolean => localState.currentlyEditingGroupId >= 0
      ),
      currentlyEditingGroupId: -1,
      showDeleteGroupDialog: false
    })

    const openGroupForEditing = groupId => {
      localState.currentlyEditingGroupId = groupId
    }
    // Get interest based on idex of the group
    const getOwnershipInterest = (index: number): string => {
      const interest = '' // getMhrRegistrationHomeOwnerGroups.value[index]?.interest
      return interest ? 'Interest: ' + interest : ''
    }

    const done = (): void => {
      localState.currentlyEditingGroupId = -1
    }

    const cancel = (): void => {
      localState.currentlyEditingGroupId = -1
    }

    watch(
      () => localState.currentlyEditingGroupId,
      () => {
        setGlobalEditingMode(localState.isEditingGroupMode)
      }
    )

    // Close Delete Group dialog or proceed to deleting a Group
    const cancelOrProceed = (proceed: boolean, groupId: string) => {
      if (proceed) {
        deleteGroup(groupId)
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
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
.group-header::v-deep {
  .group-header-summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
