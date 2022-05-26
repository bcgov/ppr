<template :class="{ 'pl-15': leftOffset, 'pr-15': rightOffset }">
  <div>
    <fee-summary
      v-if="showFeeSummary"
      :setFeeOverride="feeOverride"
      :setFeeType="setFeeType"
      :setFeeQuantity="setFeeQuantity"
      :setRegistrationLength="registrationLength"
      :setRegistrationType="registrationType"
      :setStaffReg="isStaffReg"
      :setStaffSBC="isStaffSBC"
      :additionalFees="setAdditionalFees"
      :setStaffClientPayment="isStaffClientPayment"
    />
    <buttons-stacked
      v-if="showButtons"
      class="pt-4 buttons-stacked"
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
/* eslint-disable no-unused-vars */
import { UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  AdditionalSearchFeeIF,
  FeeSummaryI,
  RegistrationLengthI
} from '@/composables/fees/interfaces'
/* eslint-enable no-unused-vars */

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
    setFeeQuantity: {
      default: null,
      type: Number
    },
    setRegistrationLength: {
      type: Object as () => RegistrationLengthI
    },
    setRegistrationType: {
      type: String as () => UIRegistrationTypes
    },
    setAdditionalFees: {
      default: null,
      type: Object as () => AdditionalSearchFeeIF
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
      getUserServiceFee, isNonBillable, getIsStaffClientPayment, isRoleStaffReg, isRoleStaffSbc, getStaffPayment
    } = useGetters<any>(
      [
        'getUserServiceFee',
        'isNonBillable',
        'getIsStaffClientPayment',
        'isRoleStaffReg',
        'isRoleStaffSbc',
        'getStaffPayment'
      ]
    )

    const localState = reactive({
      backBtn: props.setBackBtn,
      cancelBtn: props.setCancelBtn,
      errMsg: props.setErrMsg,
      leftOffset: props.setLeftOffset,
      registrationType: props.setRegistrationType,
      registrationLength: props.setRegistrationLength,
      rightOffset: props.setRightOffset,
      showButtons: props.setShowButtons,
      showFeeSummary: props.setShowFeeSummary,
      submitBtn: props.setSubmitBtn,
      saveBtn: props.setSaveBtn,
      disableSubmitBtn: props.setDisableSubmitBtn,
      feeOverride: computed(() => {
        if (isNonBillable.value || localState.isNoFeePayment) {
          return {
            feeAmount: 0,
            processingFee: null, // not used in override
            quantity: null, // not used in override
            serviceFee: getUserServiceFee.value as number
          } as FeeSummaryI
        }
        return null
      }),
      isStaffReg: computed(() => {
        return isRoleStaffReg.value as boolean
      }),
      isStaffSBC: computed(() => {
        return isRoleStaffSbc.value as boolean
      }),
      isStaffClientPayment: computed(() => {
        return getIsStaffClientPayment
      }),
      isNoFeePayment: computed(() => {
        return getStaffPayment.value?.option === 0
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
