<template>
  <v-container class="pt-14 px-0">
    <v-overlay
      v-model="submitting"
      class="overlay-container"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </v-overlay>
    <BaseDialog
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div
      v-if="dataLoaded && !dataLoadError"
      class="container pa-0"
    >
      <v-row noGutters>
        <v-col cols="9">
          <h1>Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              This is the current information for this registration as of
              <b>{{ asOfDateTime }}.</b><br><br>
              To view the full history of this registration including descriptions of any amendments and
              any court orders, you will need to conduct a separate search.
              <span v-if="registrationType === registrationTypeRL">
                <br><br>The only amendment allowed for a Repairer's Lien is the removal
                of some (but not all) of the vehicle collateral.
              </span>
            </p>
          </div>
          <CautionBox
            class="mt-9"
            :setMsg="cautionTxt"
            :setImportantWord="'Note'"
          />
          <RegistrationLengthTrustAmendment
            v-if="registrationType !== registrationTypeRL"
            :setShowErrorBar="errorBar"
            class="mt-15"
            @lengthTrustOpen="lengthTrustOpen = $event"
          />
          <RegistrationLengthTrustSummary
            v-else
            class="mt-15"
          />

          <SecuritiesActNotices
            v-if="isSecurityActNotice"
            isAmendment
          />

          <header class="summary-header mt-15 rounded-all">
            <v-icon color="darkBlue">
              mdi-account-multiple-plus
            </v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </header>
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
          <SecuredParties
            v-if="registrationType !== registrationTypeRL"
            :setShowInvalid="showInvalid"
            class="pt-4"
            :setShowErrorBar="errorBar"
            @setSecuredPartiesValid="setValidSecuredParties($event)"
            @securedPartyOpen="securedPartyOpen = $event"
          />
          <div v-if="!securedPartiesValid">
            <p
              v-if="isCrownError()"
              class="fs-14 error-text"
            >
              Your registration can only include one secured party
            </p>
            <p
              v-else
              class="fs-14 error-text"
            >
              Your registration must include at least one Secured Party
            </p>
          </div>
          <SecuredPartySummary
            v-if="registrationType === registrationTypeRL"
            class="secured-party-summary"
            :set-enable-no-data-action="false"
          />
          <h3 class="pt-6">
            Debtors
          </h3>
          <Debtors
            v-if="registrationType !== registrationTypeRL"
            :setShowInvalid="showInvalid"
            :setShowErrorBar="errorBar"
            @setDebtorValid="setValidDebtor($event)"
            @debtorOpen="debtorOpen = $event"
          />
          <div
            v-if="!debtorValid"
            class="pt-4"
          >
            <span class="fs-14">
              Your registration must include at least one Debtor
            </span>
          </div>
          <DebtorSummary
            v-if="registrationType === registrationTypeRL"
            class="debtor-summary"
            :set-enable-no-data-action="false"
          />
          <Collateral
            :setShowErrorBar="errorBar"
            class="mt-15"
            @setCollateralValid="setValidCollateral($event)"
            @collateralOpen="collateralOpen = $event"
          />
          <div
            v-if="!collateralValid"
            class="pt-4"
          >
            <span class="fs-14">
              Your registration must include at least one form of Collateral
            </span>
          </div>
          <AmendmentDescription
            class="mt-12"
            :setShowErrors="showInvalid"
            @valid="detailsValid = $event"
          />
          <CourtOrder
            class="mt-8"
            :setShowErrors="showCourtInvalid"
            :setRequireCourtOrder="requireCourtOrder"
            @setCourtOrderValid="setCourtOrderValid($event)"
          />
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <StickyContainer
              :setRightOffset="true"
              :setShowButtons="true"
              :setShowFeeSummary="true"
              :setFeeType="feeType"
              :setRegistrationType="registrationTypeUI"
              :setCancelBtn="'Cancel'"
              :setBackBtn="'Save and Resume Later'"
              :setSubmitBtn="'Review and Complete'"
              :setErrMsg="amendErrMsg"
              @cancel="cancel()"
              @submit="confirmAmendment()"
              @back="saveDraft()"
            />
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { isEqual } from 'lodash'
import { CautionBox, StickyContainer, CourtOrder } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { Debtors } from '@/components/parties/debtor'
import { SecuredParties } from '@/components/parties/party'
import {
  AmendmentDescription,
  RegistrationLengthTrustAmendment,
  RegistrationLengthTrustSummary, SecuritiesActNotices
} from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { RegisteringPartySummary, SecuredPartySummary, DebtorSummary } from '@/components/parties/summaries'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import {
  getFeatureFlag,
  getFinancingStatement,
  pacificDate,
  saveAmendmentStatementDraft,
  setupAmendmentStatementFromDraft
} from '@/utils'
import {
  APIRegistrationTypes,
  RouteNames,
  UIRegistrationTypes,
  RegistrationFlowType,
  ActionTypes
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ErrorIF,
  StateModelIF,
  CourtOrderIF,
  DialogOptionsIF,
  FinancingStatementIF,
  RegTableNewItemI
} from '@/interfaces'
import { useSecuredParty } from '@/composables/parties'
import { useAuth, useNavigation, usePprRegistration } from '@/composables'

