<template>
  <v-card>
    <header class="font-weight-bold px-3 py-3">
      <slot name="header">Fee Summary</slot>
    </header>
    <v-slide-y-transition group tag="ul" :class="[$style['fee-list'], 'px-0']">
      <template>
        <li
          v-if="!additionalFees || feeSummary.quantity > 0"
          :class="[$style['fee-container'], $style['fee-list__item'], { 'pb-4': !hintFee }, 'pr-4', 'pt-5']"
          :key="feeLabel"
        >
          <div :class="$style['fee-list__item-name']">
            {{ feeLabel }}
            <div v-if="isMhrTransfer" :class="[$style['fee-list__hint'], 'pt-2']">
              {{ transferType ? transferType : 'Select Transfer Type' }}
            </div>
          </div>
          <div
            v-if="feeSummary.feeAmount === 0"
            :class="$style['fee-list__item-value']"
          >
            No Fee
          </div>
          <div v-else-if="!isComplete" :class="$style['fee-list__item-value']">
            -
          </div>
          <div v-else-if="isMhrTransfer && !transferType" :class="$style['fee-list__item-value']">
            $ -
          </div>
          <div v-else :class="$style['fee-list__item-value']">
            ${{ totalFees.toFixed(2) }}
          </div>
        </li>
        <li
          v-if="setFeeQuantity > 0"
          :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'mt-n3']"
          :key="`Fee: ${setFeeQuantity}`"
        >
          <div id="quantity-label" class="fee-list__hint">
            {{ setFeeQuantity }} @ ${{ feeSummary.feeAmount.toFixed(2) }} each
          </div>
        </li>
        <template v-if="additionalFees">
          <li
            :class="[$style['fee-container'], $style['fee-list__item'], { 'pb-4': !hintFee }, 'pr-4', 'pt-5']"
            :key="additionalFeeLabel"
          >
            <div :class="$style['fee-list__item-name']">
              {{ additionalFeeLabel }}
            </div>
            <div
              v-if="additionalFeeSummary && additionalFeeSummary.feeAmount === 0"
              :class="$style['fee-list__item-value']"
            >
              No Fee
            </div>
            <div v-else :class="$style['fee-list__item-value']">
              ${{ totalAdditionalFees.toFixed(2) }}
            </div>
          </li>
          <li
            :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'mt-n3']"
            :key="`Additional Fee: ${additionalFeeSummary.quantity}`"
          >
            <div id="additional-quantity-label" class="fee-list__hint">
              {{ additionalFeeSummary.quantity }} @ ${{ additionalFeeSummary.feeAmount.toFixed(2) }} each
            </div>
          </li>
        </template>
        <li
          v-if="hintFee"
          :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'pr-4', 'pt-3']"
          :key="hintFee"
        >
          <div class="fee-list__hint">{{ hintFee }}</div>
        </li>
        <li
          v-if="hasPriorityFee"
          id="priority-fee"
          :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
          key="PriorityFee"
        >
          <div :class="$style['fee-list__item-name']">
            Priority Fee
          </div>
          <div :class="$style['fee-list__item-value']">
            $ 100.00
          </div>
        </li>
        <li
          v-if="hasCertifyFee"
          id="certify-fee"
          :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
          key="CertifyFee"
        >
          <div :class="$style['fee-list__item-name']">
            Certified search
          </div>
          <div :class="$style['fee-list__item-value']">
            $ 25.00
          </div>
        </li>
        <li
          v-if="hasProcessingFee && isPPRFee"
          id="processing-fee-summary"
          :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
          :key="feeSummary.processingFee"
        >
          <div :class="$style['fee-list__item-name']">
            Staff Processing Fee
          </div>
          <div
            v-if="feeSummary && feeSummary.processingFee === 0"
            :class="$style['fee-list__item-value']"
          >
            No Fee
          </div>
          <div v-else :class="$style['fee-list__item-value']">
            ${{ feeSummary.processingFee.toFixed(2) }}
          </div>
        </li>
        <li
          v-else-if="isPPRFee"
          :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
          :key="feeSummary.serviceFee"
        >
          <div :class="$style['fee-list__item-name']">
            Service Fee
          </div>
          <div
            v-if="feeSummary && feeSummary.serviceFee === 0"
            :class="$style['fee-list__item-value']"
          >
            No Fee
          </div>
          <div v-else :class="$style['fee-list__item-value']">
            ${{ feeSummary.serviceFee.toFixed(2) }}
          </div>
        </li>
        <li
          v-else-if="hasProcessingFee && feeSummary.processingFee > 0"
          id="processing-fee-summary"
          :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
          key="MHRProcessingFeeKey"
        >
          <div :class="$style['fee-list__item-name']">
            Staff Processing Fee
          </div>
          <div :class="$style['fee-list__item-value']">
            ${{ feeSummary.processingFee.toFixed(2) }}
          </div>
        </li>
        <li
          v-else-if="feeSummary && feeSummary.serviceFee > 0"
          :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
          key="MHRServiceFeeKey"
        >
          <div :class="$style['fee-list__item-name']">
            Service Fee
          </div>
          <div :class="$style['fee-list__item-value']">
            ${{ feeSummary.serviceFee.toFixed(2) }}
          </div>
        </li>
      </template>
    </v-slide-y-transition>
    <div :class="[$style['fee-container'], $style['fee-total'], 'pa-4']">
      <div :class="$style['fee-total__name']">Total Fees</div>
      <div :class="$style['fee-total__currency']">CAD</div>
      <div :class="$style['fee-total__value']">
        <v-slide-y-reverse-transition name="slide" mode="out-in">
          <div v-if="isMhrTransfer && !transferType" class="float-right">
            <b>$ -</b>
          </div>
          <div v-else-if="isComplete || transferType" class="float-right">
            <b>${{ totalAmount.toFixed(2) }}</b>
          </div>
          <div v-else class="float-right"><b>-</b></div>
        </v-slide-y-reverse-transition>
      </div>
    </div>
  </v-card>
