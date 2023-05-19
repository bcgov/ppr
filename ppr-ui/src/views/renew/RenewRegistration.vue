<template>
  <v-container
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              This is the current registration information as of
              <b>{{ asOfDateTime }}.</b> Review this information to ensure it is
              correct
              <span v-if="registrationType !== registrationTypeRL">
                and select the length of time you would like to renew this
                registration for</span
              >.<br />
            </p>
            <p class="ma-0 pt-5">
              To view the full history of this registration including
              descriptions of any previous amendments or court orders, you will
              need to conduct a separate search.
            </p>
          </div>
          <registration-length-trust
            :setShowInvalid="showInvalid"
            @lengthTrustValid="registrationValid = $event"
            v-if="registrationType !== registrationTypeRL"
            class="mt-15"
            :isRenewal="true"
          />
          <registration-repairers-lien v-else class="mt-15" :isRenewal="true" />
          <div class="summary-header mt-15 pa-4 rounded-top">
            <v-icon color="darkBlue">mdi-account-multiple-plus</v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </div>
          <h3 class="pt-6">Original Registering Party</h3>
          <registering-party-summary
            class="pt-4"
            :setEnableNoDataAction="false"
          />
          <h3 class="pt-6">Secured Parties</h3>
          <secured-party-summary class="pt-4" :setEnableNoDataAction="false" />
          <h3 class="pt-6">Debtors</h3>
          <debtor-summary class="pt-4" :setEnableNoDataAction="false" />
          <collateral class="mt-15" :isSummary="true" />
          <court-order
            :setShowErrors="showInvalid"
            :setRequireCourtOrder="true"
            @setCourtOrderValid="setValid($event)"
            v-if="registrationType === registrationTypeRL"
            class="mt-15" />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setRegistrationLength="registrationLength"
                :setRegistrationType="registrationTypeUI"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Review and Complete'"
                :setErrMsg="errMsg"
                @cancel="showCancelDialog = true"
                @submit="confirmRenewal()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router/composables'
