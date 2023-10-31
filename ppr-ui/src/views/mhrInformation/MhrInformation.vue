<template>
  <v-container
    class="view-container pa-0"
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
      :close-action="true"
      :set-options="cancelOptions"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />

    <BaseDialog
      :set-options="cancelOwnerChangeConfirm"
      :set-display="showCancelChangeDialog"
      @proceed="handleCancelDialogResp($event)"
    />

    <BaseDialog
      :set-options="transferRequiredDialogOptions"
      :set-display="showStartTransferRequiredDialog"
      reverse-action-buttons
      @proceed="handleStartTransferRequiredDialogResp($event)"
    />

    <div class="view-container px-15 pt-0 pb-5">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row
              id="mhr-information-header"
              no-gutters
              class="pt-3 soft-corners-top"
            >
              <v-col cols="auto">
              <h1>
                {{
                  isReviewMode
                  ? 'Review and Confirm'
                  : `Manufactured Home Information${isDraft ? ' - Draft' : ''}`
                }}
              </h1>
                <template v-if="!isReviewMode">
                  <p class="mt-7">
                    This is the current information for this registration as of
                    <span class="font-weight-bold">{{ asOfDateTime }}</span>.
                  </p>
                  <p
                    v-if="!hasActiveExemption"
                    data-test-id="correct-into-desc"
                  >
                    Ensure ALL of the information below is correct before making any changes to this registration.
                    Necessary fees will be applied as updates are made.
                  </p>

                  <!-- Unit Note Info -->
                  <p v-if="getMhrUnitNotes && getMhrUnitNotes.length >= 1">
                    There are Unit Notes attached to this manufactured home.
                    <span v-if="isRoleStaffReg">
                      <a href="#unit-note-component">See Unit Notes</a>
                    </span>
                    <span v-else>
                      To view Unit Note information on this home, complete a manufactured home search.
                    </span>

                    <!-- Has Alert Message (Notice of Tax Sale, and others) -->
                    <template v-if="hasAlertMsg || hasActiveExemption">
                      <CautionBox
                        class="mt-9"
                        :set-msg="alertMsg"
                        set-alert
                        data-test-id="mhr-alert-msg"
                      >
                        <template #prependSLot>
                          <v-icon
                            color="error"
                            class="alert-icon mt-1 mr-2"
                          >
                            mdi-alert
                          </v-icon>
                        </template>
                      </CautionBox>
                    </template>
                  </p>

                  <!-- Has Caution Message -->
                  <template v-if="getMhrInformation.hasCaution">
                    <CautionBox
                      class="mt-9"
                      :set-msg="cautionMsg"
                    />
                    <v-divider class="mx-0 mt-11" />
                  </template>
                </template>
                <p
                  v-else
                  class="mt-7"
                >
                  Review your changes and complete the additional information before registering.
                </p>
              </v-col>
            </v-row>

            <!-- Lien Information -->
            <v-row
              v-if="hasLien"
              id="lien-information"
              no-gutters
            >
              <v-card
                id="important-message"
                variant="outlined"
                class="rounded-0 mt-2 pt-5 px-5"
              >
                <v-icon
                  color="error"
                  class="float-left mr-2 mt-n1"
                >
                  mdi-alert
                </v-icon>
                <p class="d-block pl-8">
                  <strong>Important:</strong> There is a lien against this manufactured home preventing transfer. This
                  registration cannot be transferred until all liens filed in the Personal Property Registry (PPR)
                  against the manufactured home have been discharged or a written consent from each secured party named
                  in such lien(s) is provided. You can view liens against the manufactured home in the PPR by conducting
                  a combined Manufactured Home Registry and PPR search.
                </p>
              </v-card>

              <v-col class="mt-3">
                <v-btn
                  variant="outlined"
                  color="primary"
                  class="mt-2 px-6"
                  :ripple="false"
                  data-test-id="lien-search-btn"
                  @click="quickMhrSearch(getMhrInformation.mhrNumber)"
                >
                  <v-icon class="pr-1">
                    mdi-magnify
                  </v-icon>
                  Conduct a Combined MHR and PPR Search for MHR Number
                  <strong>{{ getMhrInformation.mhrNumber }}</strong>
                </v-btn>
                <v-divider class="mx-0 mt-10 mb-6" />
              </v-col>
            </v-row>

            <CautionBox
              v-if="isReviewMode && !isTransferToExecutorProbateWill && !isTransferDueToSaleOrGift"
              class="mt-3 mb-5"
              set-msg="This information must match the information on the bill of sale."
            />

            <!-- Mhr Information Body -->
            <section
              v-if="dataLoaded"
              class="py-4"
            >
              <!-- MHR Information Review Section -->
              <template v-if="isReviewMode">
                <!-- Review Header -->
                <header class="review-header mt-1 rounded-top">
                  <v-icon
                    class="ml-2"
                    color="darkBlue"
                  >
                    mdi-file-document-multiple
                  </v-icon>
                  <label class="font-weight-bold pl-2">Ownership Transfer or Change</label>
                </header>

                <section id="owners-review">
                  <HomeOwners
                    is-mhr-transfer
                    is-readonly-table
                    :current-home-owners="getMhrTransferCurrentHomeOwnerGroups"
                  />
                </section>

                <section>
                  <v-divider class="mx-7 ma-0" />
                  <TransferDetailsReview class="py-6 pt-4 px-8" />
                </section>

                <section
                  v-if="isRoleStaffReg"
                  id="staff-transfer-submitting-party"
                  class="submitting-party"
                >
                  <ContactInformation
                    :contact-info="getMhrTransferSubmittingParty"
                    :section-number="1"
                    :content="submittingPartyChangeContent"
                    :validate="validateSubmittingParty"
                    @setStoreProperty="setMhrTransferSubmittingParty"
                    @isValid="setValidation('isSubmittingPartyValid', $event)"
                  />
                </section>

                <section
                  v-else
                  id="transfer-submitting-party"
                  class="submitting-party"
                >
                  <AccountInfo
                    title="Submitting Party for this Change"
                    tooltip-content="The default Submitting Party is based on your BC Registries
                       user account information. This information can be updated within your account settings."
                    :account-info="accountInfo"
                  />
                </section>

                <section
                  id="transfer-ref-num-section"
                  class="mt-10 py-4"
                >
                  <Attention
                    v-if="isRoleStaffReg"
                    section-id="transfer-ref-num-section"
                    :initial-value="getMhrTransferAttentionReference"
                    :section-number="2"
                    :validate="!getInfoValidation('isRefNumValid')"
                    data-test-id="attn-ref-number-card"
                    @isAttentionValid="setValidation('isRefNumValid', $event)"
                    @setStoreProperty="setMhrTransferAttentionReference"
                  />
                  <FolioOrReferenceNumber
                    v-else
                    section-id="transfer-ref-num-section"
                    :initial-value="getMhrTransferAttentionReference"
                    :section-number="1"
                    :validate="!getInfoValidation('isRefNumValid')"
                    data-test-id="attn-ref-number-card"
                    @isFolioOrRefNumValid="setValidation('isRefNumValid', $event)"
                    @setStoreProperty="setMhrTransferAttentionReference"
                  />
                </section>

                <section
                  id="transfer-confirm-section"
                  class="mt-10 transfer-confirm"
                >
                  <ConfirmCompletion
                    :section-number="isRoleStaffReg ? 3 : 2"
                    :legal-name="getCertifyInformation.legalName"
                    :set-show-errors="validateConfirmCompletion"
                    @confirmCompletion="setValidation('isCompletionConfirmed', $event)"
                  />
                </section>

                <section
                  id="transfer-certify-section"
                  class="mt-10 pt-4"
                >
                  <CertifyInformation
                    :section-number="isRoleStaffReg ? 4 : 3"
                    :set-show-errors="validateAuthorizationError"
                    @certifyValid="setValidation('isAuthorizationValid', $event)"
                  />
                </section>

                <section
                  v-if="isRoleStaffReg"
                  id="staff-transfer-payment-section"
                  class="mt-10 pt-4 pb-10"
                >
                  <h2>
                    5. Staff Payment
                  </h2>
                  <v-card
                    flat
                    class="mt-6 pa-6"
                    :class="{ 'border-error-left': validateStaffPayment }"
                  >
                    <StaffPayment
                      id="staff-payment"
                      :display-side-label="true"
                      :display-priority-checkbox="true"
                      :staff-payment-data="staffPayment"
                      :invalid-section="validateStaffPayment"
                      :validate="validate"
                      @update:staff-payment-data="onStaffPaymentDataUpdate($event)"
                      @valid="setValidation('isStaffPaymentValid', $event)"
                    />
                  </v-card>
                </section>
              </template>

              <!-- MHR Information Section -->
              <template v-else>
                <!-- Home Details Information -->
                <div class="mt-n2">
                  <YourHomeReview is-transfer-review />
                </div>

                <!-- Home Location Information -->
                <div class="pt-4">
                  <HomeLocationReview is-transfer-review />
                </div>

                <!-- Home Owners Header -->
                <header
                  id="home-owners-header"
                  class="review-header mt-10 rounded-top"
                >
                  <v-row
                    no-gutters
                    align="center"
                  >
                    <v-col cols="9">
                      <img
                        class="home-owners-icon mb-1 ml-1"
                        src="@/assets/svgs/homeownersicon_reviewscreen.svg"
                      >
                      <span class="font-weight-bold pl-2">Home Owners</span>
                    </v-col>
                    <v-col
                      v-if="enableHomeOwnerChanges && !hasActiveExemption"
                      cols="3"
                      class="text-right"
                    >
                      <v-btn
                        id="home-owners-change-btn"
                        variant="text"
                        class="pl-1"
                        color="primary"
                        :ripple="false"
                        :disabled="isFrozenMhr && !isRoleStaffReg"
                        @click="toggleTypeSelector()"
                      >
                        <span v-if="!showTransferType">
                          <v-icon
                            color="primary"
                            size="small"
                          >mdi-pencil</v-icon> Change
                        </span>
                        <span v-else>
                          <v-icon
                            color="primary"
                            size="small"
                          >mdi-close</v-icon> Cancel Owner Change
                        </span>
                      </v-btn>
                    </v-col>
                  </v-row>
                </header>

                <!-- Transfer Type Component -->
                <v-expand-transition>
                  <div v-if="showTransferType">
                    <p class="gray7 my-8">
                      To change the ownership of this home, first select the Transfer Type
                      and enter the Declared Value of Home.
                    </p>
                    <DocumentId
                      v-if="isRoleStaff"
                      :document-id="getMhrTransferDocumentId || ''"
                      :content="{
                        sideLabel: 'Document ID',
                        hintText: 'Enter the 8-digit Document ID number'
                      }"
                      :validate="validate"
                      @setStoreProperty="handleDocumentIdUpdate($event)"
                      @isValid="setValidation('isDocumentIdValid', $event)"
                    />
                    <TransferType
                      :validate="validate"
                      :disable-select="isFrozenMhrDueToAffidavit && !isRoleStaffReg"
                      @emitType="handleTransferTypeChange($event)"
                      @emitDeclaredValue="handleDeclaredValueChange($event)"
                      @emitValid="setValidation('isValidTransferType', $event)"
                    />
                  </div>
                </v-expand-transition>

                <HomeOwners
                  ref="homeOwnersComponentRef"
                  is-mhr-transfer
                  class="mt-10"
                  :class="{ 'mb-10': !hasUnsavedChanges }"
                  :validate-transfer="validate"
                  @isValidTransferOwners="setValidation('isValidTransferOwners', $event)"
                />

                <TransferDetails
                  v-if="hasUnsavedChanges"
                  ref="transferDetailsComponent"
                  :disable-prefill="isFrozenMhrDueToAffidavit"
                  :validate="!isTransferDueToDeath && validate"
                  @isValid="setValidation('isTransferDetailsValid', $event)"
                />

                <UnitNotePanels
                  v-if="isRoleStaffReg"
                  id="unit-note-component"
                  :unit-notes="getMhrUnitNotes"
                  :disabled="!enableHomeOwnerChanges || showTransferType"
                  :has-active-exemption="hasActiveExemption"
                />

                <v-spacer class="py-10 my-10" />
              </template>
            </section>
          </v-col>
          <v-col
            v-if="showTransferType || isReviewMode"
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :set-show-buttons="true"
                :set-back-btn="showBackBtn"
                :set-cancel-btn="'Cancel'"
                :set-save-btn="'Save and Resume Later'"
                :set-submit-btn="reviewConfirmText"
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-err-msg="transferErrorMsg"
                :transfer-type="getUiTransferType()"
                data-test-id="fee-summary"
                @cancel="goToDashboard()"
                @back="isReviewMode = false"
                @save="onSave()"
                @submit="goToReview()"
              />
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, computed, defineComponent, nextTick, onMounted, reactive, ref, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import {
  StaffPayment,
  Attention,
  CautionBox,
  CertifyInformation,
  FolioOrReferenceNumber,
  ContactInformation,
  StickyContainer,
  DocumentId
} from '@/components/common'
import {
  StaffPaymentOptions,
  APIMHRMapSearchTypes,
  APISearchTypes,
  ApiTransferTypes,
  MhApiStatusTypes,
  RouteNames,
  UIMHRSearchTypes
} from '@/enums'
import {
  useAuth,
  useExemptions,
  useHomeOwners,
  useInputRules,
  useMhrInformation,
  useMhrInfoValidation,
  useNavigation,
  useTransferOwners
} from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { ConfirmCompletion, TransferDetails, TransferDetailsReview, TransferType } from '@/components/mhrTransfers'
import { HomeLocationReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { HomeOwners } from '@/views'
import { UnitNotePanels } from '@/components/unitNotes'
import { BaseDialog } from '@/components/dialogs'
import { QSLockedStateUnitNoteTypes, submittingPartyChangeContent, UnitNotesInfo } from '@/resources'
import { cancelOwnerChangeConfirm, transferRequiredDialog, unsavedChangesDialog } from '@/resources/dialogOptions'
import AccountInfo from '@/components/common/AccountInfo.vue'
/* eslint-disable no-unused-vars */
import {
  AccountInfoIF,
  DialogOptionsIF,
  ErrorIF,
  MhrTransferApiIF,
  RegTableNewItemI,
  TransferTypeSelectIF
} from '@/interfaces'
import { StaffPaymentIF } from '@/interfaces'
import {
  createMhrDraft,
  getAccountInfoFromAuth,
  getFeatureFlag,
  getMhrDraft,
  getMHRegistrationSummary,
  mhrSearch,
  pacificDate,
  submitMhrTransfer,
  updateMhrDraft
} from '@/utils'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'MhrInformation',
  components: {
    Attention,
    BaseDialog,
    CautionBox,
    FolioOrReferenceNumber,
    HomeOwners,
    ContactInformation,
    DocumentId,
    TransferType,
    TransferDetails,
    TransferDetailsReview,
    HomeLocationReview,
    StickyContainer,
    CertifyInformation,
    AccountInfo,
    ConfirmCompletion,
    YourHomeReview,
    StaffPayment,
    UnitNotePanels
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    saveDraftExit: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const router = useRouter()
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setMhrStatusType,
      setMhrTransferSubmittingParty,
      setMhrTransferAttentionReference,
      setUnsavedChanges,
      setRegTableNewItem,
      setSearchedType,
      setManufacturedHomeSearchResults,
      setLienType,
      setMhrTransferDocumentId,
      setMhrTransferType,
      setMhrTransferDeclaredValue,
      setEmptyMhrTransfer,
      setStaffPayment
    } = useStore()
    const {
      // Getters
      isRoleStaff,
      getMhrUnitNotes,
      getMhrTransferHomeOwners, // used in tests, would need to refactor to remove it
      getMhrInformation,
      getMhrTransferCurrentHomeOwnerGroups,
      getCertifyInformation,
      hasUnsavedChanges,
      hasLien,
      isRoleStaffReg,
      isRoleQualifiedSupplier,
      getMhrTransferDocumentId,
      getMhrTransferType,
      getMhrTransferDeclaredValue,
      getMhrInfoValidation,
      getMhrTransferAttentionReference,
      getMhrTransferSubmittingParty
    } = storeToRefs(useStore())
    const {
      isFrozenMhr,
      isFrozenMhrDueToAffidavit,
      buildApiData,
      initMhrTransfer,
      getUiTransferType,
      parseMhrInformation,
      initDraftMhrInformation,
      parseSubmittingPartyInfo
    } = useMhrInformation()
    const {
      setValidation,
      getInfoValidation,
      isValidTransfer,
      isValidTransferReview,
      scrollToFirstError,
      resetValidationState
    } = useMhrInfoValidation(getMhrInfoValidation.value)
    const {
      setGlobalEditingMode
    } = useHomeOwners(true)
    const { maxLength } = useInputRules()
    const {
      isTransferDueToDeath,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will
    } = useTransferOwners()

    const { getActiveExemption } = useExemptions()

    // Refs
    const homeOwnersComponentRef = ref(null) as Component
    const transferDetailsComponent = ref(null) as Component

    const localState = reactive({
      dataLoaded: false,
      loading: false,
      isReviewMode: false,
      validate: false,
      refNumValid: false,
      accountInfo: null,
      feeType: FeeSummaryTypes.MHR_TRANSFER, // FUTURE STATE: To be dynamic, dependent on what changes have been made
      staffPayment: {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      },
      showTransferType: !!getMhrInformation.value.draftNumber || isFrozenMhrDueToAffidavit.value || false,
      cancelOptions: unsavedChangesDialog,
      showCancelDialog: false,
      showCancelChangeDialog: false,
      showStartTransferRequiredDialog: false,
      hasActiveExemption: computed((): boolean => !!getActiveExemption()),
      transferRequiredDialogOptions: computed((): DialogOptionsIF => {
        transferRequiredDialog.text =
          transferRequiredDialog.text.replace('mhr_number', getMhrInformation.value.mhrNumber)
        return transferRequiredDialog
      }),
      hasTransferChanges: computed((): boolean => {
        return (
          localState.showTransferType &&
          (hasUnsavedChanges.value ||
            !!getMhrTransferDeclaredValue.value ||
            !!getMhrTransferType.value ||
            !!getMhrTransferDocumentId.value)
        )
      }),
      asOfDateTime: computed((): string => {
        return `${pacificDate(new Date())}`
      }),
      showBackBtn: computed((): string => {
        return localState.isReviewMode ? 'Back' : ''
      }),
      validateSubmittingParty: computed((): boolean => {
        return localState.validate && !getInfoValidation('isSubmittingPartyValid')
      }),
      validateConfirmCompletion: computed((): boolean => {
        return localState.validate && !getInfoValidation('isCompletionConfirmed')
      }),
      validateAuthorizationError: computed((): boolean => {
        return localState.validate && !getInfoValidation('isAuthorizationValid')
      }),
      validateStaffPayment: computed((): boolean => {
        return isRoleStaffReg.value && localState.validate && !getInfoValidation('isStaffPaymentValid')
      }),
      transferErrorMsg: computed((): string => {
        if (localState.validate && hasLien.value) return '< Lien on this home is preventing transfer'

        const isValidReview = localState.isReviewMode ? isValidTransferReview.value : isValidTransfer.value
        return localState.validate && !isValidReview ? '< Please complete required information' : ''
      }),
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      enableHomeOwnerChanges: computed((): boolean => {
        return getFeatureFlag('mhr-transfer-enabled')
      }),
      isDraft: computed((): boolean => {
        return getMhrInformation.value.draftNumber
      }),
      /** True if Jest is running the code. */
      isJestRunning: computed((): boolean => {
        return import.meta.env.JEST_WORKER_ID !== undefined
      }),
      hasAlertMsg: false,
      alertMsg: computed((): string => {
        // msg when MHR has a Residential Exemption
        if (localState.hasActiveExemption) {
          return isRoleStaffReg.value
            ? `This manufactured home is exempt as of ${pacificDate(getActiveExemption().createDateTime)} and changes can no longer be made to this home unless it is restored. See Unit Notes for further information.` // eslint-disable-line max-len
            : `This manufactured home has been exempt as of ${pacificDate(getActiveExemption().createDateTime)} and changes can no longer be made to this home unless it is restored.  If you require further information please contact BC Registries staff. ` // eslint-disable-line max-len
        }
        // not all MHR Info will have the frozenDocumentType
        if (!getMhrInformation.value?.frozenDocumentType && !localState.hasAlertMsg) return
        // display alert message based o the locker document type
        const unitNoteType = UnitNotesInfo[getMhrInformation.value?.frozenDocumentType]?.header
        return isRoleStaffReg.value
          ? `A ${unitNoteType} has been filed against this home. This will prevent qualified suppliers from making any changes to this home. See Unit Notes for further details.` // eslint-disable-line max-len
          : `A ${unitNoteType} has been filed against this home and you will be unable to make any changes. If you require further information please contact BC Registries staff.` // eslint-disable-line max-len
      }),
      cautionMsg: computed((): string => {
        const baseMsg = 'A Caution has been filed against this home.'

        return isRoleStaffReg.value
          ? `${baseMsg} See Unit Notes for further details.`
          : `${baseMsg} If you require further information please contact BC Registries staff.`
      })
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value) {
        goToDashboard()
        return
      }
      // page is ready to view
      context.emit('emitHaveData', true)

      localState.loading = true
      setEmptyMhrTransfer(initMhrTransfer())

      // Set baseline MHR Information to state
      await parseMhrInformation(isFrozenMhr.value)

      if (getMhrInformation.value.draftNumber) {
        // Retrieve draft if it exists
        const { registration } = await getMhrDraft(getMhrInformation.value.draftNumber)
        await initDraftMhrInformation(registration as MhrTransferApiIF)
      } else if (isFrozenMhrDueToAffidavit.value) {
        setMhrTransferType({ transferType: ApiTransferTypes.SALE_OR_GIFT })
        await scrollToFirstError(false, 'home-owners-header')
      } else {
        // When not a draft Transfer, force no unsaved changes after loading current owners
        await setUnsavedChanges(false)
      }

      if (isRoleQualifiedSupplier.value && !isRoleStaffReg.value) {
        // Get Account Info from Auth to be used in Submitting Party section in Review screen
        localState.accountInfo = await getAccountInfoFromAuth() as AccountInfoIF
        parseSubmittingPartyInfo(localState.accountInfo)
      }

      localState.hasAlertMsg = QSLockedStateUnitNoteTypes.includes(getMhrInformation.value.frozenDocumentType)
      localState.loading = false
      localState.dataLoaded = true
    })

    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    const onStaffPaymentDataUpdate = (val: StaffPaymentIF) => {
      let staffPaymentData: StaffPaymentIF = {
        ...val
      }

      switch (staffPaymentData.option) {
        case StaffPaymentOptions.FAS:
          staffPaymentData = {
            option: StaffPaymentOptions.FAS,
            routingSlipNumber: staffPaymentData.routingSlipNumber,
            isPriority: staffPaymentData.isPriority,
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: ''
          }
          break

        case StaffPaymentOptions.BCOL:
          staffPaymentData = {
            option: StaffPaymentOptions.BCOL,
            bcolAccountNumber: staffPaymentData.bcolAccountNumber,
            datNumber: staffPaymentData.datNumber,
            folioNumber: staffPaymentData.folioNumber,
            isPriority: staffPaymentData.isPriority,
            routingSlipNumber: ''
          }
          break

        case StaffPaymentOptions.NO_FEE:
          staffPaymentData = {
            option: StaffPaymentOptions.NO_FEE,
            routingSlipNumber: '',
            isPriority: false,
            bcolAccountNumber: '',
            datNumber: '',
            folioNumber: ''
          }
          break
        case StaffPaymentOptions.NONE: // should never happen
          break
      }

      localState.staffPayment = staffPaymentData
      setStaffPayment(staffPaymentData)
    }

    const goToReview = async (): Promise<void> => {
      localState.validate = true
      await nextTick()

      // Prevent proceeding when Lien present
      if (hasLien.value) {
        await scrollToFirstError(true)
        return
      }

      // If already in review mode, file the transfer
      if (localState.isReviewMode) {
        // Verify no lien exists prior to submitting filing
        const regSum = !localState.isJestRunning
          ? await getMHRegistrationSummary(getMhrInformation.value.mhrNumber, false)
          : null
        if (!!regSum && !!regSum.lienRegistrationType) {
          await setLienType(regSum.lienRegistrationType)
          await scrollToFirstError(true)
          return
        }

        // Check if any required fields have errors
        if (localState.isReviewMode && !isValidTransferReview.value) {
          await scrollToFirstError(false)
          return
        }

        // Complete Filing
        localState.loading = true
        // Build filing to api specs
        const apiData: MhrTransferApiIF = await buildApiData()
        // Submit Transfer filing
        const mhrTransferFiling =
          await submitMhrTransfer(apiData, getMhrInformation.value.mhrNumber, localState.staffPayment)

        if (!mhrTransferFiling.error) {
          // Set new filing to Reg Table
          // Normal flow when not Affidavit Transfer
          setUnsavedChanges(false)
          const newItem: RegTableNewItemI = {
            addedReg: mhrTransferFiling.documentId,
            addedRegParent: getMhrInformation.value.mhrNumber,
            addedRegSummary: null,
            prevDraft: mhrTransferFiling.documentId || ''
          }
          setRegTableNewItem(newItem)

          // Affidavit Transfer has a different flow
          if (isTransferToExecutorUnder25Will.value) {
            localState.validate = false
            localState.staffPayment.option = StaffPaymentOptions.NONE

            // Set Frozen state manually as the base reg isn't re-fetched in this flow
            await setMhrStatusType(MhApiStatusTypes.FROZEN)
            await setMhrTransferType({ transferType: ApiTransferTypes.SALE_OR_GIFT })
            // Set baseline MHR Information to state
            await parseMhrInformation(isFrozenMhr.value)

            // reset Document Id (Staff has this extra field which needs to be reset after Affidavit flow)
            await setMhrTransferDocumentId('')

            localState.isReviewMode = false
            localState.showStartTransferRequiredDialog = true
          } else goToDashboard()
        } else emitError(mhrTransferFiling?.error)
        localState.loading = false
      }

      // If transfer is valid, enter review mode
      // For Affidavit Transfers, need to complete affidavit before proceeding
      if (isValidTransfer.value) {
        localState.isReviewMode = true
        localState.validate = false
      }

      // Force show removed/deceased homeOwners when invalid
      if (!getInfoValidation('isValidTransferOwners')) {
        (homeOwnersComponentRef as any).value?.hideShowRemovedOwners(true)
      }

      await nextTick()
      // Scroll to the top of review screen
      await scrollToFirstError(isValidTransfer.value)
    }

    const onSave = async (): Promise<void> => {
      localState.loading = true
      const apiData = await buildApiData(true)

      const mhrTransferDraft = getMhrInformation.value.draftNumber
        ? await updateMhrDraft(getMhrInformation.value.draftNumber, getMhrTransferType.value?.transferType, apiData)
        : await createMhrDraft(getMhrTransferType.value?.transferType, apiData)

      const newItem: RegTableNewItemI = {
        addedReg: mhrTransferDraft.draftNumber,
        addedRegParent: apiData.mhrNumber,
        addedRegSummary: null,
        prevDraft: (getMhrInformation.value.changes && getMhrInformation.value.changes[0].documentId) || ''
      }
      setRegTableNewItem(newItem)

      localState.loading = false
      if (!mhrTransferDraft.error) {
        setUnsavedChanges(false)
        goToDashboard()
      } else {
        emitError(mhrTransferDraft?.error)
      }
    }

    const goToDashboard = (): void => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else {
        setUnsavedChanges(false)
        setGlobalEditingMode(false)
        setEmptyMhrTransfer(initMhrTransfer())
        resetValidationState()

        goToDash()
      }
    }

    const handleDialogResp = (val: boolean): void => {
      if (!val) {
        setUnsavedChanges(false)
        if (localState.showCancelDialog) {
          goToDashboard()
        }
      }
      localState.showCancelDialog = false
    }

    const handleCancelDialogResp = async (val: boolean): Promise<void> => {
      if (!val) {
        localState.showCancelChangeDialog = false
        return
      }
      localState.showCancelChangeDialog = false
      localState.showTransferType = false
      localState.loading = true
      await resetMhrInformation()
      localState.loading = false
    }

    // For Transfer Sale or Gift after Affidavit is completed
    const handleStartTransferRequiredDialogResp = async (proceed: boolean): Promise<void> => {
      if (proceed) {
        // Complete Later button cancels and navigates to dashboard
        setUnsavedChanges(false) // prevent unsaved changes dialog from showing up
        goToDashboard()
      } else {
        // Start Gift/Sale Transfer simply closes the dialog, since the data is already pre-filled
        localState.showStartTransferRequiredDialog = false
        await scrollToFirstError(false, 'home-owners-header')
      }
    }

    const quickMhrSearch = async (mhrNumber: string): Promise<void> => {
      localState.loading = true

      // Search for current Manufactured Home Registration Number
      const results = await mhrSearch({
        type: APISearchTypes.MHR_NUMBER,
        criteria: { value: mhrNumber },
        clientReferenceId: ''
      }, '')

      localState.loading = false
      if (results) {
        // Set search type to satisfy UI requirements
        await setSearchedType({
          searchTypeUI: UIMHRSearchTypes.MHRMHR_NUMBER,
          searchTypeAPI: APIMHRMapSearchTypes.MHRMHR_NUMBER
        })

        // There is only 1 result for a mhr number search
        // Include lien info by default
        results.results[0].includeLienInfo = true

        await setManufacturedHomeSearchResults(results)
        await router.replace({
          name: RouteNames.MHRSEARCH
        })
      } else {
        console.error('Error: MHR_NUMBER expected, but not found.')
      }
    }

    const resetMhrInformation = async (shouldResetDocId = true): Promise<void> => {
      // Set baseline MHR Information to state
      await parseMhrInformation()
      shouldResetDocId && await setMhrTransferDocumentId('')
      await handleTransferTypeChange(null)
      await handleDeclaredValueChange(null)
      localState.validate = false
    }

    const toggleTypeSelector = (): void => {
      // Confirm cancel change when changes have been made to transfer type or homeowners
      if (localState.hasTransferChanges) {
        localState.showCancelChangeDialog = true
        return
      }

      localState.showTransferType = !localState.showTransferType
    }

    const handleDocumentIdUpdate = (documentId: string) => {
      setMhrTransferDocumentId(documentId)
    }

    const handleTransferTypeChange = async (transferTypeSelect: TransferTypeSelectIF): Promise<void> => {
      // Reset state until support is built for other Transfer Types
      if (localState.hasTransferChanges && transferTypeSelect?.transferType &&
        (transferTypeSelect?.transferType !== getMhrTransferType.value?.transferType)
      ) await resetMhrInformation(false)

      await setMhrTransferType(transferTypeSelect)
    }

    const handleDeclaredValueChange = async (declaredValue: number): Promise<void> => {
      await setMhrTransferDeclaredValue(declaredValue)
    }

    watch(() => isValidTransfer.value, (val: boolean) => {
      if (val) localState.validate = false
    })

    watch(() => hasUnsavedChanges.value, (val: boolean) => {
      if (!val && transferDetailsComponent) {
        (transferDetailsComponent as any).value?.clearTransferDetailsData()
      }
    })

    watch(() => props.saveDraftExit, () => {
      // on change (T/F doesn't matter), save and go back to dash
      onSave()
    })

    watch(() => getMhrInformation.value.frozenDocumentType,
      val => {
        localState.hasAlertMsg = QSLockedStateUnitNoteTypes.includes(val)
      })

    return {
      isRoleStaff,
      isFrozenMhr,
      isFrozenMhrDueToAffidavit,
      emitError,
      setValidation,
      getInfoValidation,
      hasUnsavedChanges,
      goToReview,
      onSave,
      goToDashboard,
      getMhrTransferAttentionReference,
      getMhrTransferHomeOwners,
      getMhrTransferCurrentHomeOwnerGroups,
      getCertifyInformation,
      maxLength,
      homeOwnersComponentRef,
      transferDetailsComponent,
      getMhrInformation,
      quickMhrSearch,
      handleDialogResp,
      hasLien,
      isRoleStaffReg,
      isTransferDueToDeath,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      setMhrTransferAttentionReference,
      setMhrTransferSubmittingParty,
      handleDocumentIdUpdate,
      handleTransferTypeChange,
      getMhrTransferDocumentId,
      getUiTransferType,
      handleDeclaredValueChange,
      toggleTypeSelector,
      onStaffPaymentDataUpdate,
      handleCancelDialogResp,
      handleStartTransferRequiredDialogResp,
      cancelOwnerChangeConfirm,
      transferRequiredDialog,
      getMhrUnitNotes,
      getMhrTransferSubmittingParty,
      submittingPartyChangeContent,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.sticky-container {
  z-index: 4 !important;
}
.section {
  scroll-margin: 40px;
}

#important-message {
  background-color: $backgroundError !important;
  border-color: $error;

  p {
    line-height: 22px;
    font-size: $px-14;
    letter-spacing: 0.01rem;
    color: $gray7;
  }
}

.submitting-party {
  margin-top: 55px;
}

.alert-icon {
  font-size: 20px !important;
}

:deep() {
  #home-owners-change-btn {
    height: 24px;
    color: $primary-blue !important;
  }
  .theme--light.v-btn.v-btn--disabled {
    opacity: 0.4 !important;
  }
  .home-owners-icon {
    vertical-align: middle;
  }
}
</style>
