<template>
  <v-footer class="white pa-0">
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialogOptions"
      :setShowCertifiedCheckbox="false"
      @proceed="onStaffPaymentChanges($event)"
    />
    <v-container class="pt-8 pb-15">
      <v-row no-gutters>
        <v-col cols="6">
          <span class="pr-3" v-if="buttonConfig.showCancel">
            <v-btn
              id="reg-cancel-btn"
              outlined
              color="primary"
              @click="cancel()"
            >
              Cancel
            </v-btn>
          </span>
          <span class="pr-3" v-if="buttonConfig.showSaveResume">
            <v-btn
              id="reg-save-resume-btn"
              outlined
              color="primary"
              @click="submitSaveResume"
            >
              Save and Resume Later
            </v-btn>
          </span>
          <v-btn
            id="reg-save-btn"
            outlined
            color="primary"
            @click="saveDraft()"
            v-if="buttonConfig.showSave"
          >
            Save
          </v-btn>
        </v-col>
        <v-col cols="6" justify="end">
          <v-btn
            id="reg-next-btn"
            color="primary"
            :disabled="lastStepBcol"
            class="float-right pl-6"
            @click="submitNext"
          >
            {{ buttonConfig.nextText }}
            <v-icon color="white">mdi-chevron-right</v-icon>
          </v-btn>
          <span class="pr-3" v-if="buttonConfig.showBack">
            <v-btn
              id="reg-back-btn"
              outlined
              color="primary"
              class="float-right mr-4 pr-5"
              @click="submitBack"
            >
              <v-icon color="primary">mdi-chevron-left</v-icon> Back
            </v-btn>
          </span>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script lang="ts">
// external
import VueRouter from 'vue-router' // eslint-disable-line no-unused-vars
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import _ from 'lodash'
// local helpers/enums/interfaces/resources
import { saveFinancingStatement, saveFinancingStatementDraft } from '@/utils'
import { RouteNames, StatementTypes } from '@/enums'
import { BaseDialog } from '@/components/dialogs'
import StaffPaymentDialog from '@/components/dialogs/StaffPaymentDialog.vue'

import {
  ButtonConfigIF, // eslint-disable-line no-unused-vars
  DraftIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  FinancingStatementIF, // eslint-disable-line no-unused-vars
  RegTableNewItemI, // eslint-disable-line no-unused-vars
  StateModelIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { unsavedChangesDialog } from '@/resources/dialogOptions'

export default defineComponent({
  components: {
    BaseDialog,
    StaffPaymentDialog
  },
  props: {
    currentStatementType: {
      type: String,
      default: 'financing'
    },
    router: {
      type: Object as () => VueRouter
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
    }
  },
  setup (props, { emit }) {
    const {
      getFinancingButtons,
      getStateModel,
      hasUnsavedChanges,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc
    } = useGetters<any>([
      'getFinancingButtons',
      'getStateModel',
      'hasUnsavedChanges',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'isRoleStaffSbc'
    ])

    const { resetNewRegistration, setDraft, setRegTableNewItem, setUnsavedChanges } =
      useActions<any>(['resetNewRegistration', 'setDraft', 'setRegTableNewItem', 'setUnsavedChanges'])

    const localState = reactive({
      options: unsavedChangesDialog,
      showCancelDialog: false,
      statementType: props.currentStatementType,
      staffPaymentDialogDisplay: false,
      staffPaymentDialogOptions: {
        acceptText: 'Submit Registration',
        cancelText: 'Cancel',
        title: 'Staff Payment',
        label: ''
      },
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
      buttonConfig: computed(
        (): ButtonConfigIF => {
          if (
            localState.statementType.toUpperCase() ===
            StatementTypes.FINANCING_STATEMENT
          ) {
            const stepConfig: Array<ButtonConfigIF> = getFinancingButtons.value
            let config: ButtonConfigIF
            for (const i in stepConfig) {
              config = stepConfig[i]
              if (config.stepName === props.currentStepName) {
                return config
              }
            }
          }
          return null
        }
      )
    })
    const cancel = () => {
      if (hasUnsavedChanges.value === true) localState.showCancelDialog = true
      else goToDashboard()
    }
    const goToDashboard = () => {
      // clear all state set data
      resetNewRegistration(null)
      props.router.push({ name: RouteNames.DASHBOARD })
    }
    const handleDialogResp = (val: boolean) => {
      localState.showCancelDialog = false
      if (!val) goToDashboard()
    }
    /** Save the draft version from data stored in the state model. */
    const saveDraft = async (): Promise<Boolean> => {
      const stateModel: StateModelIF = getStateModel.value
      const draft: DraftIF = await throttleSubmitStatementDraft(stateModel)
      const prevDraftId = stateModel.registration?.draft?.financingStatement?.documentId || ''
      if (draft.error) {
        // Emit error message.
        emit('error', draft.error)
        return false
      } else {
        await setUnsavedChanges(false)
        await setDraft(draft)
        const newItem: RegTableNewItemI = {
          addedReg: draft.financingStatement.documentId,
          addedRegParent: '',
          addedRegSummary: null,
          prevDraft: prevDraftId
        }
        await setRegTableNewItem(newItem)
        return true
      }
    }
    /* Save and return to dashboard */
    const submitSaveResume = async (): Promise<void> => {
      const success = await saveDraft()
      if (success) {
        goToDashboard()
      }
    }
    const submitBack = () => {
      props.router.push({
        name: localState.buttonConfig.backRouteName
      })
    }
    const submitNext = () => {
      // Undetected Duplicate Secured Party API check to be implemented here.
      // Use secured party dialog with isDuplicate and isReview props to display error if found.
      if (
        localState.statementType.toUpperCase() ===
          StatementTypes.FINANCING_STATEMENT &&
        [RouteNames.REVIEW_CONFIRM, RouteNames.MHR_REVIEW_CONFIRM].includes(props.currentStepName as RouteNames)
      ) {
        // -- Intersect here for Submitting MHR Registration --
        if (props.currentStepName === RouteNames.MHR_REVIEW_CONFIRM) {
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
          emit('registration-incomplete', error)
        }
      } else {
        props.router.push({
          name: localState.buttonConfig.nextRouteName
        })
      }
    }

    const checkValid = (): boolean => {
      const stateModel: StateModelIF = getStateModel.value
      if (
        stateModel.registration.lengthTrust.valid &&
        stateModel.registration.parties.valid &&
        stateModel.registration.collateral.valid &&
        localState.isCertifyValid
      ) {
        return true
      }
      return false
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
          props.router.push({
            name: localState.buttonConfig.nextRouteName
          })
        }
      } else {
        // emit registation incomplete error
        const error: ErrorIF = {
          statusCode: 400,
          message: 'Registration incomplete: one or more steps is invalid.'
        }
        emit('registration-incomplete', error)
      }
    }

    const throttleSubmitStatement = _.throttle(async (stateModel: StateModelIF): Promise<FinancingStatementIF> => {
      // Prevents multiple submits (i.e. double click)
      localState.submitting = true
      const statement = await saveFinancingStatement(stateModel)
      localState.submitting = false
      return statement
    }, 2000, { trailing: false })

    const throttleSubmitStatementDraft = _.throttle(async (stateModel: StateModelIF): Promise<DraftIF> => {
      // Prevents multiple submits (i.e. double click)
      localState.submitting = true
      const statement = await saveFinancingStatementDraft(stateModel)
      localState.submitting = false
      return statement
    }, 2000, { trailing: false })

    watch(() => props.forceSave, (val: boolean) => {
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
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
