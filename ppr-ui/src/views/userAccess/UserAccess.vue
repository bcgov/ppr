<template>
  <div v-if="dataLoaded" id="user-access">
    <v-container class="view-container px-15 py-0">
      <v-container class="pa-0 mt-11">
        <!-- Overlays and Dialogs -->
        <v-overlay v-model="submitting">
          <v-progress-circular color="primary" size="50" indeterminate />
        </v-overlay>

        <!-- Request Access Type Pre-Step -->
        <section v-if="isRouteName(RouteNames.QS_ACCESS_TYPE)" class="pa-0">
          <v-row no-gutters>
            <v-col sm="12" md="12" lg="9">
              <v-row no-gutters id="registration-header" class="soft-corners-top">
                <v-col cols="auto">
                  <h1>Request MHR Qualified Supplier Access</h1>
                </v-col>
              </v-row>
              <QsSelectAccess :showErrors="!getMhrSubProduct && validateQsSelect" />
            </v-col>
          </v-row>
        </section>

        <!-- User Access Content Flow -->
        <section v-else class="pa-0">
          <v-row no-gutters>
            <v-col sm="12" md="12" lg="9">
              <v-row no-gutters id="registration-header" class="soft-corners-top">
                <v-col cols="auto">
                  <h1>Manufactured Home Registry Qualified Supplier Application</h1>
                </v-col>
              </v-row>
              <Stepper
                class="mt-11"
                :stepConfig="getUserAccessSteps"
                :showStepErrors="validateQsComponents && validateQsApplication"
              />
              <!-- Component Steps -->
              <component
                v-for="step in getUserAccessSteps"
                v-show="isRouteName(step.to)"
                :is="step.component"
                :key="step.step"
                :validate="validateQsComponents"
                :validateReview="validateQsApplication"
              />
            </v-col>
          </v-row>
        </section>
      </v-container>
    </v-container>

    <!-- Footer Navigation -->
    <v-row no-gutters class="mt-20">
      <v-col cols="12">
        <ButtonFooter
          :navConfig="MhrUserAccessButtonFooterConfig"
          :currentStepName="$route.name"
          :disableNav="!getMhrSubProduct"
          :baseDialogOptions="incompleteApplicationDialog"
          @navigationDisabled="validateQsSelect = $event"
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
import { getFeatureFlag } from '@/utils'
import { RouteNames } from '@/enums'
import QsSelectAccess from '@/views/userAccess/QsSelectAccess.vue'
import { ButtonFooter, Stepper } from '@/components/common'
import BaseDialog from '@/components/dialogs/BaseDialog.vue'
import { MhrUserAccessButtonFooterConfig } from '@/resources/buttonFooterConfig'
import { useAuth, useNavigation, useUserAccess } from '@/composables'
import { ErrorIF } from '@/interfaces'
import { incompleteApplicationDialog } from '@/resources/dialogOptions'

export default defineComponent({
  name: 'UserAccess',
  emits: ['emitHaveData', 'error'],
  components: {
    Stepper,
    BaseDialog,
    ButtonFooter,
    QsSelectAccess
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
    const { getMhrSubProduct, getUserAccessSteps } = storeToRefs(useStore())
    const { isValid, submitQsApplication } = useUserAccess()

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      validateQsSelect: false,
      validateQsComponents: false,
      validateQsApplication: false
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value ||
          (!props.isJestRunning && !getFeatureFlag('mhr-user-access-enabled'))) {
        await goToDash()
        return
      }

      emit('emitHaveData', true)
      localState.dataLoaded = true
    })

    const emitError = (error: ErrorIF): void => {
      emit('error', error)
    }

    const submit = async (): Promise<void> => {
      localState.validateQsApplication = true
      await nextTick()

      if (isValid.value) {
        localState.submitting = true
        await submitQsApplication()
        localState.submitting = false
      }
    }

    watch(() => route.name, () => {
      if (isRouteName(RouteNames.QS_ACCESS_REVIEW_CONFIRM)) localState.validateQsComponents = true
    })

    return {
      submit,
      emitError,
      isRouteName,
      RouteNames,
      getMhrSubProduct,
      getUserAccessSteps,
      incompleteApplicationDialog,
      MhrUserAccessButtonFooterConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
