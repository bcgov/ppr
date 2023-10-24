<template>
  <v-container
    id="confirm-amendment"
    class="view-container pa-15 pt-4"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular
        color="primary"
        size="50"
        indeterminate
      />
    </v-overlay>
    <base-dialog
      :set-options="options"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :set-display="staffPaymentDialogDisplay"
      :set-options="staffPaymentDialogOptions"
      :set-show-certified-checkbox="false"
      @proceed="onStaffPaymentChanges($event)"
    />
    <div
      v-if="appReady"
      class="container pa-0"
      style="min-width: 960px;"
    >
      <v-row no-gutters>
        <v-col
          class="review-page"
          cols="9"
        >
          <h1>Review and Complete Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your Amendment and complete the additional information before registering.
            </p>
          </div>
          <caution-box
            class="mt-9"
            style="margin-bottom: 60px;"
            :set-msg="cautionTxt"
            :set-important-word="'Note'"
          />

          <v-row
            no-gutters
            class="summary-header pa-2 mt-4 rounded-top"
          >
            <v-col
              cols="12"
              class="pa-2"
            >
              <label class="pl-3">
                <v-icon color="darkBlue">mdi-file-document-multiple</v-icon>
                <span class="pl-3"><strong>Amendment</strong></span>
              </label>
            </v-col>
          </v-row>
          <div class="bg-white ma-0 px-4 rounded-bottom">
            <div v-if="showLengthTrustIndenture">
              <registration-length-trust-amendment
                class="pt-4"
                :is-summary="true"
              />
            </div>

            <div v-if="showSecuredParties">
              <v-divider v-if="showLengthTrustIndenture" />
              <h3 class="pt-6 px-3">
                Secured Parties
              </h3>
              <secured-party-summary
                class="secured-party-summary px-8"
                :set-enable-no-data-action="true"
              />
            </div>

            <div
              v-if="showDebtors"
              class="pa-4"
            >
              <v-divider v-if="showSecuredParties || showLengthTrustIndenture" />
              <h3 class="pt-6">
                Debtors
              </h3>
              <debtor-summary
                class="debtor-summary px-4"
                :set-enable-no-data-action="true"
              />
            </div>

            <div v-if="showVehicleCollateral || showGeneralCollateral">
              <!-- To do: add amended collateral -->
              <div v-if="showVehicleCollateral">
                <v-divider v-if="showSecuredParties || showDebtors || showLengthTrustIndenture" />
                <vehicle-collateral
                  :is-summary="true"
                  :show-invalid="false"
                />
              </div>
              <div
                v-if="showGeneralCollateral"
                class="pt-6"
              >
                <v-divider
                  v-if="showSecuredParties || showDebtors ||
                    showVehicleCollateral || showLengthTrustIndenture"
                />
                <gen-col-summary
                  class="py-6 px-4"
                  :set-show-amend-link="false"
                  :set-show-history="false"
                  :set-show-view-link="false"
                  :set-show-confirm="true"
                />
              </div>
            </div>

            <div
              v-if="showDescription"
              class="pb-4"
            >
              <v-divider
                v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                  showGeneralCollateral || showLengthTrustIndenture"
              />
              <amendment-description
                class="pt-4"
                :is-summary="true"
              />
            </div>

            <div v-if="showCourtOrder">
              <v-divider
                v-if="showSecuredParties || showDebtors || showVehicleCollateral ||
                  showGeneralCollateral || showDescription || showLengthTrustIndenture"
              />
              <court-order
                class="py-8"
                :set-summary="true"
              />
            </div>
          </div>

          <h2 class="pt-14">
            Registering Party for this Amendment
            <v-tooltip
              class="pa-2"
              content-class="top-tooltip"
              location="top"
              transition="fade-transition"
            >
              <template #activator="{ on, attrs }">
                <v-icon
                  class="ml-1"
                  color="primary"
                  v-bind="attrs"
                  v-on="on"
                >
                  mdi-information-outline
                </v-icon>
              </template>
              <div class="pt-2 pb-2">
                {{ tooltipTxt }}
              </div>
            </v-tooltip>
          </h2>
          <registering-party-change
            class="pt-4"
            :set-show-error-bar="showErrors && registeringOpen"
            @registeringPartyOpen="regOpenClose($event)"
          />
          <caution-box
            v-if="showRegMsg"
            :set-msg="cautionTxtRP"
            :set-important-word="'Note'"
          />
          <folio-number-summary
            :set-show-errors="showErrors"
            class="pt-10"
            @folioValid="setFolioValid($event)"
          />
          <certify-information
            class="pt-10"
            :section-number="2"
            :set-show-errors="showErrors"
            @certifyValid="showErrors = false"
          />
        </v-col>
        <v-col
          class="right-page pl-6"
          cols="3"
        >
          <aside>
            <affix
              relative-element-selector=".col-9"
              :offset="{ top: 90, bottom: -100 }"
            >
              <sticky-container
                :set-err-msg="stickyComponentErrMsg"
                :set-right-offset="true"
                :set-show-buttons="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-registration-length="registrationLength"
                :set-registration-type="registrationTypeUI"
                :set-save-btn="'Save and Resume Later'"
                :set-back-btn="'Back'"
                :set-cancel-btn="'Cancel'"
                :set-submit-btn="'Register Amendment and Pay'"
                :set-disable-submit-btn="isRoleStaffBcol"
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
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
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
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  getFeatureFlag,
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
import { useAuth, useNavigation } from '@/composables'
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
  emits: ['error', 'haveData'],
  setup (props, { emit }) {
    const route = useRoute()
    const router = useRouter()
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setUnsavedChanges,
      setRegTableNewItem
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
        return !!getAmendmentDescription.value
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
      else goToDash()
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDash()
    }

    const scrollToInvalid = async (): Promise<void> => {
      let docId = ''
      if (!localState.validFolio) {
        docId = 'folio-summary'
      } else if (localState.registeringOpen) {
        docId = 'reg-party-change'
      } else if (!localState.courtOrderValid) {
        docId = 'court-order-component'
      } else if (!localState.certifyInformationValid) {
        docId = 'certify-information'
      }
      if (docId) {
        const component = document.getElementById(docId)
        await component.scrollIntoView({ behavior: 'smooth' })
      }
    }

    const goToReviewAmendment = (): void => {
      router.push({
        name: RouteNames.AMEND_REGISTRATION,
        query: { 'reg-num': localState.registrationNumber + '-confirm' }
      })
      emit('haveData', false)
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
        emit('error', draft.error)
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
        goToDash()
      }
    }

    const submitButton = (): void => {
      if (!localState.validFolio || !localState.certifyInformationValid || localState.registeringOpen) {
        localState.showErrors = true
        scrollToInvalid()
        return
      }
      if ((isRoleStaffReg.value) || (isRoleStaffSbc.value)) {
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
          emit('error', apiResponse?.error)
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
          goToDash()
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

    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        goToDash()
        return
      }

      if (!localState.registrationNumber || !getConfirmDebtorName.value ||
          localState.registrationNumber !== getRegistrationNumber.value) {
        goToDash()
        emit('error', 'Invalid Registration State')
      }
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
  :deep(.v-data-table__wrapper) {
    overflow: visible;
    height: auto;
  }
  :deep(.col-9) {
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
  :deep(.v-data-table > .v-data-table__wrapper > table > tbody > tr > td),
  :deep(.v-data-table > .v-data-table__wrapper > table > tbody > tr > th),
  :deep(.v-data-table > .v-data-table__wrapper > table > thead > tr > td),
  :deep(.v-data-table > .v-data-table__wrapper > table > thead > tr > th)
  {
    padding: 0 8px;
  }
  :deep(.buttons-stacked) {
    display: none;
  }
}

</style>
