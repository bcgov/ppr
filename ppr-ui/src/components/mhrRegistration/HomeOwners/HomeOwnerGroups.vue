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
      @click:clear="groupDropdown.blur()"
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
import { useGetters } from 'vuex-composition-helpers'
import { find } from 'lodash'
/* eslint-disable no-unused-vars */
import { MhrRegistrationFractionalOwnershipIF } from '@/interfaces/mhr-registration-interfaces'
/* eslint-enable no-unused-vars */

// Interface for readonly and Edit button states for Owner Groups
interface ReadonlyOwnerGroupStateIF {
  groupId: string,
  isReadonly: Boolean,
  hasEditButton: Boolean
}

interface FractionalOwnershipWithGroupIdIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: string
}

export default defineComponent({
  name: 'HomeOwnerGroups',
  emits: ['setOwnerGroupId'],
  components: {
    FractionalOwnership
  },
  props: {
    groupId: { type: String },
    fractionalData: { type: Object as () => FractionalOwnershipWithGroupIdIF },
    isAddingHomeOwner: { type: Boolean } // makes additional Group available in dropdown when adding a new home owner
  },

  setup (props, { emit }) {
    const { getMhrRegistrationHomeOwnerGroups } = useGetters<any>(['getMhrRegistrationHomeOwnerGroups'])
    const groupDropdown = ref(null)

    const { required } = useInputRules()
    const { getGroupDropdownItems, showGroups } = useHomeOwners()
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]

    const localState = reactive({
      ownerGroupId: props.groupId,
      groupItems: computed(() => getGroupDropdownItems(props.isAddingHomeOwner, props.groupId)),
      groupRules: computed(() => {
        return showGroups.value ? required('Select a group for this owner') : []
      }),
      groupFractionalData: find(getMhrRegistrationHomeOwnerGroups.value, { groupId: props.groupId }),
      fractionalInfo: computed(() => props.fractionalData),
      showFractionalOwnership: computed(() => Number(localState.ownerGroupId) > 0),
      allGroupsState: getMhrRegistrationHomeOwnerGroups.value
        .map(group => {
          return {
            groupId: group.groupId.toString(),
            isReadonly: true && showGroups.value,
            hasEditButton: true && showGroups.value
          }
        })
        .concat({
          groupId: (homeOwnerGroups.length + 1).toString(),
          isReadonly: false,
          hasEditButton: false
        }) as ReadonlyOwnerGroupStateIF[],
      groupState: computed(
        () => find(localState.allGroupsState, { groupId: localState.ownerGroupId }) as ReadonlyOwnerGroupStateIF
      ),
      showEditFractionalOwnershipBtn: true
    })

    const setOwnerGroupId = (groupId: string): void => {
      emit('setOwnerGroupId', groupId)
    }

    const openEditFractionalOwnership = (): void => {
      const groupState = find(
        localState.allGroupsState, { groupId: localState.ownerGroupId.toString() }) as ReadonlyOwnerGroupStateIF
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
    line-height: 24px;
  }
  .owner-groups-select {
    width: 200px;
  }
}
</style>
