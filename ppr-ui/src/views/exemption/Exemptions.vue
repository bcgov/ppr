<template>
  <div v-if="dataLoaded" id="exemptions">
    <v-container class="view-container px-15 py-0">
      <v-container class="pa-0 mt-11">
        <!-- Overlays and Dialogs -->
        <v-overlay v-model="submitting">
          <v-progress-circular color="primary" size="50" indeterminate />
        </v-overlay>

        <!-- Exemption Content Flow -->
        <section class="pa-0">
          <v-row no-gutters>
            <v-col cols="9">
              <v-row no-gutters id="exemption-header" class="soft-corners-top">
                <v-col cols="auto">
                  <h1>Residential Exemption</h1>
                </v-col>
              </v-row>
              <Stepper
                class="mt-11"
                :stepConfig="getMhrExemptionSteps"
                :showStepErrors="validate"
              />
              <!-- Component Steps -->
              <component
                v-for="step in getMhrExemptionSteps"
                v-show="isRouteName(step.to)"
                :is="step.component"
                :key="step.step"
                :showErrors="validate"
                :validateReview="false"
              />
            </v-col>
            <v-col class="pl-6 pt-5" cols="3">
              <aside>
                <affix
                  class="sticky-container overlap"
                  relative-element-selector=".col-9"
                  :offset="{ top: 90, bottom: -100 }"
                >
                  <StickyContainer
                    :setShowButtons="false"
                    :setRightOffset="true"
                    :setShowFeeSummary="true"
                    :setFeeType="FeeSummaryTypes.RESIDENTIAL_EXEMPTION"
                    data-test-id="exemption-fee-summary"
                  />
                </affix>
              </aside>
            </v-col>
          </v-row>
        </section>
      </v-container>
    </v-container>

    <!-- Footer Navigation -->
    <v-row no-gutters class="mt-20">
      <v-col cols="12">
        <ButtonFooter
          :navConfig="MhrExemptionFooterConfig"
          :currentStepName="$route.name"
          :baseDialogOptions="notCompleteDialog"
          @error="emitError($event)"
          @submit="submit()"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, nextTick, onMounted, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { createExemption, getFeatureFlag, scrollToFirstVisibleErrorComponent } from '@/utils'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { MhrExemptionFooterConfig } from '@/resources/buttonFooterConfig'
import { useAuth, useMhrInformation, useNavigation } from '@/composables'
import { ErrorDetailIF, ErrorIF } from '@/interfaces'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { notCompleteDialog } from '@/resources/dialogOptions'

export default defineComponent({
  name: 'Exemptions',
  emits: ['emitHaveData', 'error'],
  components: {
    Stepper,
    ButtonFooter,
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
    }
  },
  setup (props, { emit }) {
    const { isAuthenticated } = useAuth()
    const { isRouteName, goToDash, route } = useNavigation()
    const { parseMhrInformation } = useMhrInformation()
    const { setUnsavedChanges } = useStore()
    const { getMhrExemptionSteps, getMhrExemption, getMhrInformation, isMhrExemptionValid } = storeToRefs(useStore())

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      validate: false
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value ||
        (!props.isJestRunning && !getFeatureFlag('mhr-exemption-enabled'))) {
        await goToDash()
        return
      }

      emit('emitHaveData', true)
      localState.dataLoaded = true

      await parseMhrInformation()

      // Set unsaved changes to prompt cancel dialogs on exit
      await setUnsavedChanges(true)
    })

    const emitError = (error: ErrorIF): void => {
      emit('error', error)
    }

    const submit = async (): Promise<void> => {
      localState.submitting = true
      localState.validate = true
      await nextTick()
      await scrollToFirstVisibleErrorComponent()

      if (isMhrExemptionValid.value) {
        // Submit Filing
        const exemptionFiling = await createExemption(getMhrExemption.value, getMhrInformation.value.mhrNumber) as ErrorDetailIF
        if (!exemptionFiling?.error) {
          localState.submitting = false
          goToDash()
        } else {
          emitError(exemptionFiling?.error)
        }
      }
    }

    watch(() => route.name, async () => {
      await nextTick()
      await scrollToFirstVisibleErrorComponent()
    })

    return {
      submit,
      emitError,
      isRouteName,
      getMhrExemptionSteps,
      FeeSummaryTypes,
      getMhrExemption,
      notCompleteDialog,
      MhrExemptionFooterConfig,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
