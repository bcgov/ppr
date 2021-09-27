<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters
                    id="registration-header"
                    class="length-trust-header pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>{{ registrationTypeUI }}</h1>
              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <v-row no-gutters class="pt-10">
              <v-col cols="auto" class="sub-header">
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
                <collateral :isSummary="false" :setRegistrationType="registrationType" />
              </v-col>
            </v-row>
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <sticky-container
              :setRightOffset="true"
              :setShowFeeSummary="true"
              :setFeeType="feeType"
              :setRegistrationLength="registrationLength"
              :setRegistrationType="registrationTypeUI"
            />
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row no-gutters class='pt-10'>
      <v-col cols="12">
        <button-footer :currentStatementType="statementType" :currentStepName="stepName"
                      :router="this.$router" @draft-save-error="saveDraftError"/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { APIRegistrationTypes, RegistrationFlowType, RouteNames, StatementTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ErrorIF, LengthTrustIF, RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { getFeatureFlag } from '@/utils'
// local components
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { Collateral } from '@/components/collateral'

@Component({
  components: {
    ButtonFooter,
    Collateral,
    Stepper,
    StickyContainer
  }
})
export default class AddCollateral extends Vue {
  @Getter getLengthTrust: LengthTrustIF
  @Getter getRegistrationFlowType: RegistrationFlowType
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getRegistrationOther: string

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private dataLoaded = false
  private feeType = FeeSummaryTypes.NEW
  private statementType = StatementTypes.FINANCING_STATEMENT
  private stepName = RouteNames.ADD_COLLATERAL

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get registrationLength (): RegistrationLengthI {
    return {
      lifeInfinite: this.getLengthTrust?.lifeInfinite || false,
      lifeYears: this.getLengthTrust?.lifeYears || 0
    }
  }

  private get registrationTypeUI (): string {
    if (this.getRegistrationType?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
      return this.getRegistrationOther || ''
    }
    return this.getRegistrationType?.registrationTypeUI || ''
  }

  private get registrationType (): APIRegistrationTypes {
    return this.getRegistrationType?.registrationTypeAPI || null
  }

  mounted () {
    this.onAppReady(this.appReady)
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
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
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

  @Watch('draftSaveError')
  private saveDraftError (val: ErrorIF): void {
    alert('Error saving draft. Replace when design complete.')
  }
}

</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
