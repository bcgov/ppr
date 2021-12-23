<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row
              no-gutters
              id="registration-header"
              class="length-trust-header pt-3 pb-3 soft-corners-top"
            >
              <v-col cols="auto">
                <h1>{{ registrationTypeUI }}</h1>
              </v-col>
            </v-row>
            <stepper class="mt-4" />
            <v-row no-gutters class="pt-10">
              <v-col cols="auto" class="sub-header">
                {{ registrationTitle }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6 sub-header-info">
                {{ registrationLengthMessage }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <registration-length-trust v-if="registrationType !== registrationTypeRL" />
                <registration-repairers-lien v-else />
              </v-col>
            </v-row>
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setRegistrationLength="registrationLength"
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
          :currentStepName="stepName"
          :router="this.$router"
          @draft-save-error="saveDraftError"
        />
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
import {
  APIRegistrationTypes, // eslint-disable-line no-unused-vars
  RegistrationFlowType, // eslint-disable-line no-unused-vars
  RouteNames, // eslint-disable-line no-unused-vars
  StatementTypes // eslint-disable-line no-unused-vars
} from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ErrorIF, // eslint-disable-line no-unused-vars
  LengthTrustIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { getFeatureFlag } from '@/utils'
// local components
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { RegistrationLengthTrust, RegistrationRepairersLien } from '@/components/registration'

@Component({
  components: {
    ButtonFooter,
    RegistrationLengthTrust,
    RegistrationRepairersLien,
    Stepper,
    StickyContainer
  }
})
export default class LengthTrust extends Vue {
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
  private stepName = RouteNames.LENGTH_TRUST

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

  private get registrationType (): string {
    return this.getRegistrationType?.registrationTypeAPI || ''
  }

  private get registrationTypeRL (): string {
    return APIRegistrationTypes.REPAIRERS_LIEN
  }

  private get registrationTitle (): string {
    switch (this.registrationType) {
      case APIRegistrationTypes.SECURITY_AGREEMENT:
        return 'Registration Length and Trust Indenture'
      case APIRegistrationTypes.REPAIRERS_LIEN:
        return 'Terms of Repairers Lien'
      default:
        return 'Registration Length'
    }
  }

  private get registrationLengthMessage (): string {
    switch (this.registrationType) {
      case APIRegistrationTypes.REPAIRERS_LIEN:
        return 'Enter the amount of the Lien and the date the vehicle was (or will be) surrendered. ' +
                'Please note that this cannot be more than 21 days in the past. The length of the Lien is ' +
                'automatically set to 180 days.'

      case APIRegistrationTypes.MARRIAGE_MH:
        return (
          'The registration length for this registration is automatically set to infinite. ' +
          'There is a $10.00 fee for this registration.'
        )
      case APIRegistrationTypes.LAND_TAX_LIEN:
      case APIRegistrationTypes.MANUFACTURED_HOME_LIEN:
      case APIRegistrationTypes.INSURANCE_PREMIUM_TAX:
      case APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX:
      case APIRegistrationTypes.FOREST:
      case APIRegistrationTypes.LOGGING_TAX:
      case APIRegistrationTypes.CARBON_TAX:
      case APIRegistrationTypes.RURAL_PROPERTY_TAX:
      case APIRegistrationTypes.PROVINCIAL_SALES_TAX:
      case APIRegistrationTypes.INCOME_TAX:
      case APIRegistrationTypes.MOTOR_FUEL_TAX:
      case APIRegistrationTypes.EXCISE_TAX:
      case APIRegistrationTypes.LIEN_UNPAID_WAGES:
      case APIRegistrationTypes.PROCEEDS_CRIME_NOTICE:
      case APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE:
      case APIRegistrationTypes.MANUFACTURED_HOME_NOTICE:
      case APIRegistrationTypes.MAINTENANCE_LIEN:
      case APIRegistrationTypes.OTHER:
      case APIRegistrationTypes.SCHOOL_ACT:
      case APIRegistrationTypes.PROPERTY_TRANSFER_TAX:
      case APIRegistrationTypes.MINERAL_LAND_TAX:
        return (
          'The registration length for this registration is automatically set to infinite. ' +
          'There is no fee for this registration.'
        )
      default:
        return (
          'Enter the length of time you want the ' +
          this.getRegistrationType?.registrationTypeUI +
          ' registration to be in effect. You can renew the registration in the future (for a fee).'
        )
    }
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