import { useStore } from '@/store/store'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { StickyContainer, CourtOrder } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegistrationLengthTrust, RegistrationRepairersLien } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
import { AllRegistrationTypes } from '@/resources'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { getFeatureFlag, getFinancingStatement, pacificDate } from '@/utils'
/* eslint-disable no-unused-vars */
import {
  APIRegistrationTypes,
  RouteNames,
  RegistrationFlowType
} from '@/enums'
import {
  ErrorIF,
  AddPartiesIF,
  CertifyIF,
  AddCollateralIF,
  LengthTrustIF,
  CourtOrderIF,
  DialogOptionsIF
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'RenewRegistrations',
  components: {
    BaseDialog,
    RegistrationLengthTrust,
    RegistrationRepairersLien,
    Collateral,
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary,
    CourtOrder,
    StickyContainer
  },
  emits: ['error', 'haveData'],
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    isJestRunning: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const route = useRoute()
    const router = useRouter()
    const {
      getLengthTrust,
      getRegistrationType,
      getConfirmDebtorName,
      getRegistrationNumber,
      getRegistrationFlowType
    } = useGetters([
      'getLengthTrust',
      'getRegistrationType',
      'getConfirmDebtorName',
      'getRegistrationNumber',
      'getRegistrationFlowType'
    ])
    const {
      setLengthTrust,
      setAddCollateral,
      setStaffPayment,
      setRegistrationNumber,
      setRegistrationType,
      setRegistrationFlowType,
      setCourtOrderInformation,
      setCertifyInformation,
      setFolioOrReferenceNumber,
      setRegistrationExpiryDate,
      setRegistrationCreationDate,
      setAddSecuredPartiesAndDebtors,
      setOriginalAddSecuredPartiesAndDebtors
    } = useActions([
      'setLengthTrust',
      'setAddCollateral',
      'setStaffPayment',
      'setRegistrationNumber',
      'setRegistrationType',
      'setRegistrationFlowType',
      'setCourtOrderInformation',
      'setCertifyInformation',
      'setFolioOrReferenceNumber',
      'setRegistrationExpiryDate',
      'setRegistrationCreationDate',
      'setAddSecuredPartiesAndDebtors',
      'setOriginalAddSecuredPartiesAndDebtors'
    ])
    const localState = reactive({
      dataLoaded: false,
      dataLoadError: false,
      financingStatementDate: null as Date,
      feeType: FeeSummaryTypes.RENEW,
      loading: false,
      registrationValid: false,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      showInvalid: false,
      errMsg: '',
      asOfDateTime: computed((): string => {
        // return formatted date
        if (localState.financingStatementDate) {
          return `${pacificDate(localState.financingStatementDate)}`
        }
        return `${pacificDate(new Date())}`
      }),
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      registrationLength: computed((): RegistrationLengthI => {
        return {
          lifeInfinite: getLengthTrust.value?.lifeInfinite || false,
          lifeYears: getLengthTrust.value?.lifeYears || 0
        }
      }),
      registrationTypeUI: computed((): string => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || ''
      }),
      registrationNumber: computed((): string => {
        return (route.query['reg-num'] as string) || ''
      }),
      registrationTypeRL: computed(() => {
        return APIRegistrationTypes.REPAIRERS_LIEN
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        setRegistrationNumber(null)
        router.push({ name: RouteNames.DASHBOARD })
      }
    }

    const loadRegistration = async (): Promise<void> => {
      if (
        !getRegistrationNumber.value ||
        getRegistrationFlowType.value !== RegistrationFlowType.RENEWAL
      ) {
        if (!localState.registrationNumber || !getConfirmDebtorName.value) {
          if (!localState.registrationNumber) {
            console.error('No registration number given to discharge. Redirecting to dashboard...')
          } else {
            console.error('No debtor name confirmed for discharge. Redirecting to dashboard...')
          }
          router.push({
            name: RouteNames.DASHBOARD
          })
          return
        }
        localState.financingStatementDate = new Date()
        const financingStatement = await getFinancingStatement(true, localState.registrationNumber)
        if (financingStatement.error) {
          localState.dataLoadError = true
          emitError(financingStatement.error)
        } else {
          // load data into the store
          const registrationType = AllRegistrationTypes.find((reg, index) => {
            if (reg.registrationTypeAPI === financingStatement.type) {
              return true
            }
          })
          const collateral = {
            valid: true,
            vehicleCollateral: financingStatement.vehicleCollateral,
            generalCollateral: financingStatement.generalCollateral
          } as AddCollateralIF
          const lengthTrust = {
            valid: false,
            showInvalid: false,
            trustIndenture: financingStatement.trustIndenture || false,
            lifeInfinite: false,
            lifeYears: null,
            surrenderDate: financingStatement.surrenderDate || null,
            lienAmount: financingStatement.lienAmount || null
          } as LengthTrustIF
          if (
            registrationType.registrationTypeAPI ===
            APIRegistrationTypes.REPAIRERS_LIEN
          ) {
            lengthTrust.lifeYears = 1
            lengthTrust.valid = true
          }
          const parties = {
            valid: true,
            registeringParty: null, // will be taken from account info
            securedParties: financingStatement.securedParties,
            debtors: financingStatement.debtors
          } as AddPartiesIF
          const origParties = {
            registeringParty: financingStatement.registeringParty, // will be used for summary
            securedParties: financingStatement.securedParties,
            debtors: financingStatement.debtors
          } as AddPartiesIF
          const courtOrder: CourtOrderIF = {
            courtRegistry: '',
            courtName: '',
            fileNumber: '',
            effectOfOrder: '',
            orderDate: ''
          }
          const certifyInfo: CertifyIF = {
            valid: false,
            certified: false,
            legalName: '',
            registeringParty: null
          }
          setStaffPayment({
            option: -1,
            routingSlipNumber: '',
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: '',
            isPriority: false
          })
          setCourtOrderInformation(courtOrder)
          setRegistrationCreationDate(financingStatement.createDateTime)
          setRegistrationExpiryDate(financingStatement.expiryDate)
          setRegistrationNumber(financingStatement.baseRegistrationNumber)
          setRegistrationType(registrationType)
          setAddCollateral(collateral)
          setLengthTrust(lengthTrust)
          setAddSecuredPartiesAndDebtors(parties)
          setOriginalAddSecuredPartiesAndDebtors(origParties)
          setRegistrationFlowType(RegistrationFlowType.RENEWAL)
          setFolioOrReferenceNumber('')
          setCertifyInformation(certifyInfo)
        }
      }
    }

    const setValid = (isValid): void => {
      localState.registrationValid = isValid
      if (isValid) {
        localState.errMsg = ''
      }
    }

    const confirmRenewal = (): void => {
      localState.errMsg = ''
      if (localState.registrationValid) {
        router.push({
          name: RouteNames.CONFIRM_RENEWAL,
          query: { 'reg-num': localState.registrationNumber }
        })
      } else {
        localState.errMsg = '< You have unfinished changes'
        localState.showInvalid = true
        scrollToInvalid()
      }
    }

    const scrollToInvalid = async (): Promise<void> => {
      if (!localState.registrationValid) {
        const component = document.getElementById('court-order')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
        }
      }
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!localState.isAuthenticated || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        router.push({
          name: RouteNames.DASHBOARD
        })
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

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: Boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    return {
      setValid,
      confirmRenewal,
      handleDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
