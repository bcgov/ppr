<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="showCancelDialog = false"
    />
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="registration-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>Manufactured Home Registration</h1>
              </v-col>
            </v-row>
            <stepper class="mt-4" :showStepErrorsFlag="isValidatingApp && !isValidMhrRegistration"/>
            <!-- Component Steps -->
            <component
              v-for="step in getSteps"
              v-show="isRouteName(step.to)"
              :is="step.component"
              :key="step.step"
            />
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setRegistrationLength="registrationLength"
                  :setRegistrationType="registrationTypeUI"
                />
              </affix>
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row no-gutters class="pt-10">
      <v-col cols="12">
        <button-footer
          :currentStatementType="statementType"
          :currentStepName="$route.name"
          :router="$router"
          @registration-incomplete="registrationIncomplete()"
          @error="emitError()"
          @submit="submit()"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { RegistrationFlowType, RouteNames, StatementTypes } from '@/enums'
import { getFeatureFlag, submitMhrRegistration } from '@/utils'
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { useHomeOwners, useMhrValidations, useNewMhrRegistration } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
/* eslint-disable no-unused-vars */
import { RegistrationTypeIF, RegTableNewItemI } from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
import BaseDialog from '@/components/dialogs/BaseDialog.vue'
import { registrationCompleteError } from '@/resources/dialogOptions'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'MhrRegistration',
  components: {
    ButtonFooter,
    Stepper,
    StickyContainer,
    BaseDialog
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
  setup (props, context) {
    const {
      getRegistrationFlowType,
      getRegistrationType,
      getSteps,
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getRegistrationFlowType',
      'getRegistrationType',
      'getSteps',
      'getMhrRegistrationValidationModel'
    ])

    const {
      setEmptyMhr,
      setUnsavedChanges,
      setRegTableNewItem
    } = useActions<any>([
      'setEmptyMhr',
      'setUnsavedChanges',
      'setRegTableNewItem'
    ])

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      getValidation,
      getStepValidation,
      resetAllValidations,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const {
      initNewMhr,
      buildApiData,
      parseStaffPayment
    } = useNewMhrRegistration()

    const {
      setShowGroups
    } = useHomeOwners()

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      feeType: FeeSummaryTypes.NEW_MHR,
      statementType: StatementTypes.FINANCING_STATEMENT,
      isAuthenticated: computed((): boolean => {
        return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
      }),
      registrationLength: computed((): RegistrationLengthI => {
        return { lifeInfinite: true, lifeYears: 0 }
      }),
      registrationTypeUI: computed((): RegistrationTypeIF => {
        return getRegistrationType.value?.registrationTypeUI || ''
      }),
      isValidatingApp: computed((): boolean => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      }),
      isValidMhrRegistration: computed((): boolean => {
        return getStepValidation(MhrSectVal.YOUR_HOME_VALID) &&
            getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID) &&
            getStepValidation(MhrSectVal.HOME_OWNERS_VALID) &&
            getStepValidation(MhrSectVal.LOCATION_VALID) &&
            getStepValidation(MhrSectVal.REVIEW_CONFIRM_VALID)
      }),
      options: registrationCompleteError,
      showCancelDialog: false
    })

    /** Helper to check is the current route matches */
    const isRouteName = (routeName: RouteNames): boolean => {
      return (context.root.$route.name === routeName)
    }

    const registrationIncomplete = (): void => {
      scrollToInvalid(MhrSectVal.REVIEW_CONFIRM_VALID, 'mhr-review-confirm')
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, true)
    }

    const emitError = (): void => {
      context.emit('error', true)
    }

    const goToDash = (): void => {
      context.root.$router.push({
        name: RouteNames.DASHBOARD
      })
    }

    onMounted((): void => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !localState.isAuthenticated ||
        (!props.isJestRunning && !getFeatureFlag('mhr-registration-enabled'))) {
        goToDash()
        return
      }
      // redirect if store doesn't contain all needed data (happens on page reload, etc.)
      if (!getRegistrationType.value || getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
        goToDash()
        return
      }

      // Reset validations
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS, false)
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, false)

      // page is ready to view
      setEmptyMhr(initNewMhr())
      context.emit('emitHaveData', true)
      localState.dataLoaded = true
    })

    const submit = async () => {
      // Prompt App Validations
      await setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, true)
      await nextTick()

      if (localState.isValidMhrRegistration) {
        // Submit Filing
        localState.submitting = true
        const mhrSubmission = await submitMhrRegistration(buildApiData(), parseStaffPayment())
        localState.submitting = false
        if (!mhrSubmission.error && mhrSubmission?.mhrNumber) {
          resetAllValidations()
          setShowGroups(false)
          const newRegItem: RegTableNewItemI = {
            addedReg: mhrSubmission.mhrNumber,
            addedRegParent: '',
            addedRegSummary: mhrSubmission,
            prevDraft: mhrSubmission.documentId
          }
          setRegTableNewItem(newRegItem)
          setUnsavedChanges(false)
          await context.root.$router.push({ name: RouteNames.DASHBOARD })
        } else {
          console.log(mhrSubmission?.error) // Handle Schema or Api errors here..
          localState.options = registrationCompleteError
          localState.showCancelDialog = true
        }
      } else {
        await scrollToInvalid(MhrSectVal.REVIEW_CONFIRM_VALID, 'mhr-review-confirm',
          [
            getStepValidation(MhrSectVal.YOUR_HOME_VALID),
            getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID),
            getStepValidation(MhrSectVal.HOME_OWNERS_VALID),
            getStepValidation(MhrSectVal.LOCATION_VALID)
          ])
      }
    }

    return {
      getSteps,
      emitError,
      isRouteName,
      registrationIncomplete,
      submit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.step-container {
  margin-top: 1rem;
  padding: 1.25rem;
}
.meta-container {
  display: flex;
  flex-flow: column nowrap;
  position: relative;
  > label:first-child {
    font-weight: 700;
  }
}
@media (min-width: 768px) {
  .meta-container {
    flex-flow: row nowrap;
    > label:first-child {
      flex: 0 0 auto;
      padding-right: 2rem;
      width: 12rem;
    }
  }
}
.reg-default-btn {
  background-color: $gray3 !important;
}
.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
