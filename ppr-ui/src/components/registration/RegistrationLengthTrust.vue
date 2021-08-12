<template>
  <v-container fluid no-gutters class="white pa-0" v-if="summaryView">
    <v-card flat id="length-trust-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="#38598A">mdi-calendar-clock</v-icon>
          <label
            class="pl-3"
            v-if="registrationType !== APIRegistrationTypes.REPAIRERS_LIEN"
          >
            <strong>Registration Length and Trust Indenture</strong>
          </label>
          <label class="pl-3" v-else>
            <strong>Amount and Date of Surrender</strong>
          </label>
        </v-col>
      </v-row>
      <v-container
        class="pt-4 px-4"
        :class="{ 'invalid-message': showErrorSummary }"
      >
        <v-row no-gutters v-if="showErrorSummary" class="pa-6">
          <v-col cols="auto">
            <span :class="{ 'invalid-message': showErrorSummary }">
              <v-icon color="#D3272C">mdi-information-outline</v-icon>
              This step is unfinished.
            </span>
            <span
              id="router-link-length-trust"
              class="invalid-link"
              @click="goToLengthTrust()"
            >
              Return to this step to complete it.
            </span>
          </v-col>
        </v-row>
        <v-row no-gutters class="ps-6 pt-6 pb-3">
          <v-col cols="3" class="generic-label">
            Registration Length
          </v-col>
          <v-col :class="$style['summary-text']">
            {{ lengthSummary }}
          </v-col>
        </v-row>
        <v-row no-gutters class="ps-6 pb-6" v-if="registrationType === 'SA'">
          <v-col cols="3" class="generic-label">
            Trust Indenture
          </v-col>
          <v-col :class="$style['summary-text']">
            {{ trustIndentureSummary }}
          </v-col>
        </v-row>
        <v-row
          no-gutters
          class="ps-6 pb-3"
          v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN"
        >
          <v-col cols="3" class="generic-label">
            Amount of Lien
          </v-col>
          <v-col :class="$style['summary-text']">
            {{ lienAmountSummary }}
          </v-col>
        </v-row>
        <v-row
          no-gutters
          class="ps-6 pb-6"
          v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN"
        >
          <v-col cols="3" class="generic-label">
            Surrender Date
          </v-col>
          <v-col :class="$style['summary-text']">
            {{ surrenderDateSummary }}
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-container>
  <v-container
    fluid
    no-gutters
    class="white pt-10 pa-6 pr-10 rounded"
    :class="{ 'invalid-message': lengthTrust.showInvalid }"
    v-else
  >
    <div v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN">
      <v-row no-gutters class="ps-6 pt-6 pb-3">
        <v-col cols="3" class="generic-label">
          Registration Length
        </v-col>
        <v-col class="summary-text pl-2">
          {{ lengthSummary }}
        </v-col>
      </v-row>
      <v-row no-gutters class="ps-6 pt-6">
        <v-col cols="3" class="generic-label pt-3">
          <span :class="{ 'invalid-message': showErrorLienAmount }"
            >Amount of Lien</span
          >
        </v-col>
        <v-col>
          <v-text-field
            id="lien-amount"
            autocomplete="off"
            :error-messages="lienAmountMessage || ''"
            filled
            hint="Example: 10,500.50"
            persistent-hint
            label="Amount in Canadian Dollars ($)"
            v-model="lienAmount"
          />
        </v-col>
      </v-row>
      <v-row no-gutters class="ps-6 pt-4">
        <v-col cols="3" class="generic-label pt-3">
          <span :class="{ 'invalid-message': showErrorSurrenderDate }"
            >Surrender Date</span
          >
        </v-col>
        <v-col>
          <v-dialog
            ref="dialog"
            v-model="modal"
            :return-value.sync="surrenderDate"
            persistent
            width="450px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="surrenderDate"
                :error-messages="surrenderDateMessage || ''"
                filled
                hint="Must be within the last 21 days"
                persistent-hint
                label="Date"
                append-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="surrenderDate"
              elevation="15"
              :min="minSurrenderDate"
              :max="maxSurrenderDate"
              scrollable
              width="450px"
            >
              <v-spacer></v-spacer>
              <v-btn
                text
                color="primary"
                @click="$refs.dialog.save(surrenderDate)"
              >
                <strong>OK</strong>
              </v-btn>
              <v-btn text color="primary" @click="modal = false">
                Cancel
              </v-btn>
            </v-date-picker>
          </v-dialog>
        </v-col>
      </v-row>
    </div>
    <div v-else>
      <v-row no-gutters>
        <v-col cols="3" class="generic-label">
          <span :class="{ 'invalid-message': lengthTrust.showInvalid }"
            >Registration Length</span
          >
        </v-col>
        <v-col cols="auto">
          <span v-if="infinityPreselected()">
            Infinite
          </span>
          <v-radio-group v-else v-model="lifeInfinite">
            <v-radio
              class="years-radio pa-0 ma-0"
              :hide-details="false"
              label=""
              value="false"
              id="length-in-years"
              @click="setLifeInfinite('false')"
            >
            </v-radio>
            <v-radio
              class="infinite-radio pt-15 ma-0"
              :hide-details="false"
              label=""
              value="true"
              id="length-infinite"
              @click="setLifeInfinite('true')"
            >
            </v-radio>
          </v-radio-group>
        </v-col>
        <v-col v-if="!infinityPreselected()">
          <v-text-field
            id="life-years-field"
            autocomplete="off"
            :error-messages="lifeYearsMessage || ''"
            filled
            :readonly="lifeYearsDisabled"
            :hint="lifeYearsHint"
            persistent-hint
            label="Length in Years"
            v-model="lifeYearsEdit"
          />
          <div class="pt-5">Infinite ($500.00 non-refundable)</div>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3"></v-col>
        <v-col cols="9" v-if="!infinityPreselected()"><v-divider /></v-col>
      </v-row>
      <v-row no-gutters class="pt-10" v-if="showTrustIndenture">
        <v-col cols="3" class="generic-label">
          Trust Indenture
        </v-col>
        <v-col cols="auto">
          <v-checkbox
            class="trust-checkbox pa-0 ma-0"
            :hide-details="false"
            :hint="trustIndentureHint"
            label=""
            id="trust-indenture-checkbox"
            v-model="trustIndenture"
          >
          </v-checkbox>
        </v-col>
        <v-col cols="8">
          <v-tooltip
            top
            content-class="top-tooltip pa-5"
            transition="fade-transition"
          >
            <template v-slot:activator="{ on }">
              <span v-on="on" class="trust-indenture">Trust Indenture</span>
            </template>
            Select if the security interest is contained in a Trust Indenture.
          </v-tooltip>
        </v-col>
      </v-row>
    </div>
  </v-container>
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
import { useGetters, useActions } from 'vuex-composition-helpers'

