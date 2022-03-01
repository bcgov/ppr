<template>
  <v-container fluid no-gutters class="white pa-0">
    <v-card flat id="length-trust-summary">
      <h2 class="pt-2 pb-5 renewal-title" v-if="isRenewal">
          Renewal Length and <span v-if="showTrustIndenture">Trust Indenture</span>
          <span v-else>Terms</span>
       </h2>
      <v-row no-gutters class="summary-header pa-2" v-else>
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-calendar-clock</v-icon>
          <label
            class="pl-3"
            v-if="registrationType === APIRegistrationTypes.SECURITY_AGREEMENT"
          >
            <strong>{{ regTitle }} Length and Trust Indenture</strong>
          </label>
          <label
            class="pl-3"
            v-else-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN"
          >
            <strong>Amount and Date of Surrender</strong>
          </label>
          <label class="pl-3" v-else>
            <strong>{{ regTitle }} Length</strong>
          </label>
        </v-col>
      </v-row>
      <v-container
        :class="{ 'invalid-message': showErrorSummary }"
        style="padding: 40px 30px;"
      >
        <v-row no-gutters v-if="showErrorSummary" class="pb-6">
          <v-col cols="auto">
            <span :class="{ 'invalid-message': showErrorSummary }">
              <v-icon color="error">mdi-information-outline</v-icon>
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
        <v-row no-gutters>
          <v-col cols="3" class="generic-label"> {{ regTitle }} Length </v-col>
          <v-col class="summary-text" id="registration-length">
            {{ lengthSummary }}
          </v-col>
        </v-row>
        <v-row no-gutters class="pt-8" v-if="renewalView">
          <v-col cols="3" class="generic-label">New Expiry</v-col>
          <v-col cols="9" id="new-expiry">{{ computedExpiryDateFormatted }}</v-col>
        </v-row>
        <v-row no-gutters class="pt-6" v-if="showTrustIndenture">
          <v-col cols="3" class="generic-label">
            Trust Indenture
          </v-col>
          <v-col class="summary-text" id="trust-indenture-summary">
            {{ trustIndentureSummary }}
          </v-col>
        </v-row>
        <v-row
          no-gutters
          class="pt-6"
          v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN"
        >
          <v-col cols="3" class="generic-label">
            Amount of Lien
          </v-col>
          <v-col class="summary-text">
            {{ lienAmountSummary }}
          </v-col>
        </v-row>
        <v-row
          no-gutters
          class="pt-6"
          v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN"
        >
          <v-col cols="3" class="generic-label">
            Surrender Date
          </v-col>
          <v-col class="summary-text">
            {{ surrenderDateSummary }}
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-container>

</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

