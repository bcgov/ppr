<template>
  <v-footer class="white pa-0">
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
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local helpers/enums/interfaces/resources
import { saveFinancingStatement, saveFinancingStatementDraft } from '@/utils'
import { RouteNames, StatementTypes } from '@/enums'
import {
  ButtonConfigIF, // eslint-disable-line no-unused-vars
  DraftIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  FinancingStatementIF, // eslint-disable-line no-unused-vars
  StateModelIF // eslint-disable-line no-unused-vars
} from '@/interfaces'

export default defineComponent({
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
    }
  },
  setup (props, { emit }) {
    const { getFinancingButtons } = useGetters<any>(['getFinancingButtons'])
    const { getStateModel } = useGetters<any>(['getStateModel'])
    const { setDraft } = useActions<any>(['setDraft'])
    const { resetNewRegistration } = useActions<any>(['resetNewRegistration'])
    const localState = reactive({
      statementType: props.currentStatementType,
      stepName: props.currentStepName,
      isCertifyValid: computed((): boolean => {
        return props.certifyValid
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
      if (draft.error !== undefined) {
        console.log(
          'saveDraft error status: ' +
            draft.error.statusCode +
            ' message: ' +
            draft.error.message
        )
        // Emit error message.
        emit('save-draft-error', draft.error)
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
        submitFinancingStatement()
      } else {
        props.router.push({
          name: localState.buttonConfig.nextRouteName
        })
      }
    }

    /** Check all steps are valid, make api call to create a financing statement, handle api errors. */
    const submitFinancingStatement = async () => {
      const stateModel: StateModelIF = getStateModel.value
      if (
        stateModel.registration.lengthTrust.valid &&
        stateModel.registration.parties.valid &&
        stateModel.registration.collateral.valid &&
        localState.isCertifyValid
      ) {
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

    return {
      ...toRefs(localState),
      submitBack,
      submitCancel,
      submitNext,
      submitSave,
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