// local
import { LengthTrustIF, FeeSummaryIF, FeeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate, getFinancingFee } from '@/utils'
import { APIRegistrationTypes } from '@/enums'

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
    const { getRegistrationType } = useGetters<any>(['getRegistrationType'])
    const registrationType = getRegistrationType.value.registrationTypeAPI
    const lengthTrust: LengthTrustIF = getLengthTrust.value
    const feeSummary: FeeSummaryIF = getFeeSummary.value
    const feeInfoYears = getFinancingFee(false)
    const feeInfoInfinite = getFinancingFee(true)
    const router = context.root.$router

    if (
      registrationType === APIRegistrationTypes.REPAIRERS_LIEN &&
      lengthTrust.lifeYears !== 1
    ) {
      lengthTrust.lifeYears = 1
      feeSummary.quantity = 1
      feeSummary.feeAmount = feeInfoYears.feeAmount
      setFeeSummary(feeSummary)
    }

    const localState = reactive({
      summaryView: props.isSummary,
      trustIndenture: lengthTrust.trustIndenture,
      lifeYearsDisabled: lengthTrust.lifeInfinite,
      lifeInfinite: lengthTrust.valid
        ? lengthTrust.lifeInfinite.toString()
        : '',
      maxYears: feeInfoYears.quantityMax.toString(),
      lifeYearsEdit:
        lengthTrust.lifeYears > 0 ? lengthTrust.lifeYears.toString() : '',
      lifeYearsMessage: '',
      trustIndentureHint: '',
      surrenderDate: lengthTrust.surrenderDate,
      lienAmount: lengthTrust.lienAmount,
      lifeYearsHint:
        'Minimum 1 year, Maximum ' +
        feeInfoYears.quantityMax.toString() +
        ' years ($' +
        feeInfoYears.feeAmount.toFixed(2) +
        ' per year)',
      showTrustIndenture: computed((): boolean => {
        return (
          registrationType ===
            APIRegistrationTypes.SECURITY_AGREEMENT
        )
      }),
      showErrorSummary: computed((): boolean => {
        return !lengthTrust.valid
      }),
      showErrorLienAmount: computed((): boolean => {
        return lengthTrust.showInvalid && lengthTrust.lienAmount === ''
      }),
      showErrorSurrenderDate: computed((): boolean => {
        return lengthTrust.showInvalid && lengthTrust.surrenderDate === ''
      }),
      lienAmountMessage: computed((): string => {
        if (lengthTrust.showInvalid && lengthTrust.lienAmount === '') {
          return 'This field is required'
        }
        return ''
      }),
      surrenderDateMessage: computed((): string => {
        if (lengthTrust.showInvalid && lengthTrust.surrenderDate === '') {
          return 'This field is required'
        }
        return ''
      }),
      minSurrenderDate: computed((): string => {
        var dateOffset = 24 * 60 * 60 * 1000 * 21 // 21 days in milliseconds
        var minDate = new Date()
        minDate.setTime(minDate.getTime() - dateOffset)
        return minDate.toISOString()
      }),
      maxSurrenderDate: computed((): string => {
        return new Date().toISOString()
      }),
      lengthSummary: computed((): string => {
        if (
          registrationType === APIRegistrationTypes.REPAIRERS_LIEN
        ) {
          return '180 Days'
        }
        if (!lengthTrust.lifeInfinite && lengthTrust.lifeYears < 1) {
          return 'Not entered'
        }
        if (lengthTrust.lifeInfinite) {
          return 'Infinite'
        }
        if (lengthTrust.lifeYears === 1) {
          return lengthTrust.lifeYears.toString() + ' Year'
        }
        return lengthTrust.lifeYears.toString() + ' Years'
      }),
      trustIndentureSummary: computed((): string => {
        return lengthTrust.trustIndenture ? 'Yes' : 'No'
      }),
      lienAmountSummary: computed((): string => {
        if (lengthTrust.lienAmount !== '') {
          var currency = lengthTrust.lienAmount
            .replace('$', '')
            .replaceAll(',', '')
          var lienFloat = parseFloat(currency)
          if (isNaN(lienFloat)) {
            return lengthTrust.lienAmount
          }
          return '$' + lienFloat.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
        }
        return 'Not entered'
      }),
      surrenderDateSummary: computed((): string => {
        if (
          lengthTrust.surrenderDate !== '' &&
          lengthTrust.surrenderDate.length >= 10
        ) {
          return convertDate(
            new Date(lengthTrust.surrenderDate.substring(0, 10)),
            false,
            false
          )
        }
        if (lengthTrust.surrenderDate === '') {
          return 'Not entered'
        }
        return lengthTrust.surrenderDate
      })
    })
    const goToLengthTrust = (): void => {
      lengthTrust.showInvalid = true
      setLengthTrust(lengthTrust)
      router.push({ path: '/length-trust' })
    }

    const infinityPreselected = (): boolean => {
      const ipArray = [
        APIRegistrationTypes.MARRIAGE_MH,
        APIRegistrationTypes.LAND_TAX_LIEN,
        APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
        APIRegistrationTypes.MISCELLANEOUS_REGISTRATION
      ]
      return ipArray.includes(registrationType)
    }

    const setLifeInfinite = (val: string): void => {
      lengthTrust.lifeInfinite = String(val) === 'true'
      localState.lifeYearsDisabled = lengthTrust.lifeInfinite
      if (lengthTrust.lifeInfinite) {
        localState.lifeYearsEdit = ''
        lengthTrust.lifeYears = 0
        lengthTrust.valid = true
        lengthTrust.showInvalid = false
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

    watch(
      () => localState.lifeYearsEdit,
      (val: string) => {
        localState.lifeYearsMessage = ''
        if (val.length > 0) {
          var life = parseInt(val)
          if (isNaN(life)) {
            localState.lifeYearsMessage =
              'Registration length must be a number between 1 and ' +
              localState.maxYears
            lengthTrust.valid = false
          } else if (life < 1 || life > feeInfoYears.quantityMax) {
            localState.lifeYearsMessage =
              'Registration length must be between 1 and ' + localState.maxYears
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
          if (!lengthTrust.lifeInfinite) {
            lengthTrust.lifeYears = 0
            setLengthTrust(lengthTrust)
            lengthTrust.valid = false
          }
        }
        if (!lengthTrust.valid && !lengthTrust.lifeInfinite) {
          lengthTrust.valid = false
          setLengthTrust(lengthTrust)
          feeSummary.feeAmount = 0
          feeSummary.quantity = 0
          setFeeSummary(feeSummary)
          context.emit('updated-fee-summary', feeSummary)
        }
      }
    )
    watch(
      () => localState.trustIndenture,
      (val: boolean) => {
        lengthTrust.trustIndenture = val
        setLengthTrust(lengthTrust)
      }
    )
    watch(
      () => localState.lienAmount,
      (val: string) => {
        lengthTrust.lienAmount = val.trimRight().trimLeft()
        if (lengthTrust.lienAmount !== '' && lengthTrust.surrenderDate !== '') {
          lengthTrust.valid = true
          lengthTrust.showInvalid = false
        } else {
          lengthTrust.valid = false
        }
        setLengthTrust(lengthTrust)
      }
    )
    watch(
      () => localState.surrenderDate,
      (val: string) => {
        lengthTrust.surrenderDate = val
        if (lengthTrust.lienAmount !== '' && lengthTrust.surrenderDate !== '') {
          lengthTrust.valid = true
          lengthTrust.showInvalid = false
        } else {
          lengthTrust.valid = false
        }
        setLengthTrust(lengthTrust)
      }
    )

    return {
      goToLengthTrust,
      setLifeInfinite,
      lengthTrust,
      infinityPreselected,
      APIRegistrationTypes,
      registrationType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.summary-text {
  font-size: 16px;
  color: $gray7;
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
