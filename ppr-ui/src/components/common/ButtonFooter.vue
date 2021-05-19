<template>
  <v-footer class="white pa-0">
    <v-row no-gutters class="pl-16 pt-8 pb-15">
      <v-col cols="3"></v-col>
      <v-col cols="9" class="align=left pl-12">
        <span class="pr-3" v-if="buttonConfig.showCancel">
          <v-btn id='reg-cancel-btn' outlined color="primary" @click="submitCancel">
            Cancel
          </v-btn>
        </span>
        <span class="pr-3" v-if="buttonConfig.showSaveResume">
          <v-btn id='reg-save-resume-btn' outlined color="primary" @click="submitSaveResume">
            Save and Resume Later
          </v-btn>
        </span>
        <v-btn id='reg-save-btn' outlined color="primary" @click="submitSave" v-if="buttonConfig.showSave">
          Save
        </v-btn>
      </v-col>
      <v-col cols="3">
        <span class="pr-3" v-if="buttonConfig.showBack">
          <v-btn id='reg-back-btn' outlined color="primary" @click="submitBack">
            &lt; Back
          </v-btn>
        </span>
        <v-btn id='reg-next-btn' color="primary" @click="submitNext">
          {{buttonConfig.nextText}} >
        </v-btn>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script lang="ts">
// external
import VueRouter from 'vue-router' // eslint-disable-line no-unused-vars
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local helpers/enums/interfaces/resources
import { saveFinancingStatementDraft } from '@/utils'
import { RouteNames, StatementTypes } from '@/enums'
import {
  ActionBindingIF, ButtonConfigIF, DraftIF, ErrorIF, // eslint-disable-line no-unused-vars
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
      buttonConfig: computed((): ButtonConfigIF => {
        if (localState.statementType.toUpperCase() === StatementTypes.FINANCING_STATEMENT) {
          const stepConfig: Array<ButtonConfigIF> = getFinancingButtons.value
          var config:ButtonConfigIF
          for (var i in stepConfig) {
            config = stepConfig[i]
            if (config.stepName === localState.stepName) {
              return config
            }
          }
        }
        return null
      })
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
      const stateModel:StateModelIF = getStateModel.value
      const draft:DraftIF = await saveFinancingStatementDraft(stateModel)
      setDraft(draft)
      if (draft.error !== undefined) {
        console.log('saveDraft error status: ' + draft.error.statusCode + ' message: ' + draft.error.message)
        // Emit error message.
        emit('draft-save-error', draft.error)
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
      if (localState.statementType.toUpperCase() === StatementTypes.FINANCING_STATEMENT &&
          localState.stepName === RouteNames.REVIEW_CONFIRM) {
        submitFinancingStatement()
      } else {
        props.router.push({
          name: localState.buttonConfig.nextRouteName
        })
      }
    }

    /** Check all steps are valid, make api call to create a financing statement, handle api errors. */
    const submitFinancingStatement = () => {
      const stateModel:StateModelIF = getStateModel.value
      if (stateModel.lengthTrustStep.valid &&
          stateModel.addSecuredPartiesAndDebtorsStep.valid &&
          stateModel.addCollateralStep.valid) {
        // API call here
        // Handle API call error here
        props.router.push({
          name: localState.buttonConfig.nextRouteName
        })
      } else {
        // emit registation incomplete error
        const error:ErrorIF = {
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
