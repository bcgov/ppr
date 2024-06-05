<template>
  <v-footer class="bg-white pa-0">
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
      :closeAction="true"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />

    <StaffPaymentDialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialogOptions"
      :setShowCertifiedCheckbox="false"
      @proceed="onStaffPaymentChanges($event)"
    />

    <v-container class="pt-8 pb-15">
      <v-row noGutters>
        <v-col cols="6">
          <span
            v-if="buttonConfig.showCancel"
            class="pr-3"
          >
            <v-btn
              id="reg-cancel-btn"
              variant="outlined"
              color="primary"
              @click="cancel()"
            >
              Cancel
            </v-btn>
          </span>
          <span
            v-if="buttonConfig.showSaveResume"
            class="pr-3"
          >
            <v-btn
              id="reg-save-resume-btn"
              variant="outlined"
              color="primary"
              @click="submitSaveResume"
            >
              Save and Resume Later
            </v-btn>
          </span>
          <v-btn
            v-if="buttonConfig.showSave"
            id="reg-save-btn"
            variant="outlined"
            color="primary"
            @click="saveDraft()"
          >
            Save
          </v-btn>
        </v-col>
        <v-col
          class="justify"
          cols="6"
        >
          <v-btn
            id="reg-next-btn"
            color="primary"
            :disabled="lastStepBcol"
            class="float-right pl-6"
            @click="submitNext"
          >
            {{ buttonConfig.nextText }}
            <v-icon
              color="white"
              class="pt-1"
            >
              mdi-chevron-right
            </v-icon>
          </v-btn>
          <span
            v-if="buttonConfig.showBack"
            class="pr-3"
          >
            <v-btn
              id="reg-back-btn"
              variant="outlined"
              color="primary"
              class="float-right mr-4 pr-5"
              @click="submitBack"
            >
              <v-icon
                color="primary"
                class="pt-1"
              >mdi-chevron-left</v-icon> Back
            </v-btn>
          </span>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { throttle } from 'lodash'
