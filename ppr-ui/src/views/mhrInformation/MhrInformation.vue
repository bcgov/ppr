<template>
  <v-container class="view-container pa-0" fluid>
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

    <BaseDialog
      :setOptions="cancelOptions"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />

    <BaseDialog
      :setOptions="saveOptions"
      :setDisplay="showSaveDialog"
      @proceed="handleDialogResp($event)"
    />

    <BaseDialog
      :setOptions="cancelOwnerChangeConfirm"
      :setDisplay="showCancelChangeDialog"
      @proceed="handleCancelDialogResp($event)"
    />

    <div class="view-container px-15 pt-0 pb-5">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="mhr-information-header" class="pt-3 soft-corners-top">
              <v-col cols="auto">
                <h1>{{ isReviewMode ? 'Review and Confirm' : 'Manufactured Home Information' }}</h1>
                <template v-if="!isReviewMode">
                  <p class="mt-7">
                    This is the current information for this registration as of
                    <span class="font-weight-bold">{{ asOfDateTime }}</span>.
                  </p>
                  <p class="mt-n2">Ensure ALL of the information below is correct before making any changes to this
                    registration. Necessary fees will be applied as updates are made.</p>
                </template>
                <p class="mt-7" v-else>
                  Review your changes and complete the additional information before registering.
                </p>
              </v-col>
            </v-row>

            <!-- Lien Information -->
            <v-row v-if="hasLien" id="lien-information" no-gutters>
              <v-card outlined id="important-message" class="rounded-0 mt-2 pt-5 px-5">
                <v-icon color="error" class="float-left mr-2 mt-n1">mdi-alert</v-icon>
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
                  outlined
                  color="primary"
                  class="mt-2 px-6"
                  :ripple="false"
                  data-test-id="lien-search-btn"
                  @click="quickMhrSearch(getMhrInformation.mhrNumber)"
                >
                  <v-icon class="pr-1">mdi-magnify</v-icon>
                  Conduct a Combined MHR and PPR Search for MHR Number
                  <strong>{{ getMhrInformation.mhrNumber }}</strong>
                </v-btn>
                <v-divider class="mx-0 mt-10 mb-6" />
              </v-col>
            </v-row>

            <header id="yellow-message-bar" class="message-bar" v-if="isReviewMode">
              <label><b>Important:</b> This information must match the information on the bill of sale.</label>
            </header>

            <!-- Mhr Information Body -->
            <section v-if="dataLoaded" class="py-4">

              <!-- MHR Information Review Section -->
              <template v-if="isReviewMode" data-test-id="review-mode">
                <!-- Review Header -->
                <header class="review-header mt-1 rounded-top">
                  <v-icon class="ml-2" color="darkBlue">mdi-file-document-multiple</v-icon>
                  <label class="font-weight-bold pl-2">Ownership Transfer or Change</label>
                </header>

                <section id="owners-review">
                  <HomeOwners
                    isMhrTransfer
                    isReadonlyTable
                    :homeOwners="reviewOwners"
                    :currentHomeOwners="getMhrTransferCurrentHomeOwnerGroups"
                  />
                </section>

                <section>
                  <v-divider class="mx-7 ma-0"></v-divider>
                  <TransferDetailsReview class="py-6 pt-4 px-8" />
                </section>

                <section v-if="isRoleStaffReg" id="staff-transfer-submitting-party" class="submitting-party">
                  <h2>1. Submitting Party for this Change</h2>
                  <p class="mt-2 mb-6">
                    Provide the name and contact information for the person or business submitting this registration.
                    You can add the submitting party information manually, or, if the submitting party has a Personal
                    Property Registry party code, you can look up the party code or name.
                  </p>

                  <PartySearch isMhrPartySearch isMhrTransfer />

                  <MhrSubmittingParty
                    :validate="validateSubmittingParty"
                    :class="{ 'border-error-left': validateSubmittingParty }"
                    @isValid="setValidation('isSubmittingPartyValid', $event)"
                    :content="{ mailAddressInfo: 'Registry documents and decal will be mailed to this address.' }"
                    isMhrTransfer
                  />
                </section>

                <section v-else id="transfer-submitting-party" class="submitting-party">
                  <AccountInfo
                    title="Submitting Party for this Change"
                    tooltipContent="The default Submitting Party is based on your BC Registries
                       user account information. This information can be updated within your account settings."
                    :accountInfo="accountInfo"
                  />
                </section>

                <section id="transfer-ref-num-section" class="mt-10 py-4">
                  <h2>{{ isRoleStaffReg ? '2.' : '1.'}} Attention or Reference Number</h2>
                  <p class="mt-2">
                    Add an optional Attention or Reference Number information for this transaction. If entered, it will
                    appear on the Transfer Verification document.
                  </p>
                  <v-card
                    flat
                    rounded
                    id="attention-or-reference-number-card"
                    class="mt-8 pa-8 pr-6 pb-3"
                    :class="{ 'border-error-left': !getInfoValidation('isRefNumValid') }"
                    data-test-id="attn-ref-number-card"
                  >
                    <v-form ref="reference-number-form" v-model="refNumValid">
                      <v-row no-gutters class="pt-3">
                        <v-col cols="3">
                          <label
                            class="generic-label"
                            :class="{ 'error-text': !getInfoValidation('isRefNumValid') }"
                          >
                            Attention or Reference Number
                          </label>
                        </v-col>
                        <v-col cols="9" class="px-1">
                          <v-text-field
                            filled
                            id="attention-or-reference-number"
                            class="pr-2"
                            label="Attention or Reference Number (Optional)"
                            v-model="attentionReference"
                            :rules="maxLength(40)"
                            data-test-id="attn-ref-number-field"
                          />
                        </v-col>
                      </v-row>
                    </v-form>
                  </v-card>
                </section>

                <section id="transfer-confirm-section" class="mt-10 transfer-confirm">
                  <ConfirmCompletion
                    :sectionNumber="isRoleStaffReg ? 3 : 2"
                    :legalName="getCertifyInformation.legalName"
                    :setShowErrors="validateConfirmCompletion"
                    @confirmCompletion="setValidation('isCompletionConfirmed', $event)"
                  />
                </section>

                <section id="transfer-certify-section" class="mt-10 pt-4">
                  <CertifyInformation
                    :sectionNumber="isRoleStaffReg ? 4 : 3"
                    :setShowErrors="validateAuthorizationError"
                    @certifyValid="setValidation('isAuthorizationValid', $event)"
                  />
                </section>

                <section id="staff-transfer-payment-section" class="mt-10 pt-4 pb-10" v-if="isRoleStaffReg">
                  <h2>
                    5. Staff Payment
                  </h2>
                  <v-card flat class="mt-6 pa-6" :class="{ 'border-error-left': validateStaffPayment }">
                    <StaffPayment
                      id="staff-payment"
                      :displaySideLabel="true"
                      :displayPriorityCheckbox="true"
                      :staffPaymentData="staffPayment"
                      :invalidSection="validateStaffPayment"
                      :validate="validate"
                      @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
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
                <div class="pt-4">
                  <HomeLocationReview isTransferReview />
                </div>

                <!-- Home Owners Header -->
                <header class="review-header mt-10 rounded-top">
                  <v-row no-gutters align="center">
                    <v-col cols="10">
                      <img class="icon-img pb-1" src="@/assets/svgs/homeownersicon_reviewscreen.svg" />
                      <span class="font-weight-bold pl-1">Home Owners</span>
                    </v-col>
                    <v-col cols="2" class="text-right">
                      <v-btn
                        text id="home-owners-change-btn"
                        class="pl-1"
                        color="primary"
                        :ripple="false"
                        @click="toggleTypeSelector()"
                      >
                        <span v-if="!showTransferType">
                          <v-icon color="primary" small>mdi-pencil</v-icon> Change
                        </span>
                        <span v-else>
                          <v-icon color="primary" small>mdi-close</v-icon> Cancel Owner Change
                        </span>
                      </v-btn>
                    </v-col>
                  </v-row>
                </header>

                <!-- Transfer Type Component -->
                <v-expand-transition>
                  <TransferType
                    v-if="showTransferType"
                    :validate="validate"
                    @emitType="handleTransferTypeChange($event)"
                    @emitDeclaredValue="handleDeclaredValueChange($event)"
                    @emitValid="setValidation('isValidTransferType', $event)"
                  />
                </v-expand-transition>

                <HomeOwners
                  isMhrTransfer
                  class="mt-n2"
                  ref="homeOwnersComponentRef"
                  :class="{ 'mb-10': !hasUnsavedChanges }"
                  :validateTransfer="validate"
                  @isValidTransferOwners="setValidation('isValidTransferOwners', $event)"
                />

                <TransferDetails
                  v-if="hasUnsavedChanges"
                  ref="transferDetailsComponent"
                  :validate="!isTransferDueToDeath && validate"
                  @isValid="setValidation('isTransferDetailsValid', $event)"
                />
              </template>
            </section>
          </v-col>
          <v-col class="pl-6 pt-5" cols="3" v-if="showMhrFeeSummary || isReviewMode">
            <aside>
              <affix class="sticky-container" relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setShowButtons="true"
                  :setBackBtn="showBackBtn"
                  :setCancelBtn="'Cancel'"
                  :setSaveBtn="'Save and Resume Later'"
                  :setSubmitBtn="reviewConfirmText"
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setErrMsg="transferErrorMsg"
                  :transferType="getUiTransferType()"
                  @cancel="goToDash()"
                  @back="isReviewMode = false"
                  @save="onSave()"
                  @submit="goToReview()"
                  data-test-id="fee-summary"
                />
              </affix>
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import { CertifyInformation, StickyContainer } from '@/components/common'
import { useHomeOwners, useInputRules, useMhrInformation, useMhrInfoValidation, useTransferOwners } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { PartySearch } from '@/components/parties/party'
import { MhrSubmittingParty } from '@/components/mhrRegistration/SubmittingParty'
import { ConfirmCompletion, TransferDetails, TransferDetailsReview, TransferType } from '@/components/mhrTransfers'
import { HomeLocationReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { HomeOwners } from '@/views'
import { BaseDialog } from '@/components/dialogs'
import { BaseAddress } from '@/composables/address'
import { registrationSaveDraftError, unsavedChangesDialog, cancelOwnerChangeConfirm } from '@/resources/dialogOptions'
import AccountInfo from '@/components/common/AccountInfo.vue'
/* eslint-disable no-unused-vars */
import {
  AccountInfoIF,
  MhrTransferApiIF,
  RegTableNewItemI,
  TransferTypeSelectIF
} from '@/interfaces'
import {
  StaffPaymentIF
} from '@bcrs-shared-components/interfaces'
import {
  ActionTypes,
  APIMHRMapSearchTypes,
  APISearchTypes,
  RouteNames,
  UIMHRSearchTypes,
  UITransferTypes
} from '@/enums'
import {
  createMhrTransferDraft,
  deleteMhrDraft,
  getAccountInfoFromAuth,
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
    BaseAddress,
    BaseDialog,
    HomeOwners,
    PartySearch,
    MhrSubmittingParty,
    TransferType,
    TransferDetails,
    TransferDetailsReview,
    HomeLocationReview,
    HomeOwnersTable,
    StickyContainer,
    CertifyInformation,
    AccountInfo,
    ConfirmCompletion,
    YourHomeReview,
    StaffPayment
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const {
      getMhrTransferHomeOwners,
      getMhrInformation,
      getMhrTransferCurrentHomeOwnerGroups,
      getCertifyInformation,
      hasUnsavedChanges,
      hasLien,
      isRoleStaffReg,
      isRoleQualifiedSupplier,
      getMhrTransferType,
      getMhrTransferDeclaredValue,
      getMhrInfoValidation,
      getMhrTransferSubmittingParty
    } = useGetters<any>([
      'getMhrTransferHomeOwners',
      'getMhrInformation',
      'getMhrTransferCurrentHomeOwnerGroups',
      'getCertifyInformation',
      'hasUnsavedChanges',
      'hasLien',
      'isRoleStaffReg',
      'isRoleQualifiedSupplier',
      'getMhrTransferType',
      'getMhrTransferDeclaredValue',
      'getMhrInfoValidation',
      'getMhrTransferSubmittingParty'
    ])

    const {
      setMhrTransferSubmittingParty,
      setMhrTransferAttentionReference,
      setUnsavedChanges,
      setRegTableNewItem,
      setSearchedType,
      setManufacturedHomeSearchResults,
      setLienType,
      setMhrTransferType,
      setMhrTransferDeclaredValue,
      setEmptyMhrTransfer,
      setStaffPayment
    } = useActions<any>([
      'setMhrTransferSubmittingParty',
      'setMhrTransferAttentionReference',
      'setUnsavedChanges',
      'setRegTableNewItem',
      'setSearchedType',
      'setManufacturedHomeSearchResults',
      'setLienType',
      'setMhrTransferType',
      'setMhrTransferDeclaredValue',
      'setEmptyMhrTransfer',
      'setStaffPayment'
    ])

    // Composable Instances
    const {
      initMhrTransfer,
      buildApiData,
      getUiTransferType,
      parseMhrInformation,
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
      isTransferDueToDeath
    } = useTransferOwners()

    // Refs
    const homeOwnersComponentRef = ref(null)
    const transferDetailsComponent = ref(null)

    const localState = reactive({
      dataLoaded: false,
      loading: false,
      isReviewMode: false,
      validate: false,
      showMhrFeeSummary: false,
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
      showTransferType: false,
      attentionReference: '',
      cancelOptions: unsavedChangesDialog,
      saveOptions: registrationSaveDraftError,
      showCancelDialog: false,
      showSaveDialog: false,
      showCancelChangeDialog: false,
      hasTransferChanges: computed((): boolean => {
        return localState.showTransferType &&
          (hasUnsavedChanges.value || !!getMhrTransferDeclaredValue.value || !!getMhrTransferType.value)
      }),
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
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
      validateStaffPayment: computed(() => {
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
      reviewOwners: computed(() => {
        return getMhrTransferHomeOwners.value.filter(owner => owner.action !== ActionTypes.REMOVED)
      }),
      /** True if Jest is running the code. */
      isJestRunning: computed((): boolean => {
        return process.env.JEST_WORKER_ID !== undefined
      })
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !localState.isAuthenticated) {
        goToDash()
        return
      }
      // page is ready to view
      context.emit('emitHaveData', true)

      localState.loading = true
      setEmptyMhrTransfer(initMhrTransfer())

      // Set baseline MHR Information to state
      await parseMhrInformation()

      // When not a draft Transfer, force no unsaved changes after loading current owners
      !getMhrInformation.value.draftNumber && (await setUnsavedChanges(false))

      if (isRoleQualifiedSupplier.value && !isRoleStaffReg.value) {
        // Get Account Info from Auth to be used in Submitting Party section in Review screen
        localState.accountInfo = await getAccountInfoFromAuth() as AccountInfoIF
        parseSubmittingPartyInfo(localState.accountInfo)
      }
      localState.loading = false
      localState.dataLoaded = true
    })

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
        const apiData = await buildApiData()
        // Submit Transfer filing
        const mhrTransferFiling =
          await submitMhrTransfer(apiData, getMhrInformation.value.mhrNumber, localState.staffPayment)
        localState.loading = false

        if (!mhrTransferFiling.error) {
          setUnsavedChanges(false)
          // Delete the draft on successful submission
          if (getMhrInformation.value.draftNumber) await deleteMhrDraft(getMhrInformation.value.draftNumber)
          const newItem: RegTableNewItemI = {
            addedReg: mhrTransferFiling.documentId,
            addedRegParent: getMhrInformation.value.mhrNumber,
            addedRegSummary: null,
            prevDraft: mhrTransferFiling.documentId || ''
          }
          setRegTableNewItem(newItem)
          goToDash()
        } else console.log(mhrTransferFiling?.error) // Handle Schema or Api errors here.
      }

      // If transfer is valid, enter review mode
      if (isValidTransfer.value) {
        localState.isReviewMode = true
        localState.validate = false
      }

      // Force show removed/deceased homeOwners when invalid
      if (!getInfoValidation('isValidTransferOwners')) {
        (context.refs.homeOwnersComponentRef as any).hideShowRemovedOwners(true)
      }

      await nextTick()
      // Scroll to the top of review screen
      await scrollToFirstError(isValidTransfer.value)
    }

    const onSave = async (): Promise<void> => {
      localState.loading = true
      const apiData = await buildApiData(true)

      const mhrTransferDraft = getMhrInformation.value.draftNumber
        ? await updateMhrDraft(getMhrInformation.value.draftNumber, apiData)
        : await createMhrTransferDraft(apiData)
      if (!getMhrInformation.value.draftNumber) {
        const mhrDraft = mhrTransferDraft as MhrTransferApiIF
        const newItem: RegTableNewItemI = {
          addedReg: mhrDraft.draftNumber,
          addedRegParent: apiData.mhrNumber,
          addedRegSummary: null,
          prevDraft: (getMhrInformation.value.changes && getMhrInformation.value.changes[0].documentId) || ''
        }
        setRegTableNewItem(newItem)
      }
      localState.loading = false
      if (!mhrTransferDraft.error) {
        setUnsavedChanges(false)
        goToDash()
      } else {
        localState.showSaveDialog = true
        console.error(mhrTransferDraft?.error)
      }
    }

    const goToDash = (): void => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else {
        setUnsavedChanges(false)
        setGlobalEditingMode(false)
        setEmptyMhrTransfer(initMhrTransfer())
        resetValidationState()

        context.root.$router.push({
          name: RouteNames.DASHBOARD
        })
      }
    }

    const handleDialogResp = (val: boolean): void => {
      if (!val) {
        setUnsavedChanges(false)
        if (localState.showCancelDialog) {
          goToDash()
        }
      }
      localState.showCancelDialog = false
      localState.showSaveDialog = false
    }

    const handleCancelDialogResp = async (val: boolean): Promise<void> => {
      if (!val) {
        localState.showCancelChangeDialog = false
        return
      }
      localState.showCancelChangeDialog = false
      localState.showTransferType = false
      localState.showMhrFeeSummary = false

      localState.loading = true
      await resetMhrInformation()
      localState.loading = false
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
        await context.root.$router.replace({
          name: RouteNames.MHRSEARCH
        })
      } else {
        console.error('Error: MHR_NUMBER expected, but not found.')
      }
    }

    const resetMhrInformation = async (): Promise<void> => {
      // Set baseline MHR Information to state
      await parseMhrInformation()
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
      localState.showMhrFeeSummary = localState.showTransferType
    }

    const handleTransferTypeChange = async (transferTypeSelect: TransferTypeSelectIF): Promise<void> => {
      // Reset state until support is built for other Transfer Types
      if (localState.hasTransferChanges && transferTypeSelect?.transferType &&
        (transferTypeSelect?.transferType !== getMhrTransferType.value?.transferType)
      ) await resetMhrInformation()

      localState.showTransferChangeDialog = true
      await setMhrTransferType(transferTypeSelect)
    }

    const handleDeclaredValueChange = async (declaredValue: number): Promise<void> => {
      await setMhrTransferDeclaredValue(declaredValue)
    }
    watch(() => localState.attentionReference, (val: string) => {
      setMhrTransferAttentionReference(val)
    })
    watch(() => isValidTransfer.value, (val: boolean) => {
      if (val) localState.validate = false
    })
    watch(() => localState.refNumValid, (isValid: boolean) => {
      setValidation('isRefNumValid', isValid)
    })

    watch(() => hasUnsavedChanges.value, (val: boolean) => {
      if (!val && context.refs.transferDetailsComponent) {
        (context.refs.transferDetailsComponent as any).clearTransferDetailsData()
      }
    })

    return {
      setValidation,
      getInfoValidation,
      hasUnsavedChanges,
      goToReview,
      onSave,
      goToDash,
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
      setMhrTransferSubmittingParty,
      handleTransferTypeChange,
      getUiTransferType,
      handleDeclaredValueChange,
      toggleTypeSelector,
      onStaffPaymentDataUpdate,
      handleCancelDialogResp,
      cancelOwnerChangeConfirm,
      getMhrTransferSubmittingParty,
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

.message-bar {
  font-size: 14px;
  padding: 1.25rem;
  background-color: $BCgovGold0;
  border: 1px solid $BCgovGold5;
  color: $gray7;
  margin-top: 10px;
  margin-bottom: 20px;
}

::v-deep {
  #home-owners-change-btn {
    height: unset;
  }
  .icon-img {
    vertical-align: middle;
  }
}
</style>
