<template>
  <v-card class="mt-8">
    <header class="font-weight-bold px-3 py-3">
      <slot name="header">Fee Summary</slot>
    </header>
    <v-slide-y-transition group tag="ul" class="fee-list">
      <template>
        <li class="fee-container fee-list__item"
          :key="registrationTypeFee"
          >
          <div class="fee-list__item-name pl-3">{{registrationTypeFee}}</div>
          <div class="fee-list__item-value" v-if="!isComplete">
            -
          </div>
          <div class="fee-list__item-value" v-else>
            ${{totalFees.toFixed(2)}}
          </div>
        </li>
        <li class="fee-container fee-list__hint" :key="hintFee" v-if="!isComplete">
          <div class="fee-list__hint pl-3">{{hintFee}}</div>
        </li>
        <li class="fee-container fee-list__item"
          :key="serviceFee"
          >
          <div class="fee-list__item-name pl-3">Service Fee</div>
          <div class="fee-list__item-value">${{serviceFee.toFixed(2)}}</div>
        </li>
      </template>
    </v-slide-y-transition>
    <div class="fee-container fee-total">
      <div class="fee-total__name">Total Fees</div>
      <div class="fee-total__currency">CAD</div>
      <div class="fee-total__value">
        <v-slide-y-reverse-transition name="slide" mode="out-in">
          <div v-if="isComplete" class="float-right"><b>${{totalAmount.toFixed(2)}}</b></div>
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
import { FeeSummaryIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { getServiceFee } from '@/utils'

export default defineComponent({
  props: {
    registrationType: {
      type: String,
      default: 'Security Agreement'
    },
    hint: {
      type: String,
      default: ''
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
    const feeSummary: FeeSummaryIF = getFeeSummary.value
    const localState = reactive({
      attachFee: props.attach,
      displayFee: props.display,
      registrationTypeFee: props.registrationType,
      hintFee: props.hint,
      feeAmount: feeSummary.feeAmount || 0,
      quantity: feeSummary.quantity || 0,
      feeCode: feeSummary.feeCode || '',
      isComplete: computed((): boolean => {
        return (localState.quantity > 0 && localState.feeAmount > 0)
      }),
      totalAmount: computed((): number => {
        return (localState.feeAmount * localState.quantity + localState.serviceFee)
      }),
      totalFees: computed((): number => {
        return localState.feeAmount * localState.quantity
      }),
      serviceFee: computed((): number => {
        return getServiceFee()
      })
    })
    watch(() => props.updatedFeeSummary, (val: FeeSummaryIF) => {
      localState.feeAmount = feeSummary.feeAmount
      localState.quantity = feeSummary.quantity
    }, { immediate: true, deep: true })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
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
  padding: 5px;
}

.fee-list__item {
  &-name, &-value {
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
    color: $gray5;
    font-weight: 500;
  }

  &__value {
    font-size: 1.65rem;
    font-weight: 700;
  }
}

</style>