import { saveFinancingStatement, saveFinancingStatementDraft } from '@/utils'
import { RouteNames } from '@/enums'
import { BaseDialog } from '@/components/dialogs'
import StaffPaymentDialog from '@/components/dialogs/StaffPaymentDialog.vue'
import {
  // eslint-disable-next-line no-unused-vars
  ButtonConfigIF, DialogOptionsIF, DraftIF, ErrorIF, FinancingStatementIF, RegTableNewItemI, StateModelIF
} from '@/interfaces'
import { unsavedChangesDialog } from '@/resources/dialogOptions'
import { useMhrCorrections, useNavigation, useNewMhrRegistration } from '@/composables'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    BaseDialog,
    StaffPaymentDialog
  },
  props: {
    navConfig: {
      type: Array as () => Array<ButtonConfigIF>,
      default: null
    },
    disableNav: {
      type: Boolean,
      default: false
    },
    currentStepName: {
      type: String,
      default: 'length-trust'
    },
    certifyValid: {
      type: Boolean,
      default: false
    },
    forceSave: {
      type: Boolean,
      default: false
    },
    isMhr: {
      type: Boolean,
      default: false
    },
    baseDialogOptions: {
      type: Object as () => DialogOptionsIF,
      default: () => null
    }
  },
  emits: ['cancelProceed', 'error', 'registrationIncomplete', 'submit', 'navigationDisabled'],
  setup (props, { emit }) {
    const { goToDash, goToRoute } = useNavigation()
    const {
      // Actions
      setDraft,
      setRegTableNewItem,
      setUnsavedChanges
    } = useStore()
    const {
      // Getters
      getStateModel,
      hasUnsavedChanges,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      isMhrReRegistration,
      getMhrInformation
    } = storeToRefs(useStore())
    const { mhrDraftHandler } = useNewMhrRegistration()

    const { isMhrCorrection } = useMhrCorrections()

    const localState = reactive({
      options: props.baseDialogOptions as DialogOptionsIF || unsavedChangesDialog,
      showCancelDialog: false,
      staffPaymentDialogDisplay: false,
      staffPaymentDialogOptions: {
        acceptText: 'Submit Registration',
        cancelText: 'Cancel',
        title: 'Staff Payment',
        label: ''
      } as DialogOptionsIF,
      submitting: false,
      isCertifyValid: computed((): boolean => {
        return props.certifyValid
      }),
      isStaffReg: computed((): boolean => {
        return isRoleStaffReg.value
      }),
      isStaffBcol: computed((): boolean => {
        return isRoleStaffBcol.value
      }),
      lastStepBcol: computed((): boolean => {
        // bcol can't submit
        return ((props.currentStepName === RouteNames.REVIEW_CONFIRM) && isRoleStaffBcol.value)
      }),
      isStaffSbc: computed((): boolean => {
        return isRoleStaffSbc.value
      }),
      buttonConfig: computed((): ButtonConfigIF => {
        for (const i in props.navConfig) {
          if (props.navConfig[i].stepName === props.currentStepName) {
            return props.navConfig[i]
          }
        }
        return null
      })
    })
    const cancel = () => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else goToDash()
    }
    const handleDialogResp = (val: boolean) => {
      localState.showCancelDialog = false
      if (!val) {
        emit('cancelProceed')
        goToDash()
      }
    }
    /** Save the draft version from data stored in the state model. */
    const saveDraft = async (): Promise<boolean> => {
      let draft
      let prevDraftId
      localState.submitting = true

      if (props.isMhr) {
        draft = await mhrDraftHandler()
      } else {
        const stateModel: StateModelIF = getStateModel.value
        draft = await throttleSubmitStatementDraft(stateModel)
        prevDraftId = stateModel.registration?.draft?.financingStatement?.documentId || ''
      }

      if (draft.error) {
        // Emit error message.
        emit('error', draft.error)
        localState.submitting = false
        return false
      } else {
        await setUnsavedChanges(false)
        await setDraft(draft)

        const newItem: RegTableNewItemI = {
          addedReg: draft.financingStatement?.documentId || draft.draftNumber,
          // adding mhrNumber will scroll to draft mhr correction
          addedRegParent: (isMhrCorrection.value || isMhrReRegistration.value) ? getMhrInformation.value.mhrNumber : '',
          addedRegSummary: null,
          prevDraft: prevDraftId
        }
        await setRegTableNewItem(newItem)
        localState.submitting = false
        return true
      }
    }
    /* Save and return to dashboard */
    const submitSaveResume = async (): Promise<void> => {
      const success = await saveDraft()
      if (success) {
        goToDash()
      }
    }
    const submitBack = async () => {
      await goToRoute(localState.buttonConfig.backRouteName as RouteNames)
    }
    const submitNext = async () => {
      // Handle disabled navigation
      if (props.disableNav) {
        emit('navigationDisabled', props.disableNav)
        return
      }

      // Undetected Duplicate Secured Party API check to be implemented here.
      // Use secured party dialog with isDuplicate and isReview props to display error if found.
      if ([RouteNames.REVIEW_CONFIRM, RouteNames.MHR_REVIEW_CONFIRM, RouteNames.QS_ACCESS_REVIEW_CONFIRM,
        RouteNames.EXEMPTION_REVIEW].includes(props.currentStepName as RouteNames)) {
        // -- Intersect here for Submitting MHR Registration --
        if ([RouteNames.MHR_REVIEW_CONFIRM, RouteNames.QS_ACCESS_REVIEW_CONFIRM, RouteNames.EXEMPTION_REVIEW]
          .includes(props.currentStepName as RouteNames)) {
          emit('submit')
          return
        }

        if (checkValid()) {
          if (localState.isStaffReg) {
            localState.staffPaymentDialogDisplay = true
          } else {
            submitFinancingStatement()
          }
        } else {
          // emit registration incomplete error
          const error: ErrorIF = {
            statusCode: 400,
            message: 'Registration incomplete: one or more steps is invalid.'
          }
          emit('registrationIncomplete', error)
        }
      } else {
        await goToRoute(localState.buttonConfig.nextRouteName as RouteNames)
      }
    }

    const checkValid = (): boolean => {
      const stateModel: StateModelIF = getStateModel.value
      return stateModel.registration.lengthTrust.valid &&
        stateModel.registration.parties.valid &&
        stateModel.registration.collateral.valid &&
        localState.isCertifyValid
    }

    const onStaffPaymentChanges = (pay: boolean): void => {
      if (pay) {
        submitFinancingStatement()
      }
      localState.staffPaymentDialogDisplay = false
    }

    /** Check all steps are valid, make api call to create a financing statement, handle api errors. */
    const submitFinancingStatement = async () => {
      const stateModel: StateModelIF = getStateModel.value
      if (checkValid()) {
        // API call here
        const apiResponse: FinancingStatementIF = await throttleSubmitStatement(stateModel)
        if (apiResponse.error !== undefined) {
          // Emit error message.
          emit('error', apiResponse.error)
        } else {
          const prevDraftId = stateModel.registration?.draft?.financingStatement?.documentId || ''
          const newItem: RegTableNewItemI = {
            addedReg: apiResponse.baseRegistrationNumber,
            addedRegParent: '',
            addedRegSummary: null,
            prevDraft: prevDraftId
          }
          setRegTableNewItem(newItem)
          await goToRoute(localState.buttonConfig.nextRouteName as RouteNames)
        }
      } else {
        // emit registation incomplete error
        const error: ErrorIF = {
          statusCode: 400,
          message: 'Registration incomplete: one or more steps is invalid.'
        }
        emit('registrationIncomplete', error)
      }
    }

    const throttleSubmitStatement = throttle(async (stateModel: StateModelIF): Promise<FinancingStatementIF> => {
      // Prevents multiple submits (i.e. double click)
      localState.submitting = true
      const statement = await saveFinancingStatement(stateModel)
      localState.submitting = false
      return statement
    }, 2000, { trailing: false })

    const throttleSubmitStatementDraft = throttle(async (stateModel: StateModelIF): Promise<DraftIF> => {
      // Prevents multiple submits (i.e. double click)
      localState.submitting = true
      const statement = await saveFinancingStatementDraft(stateModel)
      localState.submitting = false
      return statement
    }, 2000, { trailing: false })

    watch(() => props.forceSave, () => {
      // on change (T/F doesn't matter), save and go back to dash
      submitSaveResume()
    })

    return {
      ...toRefs(localState),
      cancel,
      handleDialogResp,
      saveDraft,
      submitBack,
      submitNext,
      onStaffPaymentChanges,
      submitSaveResume
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.v-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 140px;
  background-color: #333;
}

.payment-fee {
  background-color: $gray1;
}

.fee-currency {
  color: $gray6;
}

.fee-list {
  padding-left: 0 !important;
  border-bottom: 1px solid $gray4;
}

.payment-total {
  font-weight: bold;
}

.header {
  color: white;
  font-size: 1.125rem;
}
</style>
