<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

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
          isMhr
          :currentStatementType="statementType"
          :currentStepName="$route.name"
          :router="$router"
          :forceSave="saveDraftExit"
          @registration-incomplete="registrationIncomplete()"
          @error="emitError($event)"
          @submit="submit()"
          @cancelProceed="resetAllValidations()"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, toRefs } from 'vue-demi'
import { useRoute, useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { RegistrationFlowType, RouteNames, StatementTypes, UIRegistrationTypes } from '@/enums'
import { getFeatureFlag, getMhrDraft, submitMhrRegistration } from '@/utils'
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { useHomeOwners, useMhrValidations, useNewMhrRegistration } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
/* eslint-disable no-unused-vars */
import { ErrorIF, MhrRegistrationIF, RegTableNewItemI, StepIF } from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
import BaseDialog from '@/components/dialogs/BaseDialog.vue'
import { storeToRefs } from 'pinia'
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
    },
    saveDraftExit: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const route = useRoute()
    const router = useRouter()
    const {
      // Actions
      setUnsavedChanges,
      setRegTableNewItem,
      setMhrTransferType
    } = useStore()
    const {
      // Getters
      getSteps,
      getMhrDraftNumber,
      getRegistrationType,
      getRegistrationFlowType,
      getMhrRegistrationValidationModel
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      getValidation,
      resetAllValidations,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const {
      initDraftMhr,
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
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || ('' as UIRegistrationTypes)
      }),
      isValidatingApp: computed((): boolean => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      }),
      isValidMhrRegistration: computed((): boolean => {
        return getSteps.value.every((step: StepIF) => step.valid)
      })
    })

    /** Helper to check is the current route matches */
    const isRouteName = (routeName: RouteNames): boolean => {
      return (route.name === routeName)
    }

    const registrationIncomplete = (): void => {
      scrollToInvalid(MhrSectVal.REVIEW_CONFIRM_VALID, 'mhr-review-confirm')
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, true)
    }

    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    const goToDash = (): void => {
      router.push({
        name: RouteNames.DASHBOARD
      })
    }

    onMounted(async (): Promise<void> => {
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
      setMhrTransferType(null)
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS, false)
      setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, false)

      // page is ready to view
      if (getMhrDraftNumber.value) {
        const { registration } = await getMhrDraft(getMhrDraftNumber.value)
        await initDraftMhr(registration as unknown as MhrRegistrationIF)
      }

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
          await router.push({ name: RouteNames.DASHBOARD })
        } else {
          emitError(mhrSubmission?.error)
        }
      } else {
        let stepsValidation = getSteps.value.filter((step : StepIF) => step.valid)
        stepsValidation.pop() // Removes review confirm step from stepsValidation
        await scrollToInvalid(MhrSectVal.REVIEW_CONFIRM_VALID, 'mhr-review-confirm', stepsValidation)
      }
    }

    return {
      getSteps,
      emitError,
      isRouteName,
      registrationIncomplete,
      submit,
      resetAllValidations,
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