</template>

<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
/* eslint-disable no-unused-vars */
import { UIRegistrationTypes, UITransferTypes } from '@/enums'
/* eslint-disable no-unused-vars */
import { FeeSummaryTypes } from './enums'
import { AdditionalSearchFeeIF, FeeSummaryI, RegistrationLengthI } from './interfaces'
// eslint-enable no-unused-vars
import { getFeeHint, getFeeSummary } from './factories'

export default defineComponent({
  name: 'FeeSummary',
  props: {
    setFeeOverride: {
      default: null,
      type: Object as () => FeeSummaryI
    },
    setFeeType: {
      type: String as () => FeeSummaryTypes
    },
    setFeeQuantity: {
      default: null,
      type: Number
    },
    additionalFees: {
      default: null,
      type: Object as () => AdditionalSearchFeeIF
    },
    setRegistrationLength: {
      type: Object as () => RegistrationLengthI
    },
    setRegistrationType: {
      type: String as () => UIRegistrationTypes
    },
    transferType: {
      type: String as () => UITransferTypes
    },
    setStaffReg: { default: false },
    setStaffSBC: { default: false },
    setStaffClientPayment: { default: false }
  },
  setup (props) {
    const {
      getLengthTrust, isRoleStaff, getStaffPayment, isSearchCertified
    } = useGetters<any>([
      'getLengthTrust', 'isRoleStaff', 'getStaffPayment', 'isSearchCertified'
    ])
    const localState = reactive({
      feeType: props.setFeeType,
      registrationType: props.setRegistrationType,
      hasPriorityFee: computed((): Boolean => getStaffPayment.value?.isPriority),
      hasCertifyFee: computed((): Boolean => isSearchCertified.value),
      registrationLength: computed((): RegistrationLengthI => props.setRegistrationLength),
      isValid: computed((): boolean => {
        return getLengthTrust.value.valid ||
          [FeeSummaryTypes.MHSEARCH, FeeSummaryTypes.NEW_MHR, FeeSummaryTypes.MHR_TRANSFER].includes(localState.feeType)
      }),
      isPPRFee: computed((): boolean => {
        return [
          FeeSummaryTypes.AMEND,
          FeeSummaryTypes.DISCHARGE,
          FeeSummaryTypes.NEW,
          FeeSummaryTypes.RENEW
        ].includes(localState.feeType)
      }),
      feeLabel: computed((): string => {
        return mapFeeTypeToDisplayName(localState.feeType)
      }),
      additionalFeeLabel: computed((): string => {
        return mapFeeTypeToDisplayName(props.additionalFees?.feeType)
      }),
      isMhrTransfer: computed((): boolean => {
        return localState.feeType === FeeSummaryTypes.MHR_TRANSFER
      }),
      feeSummary: computed((): FeeSummaryI => {
        const feeSummary = getFeeSummary(
          localState.feeType,
          localState.registrationType,
          localState.registrationLength,
          isRoleStaff.value,
          props.setStaffClientPayment
        )
        if (props.setFeeQuantity) {
          feeSummary.quantity = props.setFeeQuantity
        }
        if (localState.feeType === FeeSummaryTypes.RENEW) {
          feeSummary.processingFee = 5
        }
        if (props.setFeeOverride) {
          feeSummary.feeAmount = props.setFeeOverride?.feeAmount
        }
        if (props.setFeeOverride && feeSummary.serviceFee !== 0) {
          feeSummary.serviceFee = props.setFeeOverride.serviceFee
        }
        return feeSummary
      }),
      additionalFeeSummary: computed((): FeeSummaryI => {
        const feeSummary = props.additionalFees && getFeeSummary(
          props.additionalFees?.feeType,
          props.additionalFees?.registrationType,
          props.additionalFees?.registrationLength,
          isRoleStaff.value,
          props.setStaffClientPayment
        )
        if (props.additionalFees?.quantity) {
          feeSummary.quantity = props.additionalFees?.quantity
        }
        if (feeSummary && props.setFeeOverride) {
          feeSummary.feeAmount = props.setFeeOverride?.feeAmount
        }
        if (feeSummary && props.setFeeOverride && feeSummary.serviceFee !== 0) {
          feeSummary.serviceFee = props.setFeeOverride.serviceFee
        }
        return feeSummary
      }),
      hasProcessingFee: computed(() => {
        return props.setStaffReg || props.setStaffSBC
      }),
      hintFee: computed((): string => {
        const hint = getFeeHint(
          localState.feeType,
          localState.registrationType,
          localState.registrationLength
        )
        if (props.setFeeOverride) return hint.replace('$5', '$0')
        return hint
      }),
      isComplete: computed((): boolean => {
        return localState.isValid &&
          (localState.feeSummary?.quantity > 0 || localState.additionalFeeSummary?.quantity > 0)
      }),
      totalAmount: computed((): number => {
        if (localState.isValid) {
          let extraFee = localState.feeSummary.serviceFee
          if (localState.hasProcessingFee) {
            extraFee = localState.feeSummary.processingFee
          }
          if (getStaffPayment.value?.isPriority) {
            extraFee = extraFee + 100
          }
          if (localState.hasCertifyFee) {
            extraFee += 25
          }
          return (
            (localState.feeSummary.feeAmount *
            localState.feeSummary.quantity) +
            (localState.additionalFeeSummary && (localState.additionalFeeSummary?.feeAmount *
            localState.additionalFeeSummary?.quantity)) +
            extraFee
          )
        }
      }),
      totalFees: computed((): number => {
        if (localState.isValid) {
          return localState.feeSummary.feeAmount * localState.feeSummary.quantity
        }
      }),
      totalAdditionalFees: computed((): number => {
        if (localState.isValid) {
          return localState.additionalFeeSummary?.feeAmount * localState.additionalFeeSummary?.quantity
        }
      })
    })

    const mapFeeTypeToDisplayName = (feeType: FeeSummaryTypes): string => {
      switch (feeType) {
        case FeeSummaryTypes.DISCHARGE: return 'Total Discharge'
        case FeeSummaryTypes.RENEW: return 'Registration Renewal'
        case FeeSummaryTypes.AMEND: return 'Registration Amendment'
        case FeeSummaryTypes.MHSEARCH: return 'Manufactured Home search'
        case FeeSummaryTypes.MHR_COMBINED_SEARCH: return 'Combined Home and Lien search'
        case FeeSummaryTypes.MHR_TRANSFER: return 'Ownership Transfer or Change'
        default: return localState.registrationType
      }
    }

    watch(() => props.setFeeType, (val: FeeSummaryTypes) => {
      localState.feeType = val
    })
    watch(() => props.setRegistrationType, (val: UIRegistrationTypes) => {
      localState.registrationType = val
    })

    return {
      UIRegistrationTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';

header {
  color: #fff;
  background: $BCgovBlue5;
}

.fee-container {
  display: flex;
  flex-flow: row nowrap;
  line-height: 1.2rem;
  font-size: 0.875rem;
}

.fee-list {
  li {
    padding-left: 15px !important;
  }
}

.fee-list__hint {
  color: $gray7;
  font-size: 14px;
  font-weight: normal;
  padding-top: 0px;
  margin-top: -5px;
}

.fee-list__item {
  &-name,
  &-value {
    font-weight: 700;
  }

  &-name {
    flex: 1 1 auto;
    margin-right: 2rem;
  }

  &-value {
    flex: 0 0 auto;
    text-align: right;
  }
}

.fee-total,
.fee-list__item + .fee-list__item,
.fee-list__hint + .fee-list__item {
  border-top: 1px solid $gray3;
}

.fee-total {
  align-items: center;
  letter-spacing: -0.01rem;
  line-height: auto;

  &__name {
    flex: 1 1 auto;
    margin-right: auto;
    font-weight: 700;
  }

  &__currency {
    margin-right: 0.5rem;
    color: $gray7;
    font-weight: 500;
  }

  &__value {
    font-size: 1.65rem;
    font-weight: 700;
  }
}
</style>
