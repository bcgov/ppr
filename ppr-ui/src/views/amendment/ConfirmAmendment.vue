<template>
  <v-container
    id="confirm-amendment"
    class="view-container pa-15 pt-4"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
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
        <v-col class="review-page" cols="9">
          <h1>Review and Complete Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your Amendment and complete the additional information before registering.
            </p>
          </div>
          <caution-box class="mt-9" style="margin-bottom: 60px;" :setMsg="cautionTxt" :setImportantWord="'Note'" />

          <v-row no-gutters class="summary-header pa-2 mt-4 rounded-top">
            <v-col cols="12" class="pa-2">
              <label class="pl-3">
                <v-icon color="darkBlue">mdi-file-document-multiple</v-icon>
                <span class="pl-3"><strong>Amendment</strong></span>
              </label>
            </v-col>
          </v-row>
          <div class="white ma-0 px-4 rounded-bottom">
            <div v-if="showLengthTrustIndenture">
              <registration-length-trust-amendment class="pt-4" :isSummary="true" />
            </div>

            <div v-if="showSecuredParties">
              <v-divider v-if="showLengthTrustIndenture"></v-divider>
              <h3 class="pt-6 px-3">Secured Parties</h3>
              <secured-party-summary
                class="secured-party-summary px-8"
                :setEnableNoDataAction="true"
              />
            </div>

            <div v-if="showDebtors" class="pa-4">
              <v-divider v-if="showSecuredParties || showLengthTrustIndenture"></v-divider>
              <h3 class="pt-6">Debtors</h3>
              <debtor-summary
                class="debtor-summary px-4"
                :setEnableNoDataAction="true"
              />
            </div>

            <div v-if="showVehicleCollateral || showGeneralCollateral">
              <!-- To do: add amended collateral -->
              <div v-if="showVehicleCollateral">
                <v-divider v-if="showSecuredParties || showDebtors || showLengthTrustIndenture"></v-divider>
                <vehicle-collateral
                  :isSummary="true"
                  :showInvalid="false"
                />
              </div>
              <div v-if="showGeneralCollateral" class="pt-6">
                <v-divider v-if="showSecuredParties || showDebtors ||
                          showVehicleCollateral || showLengthTrustIndenture"></v-divider>
                <gen-col-summary class="py-6 px-4"
                  :setShowAmendLink="false"
                  :setShowHistory="false"
                  :setShowViewLink="false"
                  :setShowConfirm="true"
                />
              </div>
            </div>

            <div class="pb-4" v-if="showDescription">
              <v-divider v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                               showGeneralCollateral || showLengthTrustIndenture"></v-divider>
              <amendment-description class="pt-4" :isSummary="true" />
            </div>

            <div v-if="showCourtOrder">
              <v-divider v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                              showGeneralCollateral || showDescription || showLengthTrustIndenture"></v-divider>
              <court-order class="py-8" :setSummary="true" />
            </div>

          </div>

          <h2 class="pt-14">
            Registering Party for this Amendment
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
            @registeringPartyOpen="regOpenClose($event)"
            :setShowErrorBar="showErrors && registeringOpen"
          />
          <caution-box v-if="showRegMsg" :setMsg="cautionTxtRP" :setImportantWord="'Note'" />
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-10"
          />
          <certify-information
            @certifyValid="showErrors = false"
            :setShowErrors="showErrors"
            class="pt-10"
          />
        </v-col>
        <v-col class="right-page pl-6" cols="3">
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
                :setSaveBtn="'Save and Resume Later'"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Register Amendment and Pay'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewAmendment()"
                @save="saveDraft()"
                @cancel="cancel()"
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
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue-demi'
import { useRoute, useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import {
  CautionBox,
  CourtOrder,
  CertifyInformation,
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { GenColSummary } from '@/components/collateral/generalCollateral'
import { SecuredPartySummary, DebtorSummary } from '@/components/parties/summaries'
import { RegisteringPartyChange } from '@/components/parties/party'
import { AmendmentDescription, RegistrationLengthTrustAmendment } from '@/components/registration'
import { VehicleCollateral } from '@/components/collateral/vehicleCollateral'
import { AllRegistrationTypes } from '@/resources'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  getFeatureFlag,
  getFinancingStatement,
  saveAmendmentStatement,
  saveAmendmentStatementDraft
} from '@/utils'
/* eslint-disable no-unused-vars */
import {
  ActionTypes,
  APIRegistrationTypes,
  RouteNames,
  UIRegistrationTypes
} from '@/enums'
import {
  AddCollateralIF,
  AddPartiesIF,
  AmendmentStatementIF,
  CourtOrderIF,
  ErrorIF,
  StateModelIF,
  LengthTrustIF,
  DialogOptionsIF,
  DraftIF,
  FinancingStatementIF,
  RegTableNewItemI
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'ConfirmAmendment',
  components: {
    AmendmentDescription,
    BaseDialog,
    StaffPaymentDialog,
    CautionBox,
    CertifyInformation,
    FolioNumberSummary,
    RegisteringPartyChange,
    SecuredPartySummary,
    DebtorSummary,
    VehicleCollateral,
    GenColSummary,
    CourtOrder,
    RegistrationLengthTrustAmendment,
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
    },
    saveDraftExit: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const route = useRoute()
    const router = useRouter()
    const {
      // Actions
      setUnsavedChanges,
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
      getLengthTrust,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      getAddCollateral,
      hasUnsavedChanges,
      getRegistrationType,
      getConfirmDebtorName,
      getCertifyInformation,
      getRegistrationNumber,
      getAmendmentDescription,
      getCourtOrderInformation,
      getAddSecuredPartiesAndDebtors
    } = storeToRefs(useStore())

    const localState = reactive({
      collateralSummary: '',
      dataLoaded: false,
      dataLoadError: false,
      registeringOpen: false,
      showRegMsg: false,
      financingStatementDate: null as Date,
      options: unsavedChangesDialog as DialogOptionsIF,
      staffPaymentDialogDisplay: false,
      staffPaymentDialogOptions: {
        acceptText: 'Submit Amendment',
        cancelText: 'Cancel',
        title: 'Staff Payment',
        label: '',
        text: ''
      } as DialogOptionsIF,
      showCancelDialog: false,
      showErrors: false,
      cautionTxt: 'The Registry will provide the verification statement to all Secured Parties named in this ' +
        'registration.',
      cautionTxtRP: 'The Registry will not provide the verification statement for this amendment to the Registering ' +
        'Party named above.',
      tooltipTxt: 'The default Registering Party is based on your BC Registries user account information. This ' +
        'information can be updated within your account settings. You can change to a different Registering Party by ' +
        'using the Change button.',
      validFolio: true,
      feeType: FeeSummaryTypes.AMEND,
      submitting: false,
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
      registrationLength: computed((): RegistrationLengthI => {
        return {
          lifeInfinite: getLengthTrust.value?.lifeInfinite || false,
          lifeYears: getLengthTrust.value?.lifeYears || 0
        }
      }),
      showDescription: computed((): boolean => {
        return !!getAmendmentDescription
      }),
      currentRegNumber: computed((): string => {
        return getRegistrationNumber.value || ''
      }),
      showCourtOrder: computed((): boolean => {
        const courtOrder: CourtOrderIF = getCourtOrderInformation.value
        return courtOrder &&
          (
            courtOrder?.courtName.length > 0 ||
            courtOrder?.courtRegistry.length > 0 ||
            courtOrder?.fileNumber.length > 0 ||
            courtOrder?.orderDate.length > 0 ||
            courtOrder?.effectOfOrder.length > 0
          )
      }),
      showLengthTrustIndenture: computed((): boolean => {
        const lengthTrust: LengthTrustIF = getLengthTrust.value
        return !!lengthTrust.action
      }),
      showSecuredParties: computed((): boolean => {
        const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
        for (let i = 0; i < parties.securedParties.length; i++) {
          if (parties.securedParties[i].action) {
            return true
          }
        }
        return false
      }),

      showDebtors: computed((): boolean => {
        const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
        for (let i = 0; i < parties.debtors.length; i++) {
          if (parties.debtors[i].action) {
            return true
          }
        }
        return false
      }),
      showVehicleCollateral: computed((): boolean => {
        const addCollateral:AddCollateralIF = getAddCollateral.value
        if (!addCollateral.vehicleCollateral) {
          return false
        }
        for (let i = 0; i < addCollateral.vehicleCollateral.length; i++) {
          if (addCollateral.vehicleCollateral[i].action) {
            return true
          }
        }
        return false
      }),
      showGeneralCollateral: computed((): boolean => {
        const addCollateral:AddCollateralIF = getAddCollateral.value
        if (!addCollateral.generalCollateral) {
          return false
        }
        for (let i = 0; i < addCollateral.generalCollateral.length; i++) {
          if (!addCollateral.generalCollateral[i].collateralId) {
            return true
          }
        }
        return false
      }),
      collateralValid: computed((): boolean => {
        const addCollateral:AddCollateralIF = getAddCollateral.value
        return (addCollateral.valid || (!localState.showGeneralCollateral && !localState.showVehicleCollateral))
      }),
      partiesValid: computed((): boolean => {
        const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
        return (parties.valid || (!localState.showSecuredParties && !localState.showDebtors))
      }),
      courtOrderValid: computed((): boolean => {
        const courtOrder: CourtOrderIF = getCourtOrderInformation.value
        return (!courtOrder ||
          (courtOrder.courtName.length === 0 &&
            courtOrder.courtRegistry.length === 0 &&
            courtOrder.fileNumber.length === 0 &&
            courtOrder.orderDate.length === 0 &&
            courtOrder.effectOfOrder.length === 0) ||
          (courtOrder.courtName.length > 0 &&
            courtOrder.courtRegistry.length > 0 &&
            courtOrder.fileNumber.length > 0 &&
            courtOrder.orderDate.length > 0 &&
            courtOrder.effectOfOrder.length > 0))
      }),
      certifyInformationValid: computed((): boolean => {
        return getCertifyInformation.value.valid
      }),
      stickyComponentErrMsg: computed((): string => {
        if ((!localState.validFolio || !localState.courtOrderValid) && localState.showErrors) {
          return '< Please complete required information'
        }
        if ((localState.registeringOpen || !localState.certifyInformationValid) && localState.showErrors) {
          return '< You have unfinished changes'
        }
        return ''
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const cancel = (): void => {
      if (hasUnsavedChanges) localState.showCancelDialog = true
      else goToDashboard()
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDashboard()
    }

    const scrollToInvalid = async (): Promise<void> => {
      if (!localState.validFolio) {
        const component = document.getElementById('folio-summary')
        await component.scrollIntoView({ behavior: 'smooth' })
        return
      }
      if (localState.registeringOpen) {
        const component = document.getElementById('reg-party-change')
        await component.scrollIntoView({ behavior: 'smooth' })
        return
      }
      if (!localState.courtOrderValid) {
        const component = document.getElementById('court-order-component')
        await component.scrollIntoView({ behavior: 'smooth' })
        return
      }
      if (!localState.certifyInformationValid) {
        const component = document.getElementById('certify-information')
        await component.scrollIntoView({ behavior: 'smooth' })
      }
    }

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || !getConfirmDebtorName) {
        if (!localState.registrationNumber) {
          console.error('No registration number this amendment. Redirecting to dashboard...')
        } else {
          console.error('No debtor name confirmed for this amendment. Redirecting to dashboard...')
        }
        router.push({
          name: RouteNames.DASHBOARD
        })
        return
      }

      if (localState.currentRegNumber === localState.registrationNumber) {
        return
      }

      localState.financingStatementDate = new Date()
      localState.submitting = true
      const financingStatement = await getFinancingStatement(
        true,
        localState.registrationNumber
      )

      if (financingStatement.error) {
        localState.dataLoadError = true
        emitError(financingStatement.error)
      } else {
        await setStore(financingStatement)
        // give time for setStore to finish
        setTimeout(() => {
          setUnsavedChanges(false)
        }, 200)
      }
      localState.submitting = false
    }

    const setStore = async (financingStatement: FinancingStatementIF): Promise<void> => {
      // load data into the store
      const registrationType = AllRegistrationTypes.find((reg, index) => {
        if (reg.registrationTypeAPI === financingStatement.type) {
          return true
        }
      })
      const parties = {
        valid: true,
        registeringParty: null, // will be taken from account info
        securedParties: financingStatement.securedParties,
        debtors: financingStatement.debtors
      } as AddPartiesIF
      setRegistrationCreationDate(financingStatement.createDateTime)
      setRegistrationExpiryDate(financingStatement.expiryDate)
      setRegistrationNumber(financingStatement.baseRegistrationNumber)
      setRegistrationType(registrationType)
      setAddSecuredPartiesAndDebtors(parties)
    }

    const goToReviewAmendment = (): void => {
      router.push({
        name: RouteNames.AMEND_REGISTRATION,
        query: { 'reg-num': localState.registrationNumber + '-confirm' }
      })
      emitHaveData(false)
    }

    const setShowWarning = (): void => {
      const parties = getAddSecuredPartiesAndDebtors.value
      localState.showRegMsg = parties.registeringParty?.action === ActionTypes.EDITED
    }

    const onStaffPaymentChanges = (pay: boolean): void => {
      if (pay) {
        submitAmendment()
      }
      localState.staffPaymentDialogDisplay = false
    }

    const setFolioValid = (valid: boolean): void => {
      localState.validFolio = valid
      localState.showErrors = false
    }

    const regOpenClose = (open: boolean): void => {
      localState.registeringOpen = open
      localState.showErrors = false
      setShowWarning()
    }

    const saveDraft = async (): Promise<void> => {
      const stateModel: StateModelIF = getStateModel.value
      localState.submitting = true
      const draft: DraftIF = await saveAmendmentStatementDraft(stateModel)
      localState.submitting = false
      if (draft.error) {
        emitError(draft.error)
      } else {
        setUnsavedChanges(false)
        const prevDraftId = stateModel.registration?.draft?.amendmentStatement?.documentId || ''
        // set new added reg
        const newItem: RegTableNewItemI = {
          addedReg: draft.amendmentStatement.documentId,
          addedRegParent: draft.amendmentStatement.baseRegistrationNumber,
          addedRegSummary: null,
          prevDraft: prevDraftId
        }
        setRegTableNewItem(newItem)
        router.push({
          name: RouteNames.DASHBOARD
        })
        emitHaveData(false)
      }
    }

    const submitButton = (): void => {
      if (!localState.validFolio || !localState.certifyInformationValid || localState.registeringOpen) {
        localState.showErrors = true
        scrollToInvalid()
        return
      }
      if ((isRoleStaffReg) || (isRoleStaffSbc)) {
        localState.staffPaymentDialogDisplay = true
      } else {
        submitAmendment()
      }
    }

    const submitAmendment = async (): Promise<void> => {
      // Incomplete validation check: all changes must be valid to submit registration.
      if (localState.collateralValid && localState.partiesValid && localState.courtOrderValid) {
        const stateModel: StateModelIF = getStateModel.value
        localState.submitting = true
        const apiResponse: AmendmentStatementIF = await saveAmendmentStatement(stateModel)
        localState.submitting = false
        if (apiResponse === undefined || apiResponse?.error !== undefined) {
          emitError(apiResponse?.error)
        } else {
          const prevDraftId = stateModel.registration?.draft?.amendmentStatement?.documentId || ''
          // set new added reg
          const newItem: RegTableNewItemI = {
            addedReg: apiResponse.amendmentRegistrationNumber,
            addedRegParent: apiResponse.baseRegistrationNumber,
            addedRegSummary: null,
            prevDraft: prevDraftId
          }
          setRegTableNewItem(newItem)
          // On success return to dashboard
          goToDashboard()
        }
      } else {
        // emit registration incomplete error
        const error: ErrorIF = {
          statusCode: 400,
          message: 'Registration incomplete: one or more changes is invalid.'
        }
        console.error(error)
        alert(error.message)
      }
    }

    const goToDashboard = (): void => {
      router.push({
        name: RouteNames.DASHBOARD
      })
      emitHaveData(false)
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
      await loadRegistration()

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
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

    watch(() => props.saveDraftExit, (val: boolean) => {
      saveDraft()
    })

    return {
      cancel,
      saveDraft,
      regOpenClose,
      submitButton,
      setFolioValid,
      isRoleStaffBcol,
      handleDialogResp,
      scrollToInvalid,
      submitAmendment,
      goToReviewAmendment,
      onStaffPaymentChanges,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
@media print {
  body {
    overflow: auto;
    height: auto;
  }
  ::v-deep .v-data-table__wrapper {
    overflow: visible;
    height: auto;
  }
  ::v-deep .col-9 {
    max-width: 100%;
  }
  .review-page {
    min-width: 1024px;
  }
  .v-footer {
    display: none;
  }
  .right-page {
    width: 100%;
  }
  .vue-affix {
    position: relative;
    top: 0px !important;
  }
  table {
    table-layout: auto;
  }
  .px-15, .pa-15 {
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
  ::v-deep .v-data-table > .v-data-table__wrapper > table > tbody > tr > td,
  ::v-deep .v-data-table > .v-data-table__wrapper > table > tbody > tr > th,
  ::v-deep .v-data-table > .v-data-table__wrapper > table > thead > tr > td,
  ::v-deep .v-data-table > .v-data-table__wrapper > table > thead > tr > th
  {
    padding: 0 8px;
  }
  ::v-deep .buttons-stacked {
    display: none;
  }
}

</style>
