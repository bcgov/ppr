<template>
  <div id="exemptions">
    <v-container class="footer-view-container pa-0 mt-11">
      <!-- Overlays and Dialogs -->
      <v-overlay
        v-model="loading"
        class="overlay-container"
      >
        <v-progress-circular
          color="primary"
          size="30"
          indeterminate
        />
      </v-overlay>

      <!-- Exemption Content Flow -->
      <section
        v-if="dataLoaded"
        class="pa-0"
      >
        <v-row no-gutters>
          <v-col cols="9">
            <v-row
              id="exemption-header"
              no-gutters
              class="soft-corners-top"
            >
              <v-col cols="auto">
                <h1>{{ exemptionLabel }}</h1>
              </v-col>
            </v-row>
            <Stepper
              class="mt-11"
              :step-config="getMhrExemptionSteps"
              :show-step-errors="validate"
            />
            <!-- Component Steps -->
            <component
              :is="step.component"
              v-for="step in getMhrExemptionSteps"
              v-show="isRouteName(step.to)"
              :key="step.step"
              :show-errors="validate"
              :validate-review="false"
            />
          </v-col>
          <v-col
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :set-show-buttons="false"
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="isNonResExemption
                  ? FeeSummaryTypes.NON_RESIDENTIAL_EXEMPTION
                  : FeeSummaryTypes.RESIDENTIAL_EXEMPTION"
                data-test-id="exemption-fee-summary"
              />
            </aside>
          </v-col>
        </v-row>
      </section>
    </v-container>

    <!-- Footer Navigation -->
    <v-row
      v-if="dataLoaded"
      no-gutters
      class="mt-20"
    >
      <v-col cols="12">
        <ButtonFooter
          :nav-config="MhrExemptionFooterConfig"
          :current-step-name="$route.name"
          :BaseDialog-options="notCompleteDialog"
          @error="emitError($event)"
          @submit="submit()"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, nextTick, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { createExemption, getFeatureFlag, scrollToFirstVisibleErrorComponent } from '@/utils'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { MhrExemptionFooterConfig } from '@/resources/buttonFooterConfig'
import { useAuth, useExemptions, useMhrInformation, useNavigation } from '@/composables'
import type { ErrorIF, RegTableNewItemI } from '@/interfaces'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { RouteNames } from '@/enums'

export default defineComponent({
  name: 'Exemptions',
  components: {
    Stepper,
    ButtonFooter,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  emits: ['emitHaveData', 'error'],
  setup (props, { emit }) {
    const { isAuthenticated } = useAuth()
    const { isRouteName, goToDash, route } = useNavigation()
    const { parseMhrInformation } = useMhrInformation()
    const { buildExemptionPayload, exemptionLabel, isNonResExemption } = useExemptions()
    const { setRegTableNewItem, setUnsavedChanges } = useStore()
    const {
      getMhrExemptionSteps,
      getMhrExemption,
      getMhrInformation,
      getStaffPayment,
      isMhrExemptionValid
    } = storeToRefs(useStore())

    const localState = reactive({
      dataLoaded: false,
      loading: false,
      validate: false
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value || !getFeatureFlag('mhr-exemption-enabled')) {
        await goToDash()
        return
      }

      localState.loading = true
      await parseMhrInformation()
      emit('emitHaveData', true)
      localState.dataLoaded = true
      localState.loading = false

      // Set unsaved changes to prompt cancel dialogs on exit
      await setUnsavedChanges(true)
    })

    const emitError = (error: ErrorIF): void => {
      emit('error', error)
    }

    const submit = async (): Promise<void> => {
      // If review mode: validate and submit
      if (route.name === RouteNames.EXEMPTION_REVIEW) {
        localState.loading = true
        localState.validate = true
        await nextTick()
        await scrollToFirstVisibleErrorComponent()

        if (isMhrExemptionValid.value) {
          // Construct payload
          const payload = buildExemptionPayload()

          // Submit Filing
          const exemptionFiling =
            await createExemption(payload, getMhrInformation.value.mhrNumber, getStaffPayment.value) as any

          // Add new reg action for table scroll and go to dash
          if (!exemptionFiling?.error) {
            const newRegItem: RegTableNewItemI = {
              addedReg: exemptionFiling.documentRegistrationNumber,
              addedRegParent: exemptionFiling.mhrNumber,
              addedRegSummary: exemptionFiling,
              prevDraft: ''
            }
            setRegTableNewItem(newRegItem)
            await goToDash()
          } else emitError(exemptionFiling?.error)


          localState.loading = false
        } else localState.loading = false
      }
    }

    watch(() => route.name, async () => {
      await nextTick()
      localState.validate && await scrollToFirstVisibleErrorComponent()
    })

    return {
      submit,
      emitError,
      isRouteName,
      exemptionLabel,
      isNonResExemption,
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
@import '@/assets/styles/theme';
</style>
