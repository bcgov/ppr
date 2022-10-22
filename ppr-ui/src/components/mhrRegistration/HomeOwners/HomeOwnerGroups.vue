<template>
  <div id="mhr-home-owner-groups">
    <label class="generic-label">
      Multiple Groups of Owners (Tenants in Common)
    </label>
    <ul class="my-2">
      <li>
        Select a group if you have <b>multiple groups of owners</b> (tenants in common).
      </li>
      <li>
        Leave this empty if you have <b>only one owner</b>, or <b>one group of owners</b> (sole
        ownership or joint tenancy).
      </li>
    </ul>
    <v-select
      id="home-owner-groups"
      ref="groupDropdown"
      label="Select a Group"
      v-model="ownerGroupId"
      :items="groupItems"
      :rules="groupRules"
      class="owner-groups-select mt-8 mb-0"
      filled
      @change="setOwnerGroupId($event)"
      :clearable="groupItems.length === 1"
      @click:clear="removeGroupDropdownValidation === true && groupDropdown.blur()"
      :menu-props="{ bottom: true, offsetY: true }"
      data-test-id="owner-group-select"
    ></v-select>

    <div v-if="showFractionalOwnership">
      <v-row>
        <v-col>
          <div class="generic-label mb-3">Group {{ ownerGroupId }} Details:</div>
        </v-col>
        <v-col v-show="groupState.isReadonly" class="align-right pt-0">
          <v-btn
            v-if="groupState.hasEditButton"
            id="edit-fractional-ownership"
            text
            color="primary"
            :ripple="false"
            @click="openEditFractionalOwnership()"
          >
            <v-icon small>mdi-pencil</v-icon>
            <span>Edit</span>
          </v-btn>
        </v-col>
      </v-row>
      <FractionalOwnership
        :groupId="ownerGroupId"
        :fractionalData="fractionalData"
        :isReadOnly="groupState.isReadonly"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { useInputRules } from '@/composables'
import FractionalOwnership from './FractionalOwnership.vue'
import { find } from 'lodash'
/* eslint-disable no-unused-vars */
import { MhrRegistrationFractionalOwnershipIF } from '@/interfaces/mhr-registration-interfaces'
/* eslint-enable no-unused-vars */

// Interface for readonly and Edit button states for Owner Groups
interface ReadonlyOwnerGroupStateIF {
  groupId: number,
  isReadonly: Boolean,
  hasEditButton: Boolean
}

interface FractionalOwnershipWithGroupIdIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: number
}

export default defineComponent({
  name: 'HomeOwnerGroups',
  emits: ['setOwnerGroupId'],
  components: {
    FractionalOwnership
  },
  props: {
    groupId: { type: Number },
    fractionalData: { type: Object as () => FractionalOwnershipWithGroupIdIF },
    isAddingHomeOwner: { type: Boolean }, // makes additional Group available in dropdown when adding a new homeowner
    isMhrTransfer: { type: Boolean, default: false }
  },

  setup (props, { emit }) {
    const groupDropdown = ref(null)
    const { required } = useInputRules()
    const {
      showGroups,
      getGroupDropdownItems,
      getTransferOrRegistrationHomeOwnerGroups
    } = useHomeOwners(props.isMhrTransfer)

    const localState = reactive({
      ownerGroupId: props.groupId,
      removeGroupDropdownValidation: false,
      groupItems: computed(() => getGroupDropdownItems(props.isAddingHomeOwner, props.groupId)),
      groupRules: computed(() => {
        return showGroups.value && localState.removeGroupDropdownValidation
          ? required('Select a group for this owner')
          : []
      }),
      groupFractionalData: find(getTransferOrRegistrationHomeOwnerGroups(), { groupId: props.groupId }),
      showFractionalOwnership: computed(() => Number(localState.ownerGroupId) > 0),
      allGroupsState: getTransferOrRegistrationHomeOwnerGroups()
        .map(group => {
          return {
            groupId: group.groupId,
            isReadonly: showGroups.value,
            hasEditButton: showGroups.value
          }
        })
        .concat({
          groupId: (getTransferOrRegistrationHomeOwnerGroups().length + 1),
          isReadonly: false,
          hasEditButton: false
        }) as ReadonlyOwnerGroupStateIF[],
      groupState: computed(
        () => find(localState.allGroupsState, { groupId: localState.ownerGroupId }) as ReadonlyOwnerGroupStateIF
      ),
      showEditFractionalOwnershipBtn: true
    })

    const setOwnerGroupId = (groupId: number): void => {
      emit('setOwnerGroupId', groupId)
    }

    const openEditFractionalOwnership = (): void => {
      const groupState = find(
        localState.allGroupsState, { groupId: localState.ownerGroupId }) as ReadonlyOwnerGroupStateIF
      groupState.hasEditButton = false
      groupState.isReadonly = false
    }

    return {
      openEditFractionalOwnership,
      setOwnerGroupId,
      groupDropdown,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#mhr-home-owner-groups::v-deep {
  ul {
    color: $gray7;
    font-size: 16px;
    line-height: 24px;
  }
  .owner-groups-select {
    width: 200px;
  }

  .v-icon.mdi-close {
    color: $primary-blue;
  }
}
</style>
