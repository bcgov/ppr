<template>
  <div id="mhr-home-owner-groups">
    <label class="generic-label">
      Multiple Groups of Owners (Tenants in Common)
    </label>
    <ul class="my-2">
      <li>
        Select a group if you have
        <b>multiple groups of owners</b> (tenants in common).
      </li>
      <li>
        Leave this empty if you have <b>only one owner</b>, or
        <b>one group of owners</b> (sole ownership or joint tenancy).
      </li>
    </ul>
    <v-select
      id="home-owner-groups"
      label="Select a Group"
      v-model="ownerGroupId"
      :items="groups"
      :rules="groupRules"
      class="owner-groups-select my-8"
      filled
      @change="setOwnerGroupId($event)"
      :clearable="groups.length === 1"
    ></v-select>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { useInputRules } from '@/composables'

export default defineComponent({
  name: 'HomeOwnerGroups',
  props: {
    groupId: { type: String },
    isAddingHomeOwner: { type: Boolean } // make additional Group available in dropdown when adding a new home owner
  },
  setup (props, { emit }) {
    const { required } = useInputRules()
    const { getGroupDropdownItems, showGroups } = useHomeOwners()

    const localState = reactive({
      ownerGroupId: props.groupId,
      groups: computed(() => getGroupDropdownItems(props.isAddingHomeOwner)),
      groupRules: computed(() => {
        return showGroups.value ? required('Select a group for this owner') : []
      })
    })

    const setOwnerGroupId = (groupId: string) => {
      emit('setOwnerGroupId', groupId)
    }

    return {
      setOwnerGroupId,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#mhr-home-owner-groups::v-deep {
  ul {
    color: #495057;
  }

  .owner-groups-select {
    width: 200px;
  }
}
</style>
