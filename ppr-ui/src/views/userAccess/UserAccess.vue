<template>
  <v-container
    v-if="dataLoaded"
    id="user-access"
    class="footer-view-container px-0"
  >
    <BaseDialog
      :setOptions="confirmQsProductChangeDialog"
      :setDisplay="showChangeProductDialog"
      @proceed="handleDialogResp"
    />

    <!-- Overlays and Dialogs -->
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

    <!-- Request Access Type Pre-Step -->
    <section
      v-if="isRouteName(RouteNames.QS_ACCESS_TYPE)"
      class="pa-0"
    >
      <v-row noGutters>
        <v-col
          sm="12"
          md="12"
          lg="9"
        >
          <v-row
            id="registration-header"
            noGutters
            class="soft-corners-top"
          >
            <v-col cols="auto">
              <h1>Request MHR Qualified Supplier Access</h1>
            </v-col>
          </v-row>
          <QsSelectAccess :showErrors="!getMhrSubProduct && validateQsSelect" />
        </v-col>
      </v-row>
    </section>

    <!-- User Access Content Flow -->
    <section
      v-else
      class="pa-0"
    >
      <v-row noGutters>
        <v-col
          sm="12"
          md="12"
          lg="9"
        >
          <v-row
            id="registration-header"
            noGutters
            class="soft-corners-top"
          >
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
            :is="step.component"
            v-for="step in getUserAccessSteps"
            v-show="isRouteName(step.to)"
            :key="step.step"
            :validate="validateQsComponents"
            :validateReview="validateQsApplication"
          />
        </v-col>
      </v-row>
    </section>

    <!-- Footer Navigation -->
    <ButtonFooter
      :navConfig="MhrUserAccessButtonFooterConfig"
      :currentStepName="$route.name"
      :disableNav="!getMhrSubProduct"
      :baseDialogOptions="incompleteApplicationDialog"
      @navigation-disabled="validateQsSelect = $event"
      @error="emitError($event)"
      @submit="submit()"
    />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, nextTick, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { getFeatureFlag, scrollToFirstVisibleErrorComponent } from '@/utils'
import { RouteNames } from '@/enums'
import QsSelectAccess from '@/views/userAccess/QsSelectAccess.vue'
import { ButtonFooter, Stepper } from '@/components/common'
import BaseDialog from '@/components/dialogs/BaseDialog.vue'
import { MhrUserAccessButtonFooterConfig } from '@/resources/buttonFooterConfig'
import { useAuth, useNavigation, useUserAccess } from '@/composables'
import { ErrorIF } from '@/interfaces'
import { confirmQsProductChangeDialog, incompleteApplicationDialog } from '@/resources/dialogOptions'

export default defineComponent({
  name: 'UserAccess',
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
    }
  },
  emits: ['emitHaveData', 'error'],
  setup (props, { emit }) {
    const { isAuthenticated } = useAuth()
    const { isRouteName, goToDash, route } = useNavigation()
    const { setMhrSubProduct } = useStore()
    const { getMhrSubProduct, getUserAccessSteps } = storeToRefs(useStore())
    const {
      hasQsApplicationData,
      isValid,
      initUserAccess,
      setQsInformationModel,
      submitQsApplication
    } = useUserAccess()

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      validateQsSelect: false,
      validateQsComponents: false,
      validateQsApplication: false,
      showChangeProductDialog: false,
      previousSelectedProduct: ''
    })

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value || !getFeatureFlag('mhr-user-access-enabled')) {
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
      await scrollToFirstVisibleErrorComponent()

      if (isValid.value) {
        localState.submitting = true
        await submitQsApplication()
        localState.submitting = false
      }
    }

    const handleDialogResp = (val: boolean): void => {
      if (!val) {
        // Restore product to baseline
        setMhrSubProduct(localState.previousSelectedProduct)
        localState.showChangeProductDialog = false
        return
      }

      // Change product type and set new baseline
      localState.previousSelectedProduct = getMhrSubProduct.value
      initUserAccess(getMhrSubProduct.value)
      localState.showChangeProductDialog = false
    }

    watch(() => getMhrSubProduct.value, (val) => {
      setQsInformationModel(val)

      if (localState.previousSelectedProduct === val) return
      // Set baseline for initial product selection
      if (!localState.previousSelectedProduct) localState.previousSelectedProduct = val
      // Show Change Product Dialog when application has data
      localState.showChangeProductDialog = hasQsApplicationData.value
    })

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
      hasQsApplicationData,
      handleDialogResp,
      confirmQsProductChangeDialog,
      incompleteApplicationDialog,
      MhrUserAccessButtonFooterConfig,
      ...toRefs(localState)
    }
  }
})
</script>
