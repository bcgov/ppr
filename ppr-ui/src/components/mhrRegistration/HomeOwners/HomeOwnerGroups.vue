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
      class="owner-groups-select my-8"
      filled
      @change="setOwnerGroupId($event)"
      :clearable="groupItems.length === 1"
      @click:clear="groupDropdown.blur()"
      :menu-props="{ bottom: true, offsetY: true }"
      data-test-id="owner-group-select"
    ></v-select>

    <div v-if="showFractionalOwnership">
      <FractionalOwnership
        :groupId="ownerGroupId"
        :fractionalData="fractionalData"
        :isReadOnly="isReadOnlyFractionalOwnership"
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

export default defineComponent({
  name: 'HomeOwnerGroups',
  emits: ['setOwnerGroupId'],
  components: {
    FractionalOwnership
  },
  props: {
    groupId: { type: String },
    fractionalData: { type: Object },
    isAddingHomeOwner: { type: Boolean } // make additional Group available in dropdown when adding a new home owner
  },
  setup (props, { emit }) {
    const { getMhrRegistrationHomeOwnerGroups } = useGetters<any>([
      'getMhrRegistrationHomeOwnerGroups'
    ])
    const groupDropdown = ref(null)

    const { required } = useInputRules()
    const { getGroupDropdownItems, showGroups } = useHomeOwners()

    const localState = reactive({
      ownerGroupId: props.groupId,
      groupItems: computed(() => getGroupDropdownItems(props.isAddingHomeOwner, props.groupId)),
      groupRules: computed(() => {
        return showGroups.value ? required('Select a group for this owner') : []
      }),
      showFractionalOwnership: computed(() => Number(localState.ownerGroupId) > 0),
      isReadOnlyFractionalOwnership: computed(
        // if group already exists - show fractional ownership as readonly
        () =>
          find(
            getMhrRegistrationHomeOwnerGroups.value,
            group => group.groupId === localState.ownerGroupId
          ) !== undefined
      )
    })

    const setOwnerGroupId = (groupId: string) => {
      emit('setOwnerGroupId', groupId)
    }

    return {
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
