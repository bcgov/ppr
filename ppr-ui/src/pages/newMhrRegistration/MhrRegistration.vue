<template>
  <v-container
    v-if="dataLoaded"
    class="px-0 footer-view-container"
    fluid
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
      :set-options="outOfDateOwnersDialogOptions(getMhrInformation.mhrNumber)"
      :set-display="showOutOfDateDraftDialog"
      @proceed="handleOutOfDateDialogResp"
    />

    <div class="py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <!-- Mhr Corrections Header -->
            <template v-if="isMhrCorrection">
              <v-row
                id="registration-correction-header"
                no-gutters
                class="pt-3 pb-3 soft-corners-top"
              >
                <v-col>
                  <h1>{{ getRegistrationType.text }} {{ isDraft && ' - Draft' }} </h1>
                </v-col>
              </v-row>
              <v-row
                no-gutters
                class="pt-4 pb-5"
              >
                <p v-if="isPublicAmendment">
                  Make any necessary minor changes or updates to this home registration.
                </p>
                <p v-else>
                  Make any necessary corrections to fix typos, errors, or omissions for this home registration.
                </p>
              </v-row>
            </template>

            <template v-else-if="isMhrReRegistration">
              <v-row
                id="re-registration-header"
                no-gutters
                class="pt-3 pb-6"
              >
                <v-col>
                  <h1>{{ getRegistrationType.registrationTypeUI }} {{ isDraft && ' - Draft' }} </h1>
                  <p class="pt-7">
                    The homeowner and home location information in the Initial Registration form must align
                    with the supporting documentation.
                  </p>
                </v-col>
              </v-row>
            </template>

            <!-- Mhr Header -->
            <v-row
              id="registration-header"
              no-gutters
              class="pt-3 pb-3 soft-corners-top"
            >
              <v-col>
                <h1>{{ `Manufactured Home Registration${isDraft ? ' - Draft' : ''}` }}</h1>
              </v-col>
            </v-row>
            <Stepper
              class="mt-4"
              :step-config="getMhrSteps"
              :show-step-errors="isValidatingApp && !isValidMhrRegistration"
            />
            <!-- Component Steps -->
            <NuxtPage />

          </v-col>
          <v-col
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-fee-subtitle="getRegistrationType.registrationTypeUI"
                :set-registration-length="registrationLength"
                :set-registration-type="registrationTypeUI"
              />
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row
      no-gutters
      class="mt-20"
    >
      <v-col cols="12">
        <ButtonFooter
          is-mhr
          :nav-config="getFooterButtonConfig"
          :current-step-name="$route.name"
          :force-save="saveDraftExit"
          @error="emitError($event)"
          @submit="submit()"
          @cancel-proceed="resetAllValidations()"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onBeforeUnmount, onMounted, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import type { UIRegistrationTypes } from '@/enums';
import { APIMhrTypes, ErrorCategories, RegistrationFlowType, RouteNames } from '@/enums'
import { getFeatureFlag } from '@/utils'
import { getMhrDraft, submitAdminRegistration, submitMhrRegistration } from '@/utils/mhr-api-helper'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import {
  useAuth,
  useHomeOwners,
  useMhrCorrections,
  useMhrValidations,
  useNavigation,
  useNewMhrRegistration
} from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import type { ErrorIF, MhrRegistrationIF, RegTableNewItemI, StepIF } from '@/interfaces'
import type { RegistrationLengthI } from '@/composables/fees/interfaces'
import { outOfDateOwnersDialogOptions } from '@/resources/dialogOptions/confirmationDialogs'

