<template>
  <v-container
    v-if="dataLoaded"
    class="view-container pa-0"
    fluid
  >
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row
              id="registration-header"
              no-gutters
              class="length-trust-header pt-3 pb-3 soft-corners-top"
            >
              <v-col cols="auto">
                <h1>{{ registrationTypeUI }}</h1>
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
                class="sub-header"
              >
                Add Secured Parties and Debtors
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6 sub-header-info">
                Add the people and businesses who have an interest in this registration.
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="auto">
                <parties />
              </v-col>
            </v-row>
          </v-col>
          <v-col
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <sticky-container
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
    <v-row
      no-gutters
      class="pt-10"
    >
      <v-col cols="12">
        <ButtonFooter
          :nav-config="getFooterButtonConfig"
          :current-step-name="stepName"
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
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { Parties } from '@/components/parties'
import { getFeatureFlag } from '@/utils'
import { ErrorIF } from '@/interfaces' // eslint-disable-line
import { RegistrationLengthI } from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation } from '@/composables' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'AddParties',
  components: {
    ButtonFooter,
    Stepper,
    Parties,
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
      stepName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
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

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
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
      getFooterButtonConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
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
</style>
