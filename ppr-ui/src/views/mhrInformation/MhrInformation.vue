<template>
  <v-container class="view-container pa-0" fluid>
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

    <base-dialog
      :setOptions="cancelOptions"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <base-dialog
      :setOptions="saveOptions"
      :setDisplay="showSaveDialog"
      @proceed="handleDialogResp($event)"
    />
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="mhr-information-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>{{ isReviewMode ? 'Review and Confirm' : 'Manufactured Home Information' }}</h1>
                <p class="mt-7" v-if="!isReviewMode">
                  This is the current information for this registration as of
                  <span class="font-weight-bold">{{ asOfDateTime }}</span>.
                </p>
                <p class="mt-7" v-else>
                  Review your changes and complete the additional information before registering.
                </p>
              </v-col>
            </v-row>
            <header id="yellow-message-bar" class="message-bar" v-if="isReviewMode">
              <label><b>Important:</b> This information must match the information on the bill of sale.</label>
            </header>
            <section v-if="dataLoaded" class="py-4">
              <header class="review-header mt-1">
                <v-icon class="ml-1" color="darkBlue">mdi-home</v-icon>
                <label class="font-weight-bold pl-2">
                  {{ isReviewMode ? 'Ownership Transfer or Change - Sale or Beneficiary' : 'Home Owners' }}
                </label>
              </header>

              <!-- MHR Information Review Section -->
              <template v-if="isReviewMode" data-test-id="review-mode">
                <section id="owners-review">
                  <HomeOwners
                    isMhrTransfer
                    isReadonlyTable
                    :homeOwners="reviewOwners"
                    :currentHomeOwners="getMhrTransferCurrentHomeOwners"
                  />
                </section>
                <section>
                  <v-divider class="mx-7 ma-0"></v-divider>
                  <TransferDetailsReview class="py-6 pt-4 px-8" />
                </section>
                <section id="transfer-submitting-party" class="submitting-party">
                  <AccountInfo
                    title="Submitting Party for this Change"
                    tooltipContent="The default Submitting Party is based on your BC Registries
                       user account information. This information can be updated within your account settings."
                    :accountInfo="accountInfo"
                  />
                </section>

                <section id="transfer-ref-num-section" class="mt-10 py-4">
                  <h2>1. Attention or Reference Number</h2>
                  <p class="mt-2">
                    Add an optional Attention or Reference Number information for this transaction. If entered, it will
                    appear on the Transfer Verification document.
                  </p>
                  <v-card
                    flat
                    rounded
                    id="attention-or-reference-number-card"
                    class="mt-8 pa-8 pr-6 pb-3"
                    :class="{ 'border-error-left': !isRefNumValid }"
                    data-test-id="attn-ref-number-card"
                  >
                    <v-form ref="reference-number-form" v-model="refNumValid">
                      <v-row no-gutters class="pt-3">
                        <v-col cols="3">
                          <label class="generic-label" :class="{ 'error-text': !isRefNumValid }">
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
                    :legalName="getCertifyInformation.legalName"
                    :setShowErrors="validateConfirmCompletion"
                    @confirmCompletion="isCompletionConfirmed = $event"
                  />
                </section>

                <section id="transfer-certify-section" class="mt-10 py-4">
                  <CertifyInformation
                    :sectionNumber=3
                    :setShowErrors="validateAuthorizationError"
                    @certifyValid="authorizationValid = $event"
                  />
                </section>
              </template>

              <!-- MHR Information Section -->
              <template v-else>
                <HomeOwners isMhrTransfer class="mt-n2" />
                <TransferDetails v-if="hasUnsavedChanges" ref="transferDetailsComponent" />
              </template>
            </section>
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
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
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { ActionTypes, RouteNames } from '@/enums'
import {
  createMhrTransferDraft,
  deleteMhrDraft,
  fetchMhRegistration,
  getAccountInfoFromAuth,
  getMhrTransferDraft,
  pacificDate,
  submitMhrTransfer,
  updateMhrDraft
} from '@/utils'
import { StickyContainer, CertifyInformation } from '@/components/common'
import { useHomeOwners, useInputRules, useMhrInformation } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { TransferDetails, TransferDetailsReview, ConfirmCompletion } from '@/components/mhrTransfers'
import { HomeOwners } from '@/views'
import { BaseDialog } from '@/components/dialogs'
import { BaseAddress } from '@/composables/address'
import { unsavedChangesDialog, registrationSaveDraftError } from '@/resources/dialogOptions'
import { cloneDeep } from 'lodash'
import AccountInfo from '@/components/common/AccountInfo.vue'
import { AccountInfoIF, MhrTransferApiIF, RegTableNewItemI } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'MhrInformation',
  components: {
    BaseAddress,
    BaseDialog,
    HomeOwners,
    TransferDetails,
    TransferDetailsReview,
    HomeOwnersTable,
    StickyContainer,
    CertifyInformation,
    AccountInfo,
    ConfirmCompletion
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    isMhrTransfer: {
      type: Boolean,
      default: true
    }
  },
  // eslint-disable-next-line
  setup (props, context) {
    const {
      getMhrTransferHomeOwners,
      getMhrInformation,
      getMhrTransferCurrentHomeOwners,
      getCertifyInformation,
      hasUnsavedChanges
    } = useGetters<any>([
      'getMhrTransferHomeOwners',
      'getMhrInformation',
      'getMhrTransferCurrentHomeOwners',
      'getCertifyInformation',
      'hasUnsavedChanges'
    ])

    const {
      setMhrTransferHomeOwnerGroups,
      setMhrTransferCurrentHomeOwnerGroups,
      setMhrTransferAttentionReference,
      setUnsavedChanges,
      setRegTableNewItem
    } = useActions<any>([
      'setMhrTransferHomeOwnerGroups',
      'setMhrTransferCurrentHomeOwnerGroups',
      'setMhrTransferAttentionReference',
      'setUnsavedChanges',
      'setRegTableNewItem'
    ])

    const { setEmptyMhrTransfer } = useActions<any>(['setEmptyMhrTransfer'])

    const {
      isRefNumValid,
      setRefNumValid,
      initMhrTransfer,
      buildApiData
    } = useMhrInformation()

    const {
      isGlobalEditingMode,
      setGlobalEditingMode,
      setShowGroups
    } = useHomeOwners(props.isMhrTransfer)

    const { maxLength } = useInputRules()

    const transferDetailsComponent = ref(null)

    const localState = reactive({
      dataLoaded: false,
      loading: false,
      isReviewMode: false,
      validate: false,
      isTransferDetailsFormValid: false,
      refNumValid: false,
      authorizationValid: false,
      validateConfirmCompletion: false,
      validateAuthorizationError: false,
      accountInfo: null,
      feeType: FeeSummaryTypes.MHR_TRANSFER, // FUTURE STATE: To be dynamic, dependent on what changes have been made
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      asOfDateTime: computed((): string => {
        return `${pacificDate(new Date())}`
      }),
      showBackBtn: computed((): string => {
        return localState.isReviewMode ? 'Back' : ''
      }),
      isValidTransfer: computed((): boolean => {
        // is valid on first step
        // TODO: Add Home Owner validation check here
        return !isGlobalEditingMode.value && localState.isTransferDetailsFormValid && true
      }),
      isValidTransferReview: computed((): boolean => {
        // is valid on review step
        return (
          localState.isReviewMode &&
          isRefNumValid.value &&
          localState.isCompletionConfirmed &&
          !localState.validateAuthorizationError
        )
      }),
      transferErrorMsg: computed((): string => {
        const isValidReview = localState.isReviewMode ? !localState.isValidTransferReview : !localState.isValidTransfer
        const errorMsg = localState.isReviewMode
          ? '< Please complete required information'
          : '< Please make any required changes'
        return localState.validate && isValidReview ? errorMsg : ''
      }),
      reviewConfirmText: computed((): string => {
        return localState.isReviewMode ? 'Register Changes and Pay' : 'Review and Confirm'
      }),
      reviewOwners: computed(() => {
        return getMhrTransferHomeOwners.value.filter(owner => owner.action !== ActionTypes.REMOVED)
      }),
      attentionReference: '',
      isCompletionConfirmed: false,
      cancelOptions: unsavedChangesDialog,
      saveOptions: registrationSaveDraftError,
      showCancelDialog: false,
      showSaveDialog: false
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
      localState.accountInfo = await getSubmittingPartyInformation()
      localState.loading = false

      localState.dataLoaded = true
      await setUnsavedChanges(false)
    })

    // Future state to parse all relevant MHR Information
    const parseMhrInformation = async (): Promise<void> => {
      await parseCurrentOwnerGroups()
    }

    // Get Account Info from Auth to be used in Submitting Party section in Review screen
    const getSubmittingPartyInformation = async (): Promise<AccountInfoIF> => {
      return getAccountInfoFromAuth()
    }

    const parseCurrentOwnerGroups = async (): Promise<void> => {
      const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)
      const currentOwnerGroups = data?.ownerGroups || [] // Safety check. Should always have ownerGroups

      // Store a snapshot of the existing OwnerGroups for baseline of current state
      await setMhrTransferCurrentHomeOwnerGroups(cloneDeep(data.ownerGroups))

      currentOwnerGroups.forEach((ownerGroup, index) => {
        ownerGroup.groupId = index + 1
      })
      setShowGroups(currentOwnerGroups.length > 1)

      // Set owners to store
      if (getMhrInformation.value.draftNumber) {
        // Retrieve owners from draft if it exists
        const { registration } = await getMhrTransferDraft(getMhrInformation.value.draftNumber)

        setShowGroups(registration.addOwnerGroups.length > 1 || registration.deleteOwnerGroups.length > 1)
        setMhrTransferHomeOwnerGroups([...registration.addOwnerGroups])
      } else {
        // Set current owners if there is no draft
        setMhrTransferHomeOwnerGroups(currentOwnerGroups)
      }
    }

    const scrollToFirstError = async () => {
      setTimeout(() => {
        document.getElementsByClassName('border-error-left')[0].scrollIntoView({ behavior: 'smooth' })
      }, 10)
    }

    const goToReview = async (): Promise<void> => {
      localState.validate = true

      // If already in review mode, file the transfer
      if (localState.isReviewMode) {
        // Trigger error state for required fields (if not checked)
        localState.validateAuthorizationError = !localState.authorizationValid
        localState.validateConfirmCompletion = !localState.isCompletionConfirmed

        // Check if any required fields have errors
        if (!localState.isValidTransferReview) {
          await scrollToFirstError()
          return
        }
        localState.loading = true
        const apiData = await buildApiData()
        const mhrTransferFiling = await submitMhrTransfer(apiData, getMhrInformation.value.mhrNumber)
        localState.loading = false
        if (!mhrTransferFiling.error) {
          setUnsavedChanges(false)
          // Delete the draft on successful submission
          if (getMhrInformation.value.draftNumber) await deleteMhrDraft(getMhrInformation.value.draftNumber)
          goToDash()
        } else console.log(mhrTransferFiling?.error) // Handle Schema or Api errors here.
      }

      const transferDetailsComponent = context.refs.transferDetailsComponent as any

      // Check if TransferDetails exists on the screen
      if (transferDetailsComponent) {
        localState.isTransferDetailsFormValid = await transferDetailsComponent.validateDetailsForm()
      }

      // If transfer is valid, enter review mode
      if (localState.isValidTransfer) {
        localState.isReviewMode = true
        localState.validate = false
      } else {
        await scrollToFirstError()
      }
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
          addedReg: String(mhrDraft.draftNumber),
          addedRegParent: apiData.mhrNumber,
          addedRegSummary: null,
          prevDraft: String(getMhrInformation.value.changes[0].documentId) || ''
        }
        setRegTableNewItem(newItem)
      }
      localState.loading = false
      if (!mhrTransferDraft.error) {
        setUnsavedChanges(false)
        goToDash()
      } else {
        localState.showSaveDialog = true
        console.log(mhrTransferDraft?.error)
      }
    }

    const goToDash = (): void => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else {
        setUnsavedChanges(false)
        setGlobalEditingMode(false)
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

    watch(
      () => localState.attentionReference,
      (val: string) => {
        setMhrTransferAttentionReference(val)
      }
    )

    watch(
      () => localState.refNumValid,
      (isFormValid: boolean) => {
        setRefNumValid(isFormValid)
      }
    )

    watch(
      () => localState.authorizationValid,
      (isValid: boolean) => {
        localState.validateAuthorizationError = !isValid
      }
    )

    watch(
      () => localState.isCompletionConfirmed,
      (isValid: boolean) => {
        localState.validateConfirmCompletion = !isValid
      }
    )

    return {
      hasUnsavedChanges,
      goToReview,
      onSave,
      goToDash,
      getMhrTransferHomeOwners,
      getMhrTransferCurrentHomeOwners,
      getCertifyInformation,
      maxLength,
      isRefNumValid,
      ...toRefs(localState),
      transferDetailsComponent,
      handleDialogResp
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
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
</style>
