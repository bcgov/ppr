<template>
    <td :colspan="4"
            class="py-1"
            :class="{ 'border-error-left': borderError}"
            data-test-id="invalid-group-mixed-owners"
          >
            <div
              class="error-text my-6 text-center"
              :data-test-id="`mixed-owners-msg-group-${groupId}`"
            >
                <span v-if="hasOneHomeOwnerGroup">
                  {{ MhrErrorMsgs.HAS_MIXED_OWNER_TYPES }}
                </span>
                <span v-else>
                  {{ MhrErrorMsgs.HAS_MIXED_OWNER_TYPES_IN_GROUP }}
                </span>
              </div>
         </td>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { MhrErrorMsgs } from '@/enums/Errors/mhrErrors'

export default defineComponent({
  name: 'HomeOwnersMixedRolesError',
  props: {
    groupId: {
      type: Number,
      required: true
    },
    borderError: {
      type: Boolean,
      required: true
    }
  },
  setup () {
    const {
      getMhrRegistrationHomeOwnerGroups
    } = useGetters<any>([
      'getMhrRegistrationHomeOwnerGroups'
    ])

    const localState = reactive({
      hasOneHomeOwnerGroup: computed(() => getMhrRegistrationHomeOwnerGroups.value.length === 1)
    })

    return {
      MhrErrorMsgs,
      ...toRefs(localState)
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
