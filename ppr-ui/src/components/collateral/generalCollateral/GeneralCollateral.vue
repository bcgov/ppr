<template>
  <div class="pa-0 ma-0">
    <v-container
      v-if="registrationFlowType === RegistrationFlowType.AMENDMENT && amendMode"
      style="padding: 28px 12px 0 30px;"
    >
      <gen-col-amend @closeGenColAmend="amendMode = false" />
    </v-container>
    <v-container
      v-if="summaryView || registrationFlowType === RegistrationFlowType.AMENDMENT"
      style="padding: 28px 12px 0 30px;"
    >
      <gen-col-summary
        @initGenColAmend="amendMode = $event"
        :setShowHistory="registrationFlowType === RegistrationFlowType.AMENDMENT"
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
  setup (props) {
    const {
      getRegistrationFlowType
    } = useGetters<any>(['getRegistrationFlowType'])

    const registrationFlowType = getRegistrationFlowType.value
    const localState = reactive({
      summaryView: props.isSummary,
      amendMode: false,
      showInvalid: computed((): boolean => {
        return props.setShowInvalid
      })
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
