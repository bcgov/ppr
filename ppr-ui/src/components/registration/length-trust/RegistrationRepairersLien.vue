<template>
  <v-container fluid class="white pa-0 no-gutters" v-if="renewalView">
    <v-card flat id="length-trust-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-calendar-clock</v-icon>
          <label class="pl-3">
            <strong>Renewal Length and Terms</strong>
          </label>
        </v-col>
      </v-row>
      <v-container style="padding: 40px 30px;">
        <v-row no-gutters>
          <v-col cols="12" class="pb-8">
            The length of a Repairers Lien renewal is automatically set to 180 days.
            The registration renewal length will
            be added to any time remaining on your current registration.
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="3" class="generic-label"> {{ regTitle }} Length </v-col>
          <v-col class="summary-text">
            180 Days
          </v-col>
        </v-row>
        <v-row no-gutters class="py-6">
           <v-col cols="3"></v-col>
           <v-col cols="9" class="pl-2"><v-divider class="ml-0" /></v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="3" class="generic-label"> New Expiry </v-col>
          <v-col class="summary-text" id="new-expiry-rl">
            {{ computedExpiryDateFormatted }}
          </v-col>
        </v-row>
        <v-row no-gutters class="pt-6">
           <v-col cols="3"></v-col>
           <v-col cols="9" class="pl-2"><v-divider class="ml-0" /></v-col>
        </v-row>
        <v-row no-gutters class="pt-6">
          <v-col cols="3" class="generic-label">
            Amount of Lien
          </v-col>
          <v-col class="summary-text">
            {{ lienAmountSummary }}
          </v-col>
        </v-row>
        <v-row no-gutters class="pt-6">
          <v-col cols="3" class="generic-label">
            Surrender Date
          </v-col>
          <v-col class="summary-text" id="surrender-date">
            {{ surrenderDateSummary }}
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-container>
  <v-container
    fluid
    class="white pb-6 pr-10 pl-8 rounded no-gutters"
    :class="{ 'invalid-message': lengthTrust.showInvalid }"
    v-else
  >
  <v-row no-gutters v-if="renewalView" class="summary-header pa-2 mb-8 mt-n3 mr-n10 ml-n8">
        <v-col cols="auto" class="pa-2">
          <v-icon color="darkBlue">mdi-calendar-clock</v-icon>
          <label class="pl-3">
            <strong>Renewal Length and Terms</strong>
          </label>
        </v-col>
      </v-row>

        <v-row v-if="renewalView" no-gutters>
          <v-col cols="12" class="pb-8">
            The length of a Repairers Lien is automatically set to 180 days. The registration renewal length will
            be added to any time remaining on your current registration.
          </v-col>
        </v-row>
    <div>
      <v-row no-gutters class="ps-6 pt-6 pb-3">
        <v-col cols="3" class="generic-label"> {{ regTitle }} Length </v-col>
        <v-col class="summary-text pl-4">
          180 Days
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
          <SharedDatePicker
            clearable
            ref="datePickerRef"
            title="Date"
            nudge-right="40"
            hint="Must not be more than 21 days in the past"
            :errorMsg="surrenderDateMessage || ''"
            :initialValue="surrenderDate"
            :key="datePickerKey"
            :minDate="localTodayDate(minSurrenderDate)"
            :persistentHint="true"
            @emitDate="surrenderDate = $event"
            @emitCancel="surrenderDate = ''"
            @emitClear="surrenderDate = ''"
          />
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
// bcregistry
import SharedDatePicker from '@/components/common/SharedDatePicker.vue'
// local
import { LengthTrustIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate, formatExpiryDate, localTodayDate } from '@/utils'
import { APIRegistrationTypes } from '@/enums'

