<template>
  <v-card>
    <header class="font-weight-bold px-3 py-3">
      <slot name="header">Fee Summary</slot>
    </header>
    <v-slide-y-transition group tag="ul" :class="[$style['fee-list']]">
      <template>
        <li
          :class="[$style['fee-container'], $style['fee-list__item'], { 'pb-4': !hintFee }, 'pr-4', 'pt-5']"
          :key="feeLabel"
        >
          <div :class="$style['fee-list__item-name']">
            {{ feeLabel }}
          </div>
          <div
            v-if="feeSummary && feeSummary.feeAmount === 0"
            :class="$style['fee-list__item-value']"
          >
            No Fee
          </div>
          <div v-else-if="!isComplete" :class="$style['fee-list__item-value']">
            -
          </div>
          <div v-else :class="$style['fee-list__item-value']">
            ${{ totalFees.toFixed(2) }}
          </div>
        </li>
        <li
          v-if="hintFee"
          :class="[$style['fee-container'], $style['fee-list__hint'], 'pb-4', 'pr-4', 'pt-3']"
          :key="hintFee"
        >
          <div class="fee-list__hint">{{ hintFee }}</div>
        </li>
        <li
          v-if="hasProcessingFee"
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
          v-else
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
      </template>
    </v-slide-y-transition>
    <div :class="[$style['fee-container'], $style['fee-total'], 'pa-4']">
      <div :class="$style['fee-total__name']">Total Fees</div>
      <div :class="$style['fee-total__currency']">CAD</div>
      <div :class="$style['fee-total__value']">
        <v-slide-y-reverse-transition name="slide" mode="out-in">
          <div v-if="isComplete" class="float-right">
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
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from './enums' // eslint-disable-line no-unused-vars
import { FeeSummaryI, RegistrationLengthI } from './interfaces' // eslint-disable-line no-unused-vars
import { getFeeSummary, getFeeHint } from './factories'

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
    setRegistrationLength: {
      type: Object as () => RegistrationLengthI
    },
    setRegistrationType: {
      type: String as () => UIRegistrationTypes
    },
    setStaffReg: { default: false },
    setStaffSBC: { default: false }
  },
  setup (props) {
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const localState = reactive({
      feeType: props.setFeeType,
      registrationType: props.setRegistrationType,
      registrationLength: computed((): RegistrationLengthI => {
        return props.setRegistrationLength
      }),
      isValid: computed((): boolean => { return getLengthTrust.value.valid }),
      feeLabel: computed((): string => {
        if (localState.feeType === FeeSummaryTypes.DISCHARGE) {
          return 'Total Discharge'
        } else if (localState.feeType === FeeSummaryTypes.RENEW) {
          return 'Registration Renewal'
        } else if (localState.feeType === FeeSummaryTypes.AMEND) {
          return 'Registration Amendment'
        } else if (localState.feeType === FeeSummaryTypes.MHSEARCH) {
          return 'Manufactured Home Search'
        } else {
          return localState.registrationType
        }
      }),
      feeSummary: computed((): FeeSummaryI => {
        const feeSummary = getFeeSummary(
          localState.feeType,
          localState.registrationType,
          localState.registrationLength
        )
        if (localState.feeType === FeeSummaryTypes.RENEW) {
          feeSummary.processingFee = 5
        }
        if (props.setFeeOverride) {
          feeSummary.feeAmount = props.setFeeOverride.feeAmount
        }
        if (props.setFeeOverride && feeSummary.serviceFee !== 0) {
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
        return localState.feeSummary.quantity > 0 && localState.isValid
      }),
      totalAmount: computed((): number => {
        if (localState.isValid) {
          let extraFee = localState.feeSummary.serviceFee
          if (localState.hasProcessingFee) {
            extraFee = localState.feeSummary.processingFee
          }
          return (
            localState.feeSummary.feeAmount *
            localState.feeSummary.quantity +
            extraFee
          )
        }
      }),
      totalFees: computed((): number => {
        if (localState.isValid) {
          return localState.feeSummary.feeAmount * localState.feeSummary.quantity
        }
      })
    })

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
  padding-left: 30px !important;
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
