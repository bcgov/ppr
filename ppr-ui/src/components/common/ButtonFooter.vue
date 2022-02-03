<template>
  <v-footer class="white pa-0">
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialogOptions"
      :setShowCertifiedCheckbox="false"
      @proceed="onStaffPaymentChanges($event)"
    />
    <base-dialog
      id="draftErrorDialog"
      :setDisplay="errorDialogDisplay"
      :setOptions="errorOptions"
      @proceed="handleError($event)"
    />
    <v-container class="pt-8 pb-15">
      <v-row no-gutters>
        <v-col cols="6">
          <span class="pr-3" v-if="buttonConfig.showCancel">
            <v-btn
              id="reg-cancel-btn"
              outlined
              color="primary"
              @click="submitCancel"
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
            @click="submitSave"
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
            class="float-right"
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
              class="float-right mr-4"
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
// local helpers/enums/interfaces/resources
import { saveFinancingStatement, saveFinancingStatementDraft } from '@/utils'
import { RouteNames, StatementTypes } from '@/enums'
import { BaseDialog } from '../dialogs'
import StaffPaymentDialog from '@/components/dialogs/StaffPaymentDialog.vue'
import { registrationSaveDraftErrorDialog } from '@/resources/dialogOptions'

import {
  ButtonConfigIF, // eslint-disable-line no-unused-vars
  DraftIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  FinancingStatementIF, // eslint-disable-line no-unused-vars
  StateModelIF // eslint-disable-line no-unused-vars
} from '@/interfaces'

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
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc
    } = useGetters<any>([
      'getFinancingButtons',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'isRoleStaffSbc'
    ])
    const { getStateModel } = useGetters<any>(['getStateModel'])
    const { setDraft } = useActions<any>(['setDraft'])
    const { resetNewRegistration } = useActions<any>(['resetNewRegistration'])
    const localState = reactive({
      statementType: props.currentStatementType,
      stepName: props.currentStepName,
      staffPaymentDialogDisplay: false,
      staffPaymentDialogOptions: {
        acceptText: 'Submit Registration',
        cancelText: 'Cancel',
        title: 'Staff Payment',
        label: ''
      },
      errorDialogDisplay: false,
      errorOptions: registrationSaveDraftErrorDialog,
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
        return ((localState.stepName === RouteNames.REVIEW_CONFIRM) && isRoleStaffBcol.value)
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
            var config: ButtonConfigIF
            for (var i in stepConfig) {
              config = stepConfig[i]
              if (config.stepName === localState.stepName) {
                return config
              }
            }
          }
          return null
        }
      )
    })
    const submitCancel = () => {
      // clear all state set data
      resetNewRegistration(null)
      // navigate to dashboard
      props.router.push({
        name: RouteNames.DASHBOARD
      })
    }
    /** Save the draft version from data stored in the state model. */
    const saveDraft = async () => {
      const stateModel: StateModelIF = getStateModel.value
      const draft: DraftIF = await saveFinancingStatementDraft(stateModel)
      setDraft(draft)
      draft.error = { statusCode: 404, message: 'bad' }
      if (draft.error !== undefined) {
        console.log(
          'saveDraft error status: ' +
            draft.error.statusCode +
            ' message: ' +
            draft.error.message
        )
        // Emit error message.
        showDraftError(draft.error)
        return false
      }
      return true
    }
    /** Save and stay in flow. */
    const submitSave = () => {
      saveDraft()
    }
    /* Save and return to dashboard */
    const submitSaveResume = () => {
      const success = saveDraft()
      if (success) {
        submitCancel()
      }
    }
    const submitBack = () => {
      props.router.push({
        name: localState.buttonConfig.backRouteName
      })
    }
    const submitNext = () => {
      if (
        localState.statementType.toUpperCase() ===
          StatementTypes.FINANCING_STATEMENT &&
        localState.stepName === RouteNames.REVIEW_CONFIRM
      ) {
        if (checkValid()) {
          if (localState.isStaffReg) {
            localState.staffPaymentDialogDisplay = true
          } else {
            submitFinancingStatement()
          }
        } else {
          // emit registation incomplete error
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

    const showDraftError = (val: ErrorIF): void => {
      localState.errorDialogDisplay = true
    }

    const handleError = (stay: boolean): void => {
      localState.errorDialogDisplay = false
    }

    /** Check all steps are valid, make api call to create a financing statement, handle api errors. */
    const submitFinancingStatement = async () => {
      const stateModel: StateModelIF = getStateModel.value
      if (checkValid()) {
        // API call here
        const apiResponse: FinancingStatementIF = await saveFinancingStatement(stateModel)
        if (apiResponse.error !== undefined) {
          // Emit error message.
          emit('error', apiResponse.error)
        } else {
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

    watch(() => props.forceSave, (val: boolean) => {
      // on change (T/F doesn't matter), save and go back to dash
      submitSaveResume()
    })

    return {
      ...toRefs(localState),
      submitBack,
      submitCancel,
      submitNext,
      submitSave,
      onStaffPaymentChanges,
      handleError,
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