export default defineComponent({
  components: {
    SharedDatePicker
  },
  props: {
    isRenewal: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const { getRegistrationType, getRegistrationExpiryDate, getRegistrationSurrenderDate } = useGetters<any>([
      'getRegistrationType', 'getRegistrationExpiryDate', 'getRegistrationSurrenderDate'
    ])
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const modal = false

    const localState = reactive({
      datePickerKey: Math.random(),
      renewalView: props.isRenewal,
      trustIndentureHint: '',
      surrenderDate: getLengthTrust.value.surrenderDate,
      lienAmount: getLengthTrust.value.lienAmount,
      showErrorSummary: computed((): boolean => {
        return !getLengthTrust.value.valid
      }),
      showErrorLienAmount: computed((): boolean => {
        if (
          getLengthTrust.value.lienAmount !== '' &&
          localState.lienAmountMessage?.length > 0
        ) {
          return true
        }
        return getLengthTrust.value.showInvalid && getLengthTrust.value.lienAmount === ''
      }),
      showErrorSurrenderDate: computed((): boolean => {
        return getLengthTrust.value.showInvalid && getLengthTrust.value.surrenderDate === ''
      }),
      lienAmountMessage: computed((): string => {
        if (getLengthTrust.value.showInvalid && getLengthTrust.value.lienAmount === '') {
          return 'This field is required'
        }
        if (getLengthTrust.value.lienAmount?.length > 0 && !validLienAmount(getLengthTrust.value.lienAmount)) {
          return 'Lien amount must be a number greater than 0.'
        }
        return ''
      }),
      surrenderDateMessage: computed((): string => {
        if (getLengthTrust.value.showInvalid && getLengthTrust.value.surrenderDate === '') {
          return 'This field is required'
        }
        return ''
      }),
      regTitle: computed((): string => {
        if (props.isRenewal) {
          return 'Renewal'
        }
        return 'Registration'
      }),
      minSurrenderDate: computed((): Date => {
        var dateOffset = 24 * 60 * 60 * 1000 * 21 // 21 days in milliseconds
        var minDate = new Date()
        minDate.setTime(minDate.getTime() - dateOffset)
        return minDate
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (props.isRenewal) {
          const expiryDate = getRegistrationExpiryDate.value
          const newExpDate = new Date(new Date(expiryDate).toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
          newExpDate.setDate(newExpDate.getDate() + 180)
          return formatExpiryDate(newExpDate)
        }
        return ''
      }),
      lengthTrust: computed((): LengthTrustIF => {
        return getLengthTrust.value as LengthTrustIF || null
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
        if (getLengthTrust.value.surrenderDate?.length >= 10) {
          return convertDate(
            new Date(getLengthTrust.value.surrenderDate + 'T09:00:00Z'),
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

    const validLienAmount = (val: string): boolean => {
      if (!val || val === '') {
        return false
      }
      var lienAmount = val.trimRight().trimLeft()
      if (lienAmount.length === 0) {
        return false
      }
      if (lienAmount.startsWith('$')) {
        lienAmount = lienAmount.substr(1)
      }
      var amount = Number(lienAmount.replace(/,/g, ''))
      if (isNaN(amount) || amount < 0.01) {
        return false
      }
      return true
    }

    watch(
      () => localState.lienAmount,
      (val: string) => {
        const lt = localState.lengthTrust
        lt.lienAmount = val.trimRight().trimLeft()
        if (!validLienAmount(val)) {
          lt.valid = false
        } else if (lt.surrenderDate !== '') {
          lt.valid = true
          lt.showInvalid = false
        }
        setLengthTrust(lt)
      }
    )
    watch(
      () => localState.surrenderDate,
      (val: string) => {
        const lt = localState.lengthTrust
        lt.surrenderDate = val
        if (lt.lienAmount !== '' && lt.surrenderDate !== '') {
          lt.valid = true
          lt.showInvalid = false
        } else {
          lt.valid = false
        }
        setLengthTrust(lt)
      }
    )

    onMounted(() => {
      if (props.isRenewal && (getLengthTrust.value.lifeYears !== 1)) {
        const lt = localState.lengthTrust
        lt.valid = true
        lt.lifeYears = 1
        setLengthTrust(lt)
      }
      // rerender date-picker
      localState.datePickerKey = Math.random()
    })

    return {
      APIRegistrationTypes,
      localTodayDate,
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
