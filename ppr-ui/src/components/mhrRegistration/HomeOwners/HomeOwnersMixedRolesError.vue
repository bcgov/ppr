<template>
      <td
        class="py-1"
        :class="{ 'border-error-left': showBorderError }"
        :colspan="4"
        data-test-id="invalid-group-mixed-owners"
        >
          <div
          class="error-text my-6 text-center"
          :data-test-id="`mixed-owners-msg-group-${groupId}`"
          >
            <span>
            {{ mixedRoleErrorMsg }}
            </span>
          </div>
      </td>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { MixedRolesErrors } from '@/resources'

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
    const { getMhrRegistrationHomeOwnerGroups } = useStore()

    const localState = reactive({
      mixedRoleErrorMsg: computed(() => getMhrRegistrationHomeOwnerGroups?.length === 1
        ? MixedRolesErrors.hasMixedOwnerTypes : MixedRolesErrors.hasMixedOwnerTypesInGroup)
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
