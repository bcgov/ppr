<template>
  <v-container
    id="confirm-renewal"
    class="pt-14 px-0"
    fluid
    style="min-width: 960px;"
  >
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
      set-attach="#confirm-renewal"
      :set-options="options"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <StaffPaymentDialog
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
        <v-col cols="9">
          <h1>Review and Complete Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your renewal and complete the additional information before registering.
            </p>
          </div>

          <CautionBox
            v-if="isRlTransition"
            class="mt-7"
            :set-msg="`The Commercial Liens Act (CLA) took effect on ${ rlTransitionDate }. The repairers lien is
             continued under the CLA and any amendments, renewals, or discharges will be registered as Commercial Lien
             (CL).`"
            :set-important-word="'Important'"
          />

          <v-row no-gutters class="pt-14">
            <v-col cols="9">
              <h2 id="registering-party-change-title">
                Registering Party for this Renewal
                <v-tooltip
                  class="pa-2"
                  content-class="top-tooltip"
                  location="top"
                  transition="fade-transition"
                >
                  <template #activator="{ props }">
                    <v-icon
                      class="ml-1"
                      color="primary"
                      v-bind="props"
                    >
                      mdi-information-outline
                    </v-icon>
                  </template>
                  <div class="pt-2 pb-2">
                    {{ tooltipTxt }}
                  </div>
                </v-tooltip>
              </h2>
            </v-col>
            <v-col cols="3">
              <v-btn
                variant="plain"
                color="primary"
                class="smaller-button edit-btn float-right pr-0"
                :ripple="false"
                :disabled="registeringOpen"
                @click="changeRegisteringParty = true"
              >
                <v-icon size="small">mdi-pencil</v-icon>
                <span>Change Registering Party</span>
              </v-btn>
            </v-col>
          </v-row>

          <v-row
            v-if="isEmailRequired"
            class="no-gutters pb-2"
          >
            <v-col class="mt-0 pt-0">
              <span class="error-text fs-14">*Email address is required. Click ‘Edit’ in the dropdown to add one.</span>
            </v-col>
          </v-row>

          <RegisteringPartyChange
            class="pt-4"
            :change-party-prop="changeRegisteringParty"
            :set-show-error-bar="showErrors && registeringOpen"
            @registering-party-open="setShowWarning"
            @email-required-validation="isEmailRequired = $event"
          />
          <CautionBox
            v-if="showRegMsg"
            :set-msg="cautionTxt"
            :set-important-word="'Note'"
          />
          <RegistrationLengthTrustSummary
            class="mt-10"
            :is-renewal="true"
          />
          <CourtOrder
            v-if="showCourtOrderInfo"
            :set-summary="true"
            :is-renewal="true"
            class="mt-10"
          />
          <FolioNumberSummary
            :set-show-errors="showErrors"
            class="mt-10"
            @folio-valid="validFolio =$event"
          />
          <CertifyInformation
            class="mt-10"
            :section-number="2"
            :set-show-errors="showErrors"
            @certify-valid="validCertify = $event"
          />
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <StickyContainer
              :show-connect-fees="true"
              :set-err-msg="stickyComponentErrMsg"
              :set-right-offset="true"
              :set-show-buttons="true"
              :set-show-fee-summary="true"
              :set-fee-type="feeType"
              :set-registration-length="registrationLength"
              :set-registration-type="registrationTypeUI"
              :set-back-btn="'Back'"
              :set-cancel-btn="'Cancel'"
              :set-submit-btn="'Register Renewal and Pay'"
              :set-disable-submit-btn="isRoleStaffBcol"
              @back="goToReviewRenewal()"
              @cancel="showCancelDialog = true"
              @submit="submitButton()"
            />
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import {
  FolioNumberSummary,
  CertifyInformation,
  CourtOrder,
  StickyContainer,
  CautionBox
} from '@/components/common'
import { StaffPaymentDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { RegisteringPartyChange } from '@/components/parties/party'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { saveRenewal } from '@/utils'
import { ConnectPaymentMethod, type UIRegistrationTypes } from '@/enums'
import { ActionTypes, APIRegistrationTypes, RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import type {
  RenewRegistrationIF,
  StateModelIF,
  DialogOptionsIF,
  RegTableNewItemI, StaffPaymentIF
} from '@/interfaces'
import type { RegistrationLengthI } from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '@/composables'
import { hasNoCharge } from '@/composables/fees/factories'
import { useConnectFeeStore } from '@/store/connectFee'

export default defineComponent({
  name: 'ConfirmRenewal',
  components: {
    StaffPaymentDialog,
    CourtOrder,
    FolioNumberSummary,
    RegisteringPartyChange,
    RegistrationLengthTrustSummary,
    CertifyInformation,
    CautionBox,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  emits: ['error', 'haveData'],
  setup (props, { emit }) {
    const route = useRoute()
    const router = useRouter()
    const { goToDash, goToPay } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { setFees } = useConnectFeeStore()
    const { fees } = storeToRefs(useConnectFeeStore())
    const { userSelectedPaymentMethod } = storeToRefs(useConnectFeeStore())
    const { setRegTableNewItem } = useStore()
    const {
      // Getters
      getStaffPayment,
      rlTransitionDate,
      isRlTransition,
      getStateModel,
      getLengthTrust,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      getRegistrationNumber,
      getRegistrationType,
      getAddSecuredPartiesAndDebtors
    } = storeToRefs(useStore())

    const localState = reactive({
      registeringOpen: false,
      changeRegisteringParty: false,
      isEmailRequired: false,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      submitting: false,
      showRegMsg: false,
      staffPaymentDialogDisplay: false,
      staffPaymentDialogOptions: {
        acceptText: 'Submit Renewal',
        cancelText: 'Cancel',
        title: 'Staff Payment',
        label: '',
        text: ''
      } as DialogOptionsIF,
      showErrors: false,
      tooltipTxt: 'The default Registering Party is based on your BC ' +
        'Registries user account information. This information can be updated within ' +
        'your account settings. You can change to a different Registering Party by ' +
        'using the Change button.',
      cautionTxt: 'The Registry will not provide ' +
        'the verification statement for this renewal to the Registering Party named above.',
      validFolio: true,
      validCertify: false,
      feeType: FeeSummaryTypes.RENEW,
      registrationLength: computed((): RegistrationLengthI => {
        return {
          lifeInfinite: getLengthTrust.value?.lifeInfinite || false,
          lifeYears: getLengthTrust.value?.lifeYears || 0
        }
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || ''
      }),
      registrationNumber: computed((): string => {
        return (route.query['reg-num'] as string) || ''
      }),
      stickyComponentErrMsg: computed((): string => {
        if (!localState.validFolio && localState.showErrors) {
          return '< Please complete required information'
        }
        return ''
      }),
      showCourtOrderInfo: computed((): boolean => {
        return getRegistrationType.value && localState.registrationType === APIRegistrationTypes.REPAIRERS_LIEN &&
        !isRlTransition.value
      })
    })

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (): void => {
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value) {
        goToDash()
      }

      // if data is not accurate/missing (could be caused if user manually edits the url)
      if (!localState.registrationNumber || localState.registrationNumber !== getRegistrationNumber.value) {
        emit('error', 'Invalid Registration State')
        goToDash()
      }
    }

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) goToDash()
    }

    const goToReviewRenewal = (): void => {
      router.push({
        name: RouteNames.RENEW_REGISTRATION,
        query: { 'reg-num': localState.registrationNumber + '-confirm' }
      })
      emit('haveData', false)
    }

    const onStaffPaymentChanges = (pay: boolean): void => {
      if (pay) {
        submitRenewal()
      }
      localState.staffPaymentDialogDisplay = false
    }

    const submitButton = (): void => {
      if ((!localState.validFolio) || (!localState.validCertify) || (localState.isEmailRequired)) {
        localState.showErrors = true
        return
      }
      if ((isRoleStaffReg.value) || (isRoleStaffSbc.value)) {
        localState.staffPaymentDialogDisplay = true
      } else {
        submitRenewal()
      }
    }

    const submitRenewal = async (): Promise<void> => {
      const stateModel: StateModelIF = getStateModel.value
      localState.submitting = true
      const apiResponse: RenewRegistrationIF = await saveRenewal(
        stateModel,
        userSelectedPaymentMethod.value === ConnectPaymentMethod.DIRECT_PAY
      )
      localState.submitting = false
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        emit('error', apiResponse?.error)
      } else if (apiResponse.paymentPending) {
        goToPay(apiResponse.payment?.invoiceId, null, `pprReg-${apiResponse.documentId}`)
      } else {
        // set new added reg
        const newItem: RegTableNewItemI = {
          addedReg: apiResponse.renewalRegistrationNumber,
          addedRegParent: apiResponse.baseRegistrationNumber,
          addedRegSummary: null,
          prevDraft: ''
        }
        setRegTableNewItem(newItem)
        // On success return to dashboard
        goToDash()
      }
    }

    const setShowWarning = (open: boolean): void => {
      if (!open) {
        localState.changeRegisteringParty = false
      }
      localState.registeringOpen = open

      const parties = getAddSecuredPartiesAndDebtors.value
      localState.showRegMsg = parties.registeringParty?.action === ActionTypes.EDITED
    }

    watch(() => props.appReady, (appReady: boolean) => {
      if (appReady) onAppReady()
    }, { immediate: true })

    watch(() => getStaffPayment.value, (val: StaffPaymentIF) => {
      // If staff payment is set to waived, set the fee summary accordingly
      setFees({[FeeSummaryTypes.RENEW]: {
          ...fees.value[FeeSummaryTypes.RENEW],
          waived: val.option === 0
        }})
    })

    // Watch for changes to the changeRegisteringParty state and scroll to the title
    watch(() => localState.registeringOpen, (val) => {
      if (!val) {
        document?.querySelector('#registering-party-change-title')?.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        })
      }
    })

    return {
      rlTransitionDate,
      isRlTransition,
      submitButton,
      setShowWarning,
      isRoleStaffBcol,
      handleDialogResp,
      goToReviewRenewal,
      onStaffPaymentChanges,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme';
</style>
