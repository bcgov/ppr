<template>
  <v-container
    id="confirm-discharge"
    class="px-0 pt-14"
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
      set-attach="#confirm-discharge"
      :set-options="options"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div
      v-if="appReady"
      class="container pa-0"
    >
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Confirm and Complete Total Discharge</h1>
          <div style="padding-top: 25px;">
            <p class="ma-0">
              Confirm your Total Discharge and complete the additional information before registering.
            </p>
            <p v-if="isRlTransition" class="pt-5">
              <b>Note</b>: The Registry will provide the verification statement to all Secured Parties named in this
              registration.
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
          <caution-box
            v-else
            class="mt-9"
            :set-msg="cautionTxt"
          />

          <v-row no-gutters class="pt-14">
            <v-col cols="9">
              <h2 id="registering-party-change-title">
                Registering Party for this Discharge
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

          <registering-party-change
            class="pt-4"
            :change-party-prop="changeRegisteringParty"
            :set-show-error-bar="showErrors && registeringOpen"
            @registering-party-open="setShowWarning"
            @email-required-validation="isEmailRequired = $event"
          />
          <caution-box
            v-if="showRegMsg"
            :set-msg="cautionTxtRP"
            :set-important-word="'Note'"
          />
          <folio-number-summary
            :set-show-errors="showErrors"
            class="pt-15"
            @folio-valid="validFolio = $event"
          />
          <h2 class="pt-15">
            2. Confirm
          </h2>
          <p class="ma-0 pt-4">
            You are about to submit a Total Discharge based on the following
            details:
          </p>
          <discharge-confirm-summary
            class="mt-6 soft-corners"
            :set-reg-num="registrationNumber"
            :set-reg-type="registrationTypeUI"
            :set-collateral-summary="collateralSummary"
            :set-show-errors="showErrors"
            @valid="validConfirm = $event"
          />
          <certify-information
            class="pt-10"
            :section-number="3"
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
              :set-registration-type="registrationTypeUI"
              :set-back-btn="'Back'"
              :set-cancel-btn="'Cancel'"
              :set-submit-btn="'Register Total Discharge'"
              :set-disable-submit-btn="isRoleStaffBcol"
              @back="goToDischarge()"
              @cancel="showCancelDialog = true"
              @submit="submitDischarge()"
            />
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, toRefs, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import {
  CautionBox,
  DischargeConfirmSummary,
  FolioNumberSummary,
  CertifyInformation,
  StickyContainer
} from '@/components/common'
import { RegisteringPartyChange } from '@/components/parties/party'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { saveDischarge, scrollToFirstVisibleErrorComponent } from '@/utils'
import type { APIRegistrationTypes, UIRegistrationTypes } from '@/enums';
import { ActionTypes, RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import type {
  DischargeRegistrationIF,
  StateModelIF,
  DialogOptionsIF,
  RegTableNewItemI
} from '@/interfaces'
import { useAuth, useNavigation } from '@/composables'

export default defineComponent({
  name: 'ConfirmDischarge',
  components: {
    CautionBox,
    DischargeConfirmSummary,
    FolioNumberSummary,
    RegisteringPartyChange,
    CertifyInformation,
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
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setRegTableNewItem
    } = useStore()
    const {
      // Getters
      isRlTransition,
      rlTransitionDate,
      getStateModel,
      isRoleStaffBcol,
      getConfirmDebtorName,
      getGeneralCollateral,
      getVehicleCollateral,
      getRegistrationType,
      getRegistrationNumber,
      getAddSecuredPartiesAndDebtors
    } = storeToRefs(useStore())

    const localState = reactive({
      registeringOpen: false,
      changeRegisteringParty: false,
      isEmailRequired: false,
      cautionTxt: 'The Registry will provide the verification statement to all Secured Parties named in this ' +
        'registration.',
      cautionTxtRP: 'The Registry will not provide the verification statement for this total discharge to the ' +
        'Registering Party named above.',
      feeType: FeeSummaryTypes.DISCHARGE,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      showErrors: false,
      showRegMsg: false,
      submitting: false,
      tooltipTxt: 'The default Registering Party is based on your BC Registries user account information. This ' +
        'information can be updated within your account settings. You can change to a different Registering Party by ' +
        'using the Change button.',
      validConfirm: false,
      validFolio: true,
      validCertify: false,
      collateralSummary: computed((): string => {
        if (!getGeneralCollateral.value && !getVehicleCollateral.value) return 'No Collateral'
        return `${getGeneralCollateral.value ? '' : 'No '}General Collateral and ` +
          `${getVehicleCollateral.value?.length || 0} ` +
          `${getVehicleCollateral.value?.length !== 1 ? 'Vehicles' : 'Vehicle'}`
      }),
      registrationNumber: computed((): string => {
        return (route.query['reg-num'] as string) || ''
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || null
      }),
      stickyComponentErrMsg: computed((): string => {
        if ((!localState.validConfirm || !localState.validFolio) && localState.showErrors) {
          return '< Please complete required information'
        }
        return ''
      })
    })

    const onAppReady = (): void => {
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value) goToDash()

      // if data is not accurate/missing (could be caused if user manually edits the url)
      if (!localState.registrationNumber || !getConfirmDebtorName.value ||
        localState.registrationNumber !== getRegistrationNumber.value) {
        emit('error', 'Invalid Registration State')
        goToDash()
      }
    }

    /** Called when App is ready and this component can load its data. */
    watch(() => props.appReady, (appReady: boolean) => {
      if (appReady) onAppReady()
    }, { immediate: true })

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        goToDash()
      }
    }

    const goToDischarge = (): void => {
      router.push({
        name: RouteNames.REVIEW_DISCHARGE,
        query: { 'reg-num': localState.registrationNumber + '-confirm' }
      })
      emit('haveData', false)
    }

    const submitDischarge = async (): Promise<void> => {
      if ((!localState.validConfirm) || (!localState.validFolio) || (!localState.validCertify) ||
        (localState.isEmailRequired)) {
        localState.showErrors = true
        await nextTick()
        await scrollToFirstVisibleErrorComponent()
        return
      }

      const stateModel: StateModelIF = getStateModel.value
      localState.submitting = true
      const apiResponse: DischargeRegistrationIF = await saveDischarge(stateModel)
      localState.submitting = false
      if (apiResponse === undefined || apiResponse?.error !== undefined) {
        emit('error', apiResponse?.error)
      } else {
        // set new added reg
        const newItem: RegTableNewItemI = {
          addedReg: apiResponse.dischargeRegistrationNumber,
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
      isRlTransition,
      rlTransitionDate,
      goToDischarge,
      setShowWarning,
      isRoleStaffBcol,
      submitDischarge,
      handleDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme';
</style>
