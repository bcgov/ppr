<template :class="{ 'pl-15': leftOffset, 'pr-15': rightOffset }">
  <div>
    <fee-summary
      v-if="showFeeSummary"
      :setFeeType="feeType"
      :setRegistrationLength="registrationLength"
      :setRegistrationType="registrationType"
      :setStaffReg="isStaffReg"
      :setStaffSBC="isStaffSBC"
    />
    <buttons-stacked
      v-if="showButtons"
      class="pt-4"
      :setBackBtn="backBtn"
      :setCancelBtn="cancelBtn"
      :setSubmitBtn="submitBtn"
      :setSaveButton="saveBtn"
      :setDisableSubmitBtn="disableSubmitBtn"
      @back="back()"
      @cancel="cancel()"
      @submit="submit()"
      @save="save()"
    />
    <div v-if="errMsg" class="err-msg pt-3">
      {{ errMsg }}
    </div>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
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
    setErrMsg: {
      default: ''
    },
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
    },
    setDisableSubmitBtn: {
      default: false
    },
    setSaveBtn: {
      default: ''
    }
  },
  setup (props, { emit }) {
    const {
      isRoleStaffReg,
      isRoleStaffSbc
    } = useGetters<any>(['isRoleStaffReg', 'isRoleStaffSbc'])

    const localState = reactive({
      backBtn: props.setBackBtn,
      cancelBtn: props.setCancelBtn,
      errMsg: props.setErrMsg,
      feeType: props.setFeeType,
      leftOffset: props.setLeftOffset,
      registrationType: props.setRegistrationType,
      registrationLength: props.setRegistrationLength,
      rightOffset: props.setRightOffset,
      showButtons: props.setShowButtons,
      showFeeSummary: props.setShowFeeSummary,
      submitBtn: props.setSubmitBtn,
      saveBtn: props.setSaveBtn,
      disableSubmitBtn: props.setDisableSubmitBtn,
      isStaffReg: computed(() => {
        return isRoleStaffReg.value as boolean
      }),
      isStaffSBC: computed(() => {
        return isRoleStaffSbc.value as boolean
      })
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
    const save = () => {
      emit('save', true)
    }

    watch(() => props.setErrMsg, (val: string) => {
      localState.errMsg = val
    })

    watch(() => props.setRegistrationLength, (val: RegistrationLengthI) => {
      localState.registrationLength = val
    }, { deep: true, immediate: true })

    return {
      back,
      cancel,
      submit,
      save,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.err-msg {
  color: $error;
  font-size: 0.75rem;
  text-align: center;
}
</style>
