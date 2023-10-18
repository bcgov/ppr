<template>
      <td
        class="py-6 error-text text-center d-block"
        :class="{ 'border-error-left': showBorderError }"
        :colspan="4"
        :data-test-id="`mixed-owners-msg-group-${groupId}`"
        >
          {{ mixedRoleErrorMsg }}
      </td>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { MixedRolesErrors } from '@/resources'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'HomeOwnersMixedRolesError',
  props: {
    groupId: {
      type: Number,
      required: true
    },
    showBorderError: {
      type: Boolean,
      required: true
    }
  },
  setup () {
    const { getMhrRegistrationHomeOwnerGroups } = storeToRefs(useStore())

    const localState = reactive({
      mixedRoleErrorMsg: computed(() => getMhrRegistrationHomeOwnerGroups.value?.length === 1
        ? MixedRolesErrors.hasMixedOwnerTypes
        : MixedRolesErrors.hasMixedOwnerTypesInGroup)
    })

    return {
      ...toRefs(localState)
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
