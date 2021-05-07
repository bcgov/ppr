<template>
  <v-container fluid no-gutters class="white pa-0"  v-if="summaryView">
    <v-card flat id="length-trust-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="#38598A">mdi-calendar-clock</v-icon>
          <label class="pl-3"><strong>Registration Length and Trust Indenture</strong></label>
        </v-col>
      </v-row>
      <v-container :class="{'invalid-message': showErrorSummary}">
      <v-row no-gutters v-if="showErrorSummary" class="pa-6">
        <v-col cols="auto">
          <v-icon color="#D3272C">mdi-information-outline</v-icon>
          This step is unfinished
          <router-link id="router-link-length-trust" class="invalid-link" :to="{ path: '/length-trust' }">
            Return to this step to complete it.
          </router-link>
        </v-col>
      </v-row>
      <v-row no-gutters class="ps-6 pb-3">
        <v-col cols="3" class="length-trust-label">
          Registration Length
        </v-col>
        <v-col class="summary-text">
          {{lengthSummary}}
        </v-col>
      </v-row>
      <v-row no-gutters class="ps-6 pb-3">
        <v-col cols="3" class="length-trust-label">
          Trust Indenture
        </v-col>
        <v-col class="summary-text">
          {{trustIndentureSummary}}
        </v-col>
      </v-row>
      </v-container>
    </v-card>
  </v-container>
  <v-container fluid no-gutters class="white pa-6"  v-else>
    <v-row no-gutters>
      <v-col cols="3" class="length-trust-label">
        Registration Length
      </v-col>
      <v-col cols="1">
        <v-radio-group v-model="lifeInfinite">
            <v-radio class="years-radio pa-0 ma-0"
                        :hide-details="false"
                        label=""
                        value="false">
            </v-radio>
            <v-radio class="infinite-radio pt-15 ma-0"
                        :hide-details="false"
                        label=""
                        value="true">
            </v-radio>
        </v-radio-group>
      </v-col>
      <v-col cols="8">
        <v-text-field id="life-years-field"
                        autocomplete="off"
                        :error-messages="lifeYearsMessage || ''"
                        filled
                        :readonly="lifeYearsDisabled"
                        :hint="lifeYearsHint"
                        persistent-hint
                        placeholder="Length (years)"
                        v-model="lifeYearsEdit"/>
        <div class="pt-5">Infinite ($500.00 non-refundable)</div>
      </v-col>
      <v-divider class="mx-4" />
    </v-row>
    <v-row no-gutters class='pt-10' v-if="showTrustIndenture">
      <v-col cols="3" class="length-trust-label">
        Trust Indenture
      </v-col>
      <v-col cols="1">
        <v-checkbox class="trust-checkbox pa-0 ma-0"
                    :hide-details="false"
                    :hint="trustIndentureHint"
                    label=""
                    v-model="trustIndenture">
        </v-checkbox>
      </v-col>
      <v-col cols="8">
        Trust Indenture (Optional)
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local
import { LengthTrustIF, FeeSummaryIF, FeeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { getFinancingFee } from '@/utils'

export default defineComponent({
  props: {
    defaultTrustIndenture: {
      type: Boolean,
      default: false
    },
    defaultLifeInfinite: {
      type: Boolean,
      default: false
    },
    defaultLifeYears: {
      type: String,
      default: ''
    },
    defaultRegistrationType: {
      type: String,
      default: ''
    },
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { setFeeSummary } = useActions<any>(['setFeeSummary'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const { getFeeSummary } = useGetters<any>(['getFeeSummary'])
    const lengthTrust: LengthTrustIF = getLengthTrust.value
    const feeSummary: FeeSummaryIF = getFeeSummary.value
    const feeInfoYears = getFinancingFee(false)
    const feeInfoInfinite = getFinancingFee(true)

    const localState = reactive({
      summaryView: props.isSummary,
      registrationType: props.defaultRegistrationType,
      trustIndenture: lengthTrust.trustIndenture,
      lifeYearsDisabled: lengthTrust.lifeInfinite,
      lifeInfinite: lengthTrust.valid ? lengthTrust.lifeInfinite.toString() : '',
      maxYears: feeInfoYears.quantityMax.toString(),
      lifeYearsEdit: (lengthTrust.lifeYears > 0) ? lengthTrust.lifeYears.toString() : '',
      lifeYearsMessage: '',
      trustIndentureHint: '',
      lifeYearsHint: 'Minimum 1 year, Maximum ' + feeInfoYears.quantityMax.toString() + ' years ($' +
                     feeInfoYears.feeAmount.toFixed(2) + ' per year)',
      showTrustIndenture: computed((): boolean => {
        return (localState.registrationType === '' || localState.registrationType === 'SA' ||
                localState.registrationType === 'SG')
      }),
      showErrorSummary: computed((): boolean => {
        return (!lengthTrust.valid)
      }),
      lengthSummary: computed((): string => {
        if (!lengthTrust.lifeInfinite && lengthTrust.lifeYears < 1) {
          return 'Not entered'
        }
        if (lengthTrust.lifeInfinite) {
          return 'Infinite'
        }
        if (lengthTrust.lifeYears === 1) {
          return (lengthTrust.lifeYears.toString() + ' Year')
        }
        return lengthTrust.lifeYears.toString() + ' Years'
      }),
      trustIndentureSummary: computed((): string => {
        return (lengthTrust.trustIndenture ? 'Yes' : 'No')
      })
    })
    watch(() => localState.lifeYearsEdit, (val: string) => {
      localState.lifeYearsMessage = ''
      if (val.length > 0) {
        var life = parseInt(val)
        if (isNaN(life)) {
          localState.lifeYearsMessage = 'Registration length must be a number between 1 and ' +
                                        localState.maxYears + '.'
          if (lengthTrust.valid) {
            lengthTrust.valid = false
            setLengthTrust(lengthTrust)
          }
        } else if (life < 1 || life > feeInfoYears.quantityMax) {
          localState.lifeYearsMessage = 'Registration length must be between 1 and ' + localState.maxYears + '.'
          if (lengthTrust.valid) {
            lengthTrust.valid = false
            setLengthTrust(lengthTrust)
          }
        } else {
          lengthTrust.lifeYears = life
          lengthTrust.valid = true
          setLengthTrust(lengthTrust)
          feeSummary.quantity = life
          feeSummary.feeAmount = feeInfoYears.feeAmount
          setFeeSummary(feeSummary)
          if (feeSummary.quantity > 0 && feeSummary.feeAmount > 0) {
            emit('updated-fee-summary', feeSummary)
          }
        }
      } else if (lengthTrust.valid && !lengthTrust.lifeInfinite) {
        lengthTrust.valid = false
        setLengthTrust(lengthTrust)
        feeSummary.feeAmount = 0
        feeSummary.quantity = 0
        setFeeSummary(feeSummary)
        emit('updated-fee-summary', feeSummary)
      }
    })
    watch(() => localState.trustIndenture, (val: boolean) => {
      lengthTrust.trustIndenture = val
      setLengthTrust(lengthTrust)
    })
    watch(() => localState.lifeInfinite, (val: string) => {
      lengthTrust.lifeInfinite = (String(val) === 'true')
      localState.lifeYearsDisabled = lengthTrust.lifeInfinite
      if (lengthTrust.lifeInfinite) {
        localState.lifeYearsEdit = ''
        lengthTrust.lifeYears = 0
        lengthTrust.valid = true
        feeSummary.quantity = feeInfoInfinite.quantityMin
        feeSummary.feeAmount = feeInfoInfinite.feeAmount
      } else {
        lengthTrust.valid = false
        lengthTrust.lifeYears = 0
        feeSummary.feeAmount = 0
        feeSummary.quantity = 0
      }
      setLengthTrust(lengthTrust)
      setFeeSummary(feeSummary)
      emit('updated-fee-summary', feeSummary)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .length-trust-label {
  color: $gray9;
  font-weight: bold;
}

.summary-text{
  font-size: 16px;
  color: $gray7;
}

.invalid-link {
  padding: 1.25rem;
  font-size: 16px;
  color: #1669BB;
}
.length-trust-header {
  padding: 0.5rem 1.25rem 0.5rem 1.25rem;
  font-size: 0.875rem;
  margin-top: 1rem;
}
.length-trust-content {
  margin-top: 0.5rem;
  padding: 0.5rem 1.25rem 0.5rem 1.25rem;
  border-top: 1px solid $gray1;
  font-size: 0.875rem;
  .length-trust-title {
    color: $gray7;
  }
}
.v-list-item {
  min-height: 0;
  padding: 0 1rem 0 0.5rem;
}
.col {
  padding: 0.25rem;
  .col-roles {
    padding: 0 !important;
  }
}
.warning-text {
  position: relative;
  top: 2px;
  left: 2px;
  color: $BCgovGold9;
}

</style>
