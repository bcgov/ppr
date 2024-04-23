<template>
  <v-container
    class="pa-0 px-0"
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
      :closeAction="true"
      :setOptions="cancelOptions"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp"
    />

    <BaseDialog
      :setOptions="cancelOwnerChangeConfirm"
      :setDisplay="showCancelChangeDialog"
      @proceed="handleCancelDialogResp"
    />

    <BaseDialog
      :closeAction="true"
      :setOptions="incompleteRegistrationDialog"
      :setDisplay="showIncompleteRegistrationDialog"
      @proceed="handleIncompleteRegistrationsResp"
    />

    <BaseDialog
      :setOptions="transferRequiredDialogOptions"
      :setDisplay="showStartTransferRequiredDialog"
      reverseActionButtons
      @proceed="handleStartTransferRequiredDialogResp"
    />

    <BaseDialog
      :setOptions="isAmendLocationActive ? cancelAmendTransportPermitDialog : cancelTransportPermitDialog"
      :setDisplay="showCancelTransportPermitDialog"
      @proceed="handleCancelTransportPermitDialogResp"
    />

    <BaseDialog
      :setOptions="outOfDateOwnersDialogOptions(getMhrInformation.mhrNumber)"
      :setDisplay="showOutOfDateTransferDialog"
      @proceed="handleOutOfDateDialogResp"
    />

    <div class="pt-0 pb-5">
      <div class="container pa-0 pt-4">
        <v-row noGutters>
          <v-col cols="9">
            <v-row
              id="mhr-information-header"
              noGutters
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

                <!-- Lien Information -->
                <LienAlert
                  v-if="hasLien"
                  @isLoading="loading = $event"
                />

                <template v-if="!isReviewMode">
                  <p
                    v-if="!isExemptMhr"
                    class="mt-7"
                  >
                    This is the current information for this registration as of
                    <span class="font-weight-bold">{{ asOfDateTime }}</span>.
                  </p>
                  <p
                    v-if="!isExemptMhr && !showInProgressMsg"
                    class="mt-7"
                    data-test-id="correct-into-desc"
                  >
                    Ensure ALL of the information below is correct before making any changes to this registration.
                    Necessary fees will be applied as updates are made.
                  </p>

                  <!-- Unit Note Info -->
                  <p
                    v-if="isExemptMhr"
                    class="mt-7"
                    data-test-id="exempt-into-desc"
                  >
                    This manufactured home is exempt as of <b>{{ exemptDate }}</b> and changes can no longer be
                    made to this home unless the manufactured home is re-registered.
                  </p>
                  <p
                    v-if="getMhrUnitNotes && getMhrUnitNotes.length >= 1"
                    class="mt-7"
                  >
                    There are Unit Notes attached to this manufactured home.
                    <span v-if="isRoleStaffReg">
                      <a href="#unit-note-component">See Unit Notes</a>
                    </span>
                    <span v-else>
                      To view Unit Note information on this home, complete a manufactured home search.
                    </span>

                    <!-- Has Alert Message (Notice of Tax Sale, and others) -->
                    <template v-if="hasAlertMsg">
                      <CautionBox
                        class="mt-9"
                        :setMsg="alertMsg"
                        setAlert
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
                      :setMsg="cautionMsg"
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

            <!-- Frozen msg for Qualified Suppliers when Mhr is frozen due to Affe -->
            <CautionBox
              v-if="showInProgressMsg"
              class="mt-9"
              setAlert
              setMsg="There is a transaction already in progress for this home by another user. You will be unable
                     to make any changes to this home until the current transaction has been completed. Please try again
                     later."
            >
              <template #prependSLot>
                <v-icon
                  color="error"
                  class="mr-2 mt-n1"
                >
                  mdi-alert
                </v-icon>
              </template>
            </CautionBox>

            <CautionBox
              v-else-if="isReviewMode &&
                !isTransferToExecutorProbateWill &&
                !isTransferDueToDeath &&
                !isChangeLocationActive"
              class="mt-3 mb-5"
              setMsg="This information must match the information on the bill of sale."
            />

            <!-- Mhr Information Body -->
            <section
              v-if="dataLoaded"
              class="py-4"
            >
              <!-- MHR Information Review Section -->
              <template v-if="isReviewMode">
                <!-- Review Header -->
                <header class="review-header mt-10 rounded-top">
                  <v-icon
                    class="ml-2"
                    color="darkBlue"
                  >
                    mdi-file-document-multiple
                  </v-icon>
                  <label class="font-weight-bold pl-2">
                    {{ isChangeLocationActive ? 'Location Change' : 'Ownership Transfer or Change' }}
                  </label>
                </header>

                <section
                  v-if="!isChangeLocationActive"
                  id="owners-review"
                  class="mt-9"
                >
                  <HomeOwners
                    isMhrTransfer
                    isReadonlyTable
                    :currentHomeOwners="getMhrTransferCurrentHomeOwnerGroups"
                  />
                </section>

                <section
                  v-if="isChangeLocationActive"
                  id="location-change-review"
                >
                  <LocationChangeReview />
                </section>

                <section
                  v-if="!isChangeLocationActive"
                >
                  <v-divider class="mx-7 ma-0" />
                  <TransferDetailsReview class="py-6 pt-4 px-8" />
                </section>

                <section
                  v-if="isRoleStaffReg || isRoleStaffSbc"
                  id="staff-transfer-submitting-party"
                  class="submitting-party"
                >
                  <ContactInformation
                    :contactInfo="isChangeLocationActive
                      ? getMhrTransportPermit.submittingParty
                      : getMhrAccountSubmittingParty"
                    :sectionNumber="1"
                    :content="isTransportPermitByStaffSbc
                      ? submittingPartySbcTransportPermitContent
                      : submittingPartyChangeContent"
                    :validate="validateSubmittingParty"
                    :hidePartySearch="isTransportPermitByStaffSbc"
                    @setStoreProperty="isChangeLocationActive
                      ? setMhrTransportPermit({ key: 'submittingParty', value: $event })
                      : setMhrAccountSubmittingParty($event)"
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
                    tooltipContent="The default Submitting Party is based on your BC Registries
                       user account information. This information can be updated within your account settings."
                    :accountInfo="accountInfo"
                  />
                </section>

                <section
                  id="transfer-ref-num-section"
                  class="mt-10 py-4"
                >
                  <Attention
                    v-if="isRoleStaffReg"
                    sectionId="transfer-ref-num-section"
                    :initialValue="isChangeLocationActive
                      ? getMhrTransportPermit.attentionReference
                      : getMhrTransferAttentionReference"
                    :sectionNumber="2"
                    :validate="!getInfoValidation('isRefNumValid')"
                    data-test-id="attn-ref-number-card"
                    @isAttentionValid="setValidation('isRefNumValid', $event)"
                    @setStoreProperty="isChangeLocationActive
                      ? setMhrTransportPermit({ key: 'attentionReference', value: $event })
                      : setMhrTransferAttentionReference($event)"
                  />
                  <FolioOrReferenceNumber
                    v-else
                    sectionId="transfer-ref-num-section"
                    :initialValue="getMhrTransferAttentionReference"
                    :sectionNumber="isTransportPermitByStaffSbc ? 2 : 1"
                    :validate="!getInfoValidation('isRefNumValid')"
                    data-test-id="attn-ref-number-card"
                    @isFolioOrRefNumValid="setValidation('isRefNumValid', $event)"
                    @setStoreProperty="setMhrTransferAttentionReference($event)"
                  />
                </section>

                <section
                  id="transfer-confirm-section"
                  class="mt-10 transfer-confirm"
                >
                  <ConfirmCompletion
                    :sectionNumber="(isRoleStaffReg || isTransportPermitByStaffSbc) ? 3 : 2"
                    :legalName="getCertifyInformation.legalName"
                    :setShowErrors="validateConfirmCompletion"
                    @confirmCompletion="setValidation('isCompletionConfirmed', $event)"
                  >
                    <template
                      v-if="isChangeLocationActive"
                      #contentSlot
                    >
                      <LocationChangeConfirmCompletion v-if="isRegisteredLocationChange" />
                      <AmendTransportPermitConfirmCompletion v-else-if="isAmendLocationActive" />
                      <TransportPermitConfirmCompletion v-else />
                    </template>
                  </ConfirmCompletion>
                </section>

                <section
                  id="transfer-certify-section"
                  class="mt-10 pt-4"
                >
                  <CertifyInformation
                    :sectionNumber="(isRoleStaffReg || isTransportPermitByStaffSbc) ? 4 : 3"
                    :setShowErrors="validateAuthorizationError"
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
                      :displaySideLabel="true"
                      :displayPriorityCheckbox="true"
                      :staffPaymentData="staffPayment"
                      :invalidSection="validateStaffPayment"
                      :validate="validate"
                      @update:staff-payment-data="onStaffPaymentDataUpdate"
                      @valid="setValidation('isStaffPaymentValid', $event)"
                    />
                  </v-card>
                </section>
              </template>

              <!-- MHR Information Section -->
              <template v-else>
                <!-- Home Details Information -->
                <div class="mt-n2">
                  <YourHomeReview isTransferReview />
                </div>

                <!-- Home Location Information -->
                <div class="pt-4 mb-15">
                  <MhrTransportPermit
                    v-if="isChangeLocationEnabled"
                    :disable="isTransportPermitDisabled"
                    :validate="validate"
                    :disabledDueToLocation="disableRoleBaseLocationChange"
                    @updateLocationType="validate = false"
                    @cancelTransportPermitChanges="handleCancelTransportPermitChanges()"
                  />
                  <HomeLocationReview
                    v-if="showHomeLocationReview"
                    isTransferReview
                    :class="{ 'border-error-left': validateHomeLocationReview
                      && !getInfoValidation('isNewPadNumberValid') }"
                    :validate="validateHomeLocationReview"
                    :hideDefaultHeader="isChangeLocationEnabled"
                    :isPadEditable="transportPermitLocationType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK"
                  />
                </div>

                <!-- Home Owners Header -->
                <header
                  id="home-owners-header"
                  class="review-header mt-10 rounded-top"
                >
                  <v-row
                    noGutters
                    align="center"
                  >
                    <v-col cols="9">
                      <img
                        class="review-header-icon mb-1 ml-1"
                        src="@/assets/svgs/homeownersicon_reviewscreen.svg"
                      >
                      <span class="font-weight-bold pl-2">Home Owners</span>
                    </v-col>
                    <v-col
                      v-if="enableHomeOwnerChanges && !isExemptMhr"
                      cols="3"
                      class="text-right"
                    >
                      <v-btn
                        id="home-owners-change-btn"
                        variant="plain"
                        class="pl-1"
                        color="primary"
                        :ripple="false"
                        :disabled="isFrozenMhrDueToAffidavit || isFrozenMhrDueToUnitNote ||
                          ((hasLien && !isLienRegistrationTypeSA) &&
                            (!isRoleStaffReg || isChangeLocationActive || disableRoleBaseTransfer))"
                        @click="toggleTypeSelector()"
                      >
                        <span v-if="!showTransferType">
                          <v-icon
                            color="primary"
                            size="small"
                          >mdi-pencil</v-icon> Change Ownership
                        </span>
                        <span v-else>
                          <v-icon
                            color="primary"
                            size="small"
                          >mdi-close</v-icon> Cancel Ownership Change
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

                    <SimpleHelpToggle
                      toggleButtonTitle="Help with Ownership Transfer or Change"
                      class="mb-8"
                    >
                      <template #content>
                        <HelpWithOwners />
                      </template>
                    </SimpleHelpToggle>

                    <DocumentId
                      v-if="isRoleStaffReg"
                      :documentId="getMhrTransferDocumentId || ''"
                      :content="{
                        sideLabel: 'Document ID',
                        hintText: 'Enter the 8-digit Document ID number'
                      }"
                      :validate="validate"
                      @setStoreProperty="handleDocumentIdUpdate"
                      @isValid="setValidation('isDocumentIdValid', $event)"
                    />
                    <TransferType
                      :validate="validate"
                      :disableSelect="isFrozenMhrDueToAffidavit"
                      @emitType="handleTransferTypeChange"
                      @emitDeclaredValue="handleDeclaredValueChange"
                      @emitValid="setValidation('isValidTransferType', $event)"
                    />

                    <!-- Qualified Supplier - Transfer Notes -->
                    <p
                      v-if="isLawyerNotaryAndSjtTransfer"
                      class="mt-6"
                    >
                      <span class="font-weight-bold">Note</span>: Transfer to Surviving Joint Tenant(s) involving owners
                      that are businesses or organizations cannot be completed online and must be registered by BC
                      Registries staff.
                    </p>
                    <p
                      v-if="isRoleManufacturer || isLawyerNotaryAndSog"
                      class="mt-10"
                    >
                      <span class="font-weight-bold">Note</span>: Some complex ownership transfers, including transfers
                      to a trustee or trust of any kind, cannot be completed online and must be registered by BC
                      Registries staff.
                    </p>
                  </div>
                </v-expand-transition>
                <p
                  v-if="disableRoleBaseTransfer"
                  class="mt-9"
                >
                  <span class="font-weight-bold">Note:</span> You cannot register an ownership transfer or change
                  because the home does not have a sole owner whose name matches your manufacturer’s name. Transfers can
                  be registered by BC Registries staff or by a qualified lawyer or notary.
                </p>
                <HomeOwners
                  ref="homeOwnersComponentRef"
                  isMhrTransfer
                  class="mt-10"
                  :class="{ 'mb-10': !hasUnsavedChanges }"
                  :validateTransfer="validate && !isChangeLocationActive"
                  @isValidTransferOwners="setValidation('isValidTransferOwners', $event)"
                />

                <TransferDetails
                  v-if="hasUnsavedChanges && !isChangeLocationActive"
                  ref="transferDetailsComponent"
                  class="mt-10"
                  :disablePrefill="isFrozenMhrDueToAffidavit"
                  :validate="validate"
                  @isValid="setValidation('isTransferDetailsValid', $event)"
                />

                <UnitNotePanels
                  v-if="isRoleStaffReg"
                  id="unit-note-component"
                  class="mt-10"
                  :unitNotes="getMhrUnitNotes"
                  :disabled="!enableHomeOwnerChanges || showTransferType || isChangeLocationActive"
                  :hasActiveExemption="hasActiveExemption"
                />

                <v-spacer class="py-10 my-10" />
              </template>
            </section>
          </v-col>
          <v-col
            v-if="showTransferType || isReviewMode || isChangeLocationActive"
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :setShowButtons="true"
                :setBackBtn="showBackBtn"
                :setCancelBtn="'Cancel'"
                :setSaveBtn="isChangeLocationActive ? '' : 'Save and Resume Later'"
                :setSubmitBtn="reviewConfirmText"
                :setRightOffset="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setErrMsg="transferErrorMsg"
                :transferType="isChangeLocationActive
                  ? getUiFeeSummaryLocationType(transportPermitLocationType)
                  : getUiTransferType()"
                :setIsLoading="submitBtnLoading"
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
  DocumentId,
  LienAlert,
  SimpleHelpToggle
} from '@/components/common'
import {
  StaffPaymentOptions,
  APIMHRMapSearchTypes,
  APIRegistrationTypes,
  APISearchTypes,
  ApiTransferTypes,
  MhApiStatusTypes,
  RouteNames,
  UIMHRSearchTypes,
  LocationChangeTypes,
  ErrorCategories,
  UnitNoteDocTypes, MhApiFrozenDocumentTypes
} from '@/enums'
import {
  useAuth,
  useExemptions,
  useHomeOwners,
  useInputRules,
  useMhrCorrections,
  useMhrInformation,
  useMhrInfoValidation,
  useNavigation,
  useTransferOwners,
  useTransportPermits,
  useUserAccess
} from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ConfirmCompletion,
  HelpWithOwners,
  TransferDetails,
  TransferDetailsReview,
  TransferType
} from '@/components/mhrTransfers'
import { HomeLocationReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { HomeOwners } from '@/views'
import { UnitNotePanels } from '@/components/unitNotes'
import { BaseDialog } from '@/components/dialogs'
import {
  QSLockedStateUnitNoteTypes,
  StaffTransferTypes,
  submittingPartyChangeContent,
  submittingPartySbcTransportPermitContent,
  UnitNotesInfo
} from '@/resources'
import {
  cancelOwnerChangeConfirm,
  incompleteRegistrationDialog,
  transferRequiredDialog,
  unsavedChangesDialog,
  cancelTransportPermitDialog,
  cancelAmendTransportPermitDialog,
  changeTransportPermitLocationTypeDialog,
  outOfDateOwnersDialogOptions
} from '@/resources/dialogOptions'
import AccountInfo from '@/components/common/AccountInfo.vue'
import MhrTransportPermit from '@/views/mhrInformation/MhrTransportPermit.vue'
import {
  LocationChangeReview,
  LocationChangeConfirmCompletion,
  TransportPermitConfirmCompletion,
  AmendTransportPermitConfirmCompletion
} from '@/components/mhrTransportPermit'
import {
  AccountInfoIF,
  DialogOptionsIF,
  ErrorIF,
  MhrTransferApiIF,
  RegTableNewItemI,
  TransferTypeSelectIF,
  StaffPaymentIF,
} from '@/interfaces'
import {
  createMhrDraft,
  getAccountInfoFromAuth,
  getFeatureFlag,
  getMhrDraft,
  getMHRegistrationSummary,
  mhrSearch,
  pacificDate,
  scrollToTop,
  submitAdminRegistration,
  submitMhrTransfer,
  updateMhrDraft
} from '@/utils'

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
    MhrTransportPermit,
    HomeLocationReview,
    StickyContainer,
    CertifyInformation,
    AccountInfo,
    ConfirmCompletion,
    YourHomeReview,
    StaffPayment,
    UnitNotePanels,
    LienAlert,
    LocationChangeReview,
    LocationChangeConfirmCompletion,
    TransportPermitConfirmCompletion,
    AmendTransportPermitConfirmCompletion,
    SimpleHelpToggle,
    HelpWithOwners
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
  emits: [
    'error',
    'emitHaveData'
  ],
  setup (props, context) {
    const router = useRouter()
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setMhrStatusType,
      setMhrAccountSubmittingParty,
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
      setStaffPayment,
      setEmptyMhrTransportPermit,
      setMhrTransportPermit,
      setMhrInformationDraftId,
      setCertifyInformation
    } = useStore()
    const {
      // Getters
      getCurrentUser,
      getMhrUnitNotes,
      getMhrTransferHomeOwners, // used in tests, would need to refactor to remove it
      getMhrInformation,
      getMhrTransferCurrentHomeOwnerGroups,
      getCertifyInformation,
      hasUnsavedChanges,
      hasLien,
      getLienRegistrationType,
      isRoleStaffSbc,
      isRoleStaffReg,
      isRoleManufacturer,
      isRoleQualifiedSupplier,
      getMhrRegistrationLocation,
      getMhrTransferDocumentId,
      getMhrTransferType,
      getMhrTransferDeclaredValue,
      getMhrInfoValidation,
      getMhrTransportPermit,
      getMhrTransferAttentionReference,
      getMhrAccountSubmittingParty,
      isRoleQualifiedSupplierHomeDealer,
      isRoleQualifiedSupplierLawyersNotaries
    } = storeToRefs(useStore())
    const {
      isFrozenMhr,
      isFrozenMhrDueToAffidavit,
      isExemptMhr,
      getLienInfo,
      buildApiData,
      initMhrTransfer,
      getUiTransferType,
      parseMhrInformation,
      initDraftMhrInformation,
      parseSubmittingPartyInfo,
      isFrozenMhrDueToUnitNote
    } = useMhrInformation()
    const {
      setValidation,
      getInfoValidation,
      isValidTransfer,
      isValidTransferReview,
      isValidTransportPermit,
      isValidTransportPermitReview,
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
    const { buildLocationChange } = useMhrCorrections()
    const { disableManufacturerTransfer, disableDealerManufacturerLocationChange } = useUserAccess()
    const {
      isChangeLocationActive,
      isChangeLocationEnabled,
      isAmendLocationActive,
      isTransportPermitDisabled,
      isRegisteredLocationChange,
      setLocationChange,
      getUiFeeSummaryLocationType,
      getUiLocationType,
      resetTransportPermit,
      setLocationChangeType,
      initTransportPermit,
      populateLocationInfoForSamePark,
      buildAndSubmitTransportPermit,
    } = useTransportPermits()

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
      staffPayment: {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      },
      showTransferType: !!getMhrInformation.value.draftNumber ||
        (isRoleStaffReg.value && isFrozenMhrDueToAffidavit.value) || false,
      cancelOptions: unsavedChangesDialog,
      showCancelDialog: false,
      showCancelChangeDialog: false,
      showIncompleteRegistrationDialog: false,
      showStartTransferRequiredDialog: false,
      showOutOfDateTransferDialog: false,
      hasLienInfoDisplayed: false, // flag to track if lien info has been displayed after API check
      enableRoleBasedTransfer: true, // rendering of the transfer/change btn
      disableRoleBaseTransfer: false, // disabled state of transfer/change btn
      disableRoleBaseLocationChange: false, // disabled state of location change/transport permit btn
      submitBtnLoading: false,
      hasTransactionInProgress: false,

      // Transport Permit
      showCancelTransportPermitDialog: false,
      isTransportPermitDisabled: computed((): boolean =>
        localState.showTransferType ||
        isExemptMhr.value ||
        isTransportPermitDisabled.value ||
        (!isRoleStaffReg.value && isFrozenMhrDueToAffidavit.value)
      ),
      isTransportPermitByStaffSbc: computed((): boolean => isChangeLocationActive.value && isRoleStaffSbc.value),
      transportPermitLocationType: computed((): LocationChangeTypes => getMhrTransportPermit.value.locationChangeType),
      showInProgressMsg: computed((): boolean => {
        return localState.hasTransactionInProgress || (!isRoleStaffReg.value && isFrozenMhrDueToAffidavit.value)
      }),
      showHomeLocationReview: computed((): boolean => {
        return ![LocationChangeTypes.TRANSPORT_PERMIT, LocationChangeTypes.REGISTERED_LOCATION]
          .includes(localState.transportPermitLocationType)
      }),
      validateHomeLocationReview: computed((): boolean =>
        localState.validate &&
        isChangeLocationActive && // transport permit open
        localState.transportPermitLocationType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
      ),
      feeType: computed((): FeeSummaryTypes => {
        if (isAmendLocationActive.value && isChangeLocationActive.value) {
          return FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT
        } else {
          return isChangeLocationActive.value ? FeeSummaryTypes.MHR_TRANSPORT_PERMIT : FeeSummaryTypes.MHR_TRANSFER
        }
      }
      ),
      hasActiveExemption: computed((): boolean => !!getActiveExemption() ||
        getMhrInformation.value.statusType === MhApiStatusTypes.EXEMPT),
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
        if (localState.validate && hasLien.value &&
          (isRoleQualifiedSupplier.value && !localState.isLienRegistrationTypeSA)) {
          return '< Lien on this home is preventing transfer'
        }

        let isValidReview

        if (isChangeLocationActive.value) {
          // transport permit activated
          isValidReview = localState.isReviewMode ? isValidTransportPermitReview.value : isValidTransportPermit.value
        } else {
          isValidReview = localState.isReviewMode ? isValidTransferReview.value : isValidTransfer.value
        }

        return localState.validate && !isValidReview ? '< Please complete required information' : ''
      }),
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      enableHomeOwnerChanges: computed((): boolean => {
        return !isRoleStaffSbc.value && getFeatureFlag('mhr-transfer-enabled') &&
          localState.enableRoleBasedTransfer
      }),
      isDraft: computed((): boolean => {
        return getMhrInformation.value.draftNumber
      }),
      isLienRegistrationTypeSA: computed((): boolean => {
        return getLienRegistrationType.value === APIRegistrationTypes.SECURITY_AGREEMENT
      }),
      exemptDate: computed((): string =>
        (isExemptMhr.value && getMhrInformation.value?.exemptDateTime)
        ? pacificDate(getMhrInformation.value?.exemptDateTime, true)
        : ''
      ),
      hasAlertMsg: false,
      alertMsg: computed((): string => {
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
      }),
      /** Is true when current user is Lawyer and Notary and the current transfer type is surviving joint tenants **/
      isLawyerNotaryAndSjtTransfer: computed(() => {
        return getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT &&
          isRoleQualifiedSupplierLawyersNotaries.value
      }),
      /** Is true when current user is Lawyer and Notary and the current transfer type is sale or gift **/
      isLawyerNotaryAndSog: computed(() => {
        return getMhrTransferType.value?.transferType === ApiTransferTypes.SALE_OR_GIFT &&
          isRoleQualifiedSupplierLawyersNotaries.value
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
      setEmptyMhrTransportPermit(initTransportPermit())

      const isFrozenDueToTransportPermit =
        getMhrInformation.value.frozenDocumentType === UnitNoteDocTypes.TRANSPORT_PERMIT

      // Set baseline MHR Information to state
      // Do not parse Transfer details when frozen doc type is Transport Permit
      await parseMhrInformation(isFrozenMhr.value && !isFrozenDueToTransportPermit)
      await setLocationChange(false)

      if (getMhrInformation.value.draftNumber) {
        // Retrieve draft if it exists
        const { registration } = await getMhrDraft(getMhrInformation.value.draftNumber)
        await initDraftMhrInformation(registration as MhrTransferApiIF)
      } else if (isRoleStaffReg.value && isFrozenMhrDueToAffidavit.value) {
        // Manually set Transfer due to sale or gift
        setMhrTransferType(StaffTransferTypes[1])
        await scrollToFirstError(false, 'home-owners-header')
      } else {
        // When not a draft Transfer, force no unsaved changes after loading current owners
        await setUnsavedChanges(false)
      }

      // Check for product based Transfer access
      switch(true) {
        case isRoleManufacturer.value:
          localState.disableRoleBaseTransfer = await disableManufacturerTransfer()
          localState.disableRoleBaseLocationChange = await disableDealerManufacturerLocationChange()
          break;
        case isRoleQualifiedSupplierHomeDealer.value:
          localState.enableRoleBasedTransfer = false
          localState.disableRoleBaseLocationChange = await disableDealerManufacturerLocationChange(true)
          break;
      }

      if ((isRoleQualifiedSupplier.value || isRoleStaffSbc.value) && !isRoleStaffReg.value) {
        // Get Account Info from Auth to be used in Submitting Party section in Review screen
        localState.accountInfo = await getAccountInfoFromAuth(getCurrentUser.value) as AccountInfoIF
        parseSubmittingPartyInfo(localState.accountInfo)
      }

      localState.hasAlertMsg = QSLockedStateUnitNoteTypes.includes(getMhrInformation.value.frozenDocumentType)
      localState.loading = false
      localState.dataLoaded = true
    })

    const emitError = (error: ErrorIF): void => {
      // Intercept and handle out of date error
      if(error.category === ErrorCategories.TRANSFER_OUT_OF_DATE_OWNERS) {
        localState.showOutOfDateTransferDialog = true
        return
      }
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

      // Await vue(DOM updates) as it takes time for validation prop to propagate and  trigger validations
      // Components will then validate and emit back validation states
      await nextTick()

      // Prevent proceeding when Lien present
      if (hasLien.value && (isRoleQualifiedSupplier.value && !localState.isLienRegistrationTypeSA)) {
        await scrollToFirstError(true)
        return
      }

      // If already in review mode, file the transfer
      if (localState.isReviewMode) {
        localState.submitBtnLoading = true

        // Verify no lien exists prior to submitting filing
        const regSum = !localState.hasLienInfoDisplayed
          ? await getMHRegistrationSummary(getMhrInformation.value.mhrNumber, false)
          : null

        if (!!regSum && !!regSum.lienRegistrationType) {
          await setLienType(regSum.lienRegistrationType)
          await scrollToFirstError(true)
          localState.hasLienInfoDisplayed = true
          localState.submitBtnLoading = false
          return
        }

        if (!isRoleStaffReg.value && !!regSum && regSum.frozenDocumentType === MhApiFrozenDocumentTypes.TRANS_AFFIDAVIT)
        {
          localState.hasTransactionInProgress = true
          localState.submitBtnLoading = false
          await scrollToFirstError(true)
          return
        }

        // Check if any required fields have errors
        if (localState.isReviewMode && !isValidTransferReview.value) {
          await scrollToFirstError(false)
          localState.submitBtnLoading = false
          return
        }

        // Complete Filing
        localState.loading = true

        // Submit Location Change
        if(isRegisteredLocationChange.value) {

          const locationChangeFiling = await submitAdminRegistration(
            getMhrInformation.value.mhrNumber,
            buildLocationChange(),
            localState.staffPayment
          )

          if (!locationChangeFiling?.error) {
            // this will scroll & highlight a new row for Unit Note in Registration Table
            const newItem: RegTableNewItemI = {
              addedReg: locationChangeFiling.documentRegistrationNumber,
              addedRegParent: locationChangeFiling.mhrNumber,
              addedRegSummary: null,
              prevDraft: ''
            }

            setRegTableNewItem(newItem)
            await goToDash()
          } else {
            emitError(locationChangeFiling?.error)
          }

          localState.loading = false
          localState.submitBtnLoading = false
          return
        }

        // Submit Transport Permit
        if (isChangeLocationActive.value) {
          const transportPermitFilingResp: any =
            await buildAndSubmitTransportPermit(getMhrInformation.value.mhrNumber, localState.staffPayment)

          if (!transportPermitFilingResp?.error) {
            // this will scroll & highlight a new row for Unit Note in Registration Table
            const newItem: RegTableNewItemI = {
              addedReg: transportPermitFilingResp.documentRegistrationNumber,
              addedRegParent: transportPermitFilingResp.mhrNumber,
              addedRegSummary: null,
              prevDraft: ''
            }

            setRegTableNewItem(newItem)
            goToDash()
          } else {
            emitError(transportPermitFilingResp?.error)
          }
          localState.loading = false
          localState.submitBtnLoading = false
          return
        }

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
          if (isRoleStaffReg.value && isTransferToExecutorUnder25Will.value) {
            // Clear state for Sale or Gift Transfer
            setEmptyMhrTransfer(initMhrTransfer())
            setCertifyInformation({ ...getCertifyInformation.value, certified: false })
            localState.validate = false
            localState.staffPayment.option = StaffPaymentOptions.NONE

            // Set Frozen state manually as the base reg isn't re-fetched in this flow
            await setMhrStatusType(MhApiStatusTypes.FROZEN)
            await setMhrTransferType(StaffTransferTypes[1])
            // Set baseline MHR Information to state
            await parseMhrInformation(isFrozenMhr.value)

            // reset Document Id (Staff has this extra field which needs to be reset after Affidavit flow)
            await setMhrTransferDocumentId('')

            localState.isReviewMode = false
            localState.showStartTransferRequiredDialog = true
          } else goToDashboard()
        } else emitError(mhrTransferFiling?.error)
        localState.validate = false
        localState.loading = false
        localState.submitBtnLoading = false
      }

      // If Transfer or Transport Permit is valid, enter review mode
      // For Affidavit Transfers, need to complete affidavit before proceeding
      if (isValidTransfer.value || isValidTransportPermit.value) {
        localState.isReviewMode = true
        localState.validate = false
      }

      // Force show removed/deceased homeOwners when invalid
      if (!getInfoValidation('isValidTransferOwners')) {
        (homeOwnersComponentRef as any).value?.hideShowRemovedOwners(true)
      }

      await nextTick()
      // Scroll to the top of review screen
      await scrollToFirstError(isValidTransfer.value || isValidTransportPermit.value)
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
      if (hasUnsavedChanges.value && isChangeLocationActive.value) {
        // transport permit dialog
        localState.showIncompleteRegistrationDialog = true
      } else if (hasUnsavedChanges.value) {
        // transfers/general dialog
        localState.showCancelDialog = true
      } else {
        setUnsavedChanges(false)
        setGlobalEditingMode(false)
        setEmptyMhrTransfer(initMhrTransfer())
        resetTransportPermit(true)
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

    const handleIncompleteRegistrationsResp = async (val: boolean) => {
      if (!val) {
        setUnsavedChanges(false)
        resetTransportPermit(true)
        resetValidationState()
        localState.validate = false
        await scrollToFirstError(false, 'mhr-information-header')
      }
      localState.showIncompleteRegistrationDialog = false
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

    const handleCancelTransportPermitDialogResp = (proceed: boolean) => {
      if (proceed) {
        setUnsavedChanges(false)
        localState.validate = false
        setLocationChange(false)
        resetMhrInformation()
        resetTransportPermit()
      }
      resetValidationState()
      localState.showCancelTransportPermitDialog = false
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

    const handleCancelTransportPermitChanges = () => {
      if (hasUnsavedChanges.value) {
        // show dialog
        localState.showCancelTransportPermitDialog = true
      } else {
        // reset validation and close dialog
        resetValidationState()
        resetMhrInformation()
        resetTransportPermit(true)
        localState.validate = false
      }
    }

    const handleOutOfDateDialogResp = async (proceed: boolean) => {
      if (proceed) {
        await resetMhrInformation()
        setMhrInformationDraftId('')
        localState.isReviewMode = false
        localState.showTransferType = false
        scrollToTop()
      }
      localState.showOutOfDateTransferDialog = false
    }

    const handleDocumentIdUpdate = (documentId: string) => {
      setMhrTransferDocumentId(documentId)
    }

    const handleTransferTypeChange = async (transferTypeSelect: TransferTypeSelectIF): Promise<void> => {
      // Reset state until support is built for other Transfer Types
      if (localState.hasTransferChanges && transferTypeSelect?.transferType &&
        (transferTypeSelect?.transferType !== getMhrTransferType.value?.transferType)
      ) await resetMhrInformation(false)

      setMhrTransferType(transferTypeSelect)
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

    watch(() => localState.transportPermitLocationType, val => {
      if (val === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK) {
        populateLocationInfoForSamePark(getMhrRegistrationLocation.value)
        setUnsavedChanges(false)
      }
    })

    return {
      isRoleStaffSbc,
      isRoleStaffReg,
      isFrozenMhr,
      isFrozenMhrDueToAffidavit,
      isExemptMhr,
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
      isRoleManufacturer,
      isRoleQualifiedSupplier,
      isTransferDueToDeath,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      setMhrTransferAttentionReference,
      setMhrAccountSubmittingParty,
      setLocationChangeType,
      handleDocumentIdUpdate,
      handleTransferTypeChange,
      getMhrTransferDocumentId,
      getUiTransferType,
      handleDeclaredValueChange,
      toggleTypeSelector,
      onStaffPaymentDataUpdate,
      handleCancelDialogResp,
      handleOutOfDateDialogResp,
      handleIncompleteRegistrationsResp,
      handleStartTransferRequiredDialogResp,
      cancelOwnerChangeConfirm,
      incompleteRegistrationDialog,
      transferRequiredDialog,
      getMhrUnitNotes,
      getMhrAccountSubmittingParty,
      submittingPartyChangeContent,
      submittingPartySbcTransportPermitContent,
      isChangeLocationActive,
      isChangeLocationEnabled,
      getMhrTransferType,
      LocationChangeTypes,
      getUiLocationType,
      getUiFeeSummaryLocationType,
      getMhrInfoValidation,
      isValidTransfer,
      getLienInfo,
      outOfDateOwnersDialogOptions,
      isFrozenMhrDueToUnitNote,

      // transport permit
      isValidTransportPermit,
      isValidTransportPermitReview,
      isRegisteredLocationChange,
      isAmendLocationActive,
      getMhrTransportPermit,
      setMhrTransportPermit,
      handleCancelTransportPermitChanges,
      handleCancelTransportPermitDialogResp,
      cancelTransportPermitDialog,
      cancelAmendTransportPermitDialog,
      changeTransportPermitLocationTypeDialog,
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

.submitting-party {
  margin-top: 55px;
}

.alert-icon {
  font-size: 20px !important;
}

:deep(#home-owners-change-btn) {
  height: 24px;
  color: $primary-blue !important;
}

:deep(.theme--light.v-btn.v-btn--disabled) {
  opacity: 0.4 !important;
}
</style>
