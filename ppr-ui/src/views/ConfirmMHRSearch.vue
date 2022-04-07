<template>
  <v-container
    id="confirm-mhr-search"
    class="view-container pa-15 pt-14"
    fluid
    style="min-width: 960px;"
  >
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      setAttach="#confirm-discharge"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Review Search Result</h1>
          <div style="padding-top: 25px; max-width: 875px;">
            <p class="ma-0">
              Review the details of the manufactured home before paying. Your search result will download
              automatically after payment is received. Your search result will also be available in your searches
              list.
            </p>
          </div>
          
          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-15"
          />
          <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setErrMsg="stickyComponentErrMsg"
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Pay and Download Result'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                @back="goToReviewRegistration()"
                @cancel="showDialog()"
                @submit="submitDischarge()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local components
import {
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { SearchResultSummary } from '@/components/mhr'
import { BaseDialog } from '@/components/dialogs'
// local helpers/enums/interfaces/resources
import { RouteNames } from '@/enums' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Throttle } from '@/decorators'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF // eslint-disable-line no-unused-vars
 } from '@/interfaces'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag } from '@/utils'

@Component({
  components: {
    BaseDialog,
    FolioNumberSummary,
    SearchResultSummary,
    StickyContainer
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getStateModel: StateModelIF
  @Getter isRoleStaffBcol: boolean

  @Action setUnsavedChanges: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private dataLoaded = false
  private dataLoadError = false
  private feeType = FeeSummaryTypes.MHSEARCH
  private options: DialogOptionsIF = notCompleteDialog
  private showCancelDialog = false
  private showErrors = false
  private submitting = false
  private validConfirm = false // eslint-disable-line lines-between-class-members
  private validFolio = true
  
  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  
  private get stickyComponentErrMsg (): string {
    if ((!this.validConfirm || !this.validFolio) && this.showErrors) {
      return '< Please complete required information'
    }
    return ''
  }

  private async loadSearchResult (): Promise<void> {
    if (!this.registrationNumber || !this.getConfirmDebtorName) {
      if (!this.registrationNumber) {
        console.error('No registration number given to discharge. Redirecting to dashboard...')
      } else {
        console.error('No debtor name confirmed for discharge. Redirecting to dashboard...')
      }
      this.$router.push({
        name: RouteNames.DASHBOARD
      })
      return
    }
    this.financingStatementDate = new Date()
    const financingStatement = await getFinancingStatement(
      true,
      this.registrationNumber
    )
    
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private handleDialogResp (val: boolean): void {
    this.showCancelDialog = false
    if (!val) {
      this.setRegistrationNumber(null)
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private goToReviewRegistration (): void {
    this.$router.push({
      name: RouteNames.REVIEW_DISCHARGE,
      query: { 'reg-num': this.registrationNumber }
    })
    this.emitHaveData(false)
  }

  private setFolioValid (valid: boolean): void {
    this.validFolio = valid
  }

  private showDialog (): void {
    this.showCancelDialog = true
  }

  @Throttle(2000)
  private async submitDischarge (): Promise<void> {
    if ((!this.validConfirm) || (!this.validFolio) || (!this.validCertify)) {
      this.showErrors = true
      return
    }

    const stateModel: StateModelIF = this.getStateModel
    this.submitting = true
    const apiResponse: DischargeRegistrationIF = await saveDischarge(stateModel)
    this.submitting = false
    if (apiResponse === undefined || apiResponse?.error !== undefined) {
      this.emitError(apiResponse?.error)
    } else {
      // set new added reg
      const newItem: RegTableNewItemI = {
        addedReg: apiResponse.dischargeRegistrationNumber,
        addedRegParent: apiResponse.baseRegistrationNumber,
        addedRegSummary: null,
        prevDraft: ''
      }
      this.setRegTableNewItem(newItem)
      // On success return to dashboard
      this.goToDashboard()
    }
  }

  private goToDashboard (): void {
    this.$router.push({
      name: RouteNames.DASHBOARD
    })
    this.emitHaveData(false)
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void {}

  /** Emits error to app.vue for handling */
  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

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

    // get registration data from api and load into store
    this.submitting = true
    await this.loadRegistration()
    this.submitting = false

    // page is ready to view
    this.emitHaveData(true)
    this.dataLoaded = true
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
