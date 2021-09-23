<template>
  <v-container
    fluid
    no-gutters
    class="white pb-6 pr-10 pl-8 rounded"
    :class="{ 'invalid-message': lengthTrust.showInvalid }"
  >
  <v-row no-gutters v-if="renewalView" class="summary-header pa-2 mb-8 mt-n3 mr-n10 ml-n8">
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-calendar-clock</v-icon>
          <label class="pl-3">
            <strong>Renewal Length <span v-if="showTrustIndenture">and Trust Indenture</span></strong>
          </label>
        </v-col>
      </v-row>

      <v-row v-if="renewalView" no-gutters>
          <v-col cols="12" class="pb-2">
            The registration length entered below will be added to any time remaining on your
            current registration.
          </v-col>
        </v-row>
    <div>
      <v-row class="pt-6" no-gutters>
        <v-col cols="3" class="generic-label">
          <span :class="{ 'invalid-message': lengthTrust.showInvalid }"
            >{{ regTitle }} Length</span
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
              @click="setLifeInfinite(false)"
            >
            </v-radio>
            <v-radio
              class="infinite-radio pt-15 ma-0"
              :hide-details="false"
              label=""
              value="true"
              id="length-infinite"
              @click="setLifeInfinite(true)"
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
        <v-col cols="9" class="pl-2" v-if="!infinityPreselected()"><v-divider class="ml-0" /></v-col>
      </v-row>
      <v-row no-gutters class="py-6" v-if="renewalView">
        <v-col cols="3" class="generic-label">New Expiry</v-col>
        <v-col cols="9" id="new-expiry">{{ computedExpiryDateFormatted }}</v-col>
      </v-row>
      <v-row v-if="renewalView && showTrustIndenture">
        <v-col cols="3"></v-col>
        <v-col cols="9" class="pl-2"><v-divider class="ml-0" /></v-col>
      </v-row>
      <v-row no-gutters class="pt-6" v-if="showTrustIndenture">
        <v-col cols="3" class="generic-label">
          Trust Indenture
        </v-col>
        <v-col class="summary-text" v-if="renewalView">
            {{ trustIndentureSummary }}
        </v-col>
        <v-col cols="auto" v-if="!renewalView">
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
        <v-col cols="8" v-if="!renewalView">
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
  watch,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