// local
import { LengthTrustIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate, isInt } from '@/utils'
import { APIRegistrationTypes, RouteNames, RegistrationFlowType } from '@/enums'
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
    const {
      getRegistrationType,
      getRegistrationExpiryDate,
      getRegistrationSurrenderDate,
      getRegistrationFlowType
    } = useGetters<any>([
      'getRegistrationType',
      'getRegistrationExpiryDate',
      'getRegistrationSurrenderDate',
      'getRegistrationFlowType'
    ])
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const feeInfoYears = getFinancingFee(false)
    const router = context.root.$router
    const route = context.root.$route

    const localState = reactive({
      renewalView: props.isRenewal,
      trustIndenture: getLengthTrust.value.trustIndenture,
      lifeInfinite: getLengthTrust.value.valid
        ? getLengthTrust.value.lifeInfinite.toString()
        : '',
      surrenderDate: getLengthTrust.value.surrenderDate,
      lienAmount: getLengthTrust.value.lienAmount,
      showTrustIndenture: computed((): boolean => {
        if (localState.renewalView) {
          return getLengthTrust.value.trustIndenture
        }
        return registrationType === APIRegistrationTypes.SECURITY_AGREEMENT
      }),
      showErrorSummary: computed((): boolean => {
        return !getLengthTrust.value.valid
      }),
      regTitle: computed((): string => {
        if (props.isRenewal) {
          return 'Renewal'
        }
        return 'Registration'
      }),
      computedDateFormatted: computed((): string => {
        return getLengthTrust.value.surrenderDate !== ''
          ? convertDate(new Date(getLengthTrust.value.surrenderDate + 'T09:00:00Z'), false, false) : ''
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (props.isRenewal) {
          if (getLengthTrust.value.lifeInfinite) {
            return 'No Expiry'
          }
          if ((getRegistrationExpiryDate.value) && ((registrationType === APIRegistrationTypes.REPAIRERS_LIEN))) {
            const expiryDate = getRegistrationExpiryDate.value
            const newExpDate = new Date(expiryDate)
            newExpDate.setDate(newExpDate.getDate() + 180)
            return convertDate(newExpDate, true, true)
          }
          if ((getRegistrationExpiryDate.value) && (getLengthTrust.value.lifeYears > 0)) {
            const expiryDate = getRegistrationExpiryDate.value
            const numYears = getLengthTrust.value.lifeYears
            const newExpDate = new Date(expiryDate)
            newExpDate.setFullYear(newExpDate.getFullYear() + numYears)
            return convertDate(newExpDate, true, true)
          }
          return '-'
        }
      }),
      lengthSummary: computed((): string => {
        if (registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          return '180 Days'
        }
        if (!getLengthTrust.value.lifeInfinite && getRegistrationFlowType.value === RegistrationFlowType.NEW &&
          (!isInt(getLengthTrust.value.lifeYears) ||
          getLengthTrust.value.lifeYears < 1 || getLengthTrust.value.lifeYears > feeInfoYears.quantityMax)) {
          return 'Not valid'
        }
        if (!getLengthTrust.value.lifeInfinite && getLengthTrust.value.lifeYears < 1) {
          return 'Not entered'
        }
        if (getLengthTrust.value.lifeInfinite) {
          return 'Infinite'
        }
        if (getLengthTrust.value.lifeYears === 1) {
          return getLengthTrust.value.lifeYears.toString() + ' Year'
        }
        return getLengthTrust.value.lifeYears.toString() + ' Years'
      }),
      trustIndentureSummary: computed((): string => {
        return getLengthTrust.value.trustIndenture ? 'Yes' : 'No'
      }),
      lienAmountSummary: computed((): string => {
        if (getLengthTrust.value.lienAmount) {
          // Format as CDN currency.
          var currency = getLengthTrust.value.lienAmount
            ?.replace('$', '')
            ?.replaceAll(',', '')
          var lienFloat = parseFloat(currency)
          if (isNaN(lienFloat)) {
            return getLengthTrust.value.lienAmount
          }
          return '$' + lienFloat.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
        }
        return 'Not entered'
      }),
      lengthTrust: computed((): LengthTrustIF => {
        return getLengthTrust.value as LengthTrustIF || null
      }),
      surrenderDateSummary: computed((): string => {
        if (props.isRenewal) {
          getLengthTrust.value.surrenderDate = getRegistrationSurrenderDate.value
          return convertDate(
            new Date(getLengthTrust.value.surrenderDate),
            false,
            false
          )
        }
        if (getLengthTrust.value.surrenderDate?.length === 10) {
          return convertDate(
            new Date(getLengthTrust.value.surrenderDate + 'T09:00:00Z'),
            false,
            false
          )
        } else if (getLengthTrust.value.surrenderDate?.length > 10) {
          return convertDate(
            new Date(getLengthTrust.value.surrenderDate),
            false,
            false
          )
        }
        if (getLengthTrust.value.surrenderDate === '') {
          return 'Not entered'
        }
        return getLengthTrust.value.surrenderDate
      })
    })
    const goToLengthTrust = (): void => {
      if (!props.isRenewal) {
        const lt = localState.lengthTrust
        lt.showInvalid = true
        setLengthTrust(lt)
        router.push(RouteNames.LENGTH_TRUST)
      } else {
        const registrationNumber = route.query['reg-num'] as string || ''
        router.push({
          name: RouteNames.RENEW_REGISTRATION,
          query: { 'reg-num': registrationNumber }
        })
      }
    }

    return {
      goToLengthTrust,
      APIRegistrationTypes,
      registrationType,
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
