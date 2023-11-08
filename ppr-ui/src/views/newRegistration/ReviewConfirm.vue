<template>
  <v-container
    v-if="dataLoaded"
    class="footer-view-container pa-0"
  >
    <div class="py-0">
      <div class="container pa-0 pt-4">
        <v-row noGutters>
          <v-col
            class="left-page"
            cols="9"
          >
            <v-row
              id="registration-header"
              noGutters
              class="pt-3 pb-3"
            >
              <v-col cols="auto">
                <h1>{{ registrationTypeUI }}<span class="only-print"> - Draft</span></h1>
              </v-col>
            </v-row>
            <Stepper
              class="mt-4"
              :stepConfig="getPprSteps"
              :showStepErrors="showStepErrors"
            />
            <v-row
              class="pt-10"
              noGutters
            >
              <v-col
                cols="auto"
                class="generic-label"
              >
                Review and Confirm
              </v-col>
            </v-row>
            <v-row noGutters>
              <v-col class="pt-2 pb-6 sub-header-info">
                <p>
                  Review the information in your registration. If you need to change anything,
                  return to the step to make the necessary change.
                </p>
              </v-col>
            </v-row>
            <v-row noGutters>
              <v-container
                fluid
                class="px-0"
              >
                <v-row
                  noGutters
                  class="pt-1"
                >
                  <v-col>
                    <RegistrationLengthTrustSummary />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row
              id="parties-summary"
              noGutters
            >
              <v-container
                fluid
                class="px-0 pt-8"
              >
                <v-row
                  noGutters
                  class="pt-1"
                >
                  <v-col>
                    <Parties :isSummary="true" />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row noGutters>
              <v-container
                fluid
                class="px-0 pt-8"
              >
                <v-row
                  noGutters
                  class="pt-1"
                >
                  <v-col>
                    <Collateral :isSummary="true" />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row noGutters>
              <v-container
                fluid
                class="px-0 pt-8"
              >
                <v-row
                  noGutters
                  class="pt-1"
                >
                  <v-col>
                    <FolioNumberSummary
                      :setShowErrors="showStepErrors"
                      @folioValid="validFolio = $event"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row noGutters>
              <v-container
                fluid
                class="px-0 pt-8"
              >
                <v-row
                  noGutters
                  class="pt-1"
                >
                  <v-col>
                    <CertifyInformation
                      class="pt-10"
                      :sectionNumber="2"
                      :setShowErrors="showStepErrors"
                      @certifyValid="validCertify = $event"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
          </v-col>
          <v-col
            class="right-page pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :setRightOffset="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setRegistrationLength="registrationLength"
                :setRegistrationType="registrationTypeUI"
              />
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row
      noGutters
      class="pt-15"
    >
      <v-col cols="12">
        <ButtonFooter
          :navConfig="getFooterButtonConfig"
          :currentStepName="stepName"
          :certifyValid="validCertify && validFolio"
          :forceSave="saveDraftExit"
          @registration-incomplete="registrationIncomplete()"
          @error="emitError($event)"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { APIRegistrationTypes, RegistrationFlowType, RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Stepper, StickyContainer, CertifyInformation } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { Parties } from '@/components/parties'
import FolioNumberSummary from '@/components/common/FolioNumberSummary.vue'
import { getFeatureFlag } from '@/utils'
import { ErrorIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { RegistrationLengthI } from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '@/composables' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'ReviewConfirm',
  components: {
    ButtonFooter,
    Collateral,
    FolioNumberSummary,
    Parties,
    RegistrationLengthTrustSummary,
    Stepper,
    CertifyInformation,
    StickyContainer
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
  emits: ['error', 'haveData'],
  setup (props, context) {
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setLengthTrust,
      setAddCollateral,
      setShowStepErrors,
      setUnsavedChanges,
      setAddSecuredPartiesAndDebtors
    } = useStore()
    const {
      // Getters
      getPprSteps,
      showStepErrors,
      getAddCollateral,
      getLengthTrust,
      hasUnsavedChanges,
      getRegistrationOther,
      getRegistrationType,
      getRegistrationFlowType,
      getAddSecuredPartiesAndDebtors,
      getFooterButtonConfig
    } = storeToRefs(useStore())

    const localState = reactive({
      dataLoaded: false,
      feeType: FeeSummaryTypes.NEW,
      showStepErrors: false,
      stepName: RouteNames.REVIEW_CONFIRM,
      validCertify: false,
      validFolio: true,
      registrationLength: computed((): RegistrationLengthI => {
        return {
          lifeInfinite: getLengthTrust.value?.lifeInfinite || false,
          lifeYears: getLengthTrust.value?.lifeYears || 0
        }
      }),
      registrationTypeUI: computed((): string => {
        if (getRegistrationType.value?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
          return getRegistrationOther.value || ''
        }
        return getRegistrationType.value?.registrationTypeUI || ''
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || ''
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (val: boolean): void => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        goToDash()
        return
      }
      // redirect if store doesn't contain all needed data (happens on page reload, etc.)
      if (!getRegistrationType.value || getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
        goToDash()
        return
      }
      const unsavedChanges = hasUnsavedChanges.value
      const collateral = getAddCollateral.value
      if (!collateral.valid) {
        collateral.showInvalid = true
        setAddCollateral(collateral)
      }
      const lengthTrust = getLengthTrust.value
      if (!lengthTrust.valid) {
        lengthTrust.showInvalid = true
        setLengthTrust(lengthTrust)
      }
      const parties = getAddSecuredPartiesAndDebtors.value
      if (!parties.valid) {
        parties.showInvalid = true
        setAddSecuredPartiesAndDebtors(parties)
      }
      // set unsavedChanges back to what it was
      setUnsavedChanges(unsavedChanges)
      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    const registrationIncomplete = (): void => {
      localState.showStepErrors = true
      setShowStepErrors(true)
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    return {
      emitError,
      getPprSteps,
      showStepErrors,
      registrationIncomplete,
      getFooterButtonConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
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
@media print {
  body {
    overflow: auto;
    height: auto;
    -webkit-print-print-color-adjust: exact !important;   /* Chrome, Safari, Edge */
    print-color-adjust: exact !important;                 /*Firefox*/
  }
  :deep(.v-data-table__wrapper) {
    overflow: visible;
    height: auto;
  }
  :deep(.col-9) {
    max-width: 100%;
  }
  .v-footer {
    display: none;
  }
  .right-page {
    width: 30%;
  }
  #step-buttons-container {
    display: none;
  }
  table {
    table-layout: auto;
  }
  .px-15 {
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
  :deep(.v-data-table > .v-data-table__wrapper > table > tbody > tr > td),
  :deep(.v-data-table > .v-data-table__wrapper > table > tbody > tr > th),
  :deep(.v-data-table > .v-data-table__wrapper > table > thead > tr > td),
  :deep(.v-data-table > .v-data-table__wrapper > table > thead > tr > th)
  {
    padding: 0 8px;
  }
  #parties-summary {
    page-break-inside: avoid !important;
  }
}
.reg-default-btn {
  background-color: $gray3 !important;
}
.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
