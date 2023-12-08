<template>
  <v-container
    id="length-trust-component"
    fluid
    class="bg-white pt-0 pb-6 pr-10 pl-8 rounded noGutters"
    :class="{ 'invalid-message': showInvalid }"
  >
    <v-row
      v-if="renewalView"
      noGutters
      class="summary-header pa-2 mb-8 ml-n8 mr-n10"
    >
      <v-col
        cols="auto"
        class="pa-2"
      >
        <v-icon color="darkBlue">
          mdi-calendar-clock
        </v-icon>
        <label class="pl-3">
          <strong>Renewal Length and <span v-if="showTrustIndenture">Trust Indenture</span>
            <span v-else>Terms</span>
          </strong>
        </label>
      </v-col>
    </v-row>

    <v-row
      v-if="renewalView"
      noGutters
    >
      <v-col
        cols="12"
        class="pb-2"
      >
        The registration length entered below will be added to any time remaining on your
        current registration.
      </v-col>
    </v-row>
    <div>
      <v-row
        class="pt-6"
        noGutters
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          <span :class="{ 'invalid-message': showInvalid }">{{ regTitle }} Length</span>
        </v-col>
        <v-col cols="auto">
          <span v-if="infinityPreselected()">
            Infinite
          </span>
          <v-radio-group
            v-else
            v-model="lifeInfinite"
          >
            <v-radio
              id="length-in-years"
              class="years-radio mt-2"
              :hideDetails="false"
              label=""
              value="false"
              @click="setLifeInfinite(false)"
            />
            <v-radio
              id="length-infinite"
              class="infinite-radio mt-10"
              :hideDetails="false"
              label=""
              value="true"
              @click="setLifeInfinite(true)"
            />
          </v-radio-group>
        </v-col>
        <v-col v-if="!infinityPreselected()">
          <v-text-field
            id="life-years-field"
            v-model="lifeYearsEdit"
            autocomplete="off"
            :errorMessages="lifeYearsMessage || ''"
            variant="filled"
            :readonly="lifeYearsDisabled"
            :hint="lifeYearsHint"
            persistentHint
            label="Length in Years"
          />
          <p class="pt-5">
            Infinite ($500.00 non-refundable)
          </p>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3" />
        <v-col
          v-if="renewalView || showTrustIndenture"
          cols="9"
          class="pl-2"
        >
          <v-divider class="ml-0" />
        </v-col>
      </v-row>
      <v-row
        v-if="renewalView"
        noGutters
        class="py-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          New Expiry
        </v-col>
        <v-col
          id="new-expiry"
          cols="9"
        >
          {{ computedExpiryDateFormatted }}
        </v-col>
      </v-row>
      <v-row v-if="renewalView && showTrustIndenture">
        <v-col cols="3" />
        <v-col
          cols="9"
          class="pl-2"
        >
          <v-divider class="ml-0" />
        </v-col>
      </v-row>
      <v-row
        v-if="showTrustIndenture"
        noGutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Trust Indenture
        </v-col>
        <v-col
          v-if="renewalView"
          class="summary-text"
        >
          {{ trustIndentureSummary }}
        </v-col>
        <v-col
          v-if="!renewalView"
          cols="auto"
        >
          <v-checkbox
            id="trust-indenture-checkbox"
            v-model="trustIndenture"
            class="trust-checkbox mt-n4"
            hideDetails
            :hint="trustIndentureHint"
            label=""
          />
        </v-col>
        <v-col
          v-if="!renewalView"
          cols="8"
        >
          <v-tooltip
            location="top"
            contentClass="top-tooltip pa-5"
            transition="fade-transition"
          >
            <template #activator="{ props }">
              <p
                class="trust-indenture"
                v-bind="props"
              >
                Trust Indenture
              </p>
            </template>
            Select if the security interest is contained in a Trust Indenture.
          </v-tooltip>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from 'vue'
import { useStore } from '@/store/store'
import { LengthTrustIF } from '@/interfaces'
import { formatExpiryDate, isInt } from '@/utils'
import { APIRegistrationTypes } from '@/enums'
import { getFinancingFee } from '@/composables/fees/factories'
import { storeToRefs } from 'pinia'

