<template>
  <v-container fluid no-gutters class="white pa-1">
    <v-row no-gutters class="pt-0">
      <v-col cols="12">
        <v-card color="primary">
          <v-card-title><div class="header">Fee Summary</div></v-card-title>
        </v-card>
      </v-col>
    </v-row>
<!--
  <v-dialog permanent :attach="attach" v-model="display" width="350">
    <v-card>
      <v-card-title><div class="header">Fee Summary</div></v-card-title>
-->
    <v-row no-gutters class="pa-2">
      <v-col cols="8">
        <div><b>{{registrationType}}</b></div>
        <div v-if="!isComplete">{{hint}}</div>
      </v-col>
      <v-col cols="4">
        <div v-if="isComplete" class="float-right">${{totalFees.toFixed(2)}}</div>
        <div v-else class="float-right"><b>-</b></div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pa-2">
      <v-col cols="8">
        <div><b>Service fee</b></div>
      </v-col>
      <v-col cols="4">
        <div class="float-right">${{serviceFee.toFixed(2)}}</div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pa-2">
        <v-col cols="6">
          <div class="payment-total">Total Fees</div>
        </v-col>
        <v-col cols="2">
          <div class="fee-currency">CAD</div>
        </v-col>
        <v-col cols="4">
          <div class="payment-total">
              <v-slide-y-reverse-transition name="slide" mode="out-in">
              <div v-if="isComplete" class="float-right"><b>${{totalAmount.toFixed(2)}}</b></div>
              <div v-else class="float-right"><b>-</b></div>
              </v-slide-y-reverse-transition>
          </div>
        </v-col>
    </v-row>
<!--
    </v-card>
  </v-dialog>
-->
  </v-container>
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
      attach: props.attach,
      display: props.display,
      registrationType: props.registrationType,
      hint: props.hint,
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.payment-fee {
  background-color: $gray1;
}

.fee-currency {
  color: $gray6;
}

.fee-list {
  padding-left: 0 !important;
  border-bottom: 1px solid $gray4;
}

.payment-total {
  font-weight: bold;
}

.header {
  color: white;
  font-size: 1.125rem;
}
</style>
