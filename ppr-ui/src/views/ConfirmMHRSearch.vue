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
          <div class="mt-6">
            <p class="ma-0">
              Review the details of the manufactured home before paying. Your search result will be available in your
              Searches list.
            </p>
          </div>

          <v-card flat class="mt-6">
            <v-row no-gutters class="summary-header pa-2 rounded-top">
              <v-col cols="auto" class="pa-2">
                <v-icon color="darkBlue">mdi-home</v-icon>
                <label class="pl-3" :class="$style['sectionText']">
                  <strong>Search Results Summary</strong>
                </label>
              </v-col>
            </v-row>
            <searched-result-mhr class="soft-corners px-6" :isReviewMode="true" />
          </v-card>

          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            class="pt-15"
          />
        </v-col>
        <v-col class="pl-6" cols="3">
          <aside>
            <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
              <sticky-container
                :setErrMsg="stickyComponentErrMsg"
                :setRightOffset="true"
                :setShowButtons="true"
                :setShowFeeSummary="true"
                :setFeeType="feeType"
                :setFeeQuantity="feeQuantity"
                :setBackBtn="'Back'"
                :setCancelBtn="'Cancel'"
                :setSubmitBtn="'Pay and Download Result'"
                :setDisableSubmitBtn="isRoleStaffBcol"
                :setAdditionalFees="combinedSearchFees"
                @back="goToSearchResult()"
                @cancel="showDialog()"
                @submit="submitSearch()"
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
import { BaseDialog } from '@/components/dialogs'
// local helpers/enums/interfaces/resources
import { RouteNames } from '@/enums' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Throttle } from '@/decorators'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, ManufacturedHomeSearchResultIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import { notCompleteDialog } from '@/resources/dialogOptions'
import { getFeatureFlag } from '@/utils'
import { SearchedResultMhr } from '@/components/tables'
import { AdditionalSearchFeeIF } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars

@Component({
  components: {
    BaseDialog,
    FolioNumberSummary,
    StickyContainer,
    SearchedResultMhr
  }
})
export default class ConfirmDischarge extends Vue {
  @Getter getStateModel: StateModelIF
  @Getter isRoleStaffBcol: boolean
  @Getter getSelectedManufacturedHomes!: ManufacturedHomeSearchResultIF[]

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

  private get combinedSearchFees (): AdditionalSearchFeeIF {
    const searchQuantity = this.getSelectedManufacturedHomes?.filter(item => item.lienSelected === true).length
    return searchQuantity > 0
      ? {
        feeType: FeeSummaryTypes.MHR_COMBINED_SEARCH,
        quantity: searchQuantity
      }
      : null
  }

  private get feeQuantity (): number {
    return this.getSelectedManufacturedHomes.length
  }

  private async loadSearchResult (): Promise<void> {
  }

  mounted () {
    this.onAppReady(this.appReady)
  }

  private handleDialogResp (val: boolean): void {
    this.showCancelDialog = false
    if (!val) {
      this.$router.push({ name: RouteNames.DASHBOARD })
    }
  }

  private goToSearchResult (): void {
    this.$router.push({
      name: RouteNames.MHRSEARCH
    })
  }

  private setFolioValid (valid: boolean): void {
    this.validFolio = valid
  }

  private showDialog (): void {
    this.showCancelDialog = true
  }

  @Throttle(2000)
  private async submitSearch (): Promise<void> {
    if (!this.validFolio) {
      this.showErrors = true
      return
    }
    this.submitting = true
    // const apiResponse: DischargeRegistrationIF = await saveDischarge(stateModel)
    this.submitting = false
    // if (apiResponse === undefined || apiResponse?.error !== undefined) {
    //  this.emitError(apiResponse?.error)
    // } else {
    // On success return to dashboard
    this.goToDashboard()
    // }
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
