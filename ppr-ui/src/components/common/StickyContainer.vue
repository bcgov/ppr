<template :class="{ 'pl-15': leftOffset, 'pr-15': rightOffset }">
  <div id="sticky-container">
    <FeeSummary
      v-if="showFeeSummary"
      class="overlap"
      :setFeeOverride="feeOverride"
      :setFeeType="setFeeType"
      :setFeeSubtitle="setFeeSubtitle"
      :setFeeQuantity="setFeeQuantity"
      :setRegistrationLength="registrationLength"
      :setRegistrationType="registrationType"
      :setStaffReg="isStaffReg"
      :setStaffSBC="isStaffSBC"
      :additionalFees="setAdditionalFees"
      :setStaffClientPayment="isStaffClientPayment"
      :transferType="transferType"
    />
    <ButtonsStacked
      v-if="showButtons"
      class="pt-4 buttons-stacked overlap"
      :setBackBtn="setBackBtn"
      :setCancelBtn="cancelBtn"
      :setSubmitBtn="setSubmitBtn"
      :setSaveButton="saveBtn"
      :setDisableSubmitBtn="disableSubmitBtn"
      :setIsLoading="setIsLoading"
      @back="back()"
      @cancel="cancel()"
      @submit="submit()"
      @save="save()"
    />
    <div
      v-if="errMsg"
      class="err-msg pt-3"
    >
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
} from 'vue'
import { useStore } from '@/store/store'
import { ButtonsStacked } from '@/components/common'
import { FeeSummary } from '@/composables/fees'
import { UIRegistrationTypes, UITransferTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  AdditionalSearchFeeIF,
  FeeSummaryI,
  RegistrationLengthI
} from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'StickyContainer',
  components: {
    ButtonsStacked,
    FeeSummary
  },
  props: {
    // component options
    setErrMsg: {
      type: String,
      default: ''
    },
    setLeftOffset: {
      type: Boolean,
      default: false
    },
    setRightOffset: {
      type: Boolean,
      default: false
    },
    setShowButtons: {
      type: Boolean,
      default: false
    },
    setShowFeeSummary: {
      type: Boolean,
      default: false
    },
    // fee summary
    setFeeType: {
      type: String as () => FeeSummaryTypes,
      default: () => null
    },
    setFeeQuantity: {
      default: null,
      type: Number
    },
    setRegistrationLength: {
      type: Object as () => RegistrationLengthI,
      default: () => null
    },
    setRegistrationType: {
      type: String as () => UIRegistrationTypes,
      default: () => null
    },
    transferType: {
      type: String as () => UITransferTypes | string,
      default: () => null
    },
    setAdditionalFees: {
      type: Object as () => AdditionalSearchFeeIF,
      default: () => null,
    },
    setFeeSubtitle: {
      type: String,
      default: ''
    },
    // buttons
    setBackBtn: {
      type: String,
      default: ''
    },
    setCancelBtn: {
      type: String,
      default: ''
    },
    setSubmitBtn: {
      type: String,
      default: ''
    },
    setDisableSubmitBtn: {
      type: Boolean,
      default: false
    },
    setSaveBtn: {
      type: String,
      default: ''
    },
    setIsLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['back', 'cancel', 'submit', 'save'],
  setup (props, { emit }) {
    const {
      getUserServiceFee, isNonBillable, getIsStaffClientPayment, isRoleStaffReg, isRoleStaffSbc, getStaffPayment
    } = storeToRefs(useStore())

    const localState = reactive({
      cancelBtn: props.setCancelBtn,
      errMsg: props.setErrMsg,
      leftOffset: props.setLeftOffset,
      registrationType: props.setRegistrationType,
      registrationLength: props.setRegistrationLength,
      rightOffset: props.setRightOffset,
      showButtons: props.setShowButtons,
      showFeeSummary: props.setShowFeeSummary,
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
        return getIsStaffClientPayment.value
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
