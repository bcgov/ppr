<template>
  <div class="pa-0 ma-0">
    <v-container
      v-if="registrationFlowType === RegistrationFlowType.AMENDMENT && amendMode"
    >
      <GenColAmend
        :set-show-error-bar="showErrorBar"
        @closeGenColAmend="amendMode = false"
      />
    </v-container>
    <v-container
      v-if="summaryView || registrationFlowType === RegistrationFlowType.AMENDMENT"
    >
      <GenColSummary
        :set-show-history="false"
        :set-show-amend-link="!amendMode"
        @initGenColAmend="amendMode = $event"
      />
    </v-container>
    <v-container
      v-else
      class="px-0"
    >
      <GenColEdit :show-invalid="showInvalid" />
    </v-container>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  watch,
  toRefs
} from 'vue'
// local components
import { GenColEdit, GenColSummary, GenColAmend } from '.'
// local types/helpers/etc.
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

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
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getRegistrationFlowType
    } = storeToRefs(useStore())

    const registrationFlowType = getRegistrationFlowType.value
    const localState = reactive({
      summaryView: props.isSummary,
      amendMode: false,
      showInvalid: computed((): boolean => {
        return props.setShowInvalid
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    watch(() => localState.amendMode, (val: boolean) => {
      context.emit('collateralOpen', val)
    })

    return {
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
