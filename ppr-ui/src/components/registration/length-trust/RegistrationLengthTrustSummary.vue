<template>
  <v-card
    id="length-trust-summary"
    flat
  >
    <h2
      v-if="isRenewal"
      class="pt-2 pb-5 renewal-title"
    >
      Renewal Length and <span v-if="showTrustIndenture">Trust Indenture</span>
      <span v-else>Terms</span>
    </h2>
    <v-row
      v-else
      no-gutters
      class="summary-header py-2"
    >
      <v-col
        cols="auto"
        class="py-2 d-flex"
      >
        <v-icon color="darkBlue">
          mdi-calendar-clock
        </v-icon>
        <h3
          v-if="registrationType === APIRegistrationTypes.SECURITY_AGREEMENT"
          class="lh-24 ml-3"
        >
          {{ regTitle }} Length and Trust Indenture
        </h3>
        <h3
          v-else-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN"
          class="lh-24 ml-3"
        >
          Amount and Date of Surrender
        </h3>
        <h3
          v-else
          class="lh-24 ml-3"
        >
          {{ regTitle }} Length
        </h3>
      </v-col>
    </v-row>
    <v-container
      :class="{ 'border-error-left': showErrorSummary && !isSecurityActNotice }"
      style="padding: 40px 30px;"
    >
      <v-row
        v-if="showErrorSummary && !isSecurityActNotice"
        no-gutters
        class="pb-6"
      >
        <v-col cols="auto">
          <span :class="{ 'error-text': showErrorSummary }">
            <v-icon color="error">mdi-information-outline</v-icon>
            This step is unfinished.
          </span>
          <span
            id="router-link-length-trust"
            class="generic-link"
            @click="goToLengthTrust()"
          >
            Return to this step to complete it.
          </span>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col
          cols="3"
          class="generic-label"
        >
          {{ regTitle }} Length
        </v-col>
        <v-col
          id="registration-length"
          class="summary-text"
        >
          {{ lengthSummary }}
        </v-col>
      </v-row>
      <v-row
        v-if="renewalView"
        no-gutters
        class="pt-8"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          New Expiry Date and Time
        </v-col>
        <v-col
          id="new-expiry"
          cols="9"
        >
          {{ computedExpiryDateFormatted }}
        </v-col>
      </v-row>
      <v-row
        v-if="showTrustIndenture"
        no-gutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Trust Indenture
        </v-col>
        <v-col
          id="trust-indenture-summary"
          class="summary-text"
        >
          {{ trustIndentureSummary }}
        </v-col>
      </v-row>
      <v-row
        v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN && !isRlTransition"
        no-gutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Amount of Lien
        </v-col>
        <v-col class="summary-text">
          {{ lienAmountSummary }}
        </v-col>
      </v-row>
      <v-row
        v-if="registrationType === APIRegistrationTypes.REPAIRERS_LIEN && !isRlTransition"
        no-gutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Surrender Date
        </v-col>
        <v-col class="summary-text">
          {{ surrenderDateSummary }}
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue'
import { useStore } from '@/store/store'
import { useRoute, useRouter } from 'vue-router'

// local
import type { LengthTrustIF } from '@/interfaces'
import { convertDate, formatExpiryDate, isInt } from '@/utils'
import { APIRegistrationTypes, RouteNames, RegistrationFlowType } from '@/enums'
import { getFinancingFee } from '@/composables/fees/factories'
import { storeToRefs } from 'pinia'
import { usePprRegistration } from '@/composables'

export default defineComponent({
  props: {
    isRenewal: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const route = useRoute()
    const router = useRouter()
    const { setLengthTrust } = useStore()
    const {
      // Getters
      isRlTransition,
      getLengthTrust,
      getRegistrationType,
      getRegistrationExpiryDate,
      getRegistrationSurrenderDate,
      getRegistrationFlowType
    } = storeToRefs(useStore())
    const { isSecurityActNotice } = usePprRegistration()
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const feeInfoYears = getFinancingFee(false)

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
          ? convertDate(new Date(getLengthTrust.value.surrenderDate + 'T09:00:00Z'), false, false)
          : ''
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (props.isRenewal) {
          if (getLengthTrust.value.lifeInfinite) {
            return 'No Expiry'
          }
          if ((getRegistrationExpiryDate.value) && ((registrationType === APIRegistrationTypes.REPAIRERS_LIEN)) &&
            !isRlTransition.value) {
            const expiryDate = getRegistrationExpiryDate.value
            const newExpDate = new Date(new Date(expiryDate).toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
            newExpDate.setDate(newExpDate.getDate() + 180)
            return formatExpiryDate(newExpDate)
          }
          if ((getRegistrationExpiryDate.value) && (getLengthTrust.value.lifeYears > 0)) {
            const expiryDate = getRegistrationExpiryDate.value
            const numYears = getLengthTrust.value.lifeYears
            const newExpDate = new Date(new Date(expiryDate).toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
            newExpDate.setFullYear(newExpDate.getFullYear() + numYears)
            return formatExpiryDate(newExpDate)
          }
          return '-'
        }
        return ''
      }),
      lengthSummary: computed((): string => {
        if (registrationType === APIRegistrationTypes.REPAIRERS_LIEN && !isRlTransition.value) {
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
          const currency = getLengthTrust.value.lienAmount
            ?.replace('$', '')
            ?.replaceAll(',', '')
          const lienFloat = parseFloat(currency)
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
          // TODO: I'm not sure assigning a computed to a computed works as expected or at all. Revisit this asap.
          // eslint-disable-next-line vue/no-side-effects-in-computed-properties
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
      isRlTransition,
      goToLengthTrust,
      APIRegistrationTypes,
      registrationType,
      isSecurityActNotice,
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

:deep(.v-icon.v-icon:not(.mdi-radiobox-marked):not(.mdi-radiobox-blank):not(.mdi-checkbox-blank-outline)) {
  color: $primary-blue;
}
:deep(.v-picker__title__btn:not(.v-picker__title__btn--active)) {
  opacity: 1;
}
:deep(.v-date-picker-table__current) {
  border-color: $primary-blue !important;
}
:deep(.v-date-picker-table__current .v-btn__content) {
  color: $primary-blue !important;
}
:deep(.theme--light.v-date-picker-table th) {
  color: $gray9;
}
:deep(.v-date-picker-table .v-btn) {
  color: $gray7;
}
:deep(.theme--light.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined)) {
  background-color: $primary-blue !important;
  border-color: $primary-blue !important;
  color: white !important;
}
:deep(.v-btn:not(.v-btn--text):not(.v-btn--outlined).v-btn--active:before) {
  opacity: 0;
}
:deep(.v-icon.v-icon.v-icon--link) {
  cursor: text;
}
:deep(.theme--light.v-icon.v-icon.v-icon--disabled) {
  color: $primary-blue !important;
}
:deep(.v-input--is-disabled) {
  opacity: 0.4;
}
</style>