export default defineComponent({
  name: 'AmendRegistration',
  components: {
    SecuritiesActNotices,
    AmendmentDescription,
    BaseDialog,
    CautionBox,
    CourtOrder,
    Collateral,
    Debtors,
    RegistrationLengthTrustAmendment,
    RegistrationLengthTrustSummary,
    RegisteringPartySummary,
    SecuredParties,
    SecuredPartySummary,
    DebtorSummary,
    StickyContainer
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
    const { goToDash, goToRoute } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { initPprUpdateFilling, isSecurityActNotice } = usePprRegistration()
    const {
      // Actions
      setAddCollateral,
      setLengthTrust,
      setCollateralShowInvalid,
      setRegTableNewItem,
      setUnsavedChanges,
      setAmendmentDescription,
      setCourtOrderInformation,
      setAddSecuredPartiesAndDebtors
    } = useStore()
    const {
      // Getters
      getStateModel,
      getLengthTrust,
      getAddCollateral,
      hasUnsavedChanges,
      getRegistrationType,
      getConfirmDebtorName,
      getOriginalLengthTrust,
      getOriginalAddCollateral,
      getSecuritiesActNotices,
      getOriginalSecuritiesActNotices,
      getAmendmentDescription,
      getCourtOrderInformation,
      getAddSecuredPartiesAndDebtors,
      getOriginalAddSecuredPartiesAndDebtors
    } = storeToRefs(useStore())

    const { isSecuredPartiesRestricted } = useSecuredParty()

    const localState = reactive({
      cautionTxt: 'The Registry will provide the verification statement to all Secured Parties named in this ' +
        'registration.',
      dataLoaded: false,
      dataLoadError: false,
      feeType: FeeSummaryTypes.AMEND,
      financingStatementDate: null as Date,
      debtorValid: true,
      showInvalid: false,
      showCourtInvalid: false,
      securedPartiesValid: true,
      registrationLengthTrustValid: true,
      collateralValid: true,
      courtOrderValid: true,
      fromConfirmation: false,
      requireCourtOrder: false,
      debtorOpen: false,
      securedPartyOpen: false,
      errorBar: false,
      collateralOpen: false,
      lengthTrustOpen: false,
      detailsValid: false,
      amendErrMsg: '',
      options: unsavedChangesDialog as DialogOptionsIF,
      showCancelDialog: false,
      submitting: false,
      asOfDateTime: computed((): string => {
        // return formatted date
        if (localState.financingStatementDate) {
          return `${pacificDate(localState.financingStatementDate)}`
        }
        return `${pacificDate(new Date())}`
      }),
      registrationNumber: computed((): string => {
        let regNum = route.query['reg-num'] as string
        if (regNum && regNum.endsWith('-confirm')) {
          localState.fromConfirmation = true
          regNum = regNum.replace('-confirm', '')
        }
        return regNum || ''
      }),
      documentId: computed((): string => {
        return (route.query['document-id'] as string) || ''
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || null
      }),
      registrationTypeRL: computed((): string => {
        return APIRegistrationTypes.REPAIRERS_LIEN
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const cancel = (): void => {
      if (hasUnsavedChanges.value) localState.showCancelDialog = true
      else goToDash()
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDash()
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || (!getConfirmDebtorName.value && !localState.documentId)) {
        if (!localState.registrationNumber) {
          console.error('No registration number given to amend. Redirecting to dashboard...')
        } else {
          console.error('No debtor name confirmed for this amendment. Redirecting to dashboard...')
        }
        goToDash()
        return
      }
      // Conditionally load: could be coming back from confirm.
      if (localState.fromConfirmation) {
        return
      }
      localState.financingStatementDate = new Date()
      localState.submitting = true
      const financingStatement = await getFinancingStatement(true, localState.registrationNumber)

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
    }

    const setStore = async (financingStatement: FinancingStatementIF): Promise<void> => {
      initPprUpdateFilling(financingStatement, RegistrationFlowType.AMENDMENT)
      if (localState.documentId) {
        const stateModel: StateModelIF =
          await setupAmendmentStatementFromDraft(getStateModel.value, localState.documentId)
        if (stateModel.registration.draft.error) {
          emitError(stateModel.registration.draft.error)
          goToDash()
        } else {
          setAddCollateral(stateModel.registration.collateral)
          setLengthTrust(stateModel.registration.lengthTrust)
          setAddSecuredPartiesAndDebtors(stateModel.registration.parties)
          if (stateModel.registration.amendmentDescription) {
            setAmendmentDescription(stateModel.registration.amendmentDescription)
          }
          if (stateModel.registration.courtOrderInformation) {
            setCourtOrderInformation(stateModel.registration.courtOrderInformation)
          }
        }
      }
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return

      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) {
        goToDash()
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

    const scrollToInvalid = async (): Promise<void> => {
      if (localState.lengthTrustOpen || !localState.registrationLengthTrustValid) {
        const component = document.getElementById('length-trust-amendment')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
          return
        }
      }
      if (localState.securedPartyOpen || !localState.securedPartiesValid) {
        const component = document.getElementById('secured-parties-component')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
          return
        }
      }

      if (localState.debtorOpen || !localState.debtorValid) {
        const component = document.getElementById('debtors-component')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
          return
        }
      }
      if (localState.collateralOpen || !localState.collateralValid) {
        const component = document.getElementById('collateral-component')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
        }
      }

      if (!localState.courtOrderValid) {
        const component = document.getElementById('court-order')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
        }
      }
    }

    const confirmAmendment = (): void => {
      validateSecuredParties()
      validateDebtors()
      if (localState.collateralOpen || localState.securedPartyOpen || localState.debtorOpen ||
        localState.lengthTrustOpen) {
        localState.amendErrMsg = '< You have unfinished changes'
        localState.showInvalid = true
        localState.errorBar = true
        scrollToInvalid()
        return
      } else localState.errorBar = false
      if (!hasAmendmentChanged() || !localState.debtorValid || !localState.securedPartiesValid) {
        localState.amendErrMsg = '< Please make any required changes'
        localState.errorBar = true
        return
      }
      const description = getAmendmentDescription.value
      if (
        localState.debtorValid &&
        localState.securedPartiesValid &&
        localState.registrationLengthTrustValid &&
        localState.collateralValid &&
        (!description || description.length <= 4000) &&
        localState.courtOrderValid
      ) {
        goToRoute(RouteNames.CONFIRM_AMENDMENT, { 'reg-num': localState.registrationNumber })
        emitHaveData(false)
      } else {
        localState.showInvalid = true
        if (!localState.collateralValid) {
          setCollateralShowInvalid(true)
        }
        if (!localState.courtOrderValid) {
          localState.showCourtInvalid = true
          localState.amendErrMsg = '< You have unfinished changes'
        }
        scrollToInvalid()
      }
    }

    const hasAmendmentChanged = (): boolean => {
      let hasChanged = false

      if (isSecurityActNotice.value) {
        if (!isEqual(getSecuritiesActNotices.value, getOriginalSecuritiesActNotices.value)) {
          hasChanged = true
        }
      }
      if (!isEqual(getAddSecuredPartiesAndDebtors.value.securedParties,
        getOriginalAddSecuredPartiesAndDebtors.value.securedParties)) {
        hasChanged = true
      }
      if (!isEqual(getAddSecuredPartiesAndDebtors.value.debtors,
        getOriginalAddSecuredPartiesAndDebtors.value.debtors)) {
        hasChanged = true
      }
      if (!isEqual(getLengthTrust.value, getOriginalLengthTrust.value)) {
        hasChanged = true
      }
      if (!isEqual(getAddCollateral.value.vehicleCollateral, getOriginalAddCollateral.value.vehicleCollateral)) {
        hasChanged = true
      }
      const gcLength = getAddCollateral.value.generalCollateral?.length
      const originalLength = getOriginalAddCollateral.value.generalCollateral?.length
      if (gcLength !== originalLength) {
        hasChanged = true
      }

      if (getAmendmentDescription.value) {
        hasChanged = true
      }

      const blankCourtOrder: CourtOrderIF = {
        courtName: '',
        courtRegistry: '',
        effectOfOrder: '',
        fileNumber: '',
        orderDate: ''
      }
      if (!isEqual(getCourtOrderInformation.value, blankCourtOrder)) {
        hasChanged = true
      }
      return hasChanged
    }

    const setCourtOrderValid = (valid): void => {
      localState.courtOrderValid = valid
      if (valid) {
        localState.showCourtInvalid = false
        localState.amendErrMsg = ''
      }
    }

    const setValidSecuredParties = (val: boolean) => {
      if (!val) {
        localState.showInvalid = true
        localState.amendErrMsg = '< Please make any required changes'
      } else {
        localState.amendErrMsg = ''
      }
      localState.securedPartiesValid = val
    }

    const setValidDebtor = (val: boolean) => {
      if (!val) {
        localState.showInvalid = true
        localState.amendErrMsg = '< Please make any required changes'
      } else {
        localState.amendErrMsg = ''
      }
      localState.debtorValid = val
    }

    const validateSecuredParties = (): void => {
      if (localState.registrationType === APIRegistrationTypes.SECURITY_AGREEMENT) {
        const sp = getAddSecuredPartiesAndDebtors.value.securedParties
        const securedPartyCount = sp.filter(removed => removed.action !== ActionTypes.REMOVED).length
        setValidSecuredParties(securedPartyCount >= 1)
      }
    }

    const validateDebtors = (): void => {
      if (localState.registrationType === APIRegistrationTypes.SECURITY_AGREEMENT) {
        const sp = getAddSecuredPartiesAndDebtors.value.debtors
        const debtorCount = sp.filter(removed => removed.action !== ActionTypes.REMOVED).length
        setValidDebtor(debtorCount >= 1)
      }
    }

    const isCrownError = (): boolean => {
      if (!isSecuredPartiesRestricted.value) return false
      const securedParties = getAddSecuredPartiesAndDebtors.value.securedParties
      const securedPartyCount = securedParties.filter(party => party.action !== ActionTypes.REMOVED).length
      return securedPartyCount > 1
    }

    const setValidCollateral = (val: boolean) => {
      if (!val) {
        localState.showInvalid = true
        localState.errorBar = true
        const collateral = getAddCollateral.value
        collateral.showInvalid = true
        setAddCollateral(collateral)
        localState.amendErrMsg = '< Please make any required changes'
      } else {
        localState.amendErrMsg = ''
        localState.errorBar = false
      }
      localState.collateralValid = val
    }

    const saveDraft = async (): Promise<void> => {
      localState.submitting = true
      const stateModel: StateModelIF = getStateModel.value
      const draft = await saveAmendmentStatementDraft(stateModel)
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
        goToDash()
        emitHaveData(false)
      }
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    watch(() => [
      localState.securedPartyOpen, localState.debtorOpen, localState.collateralOpen, localState.lengthTrustOpen
    ], (val): void => {
      if (!val) {
        localState.errorBar = false
        localState.amendErrMsg = ''
      }
    })

    watch(() => localState.detailsValid, (isValid: boolean): void => {
      if (isValid) {
        localState.errorBar = false
        localState.amendErrMsg = ''
      }
    })

    return {
      cancel,
      saveDraft,
      setStore,
      isCrownError,
      handleDialogResp,
      confirmAmendment,
      isSecurityActNotice,
      setValidDebtor,
      setCourtOrderValid,
      setValidCollateral,
      setValidSecuredParties,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