// local
import { LengthTrustIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'
import { APIRegistrationTypes, RouteNames } from '@/enums'
import { getFinancingFee } from '@/composables/fees/factories'

export default defineComponent({
  props: {
    isRenewal: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const { getRegistrationType, getRegistrationExpiryDate } = useGetters<any>([
      'getRegistrationType', 'getRegistrationExpiryDate'
    ])
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const lengthTrust: LengthTrustIF = getLengthTrust.value
    const feeInfoYears = getFinancingFee(false)
    const router = context.root.$router
    const route = context.root.$route
    const modal = false

    const localState = reactive({
      renewalView: props.isRenewal,
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
      lifeYearsHint:
        'Minimum 1 year, Maximum ' +
        feeInfoYears.quantityMax.toString() +
        ' years ($' +
        feeInfoYears.feeAmount.toFixed(2) +
        ' per year)',
      showTrustIndenture: computed((): boolean => {
        if (localState.renewalView) {
          return lengthTrust.trustIndenture
        }
        return registrationType === APIRegistrationTypes.SECURITY_AGREEMENT
      }),
      showErrorSummary: computed((): boolean => {
        return !lengthTrust.valid
      }),
      regTitle: computed((): string => {
        if (props.isRenewal) {
          return 'Renewal'
        }
        return 'Registration'
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (props.isRenewal) {
          if (lengthTrust.lifeInfinite) {
            return 'No Expiry'
          }
          if ((getRegistrationExpiryDate.value) && (parseInt(localState.lifeYearsEdit) > 0)) {
            const expiryDate = getRegistrationExpiryDate.value
            const numYears = parseInt(localState.lifeYearsEdit)
            const newExpDate = new Date(expiryDate)
            newExpDate.setFullYear(newExpDate.getFullYear() + numYears)
            return convertDate(newExpDate, true, true)
          }
          return '-'
        }
      }),
      trustIndentureSummary: computed((): string => {
        return lengthTrust.trustIndenture ? 'Yes' : 'No'
      })
    })
    const goToLengthTrust = (): void => {
      if (!props.isRenewal) {
        lengthTrust.showInvalid = true
        setLengthTrust(lengthTrust)
        router.push({ path: '/new-registration/length-trust' })
      } else {
        const registrationNumber = route.query['reg-num'] as string || ''
        router.push({
          name: RouteNames.RENEW_REGISTRATION,
          query: { 'reg-num': registrationNumber }
        })
      }
    }

    const infinityPreselected = (): boolean => {
      const ipArray = [
        APIRegistrationTypes.MARRIAGE_MH,
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
        APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
        APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
        APIRegistrationTypes.MAINTENANCE_LIEN,
        APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
        APIRegistrationTypes.OTHER,
        APIRegistrationTypes.MINERAL_LAND_TAX,
        APIRegistrationTypes.PROPERTY_TRANSFER_TAX,
        APIRegistrationTypes.SCHOOL_ACT
      ]
      return ipArray.includes(registrationType)
    }

    onMounted(() => {
      if (infinityPreselected()) {
        lengthTrust.valid = true
        lengthTrust.lifeInfinite = true
        lengthTrust.lifeYears = null
        setLengthTrust(lengthTrust)
      }
    })

    const setLifeInfinite = (val: boolean): void => {
      lengthTrust.lifeInfinite = val
      localState.lifeYearsDisabled = lengthTrust.lifeInfinite
      if (lengthTrust.lifeInfinite) {
        localState.lifeYearsEdit = ''
        lengthTrust.lifeYears = null
        lengthTrust.valid = true
        lengthTrust.showInvalid = false
        setLengthTrust(lengthTrust)
      } else {
        lengthTrust.valid = false
        lengthTrust.lifeYears = 0
        setLengthTrust(lengthTrust)
      }
    }

    watch(
      () => localState.lifeYearsEdit,
      (val: string) => {
        localState.lifeYearsMessage = ''
        if (val?.length > 0) {
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

    return {
      goToLengthTrust,
      setLifeInfinite,
      lengthTrust,
      infinityPreselected,
      APIRegistrationTypes,
      registrationType,
      modal,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
/* Need scoped for date picker v-deep style overrides to work */
@import '@/assets/styles/theme.scss';
.v-list-item {
  min-height: 0;
}

.renewal-title {
   background-color: #f1f3f5;
}

::v-deep
  .v-icon.v-icon:not(.mdi-radiobox-marked):not(.mdi-radiobox-blank):not(.mdi-checkbox-blank-outline) {
  color: $primary-blue;
}
::v-deep .v-picker__title__btn:not(.v-picker__title__btn--active) {
  opacity: 1;
}
::v-deep .v-date-picker-table__current {
  border-color: $primary-blue !important;
}
::v-deep .v-date-picker-table__current .v-btn__content {
  color: $primary-blue !important;
}
::v-deep .theme--light.v-date-picker-table th {
  color: $gray9;
}
::v-deep .v-date-picker-table .v-btn {
  color: $gray7;
}
::v-deep
  .theme--light.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: $primary-blue !important;
  border-color: $primary-blue !important;
  color: white !important;
}
::v-deep .v-btn:not(.v-btn--text):not(.v-btn--outlined).v-btn--active:before {
  opacity: 0;
}
::v-deep .v-icon.v-icon.v-icon--link {
  cursor: text;
}
::v-deep .theme--light.v-icon.v-icon.v-icon--disabled {
  color: $primary-blue !important;
}
::v-deep .v-input--is-disabled {
  opacity: 0.4;
}
</style>
