<template>
  <v-container
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="loading">
      <v-progress-circular
        color="primary"
        size="50"
        indeterminate
      />
    </v-overlay>
    <base-dialog
      :set-options="options"
      :set-display="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div
      v-if="dataLoaded && !dataLoadError"
      class="container pa-0"
      style="min-width: 960px;"
    >
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Total Discharge</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              This is the current information for this registration as of
              <b>{{ asOfDateTime }}.</b><br>
              If additional amendments including court orders are still required, ensure they are completed
              prior to performing this Total Discharge.
            </p>
            <p class="ma-0 pt-5">
              To view the full history of this registration including descriptions of any
              previous amendments or court orders, you will need to conduct a separate search.
            </p>
          </div>
          <caution-box
            class="mt-9"
            :set-msg="cautionTxt"
            :set-important-word="'Note'"
          />
          <registration-length-trust-summary class="mt-15" />
          <div class="summary-header mt-15 pa-4 rounded-top">
            <v-icon color="darkBlue">
              mdi-account-multiple-plus
            </v-icon>
            <label class="pl-3">
              <strong>Registering Party, Secured Parties, and Debtors</strong>
            </label>
          </div>
          <h3 class="pt-6">
            Original Registering Party
          </h3>
          <registering-party-summary
            class="pt-4"
            :set-enable-no-data-action="false"
          />
          <h3 class="pt-6">
            Secured Parties
          </h3>
          <secured-party-summary
            class="pt-4"
            :set-enable-no-data-action="false"
          />
          <h3 class="pt-6">
            Debtors
          </h3>
          <debtor-summary
            class="pt-4"
            :set-enable-no-data-action="false"
          />
          <collateral
            class="mt-15"
            :is-summary="true"
          />
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <affix
              relative-element-selector=".col-9"
              :offset="{ top: 90, bottom: -100 }"
            >
              <sticky-container
                :set-right-offset="true"
                :set-show-buttons="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-registration-type="registrationTypeUI"
                :set-cancel-btn="'Cancel'"
                :set-submit-btn="'Confirm and Complete'"
                @cancel="showCancelDialog = true"
                @submit="confirmDischarge()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { CautionBox, StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { DebtorSummary, RegisteringPartySummary, SecuredPartySummary } from '@/components/parties/summaries'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, getFinancingStatement, pacificDate } from '@/utils'
import {
  APIRegistrationTypes,
  RouteNames,
  RegistrationFlowType,
  UIRegistrationTypes
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { ErrorIF, DialogOptionsIF } from '@/interfaces'
import { useAuth, useNavigation, usePprRegistration } from '@/composables'

export default defineComponent({
  name: 'DischargeRegistration',
  components: {
    BaseDialog,
    CautionBox,
    RegistrationLengthTrustSummary,
    Collateral,
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary,
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
    const route = useRoute()
    const router = useRouter()
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { initPprUpdateFilling } = usePprRegistration()
    const {
      // Getters
      getRegistrationType,
      getConfirmDebtorName
    } = storeToRefs(useStore())

    const localState = reactive({
      cautionTxt: 'The Registry will provide the verification statement to all Secured Parties named in this ' +
      'registration.',
      dataLoaded: false,
      dataLoadError: false,
      feeType: FeeSummaryTypes.DISCHARGE,
      financingStatementDate: null as Date,
      fromConfirmation: false,
      loading: false,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      asOfDateTime: computed((): string => {
        // return formatted date
        if (localState.financingStatementDate) {
          return `${pacificDate(localState.financingStatementDate)}`
        }
        return ''
      }),
      registrationNumber: computed((): string => {
        let regNum = route.query['reg-num'] as string
        if (regNum && regNum.endsWith('-confirm')) {
          localState.fromConfirmation = true
          regNum = regNum.replace('-confirm', '')
        }
        return regNum || ''
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || null
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
    })

    const handleDialogResp = (val: boolean): void => {
      localState.showCancelDialog = false
      if (!val) {
        goToDash()
      }
    }

    const loadRegistration = async (): Promise<void> => {
      if (!localState.registrationNumber || !getConfirmDebtorName.value) {
        if (!localState.registrationNumber) {
          console.error('No registration number given to discharge. Redirecting to dashboard...')
        } else {
          console.error('No debtor name confirmed for discharge. Redirecting to dashboard...')
        }
        goToDash()
        return
      }

      // Conditionally load: could be coming back from confirm.
      if (localState.fromConfirmation) {
        return
      }

      localState.financingStatementDate = new Date()
      const financingStatement = await getFinancingStatement(true, localState.registrationNumber)
      if (financingStatement.error) {
        localState.dataLoadError = true
        emitError(financingStatement.error)
      } else {
        initPprUpdateFilling(financingStatement, RegistrationFlowType.DISCHARGE)
      }
    }

    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || (!props.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
        goToDash()
        return
      }

      // get registration data from api and load into store
      localState.loading = true
      await loadRegistration()
      localState.loading = false

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    const confirmDischarge = (): void => {
      router.push({
        name: RouteNames.CONFIRM_DISCHARGE,
        query: { 'reg-num': localState.registrationNumber }
      })
    }

    /** Called when App is ready and this component can load its data. */
    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    return {
      confirmDischarge,
      handleDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
