<template>
  <div class="pa-0 ma-0">
    <v-container
      v-if="registrationFlowType === RegistrationFlowType.AMENDMENT && amendMode"
      style="padding: 28px 12px 0 30px;"
    >
      <gen-col-amend :setShowErrorBar="showErrorBar" @closeGenColAmend="amendMode = false" />
    </v-container>
    <v-container
      v-if="summaryView || registrationFlowType === RegistrationFlowType.AMENDMENT"
      style="padding: 28px 12px 0 30px;"
    >
      <gen-col-summary
        @initGenColAmend="amendMode = $event"
        :setShowHistory="false"
        :setShowAmendLink="!amendMode"
      />
    </v-container>
    <v-container v-else class="pa-0">
      <gen-col-edit :showInvalid="showInvalid" />
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
} from 'vue-demi'
// local components
import { GenColEdit, GenColSummary, GenColAmend } from '.'
// local types/helpers/etc.
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { useStore } from '@/store/store'

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
    } = useStore()

    const registrationFlowType = getRegistrationFlowType
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
