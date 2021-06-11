<template>
  <v-container fluid no-gutters class="white pa-0"  v-if="summaryView">
    <v-card flat id="length-trust-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="#38598A">mdi-calendar-clock</v-icon>
          <label class="pl-3"><strong>Registration Length and Trust Indenture</strong></label>
        </v-col>
      </v-row>
      <v-container class="pt-4 px-4" :class="{'invalid-message': showErrorSummary}">
      <v-row no-gutters v-if="showErrorSummary" class="pa-6">
        <v-col cols="auto">
          <span :class="{'invalid-message': showErrorSummary}">
          <v-icon color="#D3272C">mdi-information-outline</v-icon>
          This step is unfinished.
          </span>
          <span id="router-link-length-trust" :class="$style['invalid-link']" @click="goToLengthTrust()">
            Return to this step to complete it.
          </span>
        </v-col>
      </v-row>
      <v-row no-gutters class="ps-6 pt-6 pb-3">
        <v-col cols="3" class="generic-label">
          Registration Length
        </v-col>
        <v-col :class="$style['summary-text']">
          {{lengthSummary}}
        </v-col>
      </v-row>
      <v-row no-gutters class="ps-6 pb-6">
        <v-col cols="3" class="generic-label">
          Trust Indenture
        </v-col>
        <v-col :class="$style['summary-text']">
          {{trustIndentureSummary}}
        </v-col>
      </v-row>
      </v-container>
    </v-card>
  </v-container>
  <v-container fluid no-gutters class="white pt-10 pa-6 pr-10 rounded"
  :class="{'invalid-message': showErrorComponent}" v-else>
    <v-row no-gutters>
      <v-col cols="3" class="generic-label">
        <span :class="{'invalid-message': showErrorComponent}">Registration Length</span>
      </v-col>
      <v-col cols="auto">
        <v-radio-group v-model="lifeInfinite">
            <v-radio class="years-radio pa-0 ma-0"
                        :hide-details="false"
                        label=""
                        value="false"
                        @click="setLifeInfinite('false')">
            </v-radio>
            <v-radio class="infinite-radio pt-15 ma-0"
                        :hide-details="false"
                        label=""
                        value="true"
                        @click="setLifeInfinite('true')">
            </v-radio>
        </v-radio-group>
      </v-col>
      <v-col>
        <v-text-field id="life-years-field"
                        autocomplete="off"
                        :error-messages="lifeYearsMessage || ''"
                        filled
                        :readonly="lifeYearsDisabled"
                        :hint="lifeYearsHint"
                        persistent-hint
label="Length in Years"

                        v-model="lifeYearsEdit"/>
        <div class="pt-5">Infinite ($500.00 non-refundable)</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="3"></v-col>
      <v-col cols="9"><v-divider /></v-col>
    </v-row>
    <v-row no-gutters class='pt-10' v-if="showTrustIndenture">
      <v-col cols="3" class="generic-label">
        Trust Indenture
      </v-col>
      <v-col cols="auto">
        <v-checkbox class="trust-checkbox pa-0 ma-0"
                    :hide-details="false"
                    :hint="trustIndentureHint"
                    label=""
                    v-model="trustIndenture">
        </v-checkbox>
      </v-col>
      <v-col cols="8">
        <v-tooltip top content-class="top-tooltip pa-5" transition="fade-transition">
            <template v-slot:activator="{ on }">
              <span v-on="on" class="trust-indenture">Trust Indenture</span>
            </template>
Select if the security interest is contained in a Trust Indenture.

          </v-tooltip>
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
    defaultRegistrationType: {
      type: String,
      default: ''
    },
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { setFeeSummary } = useActions<any>(['setFeeSummary'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const { getFeeSummary } = useGetters<any>(['getFeeSummary'])
    const lengthTrust: LengthTrustIF = getLengthTrust.value
    const feeSummary: FeeSummaryIF = getFeeSummary.value
    const feeInfoYears = getFinancingFee(false)
    const feeInfoInfinite = getFinancingFee(true)
    const router = context.root.$router

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
      showErrorComponent: computed((): boolean => {
        return (lengthTrust.showInvalid)
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
    const goToLengthTrust = (): void => {
      lengthTrust.showInvalid = true
      setLengthTrust(lengthTrust)
      router.push({ path: '/length-trust' })
    }

    const setLifeInfinite = (val: string): void => {
      lengthTrust.lifeInfinite = (String(val) === 'true')
      localState.lifeYearsDisabled = lengthTrust.lifeInfinite
      if (lengthTrust.lifeInfinite) {
        localState.lifeYearsEdit = ''
        lengthTrust.lifeYears = 0
        lengthTrust.valid = true
        feeSummary.quantity = feeInfoInfinite.quantityMin
        feeSummary.feeAmount = feeInfoInfinite.feeAmount
        setLengthTrust(lengthTrust)
        setFeeSummary(feeSummary)
        context.emit('updated-fee-summary', feeSummary)
      } else {
        lengthTrust.valid = false
        lengthTrust.lifeYears = 0
        feeSummary.feeAmount = 0
        feeSummary.quantity = 0
        setLengthTrust(lengthTrust)
        setFeeSummary(feeSummary)
        context.emit('updated-fee-summary', feeSummary)
      }
    }

    watch(() => localState.lifeYearsEdit, (val: string) => {
      localState.lifeYearsMessage = ''
      if (val.length > 0) {
        var life = parseInt(val)
        if (isNaN(life)) {
          localState.lifeYearsMessage = 'Registration length must be a number between 1 and ' +
                                        localState.maxYears
          lengthTrust.valid = false
        } else if (life < 1 || life > feeInfoYears.quantityMax) {
          localState.lifeYearsMessage = 'Registration length must be between 1 and ' + localState.maxYears
          lengthTrust.valid = false
        } else {
          lengthTrust.lifeYears = life
          lengthTrust.valid = true
          localState.lifeInfinite = 'false'
          lengthTrust.showInvalid = false
          setLengthTrust(lengthTrust)
          feeSummary.quantity = life
          feeSummary.feeAmount = feeInfoYears.feeAmount
          setFeeSummary(feeSummary)
          if (feeSummary.quantity > 0 && feeSummary.feeAmount > 0) {
            context.emit('updated-fee-summary', feeSummary)
          }
        }
      } else {
        lengthTrust.valid = false
      }
      if (!lengthTrust.valid && !lengthTrust.lifeInfinite) {
        lengthTrust.valid = false
        setLengthTrust(lengthTrust)
        feeSummary.feeAmount = 0
        feeSummary.quantity = 0
        setFeeSummary(feeSummary)
        context.emit('updated-fee-summary', feeSummary)
      }
    })
    watch(() => localState.trustIndenture, (val: boolean) => {
      lengthTrust.trustIndenture = val
      setLengthTrust(lengthTrust)
    })

    return {
      goToLengthTrust,
      setLifeInfinite,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.summary-text{
  font-size: 16px;
  color: $gray7;
}
.invalid-link {
  padding: 0.25rem;
  font-size: 16px;
  color: #1669BB;
  text-decoration: underline;
  cursor: pointer;
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

::v-deep .theme--light.v-input.error--text input {
  color: #d3272c
}

</style>
