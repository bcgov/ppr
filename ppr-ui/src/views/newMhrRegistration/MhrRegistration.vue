<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="registration-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>Manufactured Home Registration</h1>
              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <!-- Component Steps -->
            <component
              v-for="step in getSteps"
              v-show="isRouteName(step.to)"
              :is="step.component"
              :key="step.step"
            />
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setRegistrationType="registrationTypeUI"
                />
              </affix>
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row no-gutters class="pt-10">
      <v-col cols="12">
        <button-footer
          :currentStatementType="statementType"
          :currentStepName="$route.name"
          :router="$router"
          @error="emitError($event)"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import {
  APIRegistrationTypes, // eslint-disable-line no-unused-vars
  RegistrationFlowType, // eslint-disable-line no-unused-vars
  RouteNames, // eslint-disable-line no-unused-vars
  StatementTypes, UIRegistrationTypes // eslint-disable-line no-unused-vars
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ErrorIF, GetterIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, StepIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { getFeatureFlag } from '@/utils'
// local components
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { RegistrationLengthTrust, RegistrationRepairersLien } from '@/components/registration'
/* eslint-enable no-unused-vars */

@Component({
  components: {
    ButtonFooter,
    RegistrationLengthTrust,
    RegistrationRepairersLien,
    Stepper,
    StickyContainer
  }
})
export default class MhrRegistration extends Vue {
  @Getter getLengthTrust: LengthTrustIF
  @Getter getRegistrationFlowType: RegistrationFlowType
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getRegistrationOther: string
  @Getter getSteps!: Array<StepIF>

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private dataLoaded = false
  private feeType = null // FeeSummaryTypes.NEW
  private statementType = StatementTypes.FINANCING_STATEMENT
  private stepName = RouteNames.LENGTH_TRUST

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get registrationTypeUI (): string {
    if (this.getRegistrationType?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
      return this.getRegistrationOther || ''
    }
    return this.getRegistrationType?.registrationTypeUI || ''
  }

  /** Helper to check is the current route matches */
  private isRouteName (routeName: RouteNames): boolean {
    return (this.$route.name === routeName)
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  /** Emits error to app.vue for handling */
  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void { }

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    // do not proceed if app is not ready
    if (!val) return
    // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('mhr-ui-enabled'))) {
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }

    // redirect if store doesn't contain all needed data (happens on page reload, etc.)
    if (!this.getRegistrationType || this.getRegistrationFlowType !== RegistrationFlowType.NEW) {
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }

    // page is ready to view
    this.emitHaveData(true)
    this.dataLoaded = true
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.step-container {
  margin-top: 1rem;
  padding: 1.25rem;
}
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

.reg-default-btn {
  background-color: $gray3 !important;
}

.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
