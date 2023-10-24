<template>
  <v-container
    id="confirm-renewal"
    class="view-container pa-15 pt-14"
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
      set-attach="#confirm-renewal"
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
        <v-col cols="9">
          <h1>Review and Complete Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review your renewal and complete the additional information before registering.
            </p>
          </div>
          <h2 class="pt-14">
            Registering Party for this Renewal
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
            @registeringPartyOpen="setShowWarning()"
          />
          <caution-box
            v-if="showRegMsg"
            :set-msg="cautionTxt"
            :set-important-word="'Note'"
          />
          <registration-length-trust-summary
            class="mt-10"
            :is-renewal="true"
          />
          <court-order
            v-if="showCourtOrderInfo"
            :set-summary="true"
            :is-renewal="true"
            class="mt-10"
          />

          <folio-number-summary
            :set-show-errors="showErrors"
            class="mt-10"
            @folioValid="validFolio =$event"
          />
          <certify-information
            class="mt-10"
            :section-number="2"
            :set-show-errors="showErrors"
            @certifyValid="validCertify = $event"
          />
        </v-col>
        <v-col
          class="pl-6"
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
                :set-back-btn="'Back'"
                :set-cancel-btn="'Cancel'"
                :set-submit-btn="'Register Renewal and Pay'"
                :set-disable-submit-btn="isRoleStaffBcol"
                @back="goToReviewRenewal()"
                @cancel="showCancelDialog = true"
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
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { RegisteringPartyChange } from '@/components/parties/party'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, saveRenewal } from '@/utils'
import { ActionTypes, APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  RenewRegistrationIF,
  StateModelIF,
  DialogOptionsIF,
  RegTableNewItemI
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '@/composables'

export default defineComponent({
  name: 'ConfirmRenewal',
  components: {
    BaseDialog,
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
    },
    isJestRunning: {
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
      setRegTableNewItem
    } = useStore()
    const {
      // Getters
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
        return (getRegistrationType.value && localState.registrationType === APIRegistrationTypes.REPAIRERS_LIEN)
      })
    })

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (): void => {
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        goToDash()
      }

      // if data is not accurate/missing (could be caused if user manually edits the url)
      if (!localState.registrationNumber || localState.registrationNumber !== getRegistrationNumber.value) {
        emit('error', 'Invalid Registration State')
        goToDash()
      }
    }

    watch(() => props.appReady, (appReady: boolean) => {
      if (appReady) onAppReady()
    }, { immediate: true })

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
      if ((!localState.validFolio) || (!localState.validCertify)) {
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
      const apiResponse: RenewRegistrationIF = await saveRenewal(stateModel)
      localState.submitting = false
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        emit('error', apiResponse?.error)
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

    const setShowWarning = (): void => {
      const parties = getAddSecuredPartiesAndDebtors.value
      localState.showRegMsg = parties.registeringParty?.action === ActionTypes.EDITED
    }

    return {
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
@import '@/assets/styles/theme.scss';
</style>
