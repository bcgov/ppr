<template>
  <v-card>
    <header class="font-weight-bold px-3 py-3">
      <slot name="header">Fee Summary</slot>
    </header>
    <v-slide-y-transition group tag="ul" :class="$style['fee-list']">
      <template>
        <li
          :class="[$style['fee-container'], $style['fee-list__item']]"
          :key="registrationTypeFee"
        >
          <div :class="$style['fee-list__item-name']" class="pl-3">
            {{ registrationTypeFee }}
          </div>
          <div :class="$style['fee-list__item-value']" v-if="hasNoCharge()">
            No Fee
          </div>
          <div :class="$style['fee-list__item-value']" v-else-if="!isComplete">
            -
          </div>
          <div :class="$style['fee-list__item-value']" v-else>
            ${{ totalFees.toFixed(2) }}
          </div>
        </li>
        <li
          :class="[$style['fee-container'], $style['fee-list__hint']]"
          :key="hintFee"
          v-if="!isComplete || hasNoCharge() || registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN
           || registrationTypeAPI === APIRegistrationTypes.MARRIAGE_MH"
        >
          <div class="fee-list__hint pl-3">{{ hintFee }}</div>
        </li>
        <li
          :class="[$style['fee-container'], $style['fee-list__item']]"
          :key="serviceFee"
        >
          <div :class="$style['fee-list__item-name']" class="pl-3">
            Service Fee
          </div>
          <div :class="$style['fee-list__item-value']" v-if="hasNoCharge()">
            No Fee
          </div>
          <div :class="$style['fee-list__item-value']" v-else>
            ${{ serviceFee.toFixed(2) }}
          </div>
        </li>
      </template>
    </v-slide-y-transition>
    <div :class="[$style['fee-container'], $style['fee-total']]">
      <div :class="$style['fee-total__name']">Total Fees</div>
      <div :class="$style['fee-total__currency']">CAD</div>
      <div :class="$style['fee-total__value']">
        <v-slide-y-reverse-transition name="slide" mode="out-in">
          <div v-if="hasNoCharge()" class="float-right"><b>$0.00</b></div>
          <div v-else-if="isComplete" class="float-right">
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
  watch,
  onMounted
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { FeeSummaryIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { getServiceFee, getFinancingFee } from '@/utils'
import { APIRegistrationTypes } from '@/enums'

export default defineComponent({
  props: {
    registrationType: {
      type: String,
      default: 'Security Agreement'
    },
    updatedFeeSummary: {
      type: Object as () => FeeSummaryIF
    },
    attach: {
      type: String,
      default: '#app'
    },
    display: {
      type: Boolean,
      default: true
    }
  },
  setup (props) {
    const { getFeeSummary } = useGetters<any>(['getFeeSummary'])
    const { getRegistrationType } = useGetters<any>(['getRegistrationType'])
    const feeSummary: FeeSummaryIF = getFeeSummary.value
    const registrationTypeAPI = getRegistrationType.value.registrationTypeAPI

    const hasNoCharge = (): boolean => {
      const hfArray = [
        APIRegistrationTypes.LAND_TAX_LIEN,
        APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
        APIRegistrationTypes.LAND_TAX_LIEN,
        APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
        APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
        APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
        APIRegistrationTypes.FOREST,
        APIRegistrationTypes.LOGGING_TAX,
        APIRegistrationTypes.CARBON_TAX,
        APIRegistrationTypes.RURAL_PROPERTY_TAX,
        APIRegistrationTypes.PROVINCIAL_SALES_TAX,
        APIRegistrationTypes.INCOME_TAX,
        APIRegistrationTypes.MOTOR_FUEL_TAX,
        APIRegistrationTypes.EXCISE_TAX,
        APIRegistrationTypes.LIEN_UNPAID_WAGES,
        APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
        APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
        APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
        APIRegistrationTypes.MAINTENANCE_LIEN,
        APIRegistrationTypes.OTHER
      ]
      return hfArray.includes(registrationTypeAPI)
    }

    const localState = reactive({
      attachFee: props.attach,
      displayFee: props.display,
      registrationTypeFee: props.registrationType,
      feeAmount: feeSummary.feeAmount || 0,
      quantity: feeSummary.quantity || 0,
      feeCode: feeSummary.feeCode || '',
      hintFee: computed((): string => {
        if (hasNoCharge() || (registrationTypeAPI === APIRegistrationTypes.MARRIAGE_MH)) {
          return 'Infinite Registration (default)'
        }
        if (registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
          return '180 Day Registration (default)'
        }
        return getFinancingFee(false).hint
      }),
      isComplete: computed((): boolean => {
        return localState.quantity > 0 && localState.feeAmount > 0
      }),
      totalAmount: computed((): number => {
        return (
          localState.feeAmount * localState.quantity + localState.serviceFee
        )
      }),
      totalFees: computed((): number => {
        return localState.feeAmount * localState.quantity
      }),
      serviceFee: computed((): number => {
        return getServiceFee()
      })
    })

    watch(
      () => props.updatedFeeSummary,
      (val: FeeSummaryIF) => {
        localState.feeAmount = feeSummary.feeAmount
        localState.quantity = feeSummary.quantity
      },
      { immediate: true, deep: true }
    )

    onMounted(() => {
      switch (registrationTypeAPI) {
        case APIRegistrationTypes.REPAIRERS_LIEN:
          localState.feeAmount = 5
          localState.quantity = 1
          break
        case APIRegistrationTypes.MARRIAGE_MH:
          localState.feeAmount = 10
          localState.quantity = 1
          break
      }
    })

    return {
      hasNoCharge,
      registrationTypeAPI,
      APIRegistrationTypes,
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
  padding: 1em;
}

.fee-list {
  border-bottom: 1px solid $gray3;
  padding-left: 0px;
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

.fee-list__item + .fee-list__item {
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
