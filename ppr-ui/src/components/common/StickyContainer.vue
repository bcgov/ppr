<template :class="{ 'pl-15': leftOffset, 'pr-15': rightOffset }">
  <div :class="`sticky-container-${size}`">
    <fee-summary
      v-if="showFeeSummary"
      :setFeeType="feeType"
      :setRegistrationLength="registrationLength"
      :setRegistrationType="registrationType"
    />
    <buttons-stacked
      v-if="showButtons"
      class="pt-4"
      :setBackBtn="backBtn"
      :setCancelBtn="cancelBtn"
      :setSubmitBtn="submitBtn"
      @back="back()"
      @cancel="cancel()"
      @submit="submit()"
    />
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
// local components
import { ButtonsStacked } from '@/components/common'
import { FeeSummary } from '@/composables/fees'
// local enums/interfaces/etc.
import { UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums' // eslint-disable-line no-unused-vars
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'StickyContainer',
  components: {
    ButtonsStacked,
    FeeSummary
  },
  props: {
    // component options
    setLeftOffset: {
      default: false
    },
    setRightOffset: {
      default: false
    },
    setShowButtons: {
      default: false
    },
    setShowFeeSummary: {
      default: false
    },
    setSize: {
      default: 3
    },
    // fee summary
    setFeeType: {
      type: String as () => FeeSummaryTypes
    },
    setRegistrationLength: {
      type: Object as () => RegistrationLengthI
    },
    setRegistrationType: {
      type: String as () => UIRegistrationTypes
    },
    // buttons
    setBackBtn: {
      default: ''
    },
    setCancelBtn: {
      default: ''
    },
    setSubmitBtn: {
      default: ''
    }
  },
  setup (props, { emit }) {
    const localState = reactive({
      backBtn: props.setBackBtn,
      cancelBtn: props.setCancelBtn,
      feeType: props.setFeeType,
      leftOffset: props.setLeftOffset,
      registrationType: props.setRegistrationType,
      registrationLength: props.setRegistrationLength,
      rightOffset: props.setRightOffset,
      showButtons: props.setShowButtons,
      showFeeSummary: props.setShowFeeSummary,
      size: props.setSize,
      submitBtn: props.setSubmitBtn
    })
    const back = () => {
      emit('back', true)
    }
    const cancel = () => {
      emit('cancel', true)
    }
    const submit = () => {
      emit('submit', true)
    }

    watch(() => props.setRegistrationLength, (val: RegistrationLengthI) => {
      localState.registrationLength = val
    }, { deep: true, immediate: true })

    return {
      back,
      cancel,
      submit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
// matches cols=3
.sticky-container-3 {
  max-width: 316px;
  min-width: 200px;
  position: fixed;
  width: 25%;
}
</style>
