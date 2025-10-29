<template>
  <v-container
    v-if="dataLoaded"
    class="pa-0 footer-view-container"
  >
    <div class="py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col
            cols="9"
            role="region"
          >
            <v-row
              id="registration-header"
              no-gutters
              class="length-trust-header pt-3 pb-3 soft-corners-top"
            >
              <v-col cols="auto">
                <h2 class="fs-32 lh-36">
                  {{ registrationTypeUI }}
                </h2>
              </v-col>
            </v-row>
            <Stepper
              class="mt-4"
              :step-config="getPprSteps"
              :show-step-errors="showStepErrors"
            />
            <v-row
              no-gutters
              class="pt-10"
            >
              <v-col
                cols="auto"
                class="generic-label"
              >
                Add Collateral
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6 sub-header-info">
                Add the collateral for this {{ registrationTypeUI }} registration.
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="12">
                <Collateral :is-summary="false" />
              </v-col>
            </v-row>
          </v-col>
          <v-col
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :show-connect-fees="true"
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-registration-length="registrationLength"
                :set-registration-type="registrationTypeUI"
              />
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <ButtonFooter
      :nav-config="getFooterButtonConfig"
      :current-step-name="stepName"
      @error="emitError($event)"
    />
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { APIRegistrationTypes, RegistrationFlowType, RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import type { ErrorIF } from '@/interfaces'
import type { RegistrationLengthI } from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '@/composables'

export default defineComponent({
  name: 'AddCollateral',
  components: {
    ButtonFooter,
    Stepper,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  emits: ['error', 'haveData'],
  setup (props, context) {
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      getPprSteps,
      showStepErrors,
      getLengthTrust,
      getRegistrationType,
      getRegistrationOther,
      getRegistrationFlowType,
      getFooterButtonConfig
    } = storeToRefs(useStore())
    const localState = reactive({
      dataLoaded: false,
      feeType: FeeSummaryTypes.NEW,
      stepName: RouteNames.ADD_COLLATERAL,
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
        return getRegistrationType.value?.registrationTypeAPI || null
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
      if (!isAuthenticated.value) {
        goToDash()
        return
      }

      // redirect if store doesn't contain all needed data (happens on page reload, etc.)
      if (!getRegistrationType.value || getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
        goToDash()
        return
      }

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
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
      getFooterButtonConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@use '@/assets/styles/theme' as *;
</style>