export default defineComponent({
  props: {
    isRenewal: {
      type: Boolean,
      default: false
    },
    setShowInvalid: {
      type: Boolean,
      default: false
    }
  },
  emits: ['lengthTrustValid'],
  setup (props, context) {
    const { setLengthTrust } = useStore()
    const {
      // Getters
      getLengthTrust,
      getRegistrationType,
      getRegistrationExpiryDate
    } = storeToRefs(useStore())
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const feeInfoYears = getFinancingFee(false)
    const modal = false

    const localState = reactive({
      renewalView: props.isRenewal,
      trustIndenture: getLengthTrust.value.trustIndenture,
      lifeYearsDisabled: computed((): string => {
        return getLengthTrust.value.lifeInfinite
      }),
      lifeInfinite: getLengthTrust.value.valid ? getLengthTrust.value.lifeInfinite.toString() : '',
      maxYears: feeInfoYears.quantityMax.toString(),
      lifeYearsEdit: getLengthTrust.value.lifeYears > 0 ? getLengthTrust.value.lifeYears.toString() : '',
      lifeYearsMessage: '',
      trustIndentureHint: '',
      showInvalid: getLengthTrust.value.showInvalid,
      lifeYearsHint:
        'Minimum 1 year, Maximum ' +
        feeInfoYears.quantityMax.toString() +
        ' years ($' +
        feeInfoYears.feeAmount.toFixed(2) +
        ' per year)',
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
      computedExpiryDateFormatted: computed((): string => {
        if (props.isRenewal) {
          if (getLengthTrust.value.lifeInfinite) {
            return 'No Expiry'
          }
          if ((getRegistrationExpiryDate.value) && (parseInt(localState.lifeYearsEdit) > 0)) {
            const expiryDate = getRegistrationExpiryDate.value
            const numYears = parseInt(localState.lifeYearsEdit)
            const newExpDate = new Date(new Date(expiryDate).toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
            newExpDate.setFullYear(newExpDate.getFullYear() + numYears)
            return formatExpiryDate(newExpDate)
          }
          return '-'
        }
        return ''
      }),
      lengthTrust: computed((): LengthTrustIF => {
        return getLengthTrust.value as LengthTrustIF || null
      }),
      trustIndentureSummary: computed((): string => {
        return getLengthTrust.value.trustIndenture ? 'Yes' : 'No'
      })
    })

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
        APIRegistrationTypes.SCHOOL_ACT,
        APIRegistrationTypes.TOBACCO_TAX,
        APIRegistrationTypes.SPECULATION_VACANCY_TAX
      ]
      return ipArray.includes(registrationType)
    }

    onMounted(() => {
      const lt = localState.lengthTrust
      if (infinityPreselected()) {
        lt.valid = true
        lt.lifeInfinite = true
        lt.lifeYears = null
        setLengthTrust(lt)
      }
      // inform parent component
      context.emit('lengthTrustValid', lt.valid)
    })

    const setLifeInfinite = (val: boolean): void => {
      const lt = localState.lengthTrust
      lt.lifeInfinite = val
      if (lt.lifeInfinite) {
        localState.lifeYearsEdit = ''
        lt.lifeYears = null
        lt.valid = true
        lt.showInvalid = false
        setLengthTrust(lt)
      } else {
        lt.valid = false
        lt.lifeYears = 0
        setLengthTrust(lt)
      }
      // inform parent component
      context.emit('lengthTrustValid', lt.valid)
      localState.showInvalid = lt.showInvalid
    }

    watch(
      () => localState.lifeYearsEdit,
      (val: string) => {
        localState.lifeYearsMessage = ''
        const lt = localState.lengthTrust
        if (val?.length > 0) {
          const life = val
          if (!isInt(life)) {
            localState.lifeYearsMessage =
              'Registration length must be a number between 1 and ' +
              localState.maxYears
            lt.valid = false
          } else if (parseInt(life) < 1 || parseInt(life) > feeInfoYears.quantityMax) {
            localState.lifeYearsMessage =
              'Registration length must be between 1 and ' + localState.maxYears
            lt.valid = false
            lt.lifeYears = 0
          } else {
            lt.valid = true
            localState.lifeInfinite = 'false'
            lt.showInvalid = false
          }
          lt.lifeYears = Number(life)
          setLengthTrust(lt)
        } else {
          if (!lt.lifeInfinite) {
            lt.lifeYears = 0
            setLengthTrust(lt)
            lt.valid = false
          }
        }
        if (!lt.valid && !lt.lifeInfinite) {
          lt.valid = false
          setLengthTrust(lt)
        }
        // inform parent component
        context.emit('lengthTrustValid', lt.valid)
        localState.showInvalid = lt.showInvalid
      }
    )
    watch(
      () => localState.trustIndenture,
      (val: boolean) => {
        const lt = localState.lengthTrust
        lt.trustIndenture = val
        setLengthTrust(lt)
      }
    )

    watch(
      () => props.setShowInvalid,
      (val: boolean) => {
        localState.showInvalid = val
      }
    )

    return {
      setLifeInfinite,
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
