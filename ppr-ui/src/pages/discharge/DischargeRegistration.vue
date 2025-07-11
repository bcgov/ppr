<template>
  <v-container
    class="pt-14 px-0"
    fluid
  >
    <v-overlay
      v-model="loading"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>
    <BaseDialog
      :set-options="options"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div
      v-if="dataLoaded && !dataLoadError"
      class="container pa-0"
    >
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Total Discharge</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              This is the current information for this registration as of
              <b>{{ asOfDateTime }}.</b><br>
              If additional amendments including court orders are still required, ensure they are completed
              prior to performing this Total Discharge.
            </p>
            <p class="ma-0 pt-5">
              To view the full history of this registration including descriptions of any
              previous amendments or court orders, you will need to conduct a separate search.
            </p>
            <p v-if="isRlTransition" class="pt-5">
              <b>Note</b>: The Registry will provide the verification statement to all Secured Parties named in this
              registration.
            </p>
          </div>
          <CautionBox
            v-if="isRlTransition"
            class="mt-7"
            :set-msg="`The Commercial Liens Act (CLA) took effect on ${ rlTransitionDate }. The repairers lien is
             continued under the CLA and any amendments, renewals, or discharges will be registered as Commercial Lien
             (CL).`"
            :set-important-word="'Important'"
          />
          <caution-box
            v-else
            class="mt-9"
            :set-msg="cautionTxt"
            :set-important-word="'Note'"
          />
          <RegistrationLengthTrustSummary class="mt-11" />

          <!-- Historical Repairers Lien Information -->
          <v-card
            v-if="displayHistoricalLienInfo"
            flat
            class="mt-1 pl-8 bg-white py-6 rounded"
          >
            <v-row
              no-gutters
              class="pt-1"
            >
              <v-col
                cols="12"
                class="generic-label"
              >
                Historical Information
              </v-col>
              <p>Surrender Date and Lien Amount are kept for historical reference from the original Repairers Lien.</p>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="3" class="generic-label-14">
                Surrender Date
              </v-col>
              <v-col cols="9">
                {{ convertDate(new Date(getLengthTrust.surrenderDate), false, false) }}
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="3" class="generic-label-14">
                Amount of Lien
              </v-col>
              <v-col cols="9">
                {{ lienAmountSummary }}
              </v-col>
            </v-row>
          </v-card>

          <template v-if="isSecurityActNotice">
            <v-row
              no-gutters
              class="summary-header mt-11 py-2"
            >
              <v-col
                cols="12"
                class="py-2"
              >
                <v-icon color="darkBlue">
                  mdi-shield-plus
                </v-icon>
                <label
                  class="pl-3"
                >
                  <strong>{{ UIRegistrationTypes.SECURITY_ACT_NOTICE }}</strong>
                </label>
              </v-col>
            </v-row>

            <v-row no-gutters>
              <v-col>
                <SecuritiesActNoticesPanels
                  is-summary
                  is-discharge
                />
              </v-col>
            </v-row>
          </template>

          <div class="summary-header mt-11 py-4 px-6 rounded-top">
            <v-icon color="darkBlue">
              mdi-account-multiple-plus
            </v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </div>
          <h3 class="pt-6">
            Original Registering Party
          </h3>
          <RegisteringPartySummary
            class="pt-4"
            :set-enable-no-data-action="false"
          />
          <h3 class="pt-6">
            Secured Parties
          </h3>
          <SecuredPartySummary
            class="pt-4"
            :set-enable-no-data-action="false"
          />
          <h3 class="pt-6">
            Debtors
          </h3>
          <DebtorSummary
            class="pt-4"
            :set-enable-no-data-action="false"
          />
          <Collateral
            class="mt-11"
            :is-summary="true"
          />
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <StickyContainer
              :show-connect-fees="true"
              :set-right-offset="true"
              :set-show-buttons="true"
              :set-show-fee-summary="true"
              :set-fee-type="feeType"
              :set-registration-type="registrationTypeUI"
              :set-cancel-btn="'Cancel'"
              :set-submit-btn="'Confirm and Complete'"
              @cancel="showCancelDialog = true"
              @submit="confirmDischarge()"
            />
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { RegistrationLengthTrustSummary, SecuritiesActNoticesPanels } from '@/components/registration'
import { DebtorSummary, RegisteringPartySummary, SecuredPartySummary } from '@/components/parties/summaries'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { convertDate, getFeatureFlag, pacificDate } from '@/utils'
import { getFinancingStatement } from '@/utils/ppr-api-helper'
import type { APIRegistrationTypes } from '@/enums'
import { RegistrationFlowType, RouteNames, UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import type { DialogOptionsIF, ErrorIF } from '@/interfaces'
import { useAuth, useNavigation, usePprRegistration } from '@/composables'
import { CautionBox } from '@/components/common'
import { useConnectFeeStore } from '@/store/connectFee'

export default defineComponent({
  name: 'DischargeRegistration',
  components: {
    CautionBox,
    RegistrationLengthTrustSummary,
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary,
    SecuritiesActNoticesPanels
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  emits: ['error', 'haveData'],
  setup (props, context) {
    const route = useRoute()
    const router = useRouter()
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { initPprUpdateFilling, isSecurityActNotice } = usePprRegistration()
    const { setRegistrationFees } = useConnectFeesHandler()
    const { fees, feeOptions, userSelectedPaymentMethod } = storeToRefs(useConnectFeeStore())

    const {
      // Getters
      isRoleStaffReg,
      isRlTransition,
      getLengthTrust,
      rlTransitionDate,
      getRegistrationType,
      getConfirmDebtorName,
      displayHistoricalLienInfo
    } = storeToRefs(useStore())

    const localState = reactive({
      cautionTxt: 'The Registry will provide the verification statement to all Secured Parties named in this ' +
        'registration.',
      dataLoaded: false,
      dataLoadError: false,
      feeType: FeeSummaryTypes.DISCHARGE,
      financingStatementDate: null as Date,
      fromConfirmation: false,
      loading: false,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      asOfDateTime: computed((): string => {
        // return formatted date
        if (localState.financingStatementDate) {
          return `${pacificDate(localState.financingStatementDate)}`
        }
        return ''
      }),
      registrationNumber: computed((): string => {
        let regNum = route.query['reg-num'] as string
        if (regNum && regNum.endsWith('-confirm')) {
          localState.fromConfirmation = true
          regNum = regNum.replace('-confirm', '')
        }
        return regNum || ''
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || null
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
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)

      setRegistrationFees(FeeSummaryTypes.DISCHARGE)
      feeOptions.value.showProcessingFees = isRoleStaffReg.value
      feeOptions.value.showServiceFees = !isRoleStaffReg.value
    })

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        goToDash()
      }
    }

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || !getConfirmDebtorName.value) {
        if (!localState.registrationNumber) {
          console.error('No registration number given to discharge. Redirecting to dashboard...')
        } else {
          console.error('No debtor name confirmed for discharge. Redirecting to dashboard...')
        }
        goToDash()
        return
      }

      // Conditionally load: could be coming back from confirm.
      if (localState.fromConfirmation) {
        return
      }

      localState.financingStatementDate = new Date()
      const financingStatement = await getFinancingStatement(true, localState.registrationNumber)
      if (financingStatement.error) {
        localState.dataLoadError = true
        emitError(financingStatement.error)
      } else {
        initPprUpdateFilling(financingStatement, RegistrationFlowType.DISCHARGE)
      }
    }

    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) {
        goToDash()
        return
      }

      // get registration data from api and load into store
      localState.loading = true
      await loadRegistration()
      localState.loading = false

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    const confirmDischarge = (): void => {
      router.push({
        name: RouteNames.CONFIRM_DISCHARGE,
        query: { 'reg-num': localState.registrationNumber }
      })
    }

    /** Called when App is ready and this component can load its data. */
    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    return {
      convertDate,
      getLengthTrust,
      isRlTransition,
      rlTransitionDate,
      confirmDischarge,
      handleDialogResp,
      isSecurityActNotice,
      UIRegistrationTypes,
      displayHistoricalLienInfo,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme';
</style>
