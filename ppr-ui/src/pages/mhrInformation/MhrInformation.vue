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
      :close-action="true"
      :set-options="cancelOptions"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp"
    />

    <BaseDialog
      :set-options="cancelOwnerChangeConfirm"
      :set-display="showCancelChangeDialog"
      @proceed="handleCancelDialogResp"
    />

    <BaseDialog
      :close-action="true"
      :set-options="incompleteRegistrationDialog"
      :set-display="showIncompleteRegistrationDialog"
      @proceed="handleIncompleteRegistrationsResp"
    />

    <BaseDialog
      :set-options="transferRequiredDialogOptions"
      :set-display="showStartTransferRequiredDialog"
      reverse-action-buttons
      @proceed="handleStartTransferRequiredDialogResp"
    />

    <BaseDialog
      :set-options="isAmendLocationActive ? cancelAmendTransportPermitDialog : cancelTransportPermitDialog"
      :set-display="showCancelTransportPermitDialog"
      @proceed="handleCancelTransportPermitDialogResp"
    />

    <BaseDialog
      :set-options="outOfDateOwnersDialogOptions(getMhrInformation.mhrNumber)"
      :set-display="showOutOfDateTransferDialog"
      @proceed="handleOutOfDateDialogResp"
    />

    <div class="pt-0 pb-12">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row
              id="mhr-information-header"
              no-gutters
              class="pt-3 soft-corners-top"
            >
              <v-col cols="auto">
                <h2 class="fs-32 lh-36">
                  {{
                    isReviewMode
                      ? 'Review and Confirm'
                      : `Manufactured Home Information${isDraft ? ' - Draft' : ''}`
                  }}
                </h2>

                <!-- Lien Information -->
                <LienAlert
                  v-if="hasLien"
                  @is-loading="loading = $event"
                />

                <template v-if="!isReviewMode">
                  <p
                    v-if="!isExemptMhr && !isCancelledMhr"
                    class="mt-7"
                  >
                    This is the current information for this registration as of
                    <span class="font-weight-bold">{{ asOfDateTime }}</span>.
                  </p>
                  <p
                    v-if="!isExemptMhr && !showInProgressMsg && !isCancelledMhr"
                    class="mt-7"
                    data-test-id="correct-into-desc"
                  >
                    Ensure ALL of the information below is correct before making any changes to this registration.
                    Necessary fees will be applied as updates are made.
                  </p>

                  <!-- Cancelled MHR Info -->
                  <p
                    v-if="isCancelledMhr"
                    class="mt-7"
                    data-test-id="cancelled-info-desc"
                  >
                    This manufactured home is cancelled <span class="font-weight-bold">as of {{ asOfDateTime }}</span>
                    and changes can no longer be made to this home unless the manufactured home is re-registered.
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

            <!-- Frozen msg for Qualified Suppliers when Mhr is frozen due to Affe -->
            <CautionBox
              v-if="showInProgressMsg"
              class="mt-9"
              set-alert
              set-msg="There is a transaction already in progress for this home by another user. You will be unable
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
                !isChangeLocationActive &&
                !isCancelChangeLocationActive &&
                !isTransferWithoutBillOfSale &&
                !isExtendChangeLocationActive"
              class="mt-7 mb-5"
              set-msg="This information must match the information on the bill of sale."
            />

            <CautionBox
              v-if="isReviewMode && isNewPermitActive"
              class="my-9"
              :set-msg="`Creating a new transport can only be performed once the manufactured home has been transported
               to the current registered location. When the new transport permit is issued, the current Transport Permit
               ${getMhrInformation.permitRegistrationNumber} will no longer be valid.`"
            />

            <!-- Mhr Information Body -->
            <section
              v-if="dataLoaded"
              class="pb-4"
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
                  <h3 class="fs-16 lh-24 ml-2">
                    {{ reviewModeHeader }}
                  </h3>
                </header>

                <section
                  v-if="!isChangeLocationActive && !isCancelChangeLocationActive && !isExtendChangeLocationActive"
                  id="owners-review"
                  class="mt-9"
                >
                  <HomeOwners
                    is-mhr-transfer
                    is-readonly-table
                    :current-home-owners="getMhrTransferCurrentHomeOwnerGroups"
                  />
                </section>

                <section
                  v-if="isChangeLocationActive || isCancelChangeLocationActive || isExtendChangeLocationActive"
                  id="location-change-review"
                >
                  <LocationChangeReview />

                  <v-card
                    v-if="isNewPermitActive"
                    flat
                    class="mt-2"
                  >
                    <TransportPermitDetails
                      is-completed-location
                    />
                  </v-card>
                </section>

                <section
                  v-if="isCancelChangeLocationActive"
                  id="cancelled-location-change-review"
                >
                  <HomeLocationReview
                    id="cancelled-location-review"
                    hide-default-header
                    hide-section-header
                    is-transfer-review
                  />
                </section>

                <section
                  v-if="!isChangeLocationActive && !isCancelChangeLocationActive && !isExtendChangeLocationActive"
                >
                  <TransferDetailsReview class="py-6 pt-4 px-8" />
                </section>

                <section
                  v-if="isRoleStaffReg || isRoleStaffSbc"
                  id="staff-transfer-submitting-party"
                  class="submitting-party"
                >
                  <ContactInformation
                    :contact-info="(isChangeLocationActive || isCancelChangeLocationActive ||
                      isExtendChangeLocationActive)
                      ? getMhrTransportPermit.submittingParty
                      : getMhrAccountSubmittingParty"
                    :section-number="1"
                    :content="isTransportPermitByStaffSbc
                      ? submittingPartySbcTransportPermitContent
                      : submittingPartyChangeContent"
                    :validate="validateSubmittingParty"
                    :hide-party-search="isTransportPermitByStaffSbc"
                    @set-store-property="(isChangeLocationActive || isCancelChangeLocationActive ||
                      isExtendChangeLocationActive)
                      ? setMhrTransportPermit({ key: 'submittingParty', value: $event })
                      : setMhrAccountSubmittingParty($event)"
                    @is-valid="setValidation('isSubmittingPartyValid', $event)"
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
                    :initial-value="(isChangeLocationActive || isCancelChangeLocationActive ||
                      isExtendChangeLocationActive)
                      ? getMhrTransportPermit.attentionReference
                      : getMhrTransferAttentionReference"
                    :section-number="2"
                    :validate="!getInfoValidation('isRefNumValid')"
                    data-test-id="attn-ref-number-card"
                    @is-attention-valid="setValidation('isRefNumValid', $event)"
                    @set-store-property="(isChangeLocationActive || isCancelChangeLocationActive ||
                      isExtendChangeLocationActive)
                      ? setMhrTransportPermit({ key: 'attentionReference', value: $event })
                      : setMhrTransferAttentionReference($event)"
                  />
                  <FolioOrReferenceNumber
                    v-else
                    section-id="transfer-ref-num-section"
                    :initial-value="getMhrTransferAttentionReference"
                    :section-number="isTransportPermitByStaffSbc ? 2 : 1"
                    :validate="!getInfoValidation('isRefNumValid')"
                    data-test-id="attn-ref-number-card"
                    @is-folio-or-ref-num-valid="setValidation('isRefNumValid', $event)"
                    @set-store-property="setMhrTransferAttentionReference($event)"
                  />
                </section>

                <section
                  id="transfer-confirm-section"
                  class="mt-10 transfer-confirm"
                >
                  <ConfirmCompletion
                    :section-number="(isRoleStaffReg || isTransportPermitByStaffSbc) ? 3 : 2"
                    :legal-name="getCertifyInformation.legalName"
                    :set-show-errors="validateConfirmCompletion"
                    @confirm-completion="setValidation('isCompletionConfirmed', $event)"
                  >
                    <template
                      v-if="isChangeLocationActive || isCancelChangeLocationActive"
                      #contentSlot
                    >
                      <LocationChangeConfirmCompletion v-if="isRegisteredLocationChange" />
                      <AmendTransportPermitConfirmCompletion v-else-if="isAmendLocationActive" />
                      <CancelTransportPermitConfirmCompletion v-else-if="isCancelChangeLocationActive" />
                      <TransportPermitConfirmCompletion v-else />
                    </template>
                  </ConfirmCompletion>
                </section>

                <section
                  id="transfer-certify-section"
                  class="mt-10 pt-4"
                >
                  <CertifyInformation
                    :section-number="(isRoleStaffReg || isTransportPermitByStaffSbc) ? 4 : 3"
                    :set-show-errors="validateAuthorizationError"
                    @certify-valid="setValidation('isAuthorizationValid', $event)"
                  />
                </section>

                <section
                  v-if="isRoleStaffReg"
                  id="staff-transfer-payment-section"
                  class="mt-10 pt-4 pb-4"
                >
                  <h3 class="fs-18">
                    5. Staff Payment
                  </h3>
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
                  <YourHomeReview is-transfer-review />
                </div>

                <!-- Home Location Information -->
                <div class="pt-4 mb-15">
                  <MhrTransportPermit
                    v-if="isChangeLocationEnabled"
                    :disable="isTransportPermitDisabled"
                    :validate="validate"
                    :disabled-due-to-location="disableRoleBaseLocationChange"
                    @update-location-type="validate = false"
                    @cancel-transport-permit-changes="handleCancelTransportPermitChanges($event)"
                  />

                  <HomeLocationReview
                    v-if="showHomeLocationReview"
                    is-transfer-review
                    :class="{ 'border-error-left': validateHomeLocationReview
                      && !getInfoValidation('isNewPadNumberValid') }"
                    :validate="validateHomeLocationReview"
                    :hide-default-header="isChangeLocationEnabled"
                    :is-pad-editable="transportPermitLocationType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK"
                  />

                  <HomeLocationReview
                    v-if="isCancelChangeLocationActive"
                    id="transport-permit-prev-location"
                    is-transfer-review
                    is-prev-transport-permit-location
                    hide-default-header
                  />
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
                    <v-col
                      cols="9"
                      class="d-flex"
                    >
                      <img
                        class="review-header-icon mb-1 ml-1"
                        src="@/assets/svgs/homeownersicon_reviewscreen.svg"
                      >
                      <h3 class="fs-16 lh-24 ml-2">
                        Home Owners
                      </h3>
                    </v-col>
                    <v-col
                      v-if="enableHomeOwnerChanges && !isExemptMhr && !isCancelledMhr"
                      cols="3"
                      class="text-right"
                    >
                      <v-btn
                        id="home-owners-change-btn"
                        variant="plain"
                        class="pl-1"
                        color="primary"
                        :ripple="false"
                        :disabled="isChangeOwnershipBtnDisabled"
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
                      toggle-button-title="Help with Ownership Transfer or Change"
                      class="mb-8"
                    >
                      <template #content>
                        <HelpWithOwners />
                      </template>
                    </SimpleHelpToggle>

                    <DocumentId
                      v-if="isRoleStaffReg"
                      :document-id="getMhrTransferDocumentId || ''"
                      :content="{
                        sideLabel: 'Document ID',
                        hintText: 'Enter the 8-digit Document ID number'
                      }"
                      :validate="validate"
                      @set-store-property="handleDocumentIdUpdate"
                      @is-valid="setValidation('isDocumentIdValid', $event)"
                    />
                    <TransferType
                      :validate="validate"
                      :disable-select="isFrozenMhrDueToAffidavit"
                      @emit-type="handleTransferTypeChange"
                      @emit-declared-value="handleDeclaredValueChange"
                      @emit-valid="setValidation('isValidTransferType', $event)"
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
                  class="dealer-manufacturer-mismatch-text mt-9"
                >
                  <span class="font-weight-bold">Note:</span> You cannot register an ownership transfer or change
                  because the home does not have a sole owner whose name matches your dealer's or manufacturer’s name.
                  Transfers can be registered by BC Registries staff or by a qualified lawyer or notary.
                </p>
                <HomeOwners
                  ref="homeOwnersComponentRef"
                  is-mhr-transfer
                  class="mt-10"
                  :class="{ 'mb-10': !hasUnsavedChanges }"
                  :validate-transfer="validate && !isChangeLocationActive && !isCancelChangeLocationActive &&
                    !isExtendChangeLocationActive"
                  @is-valid-transfer-owners="setValidation('isValidTransferOwners', $event)"
                />

                <TransferDetails
                  v-if="hasUnsavedChanges && !isChangeLocationActive && !isCancelChangeLocationActive &&
                    !isExtendChangeLocationActive"
                  ref="transferDetailsComponent"
                  class="mt-10"
                  :disable-prefill="isFrozenMhrDueToAffidavit"
                  :validate="validate"
                  @is-valid="setValidation('isTransferDetailsValid', $event)"
                />

                <UnitNotePanels
                  v-if="isRoleStaffReg"
                  id="unit-note-component"
                  class="mt-10"
                  :unit-notes="getMhrUnitNotes"
                  :disabled="!enableHomeOwnerChanges ||
                    showTransferType ||
                    isChangeLocationActive ||
                    isCancelChangeLocationActive"
                  :has-active-exemption="hasActiveExemption"
                />

                <v-spacer class="py-10 my-10" />
              </template>
            </section>
          </v-col>
          <v-col
            v-if="showTransferType || isReviewMode || isChangeLocationActive || isCancelChangeLocationActive ||
              isExtendChangeLocationActive"
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :set-show-buttons="true"
                :set-back-btn="showBackBtn"
                :set-cancel-btn="'Cancel'"
                :set-save-btn="(isChangeLocationActive || isCancelChangeLocationActive) ? '' : 'Save and Resume Later'"
                :set-submit-btn="reviewConfirmText"
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-err-msg="transferErrorMsg"
                :transfer-type="(isChangeLocationActive || isCancelChangeLocationActive || isExtendChangeLocationActive)
                  ? getUiFeeSummaryLocationType(transportPermitLocationType)
                  : getUiTransferType()"
                :set-is-loading="submitBtnLoading"
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
import type { Component } from 'vue';
import { computed, defineComponent, nextTick, onMounted, reactive, ref, toRefs, watch } from 'vue'
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
  APISearchTypes,
  ApiTransferTypes,
  MhApiStatusTypes,
  RouteNames,
  UIMHRSearchTypes,
  LocationChangeTypes,
  ErrorCategories,
  UnitNoteDocTypes,
  MhApiFrozenDocumentTypes,
  APIMhrTypes
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
import { HomeOwners } from '../index'
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
import MhrTransportPermit from './MhrTransportPermit.vue'
import { LocationChangeReview, TransportPermitDetails } from '@/components/mhrTransportPermits'
import {
  LocationChangeConfirmCompletion,
  TransportPermitConfirmCompletion,
  AmendTransportPermitConfirmCompletion,
  CancelTransportPermitConfirmCompletion
} from '@/components/mhrTransportPermits/ConfirmCompletionContent'
import type {
  AccountInfoIF,
  DialogOptionsIF,
  ErrorIF,
  MhrTransferApiIF,
  RegTableNewItemI,
  TransferTypeSelectIF,
  StaffPaymentIF,
} from '@/interfaces'
import {
  getAccountInfoFromAuth,
  getFeatureFlag,
  pacificDate,
  scrollToTop
} from '@/utils'
import {
  createMhrDraft,
  getMhrDraft,
  getMHRegistrationSummary,
  mhrSearch,
  submitAdminRegistration,
  submitMhrTransfer,
  updateMhrDraft
} from '@/utils/mhr-api-helper'

export default defineComponent({
  name: 'MhrInformation',
  components: {
    TransportPermitDetails,
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
    CancelTransportPermitConfirmCompletion,
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
    'emitHaveData',
    'actionInProgress'
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
      setMhrGenerateDocId,
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
      isRoleStaffSbc,
      isRoleStaffReg,
      isRoleManufacturer,
      isRoleQualifiedSupplier,
      hasEnhancedDealerEnabled,
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
      isCancelledMhr,
      getLienInfo,
      buildApiData,
      initMhrTransfer,
      getUiTransferType,
      parseMhrInformation,
      includesBlockingLien,
      initDraftMhrInformation,
      parseSubmittingPartyInfo,
      isFrozenMhrDueToUnitNote,
      hasQsTransferOrExemptionBlockingLien
    } = useMhrInformation()
    const {
      setValidation,
      getInfoValidation,
      isValidTransfer,
      isValidTransferReview,
      isValidTransportPermit,
      isValidTransportPermitReview,
      isValidExtendTransportPermit,
      scrollToFirstError,
      resetValidationState
    } = useMhrInfoValidation(getMhrInfoValidation.value)

    const {
      setGlobalEditingMode
    } = useHomeOwners(true)
    const { maxLength } = useInputRules()
    const {
      isTransferDueToDeath,
      isTransferNonGiftBillOfSale,
      isTransferWithoutBillOfSale,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will
    } = useTransferOwners()

    const { getActiveExemption } = useExemptions()
    const { buildLocationChange } = useMhrCorrections()
    const { disableDealerManufacturerTransfer, disableDealerManufacturerLocationChange } = useUserAccess()
    const {
      isNewPermitActive,
      isChangeLocationActive,
      isChangeLocationEnabled,
      isAmendLocationActive,
      isCancelChangeLocationActive,
      isTransportPermitDisabled,
      isRegisteredLocationChange,
      isExtendChangeLocationActive,
      isExemptMhrTransportPermitChangesEnabled,
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
      disableRoleBaseTransfer: false, // disabled state of transfer/change btn
      disableRoleBaseLocationChange: false, // disabled state of location change/transport permit btn
      submitBtnLoading: false,
      hasTransactionInProgress: false,
      reviewModeHeader: computed((): string =>
        isCancelChangeLocationActive.value ? 'Location of Home' :
          (isChangeLocationActive.value || isExtendChangeLocationActive) ? 'Location Change' :
        'Ownership Transfer or Change'
      ),
      isChangeOwnershipBtnDisabled: computed((): boolean => {
        if(isRoleStaffReg.value && hasLien.value && !isFrozenMhrDueToAffidavit.value){
          return false
        }

        const isFrozenMhr = isFrozenMhrDueToAffidavit.value || isFrozenMhrDueToUnitNote.value

        const isTransportPermitDisabled = isChangeLocationActive.value ||
          isAmendLocationActive.value || isCancelChangeLocationActive.value || isExtendChangeLocationActive.value

        const isRoleBasedTransferDisabled = !isRoleStaffReg.value && localState.disableRoleBaseTransfer

        return isFrozenMhr || isTransportPermitDisabled ||
          ((hasLien.value && hasQsTransferOrExemptionBlockingLien.value) || isRoleBasedTransferDisabled)
      }),

      // Transport Permit
      showCancelTransportPermitDialog: false,
      isTransportPermitDisabled: computed((): boolean =>
        localState.showTransferType ||
        (isExemptMhr.value && !isExemptMhrTransportPermitChangesEnabled.value) ||
        isTransportPermitDisabled.value ||
        (!isRoleStaffReg.value && isFrozenMhrDueToAffidavit.value)
      ),
      isTransportPermitByStaffSbc: computed((): boolean =>
        (isChangeLocationActive.value || isCancelChangeLocationActive.value) && isRoleStaffSbc.value),
      transportPermitLocationType: computed((): LocationChangeTypes => getMhrTransportPermit.value.locationChangeType),
      showInProgressMsg: computed((): boolean => {
        return localState.hasTransactionInProgress || (!isRoleStaffReg.value && isFrozenMhrDueToAffidavit.value)
      }),
      showHomeLocationReview: computed((): boolean => {
        return ![
          LocationChangeTypes.TRANSPORT_PERMIT,
          LocationChangeTypes.REGISTERED_LOCATION,
          LocationChangeTypes.EXTEND_PERMIT
        ].includes(localState.transportPermitLocationType)
      }),
      validateHomeLocationReview: computed((): boolean =>
        localState.validate &&
        isChangeLocationActive.value && // transport permit open
        localState.transportPermitLocationType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
      ),
      feeType: computed((): FeeSummaryTypes => {
        if (isAmendLocationActive.value && isChangeLocationActive.value) {
          return FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT
        } else if (isCancelChangeLocationActive.value) {
          return FeeSummaryTypes.MHR_TRANSPORT_PERMIT_CANCEL
        } else if (isExtendChangeLocationActive.value) {
          return FeeSummaryTypes.MHR_TRANSPORT_PERMIT
        } else {
          return isChangeLocationActive.value ? FeeSummaryTypes.MHR_TRANSPORT_PERMIT : FeeSummaryTypes.MHR_TRANSFER
        }
      }
      ),
      hasActiveExemption: computed((): boolean => !!getActiveExemption() ||
        getMhrInformation.value.statusType === MhApiStatusTypes.EXEMPT),
      transferRequiredDialogOptions: computed((): DialogOptionsIF => {
        const textArray = transferRequiredDialog.text.split(' mhr_number')
        return {
          ...transferRequiredDialog,
          text: `${textArray[0]} ${getMhrInformation.value.mhrNumber} ${textArray[1]}`
        }
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
          (isRoleQualifiedSupplier.value && hasQsTransferOrExemptionBlockingLien.value)) {
          return '< Lien on this home is preventing transfer'
        }

        let isValidReview

        if (isChangeLocationActive.value || isCancelChangeLocationActive.value) {
          // transport permit activated
          isValidReview = localState.isReviewMode
            ? isValidTransportPermitReview.value
            : isExtendChangeLocationActive.value ? isValidExtendTransportPermit.value : isValidTransportPermit.value
        } else {
          isValidReview = localState.isReviewMode ? isValidTransferReview.value : isValidTransfer.value
        }

        return localState.validate && !isValidReview ? '< Please complete required information' : ''
      }),
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      enableHomeOwnerChanges: computed((): boolean => {
        return !isRoleStaffSbc.value && getFeatureFlag('mhr-transfer-enabled')
      }),
      isDraft: computed((): string => {
        return getMhrInformation.value.draftNumber
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
      setMhrGenerateDocId(false)
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
        setMhrTransferType(StaffTransferTypes.find(type => type.transferType === ApiTransferTypes.SALE_OR_GIFT))
        await scrollToFirstError(false, 'home-owners-header')
      } else {
        // When not a draft Transfer, force no unsaved changes after loading current owners
        await setUnsavedChanges(false)
      }

      // Check for product based Transfer access
      switch(true) {
        case isRoleManufacturer.value:
          localState.disableRoleBaseTransfer = await disableDealerManufacturerTransfer()
          localState.disableRoleBaseLocationChange = await disableDealerManufacturerLocationChange()
          break
        case isRoleQualifiedSupplierHomeDealer.value:
          if (hasEnhancedDealerEnabled.value) break
          localState.disableRoleBaseTransfer = await disableDealerManufacturerTransfer(true)
          localState.disableRoleBaseLocationChange = await disableDealerManufacturerLocationChange(true)
          break
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
      if (hasLien.value && (isRoleQualifiedSupplier.value && hasQsTransferOrExemptionBlockingLien.value)) {
        await scrollToFirstError(true)
        return
      }

      // If already in review mode, file the transfer
      if (localState.isReviewMode) {
        localState.submitBtnLoading = true

        // 1 - Check if any required fields have errors
        const isValidReview: boolean =
          (isChangeLocationActive.value || isAmendLocationActive.value || isCancelChangeLocationActive.value ||
            isExtendChangeLocationActive)
            ? isValidTransportPermitReview.value
            : isValidTransferReview.value

        if (localState.isReviewMode && !isValidReview) {
          await scrollToFirstError(false)
          localState.submitBtnLoading = false
          return
        }

        // 2 - Verify no lien exists prior to submitting filing
        const regSum = !localState.hasLienInfoDisplayed
          ? await getMHRegistrationSummary(getMhrInformation.value.mhrNumber, false)
          : null

        if (!!regSum && !!regSum.lienRegistrationType && includesBlockingLien(regSum.lienRegistrationType) &&
          !isRoleStaffReg.value) {
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

        // 3 - Complete Filing
        localState.loading = true

        // 3a - Submit Location Change or Cancel Transport Permit
        if(isRegisteredLocationChange.value || isCancelChangeLocationActive.value) {

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

        // 3b - Submit Transport Permit
        if (isChangeLocationActive.value || isExtendChangeLocationActive.value) {
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

        // 3c - Submit Transfer filing
        const apiData: MhrTransferApiIF = await buildApiData()

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
            await setMhrTransferType(StaffTransferTypes
              .find(type => type.transferType === ApiTransferTypes.SALE_OR_GIFT))
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
      if (isValidTransfer.value || isValidTransportPermit.value ||
        (isExtendChangeLocationActive.value && isValidExtendTransportPermit.value)) {
        localState.isReviewMode = true
        localState.validate = false
        scrollToTop()
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
      const draftType = (isTransferNonGiftBillOfSale.value || isTransferWithoutBillOfSale.value)
        ? APIMhrTypes.TRANSFER_OF_SALE
        : getMhrTransferType.value?.transferType

      const mhrTransferDraft = getMhrInformation.value.draftNumber
        ? await updateMhrDraft(getMhrInformation.value.draftNumber, draftType, apiData)
        : await createMhrDraft(draftType, apiData)

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
        await resetTransportPermit(true)
        resetValidationState()
        localState.validate = false
        localState.isReviewMode = false
        setMhrGenerateDocId(false)
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

    const handleCancelTransportPermitChanges = (showConfirmationDialog = true) => {
      if (hasUnsavedChanges.value && showConfirmationDialog) {
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

    watch(() => getMhrInformation.value.frozenDocumentType, val => {
      localState.hasAlertMsg = QSLockedStateUnitNoteTypes.includes(val)
    })

    watch(() => localState.transportPermitLocationType, val => {
      if (val === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK) {
        populateLocationInfoForSamePark(getMhrRegistrationLocation.value)
        setUnsavedChanges(false)
      }
    })

    /** Inform root level components when there is an MHR action in Progress **/
    watch(() => [
      localState.showTransferType, isChangeLocationActive.value, localState.isReviewMode
    ], (watchedConditions) => {
      context.emit('actionInProgress', watchedConditions.includes(true))
    }, { immediate: true })

    return {
      isNewPermitActive,
      isRoleStaffSbc,
      isRoleStaffReg,
      isFrozenMhr,
      isFrozenMhrDueToAffidavit,
      isExemptMhr,
      isCancelledMhr,
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
      isTransferWithoutBillOfSale,
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
      isCancelChangeLocationActive,
      isExtendChangeLocationActive,
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
@import '@/assets/styles/theme';
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
