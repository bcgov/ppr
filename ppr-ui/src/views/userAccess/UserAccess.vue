<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <!-- Overlays and Dialogs -->
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

    <!-- Request Access Type Pre-Step -->
    <div v-if="isRouteName(RouteNames.QS_ACCESS_TYPE)" class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="registration-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>Request MHR Qualified Supplier Access</h1>
              </v-col>
            </v-row>
            <QsSelectAccess :showErrors="!getMhrSubProduct && promptAccessSelect" />
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- User Access Content Flow -->
    <div v-else class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="registration-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>Manufactured Home Registry Qualified Supplier Application</h1>
              </v-col>
            </v-row>
            <Stepper
              class="mt-4"
              :stepConfig="getUserAccessSteps"
              :showStepErrorsFlag="false"
            />
            <!-- Component Steps -->
            <component
              v-for="step in getUserAccessSteps"
              v-show="isRouteName(step.to)"
              :is="step.component"
              :key="step.step"
            />
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- Footer Navigation -->
    <v-row no-gutters class="mt-20">
      <v-col cols="12">
        <ButtonFooter
          :navConfig="MhrUserAccessButtonFooterConfig"
          :currentStepName="$route.name"
          :disableNav="!getMhrSubProduct"
          @navigationDisabled="promptAccessSelect = $event"
          @error="emitError($event)"
          @submit="submit()"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, toRefs } from 'vue-demi'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { getFeatureFlag } from '@/utils'
import { RouteNames } from '@/enums'
import QsSelectAccess from '@/views/userAccess/QsSelectAccess.vue'
import { ButtonFooter, Stepper } from '@/components/common'
import BaseDialog from '@/components/dialogs/BaseDialog.vue'
import { MhrUserAccessButtonFooterConfig } from '@/resources/buttonFooterConfig'
import { useAuth, useNavigation } from '@/composables'
import { ErrorIF } from '@/interfaces'

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
    const { getMhrSubProduct, getUserAccessSteps } = storeToRefs(useStore())
    const { isRouteName, goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      promptAccessSelect: false
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

    const submit = (): void => {
      // Submit the filing, do stuff
    }

    return {
      submit,
      emitError,
      isRouteName,
      RouteNames,
      getMhrSubProduct,
      getUserAccessSteps,
      MhrUserAccessButtonFooterConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
