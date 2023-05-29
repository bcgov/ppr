<template>
  <v-container
    id="confirm-discharge"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      setAttach="#confirm-discharge"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Confirm and Complete Total Discharge</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Confirm your Total Discharge and complete the additional information before registering.
            </p>
          </div>
          <caution-box class="mt-9" :setMsg="cautionTxt" />
          <h2 class="pt-14">
            Registering Party for this Discharge
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
          <caution-box v-if="showRegMsg" :setMsg="cautionTxtRP" :setImportantWord="'Note'"/>
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-15"
          />
          <h2 class="pt-15">2. Confirm</h2>
          <p class="ma-0 pt-4">
            You are about to submit a Total Discharge based on the following
            details:
          </p>
          <discharge-confirm-summary
            class="mt-6 soft-corners"
            :setRegNum="registrationNumber"
            :setRegType="registrationTypeUI"
            :setCollateralSummary="collateralSummary"
            :setShowErrors="showErrors"
            @valid="validConfirm = $event"
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
                :setRegistrationType="registrationTypeUI"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Register Total Discharge'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewRegistration()"
                @cancel="showDialog()"
                @submit="submitDischarge()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue-demi'
import { useRoute, useRouter } from 'vue-router/composables'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import {
  CautionBox,
  DischargeConfirmSummary,
  FolioNumberSummary,
  CertifyInformation,
  StickyContainer
} from '@/components/common'
import { RegisteringPartyChange } from '@/components/parties/party'
import { BaseDialog } from '@/components/dialogs'
import { AllRegistrationTypes } from '@/resources'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, getFinancingStatement, saveDischarge } from '@/utils'
/* eslint-disable no-unused-vars */
import { ActionTypes, APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  DischargeRegistrationIF,
  ErrorIF,
  AddPartiesIF,
  StateModelIF,
  DialogOptionsIF,
  RegTableNewItemI
} from '@/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'ConfirmDischarge',
  components: {
    BaseDialog,
    CautionBox,
    DischargeConfirmSummary,
    FolioNumberSummary,
    RegisteringPartyChange,
    CertifyInformation,
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
      // Actions
      setRegTableNewItem,
      setRegistrationType,
      setRegistrationNumber,
      setRegistrationExpiryDate,
      setRegistrationCreationDate,
      setAddSecuredPartiesAndDebtors
    } = useStore()
    const {
      // Getters
      getStateModel,
      isRoleStaffBcol,
      getConfirmDebtorName,
      getRegistrationType,
      getAddSecuredPartiesAndDebtors
    } = storeToRefs(useStore())

    const localState = reactive({
      cautionTxt: 'The Registry will provide the verification statement to all Secured Parties named in this ' +
        'registration.',
      cautionTxtRP: 'The Registry will not provide the verification statement for this total discharge to the ' +
        'Registering Party named above.',
      collateralSummary: '',
      dataLoaded: false,
      dataLoadError: false,
      feeType: FeeSummaryTypes.DISCHARGE,
      financingStatementDate: null as Date,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      showErrors: false,
      showRegMsg: false,
      submitting: false,
      tooltipTxt: 'The default Registering Party is based on your BC Registries user account information. This ' +
        'information can be updated within your account settings. You can change to a different Registering Party by ' +
        'using the Change button.',
      validConfirm: false,
      validFolio: true,
      validCertify: false,
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      registrationNumber: computed((): string => {
        return (route.query['reg-num'] as string) || ''
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || null
      }),
      stickyComponentErrMsg: computed((): string => {
        if ((!localState.validConfirm || !localState.validFolio) && localState.showErrors) {
          return '< Please complete required information'
        }
        return ''
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || !getConfirmDebtorName) {
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
          localState.collateralSummary = `General Collateral and ${financingStatement.vehicleCollateral.length} ` +
            'Vehicles'
        } else if (financingStatement.vehicleCollateral) {
          localState.collateralSummary = `No General Collateral and ${financingStatement.vehicleCollateral.length} ` +
            'Vehicles'
        } else {
          localState.collateralSummary += 'No Collateral'
        }
        if (financingStatement.vehicleCollateral?.length === 1) {
          localState.collateralSummary = localState.collateralSummary
            .replace('Vehicles', 'Vehicle')
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
      localState.submitting = true
      await loadRegistration()
      localState.submitting = false

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        setRegistrationNumber(null)
        router.push({ name: RouteNames.DASHBOARD })
      }
    }

    const goToReviewRegistration = (): void => {
      router.push({
        name: RouteNames.REVIEW_DISCHARGE,
        query: { 'reg-num': localState.registrationNumber }
      })
      emitHaveData(false)
    }

    const setFolioValid = (valid: boolean): void => {
      localState.validFolio = valid
    }

    const showDialog = (): void => {
      localState.showCancelDialog = true
    }

    const submitDischarge = async (): Promise<void> => {
      if ((!localState.validConfirm) || (!localState.validFolio) || (!localState.validCertify)) {
        localState.showErrors = true
        return
      }

      const stateModel: StateModelIF = getStateModel.value
      localState.submitting = true
      const apiResponse: DischargeRegistrationIF = await saveDischarge(stateModel)
      localState.submitting = false
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        emitError(apiResponse?.error)
      } else {
        // set new added reg
        const newItem: RegTableNewItemI = {
          addedReg: apiResponse.dischargeRegistrationNumber,
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
      router.push({
        name: RouteNames.DASHBOARD
      })
      emitHaveData(false)
    }

    const setShowWarning = (): void => {
      const parties = getAddSecuredPartiesAndDebtors.value
      localState.showRegMsg = parties.registeringParty?.action === ActionTypes.EDITED
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: Boolean = true): void => {
      context.emit('haveData', haveData)
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    /** Called when App is ready and this component can load its data. */
    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    return {
      showDialog,
      setFolioValid,
      goToDashboard,
      setShowWarning,
      isRoleStaffBcol,
      submitDischarge,
      handleDialogResp,
      goToReviewRegistration,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
