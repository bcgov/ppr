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
      setAttach="#confirm-discharge"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div
      v-if="appReady"
      class="container pa-0"
    >
      <v-row noGutters>
        <v-col cols="9">
          <h1>Confirm and Complete Total Discharge</h1>
          <div style="padding-top: 25px;">
            <p class="ma-0">
              Confirm your Total Discharge and complete the additional information before registering.
            </p>
          </div>
          <caution-box
            class="mt-9"
            :setMsg="cautionTxt"
          />
          <h2 class="pt-14">
            Registering Party for this Discharge
            <v-tooltip
              class="pa-2"
              contentClass="top-tooltip"
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
          <registering-party-change
            class="pt-4"
            @registeringPartyOpen="setShowWarning()"
          />
          <caution-box
            v-if="showRegMsg"
            :setMsg="cautionTxtRP"
            :setImportantWord="'Note'"
          />
          <folio-number-summary
            :setShowErrors="showErrors"
            class="pt-15"
            @folioValid="validFolio = $event"
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
            :setRegNum="registrationNumber"
            :setRegType="registrationTypeUI"
            :setCollateralSummary="collateralSummary"
            :setShowErrors="showErrors"
            @valid="validConfirm = $event"
          />
          <certify-information
            class="pt-10"
            :sectionNumber="3"
            :setShowErrors="showErrors"
            @certifyValid="validCertify = $event"
          />
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <StickyContainer
              :setErrMsg="stickyComponentErrMsg"
              :setRightOffset="true"
              :setShowButtons="true"
              :setShowFeeSummary="true"
              :setFeeType="feeType"
              :setRegistrationType="registrationTypeUI"
              :setBackBtn="'Back'"
              :setCancelBtn="'Cancel'"
              :setSubmitBtn="'Register Total Discharge'"
              :setDisableSubmitBtn="isRoleStaffBcol"
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
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
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
import { BaseDialog } from '@/components/dialogs'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, saveDischarge } from '@/utils'
import { ActionTypes, APIRegistrationTypes, RouteNames, UIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  DischargeRegistrationIF,
  StateModelIF,
  DialogOptionsIF,
  RegTableNewItemI
} from '@/interfaces'
import { useAuth, useNavigation } from '@/composables'

export default defineComponent({
  name: 'ConfirmDischarge',
  components: {
    BaseDialog,
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
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) goToDash()

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
      if ((!localState.validConfirm) || (!localState.validFolio) || (!localState.validCertify)) {
        localState.showErrors = true
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

    const setShowWarning = (): void => {
      const parties = getAddSecuredPartiesAndDebtors.value
      localState.showRegMsg = parties.registeringParty?.action === ActionTypes.EDITED
    }

    return {
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
@import '@/assets/styles/theme.scss';
</style>
