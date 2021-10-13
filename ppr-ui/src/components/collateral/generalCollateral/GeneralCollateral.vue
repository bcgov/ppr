<template>
  <v-container v-if="summaryView" style="padding: 28px 12px 0 30px;">
    <gen-col-summary />
  </v-container>
  <v-container
    v-else-if="registrationFlowType === RegistrationFlowType.AMENDMENT"
    style="padding: 28px 12px 0 30px;"
  >
    <gen-col-amend />
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
import { GenColEdit, GenColSummary, GenColAmend } from '.'
// local types/helpers/etc.
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'GeneralCollateral',
  components: {
    GenColEdit,
    GenColSummary,
    GenColAmend
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
    const {
      getRegistrationFlowType
    } = useGetters<any>(['getRegistrationFlowType'])

    const registrationFlowType = getRegistrationFlowType.value
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
      registrationFlowType,
      RegistrationFlowType,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
