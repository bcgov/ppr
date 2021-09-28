<template>
  <v-container v-if="summaryView" style="padding: 16px 12px 0 30px;">
    <gen-col-summary />
  </v-container>
  <v-container v-else class="pa-0">
    <gen-col-edit
      :showInvalid="showInvalid"
      @valid="emitValid"
    />
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
// local components
import { GenColEdit, GenColSummary } from '.'
// local types/helpers/etc.
import { APIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'GeneralCollateral',
  components: {
    GenColEdit,
    GenColSummary
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setRegistrationType: String as () => APIRegistrationTypes,
    setShowInvalid: {
      type: Boolean,
      default: false
    }
  },
  emits: ['valid'],
  setup (props, { emit }) {
    const localState = reactive({
      summaryView: props.isSummary,
      showInvalid: computed((): boolean => {
        return props.setShowInvalid
      })
    })

    const emitValid = (valid: boolean) => {
      emit('valid', valid)
    }

    return {
      emitValid,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
