<template>
  <v-card>
    <header class="font-weight-bold px-3 py-3">
      <slot name="header">
        <h3 class="lh-24 text-white">
          Fee Summary
        </h3>
      </slot>
    </header>
    <ul :class="[$style['fee-list'], 'px-0']">
      <li
        v-if="!additionalFees || feeSummary.quantity > 0"
        :key="feeLabel"
        :class="[$style['fee-container'], $style['fee-list__item'], { 'pb-4': !hintFee }, 'pr-4', 'pt-5']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            {{ feeLabel }}
          </h4>
          <div
            v-if="isMhrTransaction"
            id="transfer-type-text"
            :class="[$style['fee-list__hint'], 'pt-2']"
          >
            <span v-if="feeType === FeeSummaryTypes.MHR_TRANSFER">
              {{ transferType ? transferType : 'Select Transfer Type' }}
            </span>
            <span v-if="feeType === FeeSummaryTypes.MHR_TRANSPORT_PERMIT">
              {{ transferType ? transferType : 'Select Location Change Type' }}
            </span>
            <span v-if="feeType === FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT">
              {{ transferType }}
            </span>
          </div>
          <div
            v-if="isMhrCorrection"
            :class="[$style['fee-list__hint'], 'pt-2']"
          >
            <span>{{ setFeeSubtitle }}</span>
          </div>
        </div>
        <div
          v-if="feeSummary.feeAmount === 0"
          :class="$style['fee-list__item-value']"
        >
          No Fee
        </div>
        <div
          v-else-if="!isComplete"
          :class="$style['fee-list__item-value']"
        >
          -
        </div>
        <div
          v-else-if="isMhrTransaction && !transferType"
          :class="$style['fee-list__item-value']"
        >
          $ -
        </div>
        <div
          v-else
          :class="$style['fee-list__item-value']"
        >
          ${{ totalFees.toFixed(2) }}
        </div>
      </li>
      <li
        v-if="setFeeQuantity > 0"
        :key="`Fee: ${setFeeQuantity}`"
        :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'mt-n3']"
      >
        <div
          id="quantity-label"
          class="fee-list__hint"
        >
          {{ setFeeQuantity }} @ ${{ feeSummary.feeAmount.toFixed(2) }} each
        </div>
      </li>
      <template v-if="additionalFees">
        <li
          :key="additionalFeeLabel"
          :class="[$style['fee-container'], $style['fee-list__item'], { 'pb-4': !hintFee }, 'pr-4', 'pt-5']"
        >
          <div :class="$style['fee-list__item-name']">
            <h4 class="lh-20">
              {{ additionalFeeLabel }}
            </h4>
          </div>
          <div
            v-if="additionalFeeSummary && additionalFeeSummary.feeAmount === 0"
            :class="$style['fee-list__item-value']"
          >
            No Fee
          </div>
          <div
            v-else
            :class="$style['fee-list__item-value']"
          >
            ${{ totalAdditionalFees.toFixed(2) }}
          </div>
        </li>
        <li
          :key="`Additional Fee: ${additionalFeeSummary.quantity}`"
          :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'mt-n3']"
        >
          <div
            id="additional-quantity-label"
            class="fee-list__hint"
          >
            {{ additionalFeeSummary.quantity }} @ ${{ additionalFeeSummary.feeAmount.toFixed(2) }} each
          </div>
        </li>
      </template>
      <li
        v-if="hintFee"
        :key="hintFee"
        :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'pr-4', 'pt-3']"
      >
        <div class="fee-list__hint">
          {{ hintFee }}
        </div>
      </li>
      <li
        v-if="hasPriorityFee"
        id="priority-fee"
        key="PriorityFee"
        :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            Priority Fee
          </h4>
        </div>
        <div :class="$style['fee-list__item-value']">
          $ 100.00
        </div>
      </li>
      <li
        v-if="hasCertifyFee"
        id="certify-fee"
        key="CertifyFee"
        :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            Certified search
          </h4>
        </div>
        <div :class="$style['fee-list__item-value']">
          $ 25.00
        </div>
      </li>
      <li
        v-if="hasProcessingFee && isPPRFee"
        id="processing-fee-summary"
        :key="feeSummary.processingFee"
        :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            Staff Processing Fee
          </h4>
        </div>
        <div
          v-if="feeSummary && feeSummary.processingFee === 0"
          :class="$style['fee-list__item-value']"
        >
          No Fee
        </div>
        <div
          v-else
          :class="$style['fee-list__item-value']"
        >
          ${{ feeSummary.processingFee.toFixed(2) }}
        </div>
      </li>
      <li
        v-else-if="isPPRFee"
        :key="feeSummary.serviceFee"
        :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            Service Fee
          </h4>
        </div>
        <div
          v-if="feeSummary && feeSummary.serviceFee === 0"
          :class="$style['fee-list__item-value']"
        >
          No Fee
        </div>
        <div
          v-else
          :class="$style['fee-list__item-value']"
        >
          ${{ feeSummary.serviceFee.toFixed(2) }}
        </div>
      </li>
      <li
        v-else-if="hasProcessingFee && feeSummary.processingFee > 0"
        id="processing-fee-summary"
        key="MHRProcessingFeeKey"
        :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            Staff Processing Fee
          </h4>
        </div>
        <div :class="$style['fee-list__item-value']">
          ${{ feeSummary.processingFee.toFixed(2) }}
        </div>
      </li>
      <li
        v-else-if="feeSummary && feeSummary.serviceFee > 0"
        key="MHRServiceFeeKey"
        :class="[$style['fee-container'], $style['fee-list__item'], 'pb-4', 'pr-4', 'py-4']"
      >
        <div :class="$style['fee-list__item-name']">
          <h4 class="lh-20">
            Service Fee
          </h4>
        </div>
        <div :class="$style['fee-list__item-value']">
          ${{ feeSummary.serviceFee.toFixed(2) }}
        </div>
      </li>
    </ul>
    <div :class="[$style['fee-container'], $style['fee-total'], 'pa-4']">
      <div :class="$style['fee-total__name']">
        <h4 class="lh-20">
          Total Fees
        </h4>
      </div>
      <div :class="$style['fee-total__currency']">
        CAD
      </div>
      <div :class="$style['fee-total__value']">
        <v-slide-y-reverse-transition
          name="slide"
          mode="out-in"
        >
          <div
            v-if="isMhrTransaction && !transferType"
            class="float-right"
          >
            <b>$ -</b>
          </div>
          <div
            v-else-if="isComplete || transferType || isMhrCorrection"
            class="float-right"
          >
            <b>${{ totalAmount?.toFixed(2) }}</b>
          </div>
          <div
            v-else
            class="float-right"
          >
            <b>-</b>
          </div>
        </v-slide-y-reverse-transition>
      </div>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import type { UITransferTypes, UnitNoteDocTypes } from '@/enums';
import { UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from './enums'
import type { AdditionalSearchFeeIF, FeeSummaryI, RegistrationLengthI } from './interfaces'
import { getFeeHint, getFeeSummary } from './factories'
import { storeToRefs } from 'pinia'
import { UnitNotesInfo } from '@/resources/unitNotes'

export default defineComponent({
  name: 'FeeSummary',
  props: {
    setFeeOverride: {
      default: null,
      type: Object as () => FeeSummaryI
    },
    setFeeType: {
      type: String as () => FeeSummaryTypes,
      default: () => ''
    },
    setFeeSubtitle: {
      type: String,
      default: ''
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
    setStaffReg: { type: Boolean, default: false },
    setStaffSBC: { type: Boolean, default: false },
    setStaffClientPayment: { type: Boolean, default: false }
  },
  setup (props) {
    const {
      getLengthTrust, isRoleStaff, getStaffPayment, isSearchCertified, getMhrUnitNoteType
    } = storeToRefs(useStore())

    const localState = reactive({
      feeType: props.setFeeType,
      feeSubType: computed((): UnitNoteDocTypes => getMhrUnitNoteType.value),
      registrationType: props.setRegistrationType,
      hasPriorityFee: computed((): boolean => getStaffPayment.value?.isPriority),
      hasCertifyFee: computed((): boolean => isSearchCertified.value),
      registrationLength: computed((): RegistrationLengthI => props.setRegistrationLength),
      isValid: computed((): boolean => {
        return getLengthTrust.value.valid ||
          [FeeSummaryTypes.MHR_SEARCH, FeeSummaryTypes.NEW_MHR, FeeSummaryTypes.MHR_TRANSFER,
            FeeSummaryTypes.MHR_UNIT_NOTE, FeeSummaryTypes.RESIDENTIAL_EXEMPTION,
            FeeSummaryTypes.NON_RESIDENTIAL_EXEMPTION, FeeSummaryTypes.MHR_TRANSPORT_PERMIT,
            FeeSummaryTypes.MHR_TRANSPORT_PERMIT_CANCEL,
            FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT, FeeSummaryTypes.MHR_STAFF_CORRECTION,
            FeeSummaryTypes.MHR_CLIENT_CORRECTION, FeeSummaryTypes.MHR_PUBLIC_AMENDMENT,
            FeeSummaryTypes.MHR_RE_REGISTRATION
          ]
          .includes(localState.feeType)
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
      isMhrTransaction: computed((): boolean => {
        return [FeeSummaryTypes.MHR_TRANSFER, FeeSummaryTypes.MHR_TRANSPORT_PERMIT]
          .includes(localState.feeType)
      }),
      isMhrCorrection: computed((): boolean => {
        return [FeeSummaryTypes.MHR_STAFF_CORRECTION, FeeSummaryTypes.MHR_CLIENT_CORRECTION]
          .includes(localState.feeType)
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
        return null
      }),
      totalFees: computed((): number => {
        if (localState.isValid) {
          return localState.feeSummary.feeAmount * localState.feeSummary.quantity
        }
        return null
      }),
      totalAdditionalFees: computed((): number => {
        if (localState.isValid) {
          return localState.additionalFeeSummary?.feeAmount * localState.additionalFeeSummary?.quantity
        }
        return null
      })
    })

    const mapFeeTypeToDisplayName = (feeType: FeeSummaryTypes): string => {
      switch (feeType) {
        case FeeSummaryTypes.DISCHARGE:
          return 'Total Discharge'
        case FeeSummaryTypes.RENEW:
          return 'Registration Renewal'
        case FeeSummaryTypes.AMEND:
          return 'Registration Amendment'
        case FeeSummaryTypes.MHR_SEARCH:
          return 'Manufactured Home search'
        case FeeSummaryTypes.MHR_COMBINED_SEARCH:
          return 'Combined Home and Lien search'
        case FeeSummaryTypes.MHR_TRANSFER:
          return 'Ownership Transfer or Change'
        case FeeSummaryTypes.MHR_TRANSPORT_PERMIT:
          return 'Location Change'
        case FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT:
          return 'Amend Transport Permit'
        case FeeSummaryTypes.MHR_TRANSPORT_PERMIT_CANCEL:
          return 'Cancel Transport Permit'
        case FeeSummaryTypes.MHR_UNIT_NOTE:
          return UnitNotesInfo[localState.feeSubType].header
        case FeeSummaryTypes.RESIDENTIAL_EXEMPTION:
          return 'Residential Exemption'
        case FeeSummaryTypes.NON_RESIDENTIAL_EXEMPTION:
          return 'Non-Residential Exemption'
        case FeeSummaryTypes.MHR_STAFF_CORRECTION:
        case FeeSummaryTypes.MHR_CLIENT_CORRECTION:
          return 'Registry Correction'
        default:
          return localState.registrationType
      }
    }

    watch(() => props.setFeeType, (val: FeeSummaryTypes) => {
      localState.feeType = val
    })
    watch(() => props.setRegistrationType, (val: UIRegistrationTypes) => {
      localState.registrationType = val
    })

    return {
      FeeSummaryTypes,
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
  &-name {
    color: $gray9;
  }
  &-name,
  &-value {
    font-weight: 700;
  }

  &-name {
    flex: 1 1 auto;
    margin-right: 1rem;
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
