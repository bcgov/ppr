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
      setAttach="#confirm-mhr-search"
      :setOptions="options"
      :setDisplay="showCancelDialog"
      @proceed="handleDialogResp($event)"
    />
    <div v-if="dataLoaded && !dataLoadError" class="container pa-0" style="min-width: 960px;">
      <v-row no-gutters>
        <v-col cols="9">
          <h1>Review Selection(s)</h1>
          <div class="mt-6">
            <p class="ma-0">
              Review the selected manufactured home registration(s) before paying. Your search result will be available
              in your Searches list for up to 14 days. <b>Note : Search fees are charged per unique manufactured home
              registration number.</b>
            </p>
          </div>

          <v-card flat class="mt-6">
            <v-row no-gutters class="summary-header pa-2 rounded-top">
              <v-col cols="auto" class="pa-2">
                <v-icon color="darkBlue">mdi-home</v-icon>
                <label class="pl-3" :class="$style['sectionText']">
                  <strong>Selection Summary</strong>
                </label>
              </v-col>
            </v-row>
            <searched-result-mhr class="soft-corners px-6" :isReviewMode="true" />
          </v-card>

          <folio-number-summary
            @folioValid="setFolioValid($event)"
            :setShowErrors="showErrors"
            :setIsMhr="true"
            class="pt-15"
          />

          <!-- Staff Payment Section -->
          <section v-if="getIsStaffClientPayment && !isRoleStaffSbc" class="mt-10">
            <v-row no-gutters>
              <v-col class="generic-label">
                <h2>2. Staff Payment</h2>
              </v-col>
            </v-row>

            <v-card flat class="mt-6 pa-6" :class="showErrorAlert ? 'border-error-left' : ''">
              <staff-payment-component
                id="staff-payment-dialog"
                :staffPaymentData="staffPaymentData"
                :validate="validating||showErrors"
                :displaySideLabel="true"
                :displayPriorityCheckbox="true"
                :invalidSection="showErrorAlert"
                @update:staffPaymentData="onStaffPaymentDataUpdate($event)"
                @valid="staffPaymentValid = $event"
              />
              <v-row no-gutters>
                <v-spacer></v-spacer>
                <v-col cols="12" :sm="9">
                  <v-checkbox
                    class="mt-2"
                    id="certify-checkbox"
                    label="Make this a Certified search (add $25.00)"
                    @change="setSearchCertified($event)"
                  />
                </v-col>
              </v-row>
            </v-card>
          </section>

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
                :setAdditionalFees="combinedSearchFees"
                @back="goToSearchResult()"
                @cancel="showDialog()"
                @submit="submit()"
              />
            </affix>
          </aside>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
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
import { StaffPayment as StaffPaymentComponent } from '@bcrs-shared-components/staff-payment'
// local helpers/enums/interfaces/resources
import { RouteNames, UIMHRSearchTypeValues } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import {
  ActionBindingIF,
  ErrorIF,
  StateModelIF,
  DialogOptionsIF,
  ManufacturedHomeSearchResultIF, ManufacturedHomeSearchResponseIF
} from '@/interfaces'
import { notCompleteSearchDialog } from '@/resources/dialogOptions'
import { getFeatureFlag, submitSelectedMhr } from '@/utils'
import { SearchedResultMhr } from '@/components/tables'
import { AdditionalSearchFeeIF } from '@/composables/fees/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { uniqBy } from 'lodash'
/* eslint-enable no-unused-vars */

@Component({
  components: {
    BaseDialog,
    FolioNumberSummary,
    StickyContainer,
    SearchedResultMhr,
    StaffPaymentComponent
  }
})
export default class ConfirmMHRSearch extends Vue {
  @Getter getStateModel: StateModelIF
  @Getter isSearchCertified!: boolean
  @Getter isRoleStaffBcol: boolean
  @Getter isRoleStaffReg!: boolean
  @Getter isRoleStaffSbc!: boolean
  @Getter getIsStaffClientPayment!: boolean
  @Getter getStaffPayment!: StaffPaymentIF
  @Getter getManufacturedHomeSearchResults!: ManufacturedHomeSearchResponseIF
  @Getter getSelectedManufacturedHomes!: ManufacturedHomeSearchResultIF[]
  @Getter getFolioOrReferenceNumber!: string

