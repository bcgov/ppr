<template>
  <v-container fluid no-gutters class="white pa-6">
    <v-row no-gutters>
      <v-col cols="2" :class="$style[length-trust-label]">
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
      <v-col cols="auto">
        <v-text-field id="life-years-field"
                        autocomplete="off"
                        :error-messages="lifeYearsMessage || ''"
                        filled
                        :disabled="lifeYearsDisabled"
                        :hint="lifeYearsHint"
                        persistent-hint
                        placeholder="Length (years)"
                        v-model="lifeYearsEdit"/>
        <div class="pt-5">Infinite ($500.00 non-refundable)</div>
      </v-col>
    </v-row>
    <v-row no-gutters class='pt-10' v-if="showTrustIndenture">
      <v-col cols="2" :class="$style[length-trust-label]">
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
      <v-col cols="auto">
        Trust Indenture (Optional)
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { LengthTrustIF, FeeSummaryIF } from '@/interfaces' // eslint-disable-line no-unused-vars

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
    }
  },
  setup (props, { emit }) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { setFeeSummary } = useActions<any>(['setFeeSummary'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const { getFeeSummary } = useGetters<any>(['getFeeSummary'])
    const lengthTrust: LengthTrustIF = getLengthTrust.value
    const feeSummary: FeeSummaryIF = getFeeSummary.value
    const localState = reactive({
      registrationType: props.defaultRegistrationType,
      trustIndenture: lengthTrust.trustIndenture,
      lifeYearsDisabled: false,
      lifeInfinite: lengthTrust.lifeInfinite,
      lifeYearsEdit: (lengthTrust.lifeYears > 0) ? lengthTrust.lifeYears.toString() : '',
      lifeYearsMessage: '',
      trustIndentureHint: '',
      lifeYearsHint: 'Minimum 1 year, Maximum 25 years ($5.00 per year)',
      showTrustIndenture: computed((): boolean => {
        return (localState.registrationType === '' || localState.registrationType === 'SA' ||
                localState.registrationType === 'SG')
      })
    })
    watch(() => localState.lifeYearsEdit, (val: string) => {
      localState.lifeYearsMessage = ''
      if (val.length > 0) {
        var life = parseInt(val)
        if (isNaN(life)) {
          localState.lifeYearsMessage = 'Registration length must be a number between 1 and 25.'
        } else if (life < 1 || life > 25) {
          localState.lifeYearsMessage = 'Registration length must be between 1 and 25.'
        } else {
          lengthTrust.lifeYears = life
          setLengthTrust(lengthTrust)
          feeSummary.quantity = life
          feeSummary.feeAmount = 5.00
          setFeeSummary(feeSummary)
        }
      }
    })
    watch(() => localState.trustIndenture, (val: boolean) => {
      lengthTrust.trustIndenture = val
      setLengthTrust(lengthTrust)
    })
    watch(() => localState.lifeInfinite, (val: boolean) => {
      // localState.lifeYearsDisabled = localState.lifeInfinite
      lengthTrust.lifeInfinite = val
      if (localState.lifeInfinite) {
        localState.lifeYearsEdit = ''
        lengthTrust.lifeYears = 0
        feeSummary.quantity = 1
        feeSummary.feeAmount = 500.00
        setFeeSummary(feeSummary)
      }
      setLengthTrust(lengthTrust)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.length-trust-label {
  font-size: 0.875rem;
}
</style>
