<template>
  <v-container
    class="pt-14 px-0"
    fluid
    style="min-width: 960px;"
  >
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
    <BaseDialog
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
          <h1>Renewal</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              This is the current registration information as of
              <b>{{ asOfDateTime }}.</b> Review this information to ensure it is
              correct
              <span v-if="registrationType !== registrationTypeRL">
                and select the length of time you would like to renew this
                registration for</span>.<br>
            </p>
            <p class="ma-0 pt-5">
              To view the full history of this registration including
              descriptions of any previous amendments or court orders, you will
              need to conduct a separate search.
            </p>
          </div>
          <registration-length-trust
            v-if="registrationType !== registrationTypeRL"
            :set-show-invalid="showInvalid"
            class="mt-15"
            :is-renewal="true"
            @length-trust-valid="registrationValid = $event"
          />
          <registration-repairers-lien
            v-else
            class="mt-15"
            :is-renewal="true"
          />
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
          <CourtOrder
            v-if="registrationType === registrationTypeRL"
            :set-show-errors="showInvalid"
            :set-require-court-order="true"
            class="mt-15"
            @set-court-order-valid="setValid($event)"
          />
        </v-col>
        <v-col
          class="pl-6"
          cols="3"
        >
          <aside>
            <StickyContainer
              :set-right-offset="true"
              :set-show-buttons="true"
              :set-show-fee-summary="true"
              :set-fee-type="feeType"
              :set-registration-length="registrationLength"
              :set-registration-type="registrationTypeUI"
              :set-cancel-btn="'Cancel'"
              :set-submit-btn="'Review and Complete'"
              :set-err-msg="errMsg"
              @cancel="showCancelDialog = true"
              @submit="confirmRenewal()"
            />
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '../../src/store/store'
import { StickyContainer, CourtOrder } from '../../src/components/common'
import { BaseDialog } from '../../src/components/dialogs'
import { RegistrationLengthTrust, RegistrationRepairersLien } from '../../src/components/registration'
import { Collateral } from '../../src/components/collateral'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '../../src/components/parties/summaries'
import { notCompleteDialog } from '../../src/resources/dialogOptions'
import { FeeSummaryTypes } from '../../src/composables/fees/enums'
import { getFeatureFlag, getFinancingStatement, pacificDate } from '../../src/utils'
import type {
  UIRegistrationTypes
} from '../../src/enums';
import {
  APIRegistrationTypes,
  RouteNames,
  RegistrationFlowType
} from '../../src/enums'
import type {
  ErrorIF,
  DialogOptionsIF
} from '../../src/interfaces'
import type { RegistrationLengthI } from '../../src/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation, usePprRegistration } from '../../src/composables'

export default defineComponent({
  name: 'RenewRegistrations',
  components: {
    BaseDialog,
    RegistrationLengthTrust,
    RegistrationRepairersLien,
    Collateral,
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary,
    CourtOrder,
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
    const route = useRoute()
    const { goToDash, goToRoute } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { initPprUpdateFilling } = usePprRegistration()

    const {
      // Getters
      getLengthTrust,
      getRegistrationType,
      getConfirmDebtorName,
      getRegistrationNumber,
      getRegistrationFlowType
    } = storeToRefs(useStore())

    const localState = reactive({
      dataLoaded: false,
      dataLoadError: false,
      financingStatementDate: null as Date,
      feeType: FeeSummaryTypes.RENEW,
      fromConfirmation: false,
      loading: false,
      registrationValid: false,
      options: notCompleteDialog as DialogOptionsIF,
      showCancelDialog: false,
      showInvalid: false,
      errMsg: '',
      asOfDateTime: computed((): string => {
        // return formatted date
        if (localState.financingStatementDate) {
          return `${pacificDate(localState.financingStatementDate)}`
        }
        return `${pacificDate(new Date())}`
      }),
      registrationLength: computed((): RegistrationLengthI => {
        return {
          lifeInfinite: getLengthTrust.value?.lifeInfinite || false,
          lifeYears: getLengthTrust.value?.lifeYears || 0
        }
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || null
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || ''
      }),
      registrationNumber: computed((): string => {
        let regNum = route.query['reg-num'] as string
        if (regNum && regNum.endsWith('-confirm')) {
          localState.fromConfirmation = true
          regNum = regNum.replace('-confirm', '')
        }
        return regNum || ''
      }),
      registrationTypeRL: computed(() => {
        return APIRegistrationTypes.REPAIRERS_LIEN
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
      if (
        !getRegistrationNumber.value ||
        getRegistrationFlowType.value !== RegistrationFlowType.RENEWAL
      ) {
        if (!localState.registrationNumber || !getConfirmDebtorName) {
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
          initPprUpdateFilling(financingStatement, RegistrationFlowType.RENEWAL)
        }
      }
    }

    const setValid = (isValid): void => {
      localState.registrationValid = isValid
      if (isValid) {
        localState.errMsg = ''
      }
    }

    const confirmRenewal = (): void => {
      localState.errMsg = ''
      if (localState.registrationValid) {
        goToRoute(RouteNames.CONFIRM_RENEWAL, { 'reg-num': localState.registrationNumber })
      } else {
        localState.errMsg = '< You have unfinished changes'
        localState.showInvalid = true
        scrollToInvalid()
      }
    }

    const scrollToInvalid = async (): Promise<void> => {
      if (!localState.registrationValid) {
        const component = document.getElementById('court-order')
        if (component) {
          await component.scrollIntoView({ behavior: 'smooth' })
        }
      }
    }

    /** Called when App is ready and this component can load its data. */
    const onAppReady = async (val: boolean): Promise<void> => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value || !getFeatureFlag('ppr-ui-enabled')) {
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
      setValid,
      confirmRenewal,
      handleDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '../../src/assets/styles/theme';
</style>