export default defineComponent({
  name: 'MhrRegistration',
  components: {
    ButtonFooter,
    Stepper,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    saveDraftExit: {
      type: Boolean,
      default: false
    }
  },
  emits: ['error', 'emitHaveData'],
  setup (props, context) {
    const { isRouteName, goToDash, goToRoute, goToPay } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setUnsavedChanges,
      setRegTableNewItem,
      setMhrTransferType,
      setDraft,
      setMhrInformationDraftId,
      setMhrCorrectStatusType
    } = useStore()
    const {
      // Getters
      getMhrSteps,
      getFooterButtonConfig,
      getMhrInformation,
      getMhrDraftNumber,
      getRegistrationType,
      getRegistrationFlowType,
      getMhrRegistrationValidationModel,
      isMhrReRegistration
    } = storeToRefs(useStore())
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      getValidation,
      resetAllValidations,
      scrollToInvalidReviewConfirm
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const {
      isMhrCorrection,
      isStaffCorrection,
      isClientCorrection,
      isPublicAmendment,
      getCorrectionsList,
      buildCorrectionPayload
    } = useMhrCorrections()
    const {
      initDraftOrCurrentMhr,
      buildApiData,
      parseStaffPayment
    } = useNewMhrRegistration(isMhrCorrection.value)
    const {
      setShowGroups
    } = useHomeOwners(false, isMhrCorrection.value)

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      showOutOfDateDraftDialog: false,
      feeType: computed(() => {
        switch(true) {
          case isStaffCorrection.value:
            return FeeSummaryTypes.MHR_STAFF_CORRECTION
          case isClientCorrection.value:
            return FeeSummaryTypes.MHR_CLIENT_CORRECTION
          case isPublicAmendment.value:
            return FeeSummaryTypes.MHR_PUBLIC_AMENDMENT
          case isMhrReRegistration.value:
            return FeeSummaryTypes.MHR_RE_REGISTRATION
          default:
            return FeeSummaryTypes.NEW_MHR
        }
      }),
      registrationLength: computed((): RegistrationLengthI => {
        return { lifeInfinite: true, lifeYears: 0 }
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || ('' as UIRegistrationTypes)
      }),
      isDraft: computed((): boolean => {
        return getMhrDraftNumber.value
      }),
      isValidatingApp: computed((): boolean => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      }),
      isValidMhrRegistration: computed((): boolean => {
        return getMhrSteps.value.every((step: StepIF) => step.valid)
      }),
      navConfiguration: computed(() => {
        return getFooterButtonConfig.value
      })
    })

    const emitError = (error: ErrorIF): void => {
      // Intercept and handle out of date error (stale draft)
      if (error?.category === ErrorCategories.DRAFT_OUT_OF_DATE) {
        localState.showOutOfDateDraftDialog = true
        return
      }
      context.emit('error', error)
    }

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value || !getFeatureFlag('mhr-registration-enabled')) {
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
      resetAllValidations()

      // page is ready to view
      if (getMhrDraftNumber.value && !isMhrCorrection.value) {
        const { registration } = await getMhrDraft(getMhrDraftNumber.value)
        await initDraftOrCurrentMhr(registration as unknown as MhrRegistrationIF)
      }
      context.emit('emitHaveData', true)
      localState.dataLoaded = true
    })

    onBeforeUnmount(async () => {
      // fixes the issue when user is navigated from Draft Corrections to MHR Info page
      if (getMhrInformation.value?.registrationType === APIMhrTypes.REGISTRY_STAFF_ADMIN) {
        await setMhrInformationDraftId('')
      }
    })

    const submit = async () => {
      // Prompt App Validations
      await setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, true)
      await nextTick()

      // MHR Correction: Scroll to top and return when no Corrections have been made
      if(isMhrCorrection.value && !getCorrectionsList().length) {
        window.scrollTo({ top: 0, behavior: 'smooth' })
        return
      }

      if (localState.isValidMhrRegistration) {
        // Submit Filing
        localState.submitting = true
        const data = buildApiData()

        // In cases where hasNoCertification is selected:
        // Need to clear hasNoCertification for submission and replace it with an empty csa number
        // This is to meet the API Schema requirements.
        // This does not apply to drafts as we want to maintain that property for resuming drafts
        if (data?.description?.hasNoCertification) {
          delete data.description.hasNoCertification
          data.description.csaNumber = ''
        }

        // Property is maintained for resuming draft but removed for submission
        if (data.submittingParty.hasUsedPartyLookup) {
          delete data.submittingParty.hasUsedPartyLookup
        }

        // Because Corrections flow is reused for Re-Registrations, the Mhr status needs to be set in corrections
        if (isMhrReRegistration.value) {
          setMhrCorrectStatusType(getMhrInformation.value.statusType)
        }

        const mhrSubmission = isMhrCorrection.value || isMhrReRegistration.value
          ? await submitAdminRegistration(
              getMhrInformation.value.mhrNumber,
              buildCorrectionPayload(data),
              parseStaffPayment()
            )
          : await submitMhrRegistration(data, parseStaffPayment())

        localState.submitting = false
        if (!mhrSubmission.error && mhrSubmission?.mhrNumber) {
          resetAllValidations()
          setShowGroups(false)
          const newRegItem: RegTableNewItemI = {
            addedReg: (isMhrCorrection.value || isMhrReRegistration.value)
             ? mhrSubmission.documentRegistrationNumber : mhrSubmission.mhrNumber,
            addedRegParent: (isMhrCorrection.value || isMhrReRegistration.value)
              ? getMhrInformation.value.mhrNumber : '',
            addedRegSummary: mhrSubmission,
            prevDraft: mhrSubmission.documentId
          }
          setRegTableNewItem(newRegItem)
          setUnsavedChanges(false)
          goToDash()
        } else if (mhrSubmission?.paymentPending) {
          goToPay(mhrSubmission.payment?.invoiceId)
        } else {
          emitError(mhrSubmission?.error)
        }
      } else {
        const stepsValidation = getMhrSteps.value.map((step: StepIF) => step.valid)
        stepsValidation.pop() // Removes review confirm step from stepsValidation
        scrollToInvalidReviewConfirm(stepsValidation)
      }
    }

    const handleOutOfDateDialogResp = async (proceed: boolean) => {
      if (proceed) {
        await setDraft(null)
        await goToRoute(RouteNames.MHR_INFORMATION)
      }
      localState.showOutOfDateDraftDialog = false
    }

    return {
      getMhrSteps,
      emitError,
      isRouteName,
      submit,
      isMhrCorrection,
      isMhrReRegistration,
      isPublicAmendment,
      getRegistrationType,
      resetAllValidations,
      getFooterButtonConfig,
      getMhrInformation,
      outOfDateOwnersDialogOptions,
      handleOutOfDateDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme';

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
