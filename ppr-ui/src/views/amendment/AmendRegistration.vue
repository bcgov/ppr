<template>
  <v-container
    class="view-container pa-15 pt-14"
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
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Amendment</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              This is the current information for this registration as of
              <b>{{ asOfDateTime }}.</b><br /><br />
              To view the full history of this registration including descriptions of any amendments and
              any court orders, you will need to conduct a separate search.
              <span v-if="registrationType === registrationTypeRL">
                <br /><br />The only amendment allowed for a Repairer's Lien is the removal
                of some (but not all) of the vehicle collateral.
              </span>
            </p>
          </div>
          <caution-box class="mt-9" :setMsg="cautionTxt" :setImportantWord="'Note'" />
          <registration-length-trust-amendment
            v-if="registrationType !== registrationTypeRL"
            :setShowErrorBar="errorBar"
            @lengthTrustOpen="lengthTrustOpen = $event"
            class="mt-15"
          />
          <registration-length-trust-summary class="mt-15" v-else />
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
          <secured-parties
            v-if="registrationType !== registrationTypeRL"
            @setSecuredPartiesValid="setValidSecuredParties($event)"
            @securedPartyOpen="securedPartyOpen = $event"
            :setShowInvalid="showInvalid" class="pt-4"
            :setShowErrorBar="errorBar"
          />
          <div v-if="!securedPartiesValid">
          <span v-if="isCrownError()" class="invalid-message">
            Your registration can only include one secured party
          </span>
          <span v-else class="invalid-message">
            Your registration must include at least one Secured Party
          </span>
          </div>
          <secured-party-summary
            v-if="registrationType === registrationTypeRL"
            class="secured-party-summary"
            :setEnableNoDataAction="false"
          />
          <h3 class="pt-6">Debtors</h3>
          <debtors
            v-if="registrationType !== registrationTypeRL"
            @setDebtorValid="setValidDebtor($event)"
            @debtorOpen="debtorOpen = $event"
            :setShowInvalid="showInvalid"
            :setShowErrorBar="errorBar"
          />
          <div class="pt-4" v-if="!debtorValid">
          <span class="invalid-message">
            Your registration must include at least one Debtor
          </span>
          </div>
          <debtor-summary
            v-if="registrationType === registrationTypeRL"
            class="debtor-summary"
            :setEnableNoDataAction="false"
          />
          <collateral
            @setCollateralValid="setValidCollateral($event)"
            @collateralOpen="collateralOpen = $event"
            :setShowErrorBar="errorBar"
            class="mt-15"
          />
          <div class="pt-4" v-if="!collateralValid">
          <span class="invalid-message">
            Your registration must include at least one form of Collateral
          </span>
          </div>
          <amendment-description class="mt-12"
            @valid="detailsValid = $event"
            :setShowErrors="showInvalid"
          />
          <court-order class="mt-8"
            :setShowErrors="showCourtInvalid"
            :setRequireCourtOrder="requireCourtOrder"
            @setCourtOrderValid="setCourtOrderValid($event)"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
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
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { cloneDeep, isEqual } from 'lodash'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { CautionBox, StickyContainer, CourtOrder } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { Debtors } from '@/components/parties/debtor'
import { SecuredParties } from '@/components/parties/party'
import {
  AmendmentDescription,
  RegistrationLengthTrustAmendment,
  RegistrationLengthTrustSummary
} from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { RegisteringPartySummary, SecuredPartySummary, DebtorSummary } from '@/components/parties/summaries'
import { AllRegistrationTypes } from '@/resources'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import {
  getFeatureFlag,
  getFinancingStatement,
  isSecuredPartyRestrictedList,
  pacificDate,
  saveAmendmentStatementDraft,
  setupAmendmentStatementFromDraft
} from '@/utils'
/* eslint-disable no-unused-vars */
import {
  APIRegistrationTypes,
  RouteNames,
  UIRegistrationTypes,
  RegistrationFlowType,
  ActionTypes
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Throttle } from '@/decorators'
import {
  ErrorIF,
  AddPartiesIF,
  CertifyIF,
  AddCollateralIF,
  LengthTrustIF,
  StateModelIF,
  CourtOrderIF,
  DialogOptionsIF,
  FinancingStatementIF,
  RegTableNewItemI
} from '@/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'AmendRegistration',
  components: {
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
      getAddCollateral,
      hasUnsavedChanges,
      getRegistrationType,
      getConfirmDebtorName,
      getOriginalLengthTrust,
      getOriginalAddCollateral,
      getAmendmentDescription,
      getCourtOrderInformation,
      getAddSecuredPartiesAndDebtors,
      getOriginalAddSecuredPartiesAndDebtors
    } = useGetters<any>([
      'getStateModel',
      'getLengthTrust',
      'getAddCollateral',
      'hasUnsavedChanges',
      'getRegistrationType',
      'getConfirmDebtorName',
      'getOriginalAddCollateral',
      'getOriginalLengthTrust',
      'getOriginalAddCollateral',
      'getAmendmentDescription',
      'getCourtOrderInformation',
      'getAddSecuredPartiesAndDebtors',
      'getOriginalAddSecuredPartiesAndDebtors'
    ])
    const {
      setAddCollateral,
      setStaffPayment,
      setLengthTrust,
      setOriginalAddCollateral,
      setRegistrationNumber,
      setRegistrationType,
      setRegistrationFlowType,
      setCertifyInformation,
      setCollateralShowInvalid,
      setRegTableNewItem,
      setUnsavedChanges,
      setAmendmentDescription,
      setCourtOrderInformation,
      setFolioOrReferenceNumber,
      setOriginalLengthTrust,
      setRegistrationCreationDate,
      setRegistrationExpiryDate,
      setAddSecuredPartiesAndDebtors,
      setOriginalAddSecuredPartiesAndDebtors
    } = useActions<any>([
      'setAddCollateral',
      'setStaffPayment',
      'setLengthTrust',
      'setOriginalAddCollateral',
      'setRegistrationNumber',
      'setRegistrationType',
      'setRegistrationFlowType',
      'setCertifyInformation',
      'setCollateralShowInvalid',
      'setRegTableNewItem',
      'setUnsavedChanges',
      'setAmendmentDescription',
      'setCourtOrderInformation',
      'setFolioOrReferenceNumber',
      'setOriginalLengthTrust',
      'setRegistrationCreationDate',
      'setRegistrationExpiryDate',
      'setAddSecuredPartiesAndDebtors',
      'setOriginalAddSecuredPartiesAndDebtors'
    ])

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
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      registrationNumber: computed((): string => {
        let regNum = context.root.$route.query['reg-num'] as string
        if (regNum && regNum.endsWith('-confirm')) {
          localState.fromConfirmation = true
          regNum = regNum.replace('-confirm', '')
        }
        return regNum || ''
      }),
      documentId: computed((): string => {
        return (context.root.$route.query['document-id'] as string) || ''
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
      else goToDashboard()
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDashboard()
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

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || (!getConfirmDebtorName.value && !localState.documentId)) {
        if (!localState.registrationNumber) {
          console.error('No registration number given to amend. Redirecting to dashboard...')
        } else {
          console.error('No debtor name confirmed for this amendment. Redirecting to dashboard...')
        }
        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
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
      // load data into the store
      const registrationType = AllRegistrationTypes.find((reg, index) => {
        if (reg.registrationTypeAPI === financingStatement.type) {
          return true
        }
      })
      const collateral = {
        valid: true,
        vehicleCollateral: financingStatement.vehicleCollateral || null,
        generalCollateral: financingStatement.generalCollateral
      } as AddCollateralIF
      const lengthTrust = {
        valid: true,
        trustIndenture: financingStatement.trustIndenture || false,
        lifeInfinite: financingStatement.lifeInfinite || false,
        lifeYears: financingStatement.lifeYears || null,
        surrenderDate: financingStatement.surrenderDate || null,
        lienAmount: financingStatement.lienAmount || null
      } as LengthTrustIF
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
      setRegistrationCreationDate(financingStatement.createDateTime)
      setRegistrationExpiryDate(financingStatement.expiryDate)
      setRegistrationNumber(financingStatement.baseRegistrationNumber)
      setRegistrationType(registrationType)
      setAddCollateral(collateral)
      setLengthTrust(lengthTrust)
      setAddSecuredPartiesAndDebtors(cloneDeep(parties))
      setOriginalAddCollateral(cloneDeep(collateral))
      setOriginalLengthTrust(cloneDeep(lengthTrust))
      setOriginalAddSecuredPartiesAndDebtors(cloneDeep(origParties))
      setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
      // Reset anything left in the store that is amendment registration related.
      setAmendmentDescription('')
      setCourtOrderInformation(courtOrder)
      setFolioOrReferenceNumber('')
      setCertifyInformation(certifyInfo)
      setStaffPayment({
        option: -1,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      })
      if (localState.documentId) {
        const stateModel: StateModelIF =
          await setupAmendmentStatementFromDraft(getStateModel.value, localState.documentId)
        if (stateModel.registration.draft.error) {
          emitError(stateModel.registration.draft.error)
          context.root.$router.push({ name: RouteNames.DASHBOARD })
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
      }
      if (!hasAmendmentChanged() || !localState.debtorValid || !localState.securedPartiesValid) {
        localState.amendErrMsg = '< Please make any required changes'
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
        context.root.$router.push({
          name: RouteNames.CONFIRM_AMENDMENT,
          query: { 'reg-num': localState.registrationNumber }
        })
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

    const goToDashboard = (): void => {
      // unset registration number
      setRegistrationNumber(null)
      context.root.$router.push({ name: RouteNames.DASHBOARD })
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
      const sp = getAddSecuredPartiesAndDebtors.value.securedParties
      let securedPartyCount = 0
      if (isSecuredPartyRestrictedList(localState.registrationType)) {
        for (let i = 0; i < sp.length; i++) {
          // is valid if there is at least one secured party
          if (sp[i].action !== ActionTypes.REMOVED) {
            securedPartyCount++
          }
        }
        if (securedPartyCount > 1) {
          return true
        }
      }
      return false
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
        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
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
      isCrownError,
      handleDialogResp,
      confirmAmendment,
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
.invalid-message {
  font-size: 14px;
}
</style>
