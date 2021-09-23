<template>
  <v-container fluid no-gutters class="white pa-0" v-if="renewalView">
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
            {{ lengthSummary }}
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
    no-gutters
    class="white pb-6 pr-10 pl-8 rounded"
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
          <v-dialog
            ref="dialog"
            v-model="modal"
            :return-value.sync="surrenderDate"
            persistent
            width="450px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                id="date-text-field"
                :value="computedDateFormatted"
                :error-messages="surrenderDateMessage || ''"
                filled
                hint="Must be within the last 21 days"
                persistent-hint
                label="Date"
                append-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                v-on:click:append="on.click"
              >
              </v-text-field>
            </template>
            <v-date-picker
              id="date-picker-calendar"
              v-model="surrenderDate"
              elevation="15"
              :min="minSurrenderDate"
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
import { LengthTrustIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'
import { APIRegistrationTypes, RouteNames } from '@/enums'

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
    const { getRegistrationType, getRegistrationExpiryDate, getRegistrationSurrenderDate } = useGetters<any>([
      'getRegistrationType', 'getRegistrationExpiryDate', 'getRegistrationSurrenderDate'
    ])
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const lengthTrust: LengthTrustIF = getLengthTrust.value
    const router = context.root.$router
    const route = context.root.$route
    const modal = false

    if (
      registrationType === APIRegistrationTypes.REPAIRERS_LIEN &&
      lengthTrust.lifeYears !== 1
    ) {
      lengthTrust.valid = true
      lengthTrust.lifeYears = 1
      setLengthTrust(lengthTrust)
    }

    const localState = reactive({
      renewalView: props.isRenewal,
      trustIndentureHint: '',
      surrenderDate: lengthTrust.surrenderDate,
      lienAmount: lengthTrust.lienAmount,
      showErrorSummary: computed((): boolean => {
        return !lengthTrust.valid
      }),
      showErrorLienAmount: computed((): boolean => {
        if (
          lengthTrust.lienAmount !== '' &&
          localState.lienAmountMessage?.length > 0
        ) {
          return true
        }
        return lengthTrust.showInvalid && lengthTrust.lienAmount === ''
      }),
      showErrorSurrenderDate: computed((): boolean => {
        return lengthTrust.showInvalid && lengthTrust.surrenderDate === ''
      }),
      lienAmountMessage: computed((): string => {
        if (lengthTrust.showInvalid && lengthTrust.lienAmount === '') {
          return 'This field is required'
        }
        if (lengthTrust.lienAmount?.length > 0 && !validLienAmount(lengthTrust.lienAmount)) {
          return 'Lien amount must be a number greater than 0.'
        }
        return ''
      }),
      surrenderDateMessage: computed((): string => {
        if (lengthTrust.showInvalid && lengthTrust.surrenderDate === '') {
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
      minSurrenderDate: computed((): string => {
        var dateOffset = 24 * 60 * 60 * 1000 * 21 // 21 days in milliseconds
        var minDate = new Date()
        minDate.setTime(minDate.getTime() - dateOffset)
        return minDate.toISOString()
      }),
      computedDateFormatted: computed((): string => {
        return lengthTrust.surrenderDate !== ''
          ? convertDate(new Date(lengthTrust.surrenderDate + 'T09:00:00Z'), false, false) : ''
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (props.isRenewal) {
          const expiryDate = getRegistrationExpiryDate.value
          const newExpDate = new Date(expiryDate)
          newExpDate.setDate(newExpDate.getDate() + 180)
          return convertDate(newExpDate, true, true)
        }
      }),
      lienAmountSummary: computed((): string => {
        if (lengthTrust.lienAmount) {
          // Format as CDN currency.
          var currency = lengthTrust.lienAmount
            ?.replace('$', '')
            ?.replaceAll(',', '')
          var lienFloat = parseFloat(currency)
          if (isNaN(lienFloat)) {
            return lengthTrust.lienAmount
          }
          return '$' + lienFloat.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
        }
        return 'Not entered'
      }),
      surrenderDateSummary: computed((): string => {
        if (props.isRenewal) {
          lengthTrust.surrenderDate = getRegistrationSurrenderDate.value
          return convertDate(
            new Date(lengthTrust.surrenderDate),
            false,
            false
          )
        }
        if (lengthTrust.surrenderDate?.length >= 10) {
          return convertDate(
            new Date(lengthTrust.surrenderDate + 'T09:00:00Z'),
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
        lengthTrust.lienAmount = val.trimRight().trimLeft()
        if (!validLienAmount(val)) {
          lengthTrust.valid = false
        } else if (lengthTrust.surrenderDate !== '') {
          lengthTrust.valid = true
          lengthTrust.showInvalid = false
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
      lengthTrust,
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
