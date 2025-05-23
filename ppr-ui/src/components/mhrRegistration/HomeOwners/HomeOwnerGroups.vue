<template>
  <div id="mhr-home-owner-groups">
    <label class="generic-label">
      Tenants in Common
    </label>
    <ul class="my-2 pl-6">
      <li>
        Select a group if the tenancy type is tenants in common.
      </li>
      <li>
        <b>Note</b>: Do not select a group if this is a sole ownership, or joint tenancy.
      </li>
    </ul>
    <v-select
      id="home-owner-groups"
      ref="groupDropdown"
      v-model="ownerGroupId"
      label="Select a Group"
      :items="groupItems"
      :rules="groupRules"
      class="owner-groups-select mt-8 mb-0"
      variant="filled"
      color="primary"
      :clearable="groupItems.length === 1"
      :clear-icon="'mdi-close'"
      persistent-clear
      data-test-id="owner-group-select"
      @update:model-value="setOwnerGroupId($event)"
      @click:clear="removeGroupDropdownValidation === true && groupDropdown.blur()"
    />

    <div v-if="showFractionalOwnership">
      <v-row>
        <v-col>
          <div class="generic-label mb-3">
            Group {{ getGroupNumberById(ownerGroupId) }} Details:
          </div>
        </v-col>
        <v-col
          v-show="groupState?.isReadonly && isDefinedGroup"
          class="align-right pt-0"
        >
          <v-btn
            v-if="groupState?.hasEditButton"
            id="edit-fractional-ownership"
            variant="plain"
            color="primary"
            :ripple="false"
            @click="openEditFractionalOwnership()"
          >
            <v-icon size="small">
              mdi-pencil
            </v-icon>
            <span>Edit</span>
          </v-btn>
        </v-col>
      </v-row>
      <FractionalOwnership
        :key="ownerGroupId"
        :group-id="ownerGroupId"
        :fractional-data="fractionalData"
        :is-read-only="groupState?.isReadonly && isDefinedGroup"
        :is-mhr-transfer="isMhrTransfer"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs } from 'vue'
import { useHomeOwners, useMhrCorrections } from '@/composables/mhrRegistration'
import { useInputRules } from '@/composables'
import FractionalOwnership from './FractionalOwnership.vue'
import { find } from 'lodash'
import type { MhrRegistrationFractionalOwnershipIF } from '@/interfaces/mhr-registration-interfaces'


// Interface for readonly and Edit button states for Owner Groups
interface ReadonlyOwnerGroupStateIF {
  groupId: number,
  isReadonly: boolean,
  hasEditButton: boolean
}

interface FractionalOwnershipWithGroupIdIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: number
}

export default defineComponent({
  name: 'HomeOwnerGroups',
  components: {
    FractionalOwnership
  },
  props: {
    groupId: {
      type: Number,
      default: null
    },
    fractionalData: {
      type: Object as () => FractionalOwnershipWithGroupIdIF,
      default: () => {}
    },
    isAddingHomeOwner: {
      type: Boolean,
      default: false
    }, // makes additional Group available in dropdown when adding a new homeowner
    isMhrTransfer: {
      type: Boolean,
      default: false
    }
  },
  emits: ['setOwnerGroupId'],

  setup (props, { emit }) {
    const groupDropdown = ref(null)
    const { required } = useInputRules()
    const { isMhrCorrection } = useMhrCorrections()
    const {
      showGroups,
      getGroupDropdownItems,
      hasUndefinedGroupInterest,
      getTransferOrRegistrationHomeOwnerGroups,
      getGroupNumberById
    } = useHomeOwners(props.isMhrTransfer, isMhrCorrection.value)

    const localState = reactive({
      ownerGroupId: props.groupId,
      removeGroupDropdownValidation: false,
      groupItems: computed(() => getGroupDropdownItems(props.isAddingHomeOwner, props.groupId)),
      groupRules: computed(() => {
        return (showGroups.value && localState.groupItems.length >= 2 &&
        !hasUndefinedGroupInterest(getTransferOrRegistrationHomeOwnerGroups())) || // Default state
        localState.groupItems.length >= 3 // Safety check, to catch undefined groups after marking groups for removal
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
      showEditFractionalOwnershipBtn: true,
      isDefinedGroup: computed((): boolean => {
        return !!localState.groupFractionalData?.interestNumerator &&
          !!localState.groupFractionalData?.interestDenominator
      })
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
      getGroupNumberById,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(#mhr-home-owner-groups) {
  ul {
    color: $gray7;
    font-size: 16px;
    line-height: 24px;
  }

  .v-icon.mdi-close {
    color: $primary-blue;
  }
}
.owner-groups-select {
  max-width: 275px;
}
</style>
