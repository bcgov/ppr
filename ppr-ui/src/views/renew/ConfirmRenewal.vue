<template>
  <v-container
    id="confirm-renewal"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      setAttach="#confirm-renewal"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialogOptions"
      :setShowCertifiedCheckbox="false"
      @proceed="onStaffPaymentChanges($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Review and Complete Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your renewal and complete the additional information before registering.
            </p>
          </div>
           <h2 class="pt-14">
            Registering Party for this Renewal
            <v-tooltip
              class="pa-2"
              content-class="top-tooltip"
              top
              transition="fade-transition"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-icon class="ml-1" color="primary" v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
              </template>
              <div class="pt-2 pb-2">
                {{ tooltipTxt }}
              </div>
            </v-tooltip>
          </h2>
          <registering-party-change
            class="pt-4"
            @registeringPartyOpen="setShowWarning()"
          />
          <caution-box v-if="showRegMsg" :setMsg="cautionTxt" :setImportantWord="'Note'" />
          <registration-length-trust-summary class="mt-10" :isRenewal="true"
          />
          <div v-if="showCourtOrderInfo">
            <court-order :setSummary="true" :isRenewal="true" class="pt-10" />
          </div>

          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-10"
          />
          <certify-information
            @certifyValid="validCertify = $event"
            :setShowErrors="showErrors"
            class="pt-10"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setErrMsg="stickyComponentErrMsg"
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setRegistrationLength="registrationLength"
                :setRegistrationType="registrationTypeUI"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Register Renewal and Pay'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewRenewal()"
                @cancel="showCancelDialog = true"
                @submit="submitButton()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import {
  FolioNumberSummary,
  CertifyInformation,
  CourtOrder,
  StickyContainer,
  CautionBox
} from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { RegisteringPartyChange } from '@/components/parties/party'
import { AllRegistrationTypes } from '@/resources'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, getFinancingStatement, saveRenewal } from '@/utils'
/* eslint-disable no-unused-vars */
import { ActionTypes, APIRegistrationTypes, RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  RenewRegistrationIF,
  ErrorIF,
  AddPartiesIF,
  StateModelIF,
  DialogOptionsIF,
  RegTableNewItemI
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'ConfirmRenewal',
  components: {
    BaseDialog,
    StaffPaymentDialog,
    CourtOrder,
    FolioNumberSummary,
    RegisteringPartyChange,
    RegistrationLengthTrustSummary,
    CertifyInformation,
    CautionBox,
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
    const {
      getStateModel,
      getLengthTrust,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      getRegistrationType,
      getConfirmDebtorName,
      getAddSecuredPartiesAndDebtors
    } = useGetters([
      'getStateModel',
      'getLengthTrust',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'isRoleStaffSbc',
      'getRegistrationType',
      'getConfirmDebtorName',
      'getAddSecuredPartiesAndDebtors'
    ])
    const {
      setRegistrationType,
      setRegTableNewItem,
      setRegistrationNumber,
      setRegistrationCreationDate,
      setRegistrationExpiryDate,
      setAddSecuredPartiesAndDebtors
    } = useActions([
      'setRegistrationType',
      'setRegTableNewItem',
      'setRegistrationNumber',
      'setRegistrationCreationDate',
      'setRegistrationExpiryDate',
      'setAddSecuredPartiesAndDebtors'
    ])

    const localState = reactive({
      collateralSummary: '', // eslint-disable-line lines-between-class-members
      dataLoaded: false,
      dataLoadError: false,
      financingStatementDate: null as Date,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      submitting: false,
      showRegMsg: false,
      staffPaymentDialogDisplay: false,
      staffPaymentDialogOptions: {
        acceptText: 'Submit Renewal',
        cancelText: 'Cancel',
        title: 'Staff Payment',
        label: '',
        text: ''
      } as DialogOptionsIF,
      showErrors: false,
      tooltipTxt: 'The default Registering Party is based on your BC ' +
        'Registries user account information. This information can be updated within ' +
        'your account settings. You can change to a different Registering Party by ' +
        'using the Change button.',
      cautionTxt: 'The Registry will not provide ' +
        'the verification statement for this renewal to the Registering Party named above.',
      validFolio: true,
      validCertify: false,
      feeType: FeeSummaryTypes.RENEW,
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
        return (context.root.$route.query['reg-num'] as string) || ''
      }),
      stickyComponentErrMsg: computed((): string => {
        if (!localState.validFolio && localState.showErrors) {
          return '< Please complete required information'
        }
        return ''
      }),
      showCourtOrderInfo: computed((): boolean => {
        return (getRegistrationType.value && localState.registrationType === APIRegistrationTypes.REPAIRERS_LIEN)
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        setRegistrationNumber(null)
        context.root.$router.push({ name: RouteNames.DASHBOARD })
      }
    }

    const goToReviewRenewal = (): void => {
      context.root.$router.push({
        name: RouteNames.RENEW_REGISTRATION,
        query: { 'reg-num': localState.registrationNumber }
      })
      emitHaveData(false)
    }

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || !getConfirmDebtorName.value) {
        if (!localState.registrationNumber) {
          console.error('No registration number given to discharge. Redirecting to dashboard...')
        } else {
          console.error('No debtor name confirmed for discharge. Redirecting to dashboard...')
        }
        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
        return
      }
      localState.financingStatementDate = new Date()
      const financingStatement = await getFinancingStatement(
        true,
        localState.registrationNumber
      )
      if (financingStatement.error) {
        localState.dataLoadError = true
        emitError(financingStatement.error)
      } else {
        // set collateral summary
        if (
          financingStatement.generalCollateral &&
          !financingStatement.vehicleCollateral
        ) {
          localState.collateralSummary = 'General Collateral and 0 Vehicles'
        } else if (financingStatement.generalCollateral) {
          localState.collateralSummary =
            `General Collateral and ${financingStatement.vehicleCollateral.length} Vehicles`
        } else if (financingStatement.vehicleCollateral) {
          localState.collateralSummary =
            `No General Collateral and ${financingStatement.vehicleCollateral.length} Vehicles`
        } else {
          localState.collateralSummary += 'No Collateral'
        }
        if (financingStatement.vehicleCollateral?.length === 1) {
          localState.collateralSummary =
            localState.collateralSummary.replace('Vehicles', 'Vehicle')
        }
        // load data into the store
        const registrationType = AllRegistrationTypes.find((reg, index) => {
          if (reg.registrationTypeAPI === financingStatement.type) {
            return true
          }
        })
        const parties = {
          valid: true,
          registeringParty: null,
          securedParties: financingStatement.securedParties,
          debtors: financingStatement.debtors
        } as AddPartiesIF
        setRegistrationCreationDate(financingStatement.createDateTime)
        setRegistrationExpiryDate(financingStatement.expiryDate)
        setRegistrationNumber(financingStatement.baseRegistrationNumber)
        setRegistrationType(registrationType)
        setAddSecuredPartiesAndDebtors(parties)
      }
    }

    const setFolioValid = (valid: boolean): void => {
      localState.validFolio = valid
    }

    const onStaffPaymentChanges = (pay: boolean): void => {
      if (pay) {
        submitRenewal()
      }
      localState.staffPaymentDialogDisplay = false
    }

    const submitButton = (): void => {
      if ((!localState.validFolio) || (!localState.validCertify)) {
        localState.showErrors = true
        return
      }
      if ((isRoleStaffReg.value) || (isRoleStaffSbc.value)) {
        localState.staffPaymentDialogDisplay = true
      } else {
        submitRenewal()
      }
    }

    const submitRenewal = async (): Promise<void> => {
      const stateModel: StateModelIF = getStateModel.value
      localState.submitting = true
      const apiResponse: RenewRegistrationIF = await saveRenewal(stateModel)
      localState.submitting = false
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        console.error(apiResponse?.error)
        emitError(apiResponse?.error)
      } else {
        // unset registration number
        setRegistrationNumber(null)
        // set new added reg
        const newItem: RegTableNewItemI = {
          addedReg: apiResponse.renewalRegistrationNumber,
          addedRegParent: apiResponse.baseRegistrationNumber,
          addedRegSummary: null,
          prevDraft: ''
        }
        setRegTableNewItem(newItem)
        // On success return to dashboard
        goToDashboard()
      }
    }

    const goToDashboard = (): void => {
      // unset registration number
      setRegistrationNumber(null)
      context.root.$router.push({
        name: RouteNames.DASHBOARD
      })
      emitHaveData(false)
    }

    const setShowWarning = (): void => {
      const parties = getAddSecuredPartiesAndDebtors.value
      localState.showRegMsg = parties.registeringParty?.action === ActionTypes.EDITED
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!localState.isAuthenticated || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
        return
      }

      // get registration data from api and load into store
      localState.submitting = true
      await loadRegistration()
      localState.submitting = false

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
      submitButton,
      setFolioValid,
      setShowWarning,
      isRoleStaffBcol,
      handleDialogResp,
      goToReviewRenewal,
      onStaffPaymentChanges,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