  @Action setUnsavedChanges: ActionBindingIF
  @Action setStaffPayment!: ActionBindingIF
  @Action setSearchCertified!: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  private dataLoaded = false
  private dataLoadError = false
  private feeType = FeeSummaryTypes.MHSEARCH
  private options: DialogOptionsIF = notCompleteSearchDialog
  private showCancelDialog = false
  private showErrors = false
  private submitting = false
  private validFolio = true
  private staffPaymentValid = false
  private validating = false
  private paymentOption = StaffPaymentOptions.NONE

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get showErrorAlert (): boolean {
    return (!this.validFolio || !this.staffPaymentValid) && this.showErrors
  }

  private get stickyComponentErrMsg (): string {
    if (this.showErrorAlert) {
      return '< Please complete required information'
    }
    return ''
  }

  private get combinedSearchFees (): AdditionalSearchFeeIF {
    const searchQuantity = uniqBy(this.getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER)
      .filter(item => item.includeLienInfo === true)
      .length
    return searchQuantity > 0
      ? {
        feeType: FeeSummaryTypes.MHR_COMBINED_SEARCH,
        quantity: searchQuantity
      }
      : null
  }

  private get feeQuantity (): number {
    // Return selected quantity that is not a combination search
    return uniqBy(this.getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER)
      .filter(result => result.selected && !result.includeLienInfo)
      .length
  }

  private get staffPaymentData (): any {
    let pd = this.getStaffPayment
    if (!pd) {
      pd = {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      }
    }
    return pd
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

  private async submit (): Promise<void> {
    this.validating = true
    await Vue.nextTick()
    if (!this.validFolio || ((this.getIsStaffClientPayment && !this.isRoleStaffSbc) && !this.staffPaymentValid)) {
      this.showErrors = true
      document.getElementById('staff-payment-dialog').scrollIntoView({ behavior: 'smooth' })
      return
    }
    this.submitting = true
    let apiResponse
    if (this.isRoleStaffReg) {
      apiResponse = await submitSelectedMhr(
        this.getManufacturedHomeSearchResults.searchId,
        uniqBy(this.getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER),
        this.getFolioOrReferenceNumber,
        this.getStaffPayment,
        this.isSearchCertified
      )
    } else {
      apiResponse = await submitSelectedMhr(
        this.getManufacturedHomeSearchResults.searchId,
        uniqBy(this.getSelectedManufacturedHomes, UIMHRSearchTypeValues.MHRMHR_NUMBER),
        this.getFolioOrReferenceNumber
      )
    }
    this.submitting = false
    if (apiResponse === undefined || apiResponse !== 200) {
      // Expand Error Handling
      console.error('Api Error: ' + apiResponse)
    } else {
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

  /** Called when component's staff payment data has been updated. */
  private onStaffPaymentDataUpdate (val: StaffPaymentIF) {
    let staffPaymentData: StaffPaymentIF = {
      ...val
    }

    if (staffPaymentData.routingSlipNumber || staffPaymentData.bcolAccountNumber || staffPaymentData.datNumber) {
      this.validating = true
    } else {
      if (staffPaymentData.option !== this.paymentOption) {
        this.validating = false
        this.paymentOption = staffPaymentData.option
      }
    }

    // disable validation
    switch (staffPaymentData.option) {
      case StaffPaymentOptions.FAS:
        staffPaymentData = {
          option: StaffPaymentOptions.FAS,
          routingSlipNumber: staffPaymentData.routingSlipNumber,
          isPriority: staffPaymentData.isPriority,
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: ''
        }
        break

      case StaffPaymentOptions.BCOL:
        staffPaymentData = {
          option: StaffPaymentOptions.BCOL,
          bcolAccountNumber: staffPaymentData.bcolAccountNumber,
          datNumber: staffPaymentData.datNumber,
          folioNumber: staffPaymentData.folioNumber,
          isPriority: staffPaymentData.isPriority,
          routingSlipNumber: ''
        }
        break

      case StaffPaymentOptions.NO_FEE:
        staffPaymentData = {
          option: StaffPaymentOptions.NO_FEE,
          routingSlipNumber: '',
          isPriority: false,
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: ''
        }
        break

      case StaffPaymentOptions.NONE: // should never happen
        break
    }

    this.setStaffPayment(staffPaymentData)
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
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('mhr-ui-enabled'))) {
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
