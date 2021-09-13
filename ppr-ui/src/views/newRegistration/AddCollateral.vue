<template>
  <v-container class="view-container pa-0" fluid>
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
              <v-col class="pt-2 pb-6">
                Add the collateral for this {{ registrationTypeUI }} registration.
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="12">
                <collateral />
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
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { RouteNames, StatementTypes, APIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  ActionBindingIF, ErrorIF, LengthTrustIF, RegistrationTypeIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
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
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getRegistrationOther: string

  @Action resetNewRegistration: ActionBindingIF

  @Prop({ default: '#app' })
  private attachDialog: string

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private feeType = FeeSummaryTypes.NEW

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

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private get statementType (): string {
    return StatementTypes.FINANCING_STATEMENT
  }

  private get stepName (): string {
    return RouteNames.ADD_COLLATERAL
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
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
