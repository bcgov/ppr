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
            <aside>{{userSelectedPaymentMethod}}
              <StickyContainer
                :show-connect-fees="true"
                :set-show-buttons="false"
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
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
          :base-dialog-options="notCompleteDialog"
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
import { createExemption } from '@/utils/mhr-api-helper'
import { scrollToFirstVisibleErrorComponent } from '@/utils'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { MhrExemptionFooterConfig } from '@/resources/buttonFooterConfig'
import { useAuth, useExemptions, useMhrInformation, useNavigation } from '@/composables'
import type { ErrorIF, RegTableNewItemI } from '@/interfaces'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { ConnectPaymentMethod, RouteNames } from '@/enums'

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
    const { isRouteName, goToDash, goToPay, route } = useNavigation()
    const { parseMhrInformation } = useMhrInformation()
    const { buildExemptionPayload, exemptionLabel, isNonResExemption } = useExemptions()
    const { setRegistrationFees } = useConnectFeesHandler()
    const { userSelectedPaymentMethod } = storeToRefs(useConnectFeeStore())
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
      validate: false,
      feeType: computed(() => {
        return isNonResExemption.value
          ? FeeSummaryTypes.NON_RESIDENTIAL_EXEMPTION
          : FeeSummaryTypes.RESIDENTIAL_EXEMPTION
      })
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value) {
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
            await createExemption(
              payload,
              getMhrInformation.value.mhrNumber,
              getStaffPayment.value,
              userSelectedPaymentMethod.value === ConnectPaymentMethod.DIRECT_PAY
            ) as any

          if(exemptionFiling?.paymentPending) {
            goToPay(exemptionFiling.payment?.invoiceId, null, `mhReg-${getMhrInformation.value.mhrNumber}`)
          }

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

    watch(() => localState.feeType, async (val: FeeSummaryTypes) => {
      setRegistrationFees(val)
    }, { immediate: true })

    watch(() => route.name, async () => {
      await nextTick()
      localState.validate && await scrollToFirstVisibleErrorComponent()
    })

    return {
      userSelectedPaymentMethod,
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
@use '@/assets/styles/theme' as *;
</style>
