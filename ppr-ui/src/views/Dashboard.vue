<template>
  <v-container id="dashboard" class="view-container px-15 py-10 ma-0" fluid>
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      id="myRegAddDialog"
      :setDisplay="myRegAddDialogDisplay"
      :setOptions="myRegAddDialog"
      @proceed="myRegAddDialogProceed($event)"
    />
    <base-dialog
      id="myRegErrDialog"
      :setDisplay="myRegErrDialogDisplay"
      :setOptions="myRegErrDialog"
      @proceed="myRegErrDialogProceed($event)"
    />
    <base-dialog
      id="myRegDeleteDialog"
      :setDisplay="myRegDeleteDialogDisplay"
      :setOptions="myRegDeleteDialog"
      @proceed="myRegDeleteDialogProceed($event)"
    />
    <base-dialog
      id="payErrorDialogDash"
      :setDisplay="payErrorDisplay"
      :setOptions="payErrorOptions"
      @proceed="payErrorDisplay=false"
    />
    <registration-confirmation
      attach=""
      :options="myRegActionDialog"
      :display="myRegActionDialogDisplay"
      :registrationNumber="myRegActionRegNum"
      @proceed="myRegActionDialogHandler($event)"
    />
    <base-snackbar :setMessage="snackbarMsg" :toggleSnackbar="toggleSnackbar" />
    <div class="container pa-0">
      <v-row no-gutters>
        <v-col>
          <v-row no-gutters
                  id="search-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b>Personal Property Search</b>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-bar class="soft-corners-bottom"
                        @debtor-name="setSearchDebtorName"
                        @searched-type="setSearchedType"
                        @searched-value="setSearchedValue"
                        @search-data="setSearchResults"
                        @toggleStaffPaymentDialog="staffPaymentDialogDisplay = true"
                        @search-error="searchError($event)"/>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class='pt-12'>
        <v-col>
          <v-row no-gutters
                  id="search-history-header"
                  :class="[$style['dashboard-title'], 'pl-6', 'pt-3', 'pb-3', 'soft-corners-top']">
            <v-col cols="auto">
              <b>Searches</b> ({{ searchHistoryLength }})
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-history class="soft-corners-bottom" @retry="retrieveSearchHistory" @error="historyError"/>
          </v-row>
        </v-col>
      </v-row>
      <v-row class="pt-15" align="baseline" no-gutters>
        <v-col cols="auto">
          <registration-bar
            class="soft-corners-bottom"
            @selected-registration-type="startNewRegistration($event)"
          />
        </v-col>
        <v-col class="pl-3">
          <v-row justify="end" no-gutters>
            <v-col cols="auto" style="padding-top: 23px;">
              <v-tooltip
                class="pa-2"
                content-class="top-tooltip"
                nudge-right="2"
                top
                transition="fade-transition"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-icon color="primary" v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
                </template>
                <div class="pt-2 pb-2">
                  {{ tooltipTxtRegSrch }}
                </div>
              </v-tooltip>
              <label :class="[$style['copy-normal'], 'pl-1']">
                Retrieve an existing registration to add to your table:
              </label>
            </v-col>
            <v-col class="pl-3 pt-3" cols="auto">
              <v-text-field
                id="my-reg-add"
                :class="[
                  $style['text-input-style-above'],
                  'column-selection',
                  'ma-0',
                  'soft-corners-top'
                ]"
                append-icon="mdi-magnify"
                autocomplete="chrome-off"
                dense
                :error-messages="myRegAddInvalid ? 'error' : ''"
                hide-details
                label="Registration Number"
                :name="Math.random()"
                persistent-hint
                single-line
                style="width:270px"
                v-model="myRegAdd"
                @click:append="findRegistration(myRegAdd)"
                @keypress.enter="findRegistration(myRegAdd)"
              />
              <p v-if="myRegAddInvalid" :class="[$style['validation-msg'], 'mx-3', 'my-1']">
                Registration numbers contain 7 characters
              </p>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="pt-7" style="margin-top: 2px; margin-bottom: 80px;">
        <v-col>
          <v-row
            id="registration-header"
            :class="[$style['dashboard-title'], 'px-6', 'py-3', 'soft-corners-top']"
            align="center"
            no-gutters
          >
            <v-col cols="auto">
              <b>Registrations</b> ({{ myRegTotalBaseRegLength }})
            </v-col>
            <v-col>
              <v-row justify="end" no-gutters>
                <!-- commented out until groomed / design verifies it is needed -->
                <!-- <v-col class="py-1" cols="auto">
                  <v-text-field
                    id="my-reg-table-filter"
                    :class="[
                      $style['text-input-style-above'],
                      'column-selection',
                      'ma-0',
                      'soft-corners-top'
                    ]"
                    append-icon="mdi-filter-outline"
                    autocomplete="new-password"
                    dense
                    hide-details
                    label="Filter by Keyword"
                    :name="Math.random()"
                    single-line
                    style="width:270px"
                    v-model="myRegFilter"
                  />
                </v-col> -->
                <v-col class="pl-4 py-1" cols="auto">
                  <v-select
                    id="column-selection"
                    :class="[
                      $style['text-input-style-above'],
                      'column-selection',
                      'ma-0',
                      'soft-corners-top'
                    ]"
                    attach
                    autocomplete="off"
                    dense
                    hide-details="true"
                    :items="myRegHeadersSelectable"
                    item-text="text"
                    :menu-props="{
                      bottom: true,
                      minWidth: '240px',
                      maxHeight: 'none',
                      offsetY: true
                    }"
                    multiple
                    placeholder="Columns to Show"
                    return-object
                    style="width: 240px;"
                    v-model="myRegHeadersSelected"
                  >
                    <template v-slot:selection="{ index }">
                      <span v-if="index === 0">Columns to Show</span>
                    </template>
                  </v-select>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row no-gutters class="white">
            <v-col cols="12">
              <registration-table
                :setHeaders="myRegHeaders"
                :setLoading="myRegDataLoading"
                :setRegistrationHistory="myRegistrations"
                :setSearch="myRegFilter"
                :setSort="myRegSortOptions"
                @action="myRegActionHandler($event)"
                @error="emitError($event)"
                @getNext="myRegGetNext()"
                @sort="myRegSort($event)"
              />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
// external
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
import { StatusCodes } from 'http-status-codes'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import { ErrorCodes, RouteNames, SettingOptions, TableActions } from '@/enums' // eslint-disable-line no-unused-vars
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  BaseHeaderIF, // eslint-disable-line no-unused-vars
  BreadcrumbIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  DraftResultIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  RegistrationSortIF, // eslint-disable-line no-unused-vars
  RegistrationSummaryIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, // eslint-disable-line no-unused-vars
  SearchResponseIF, // eslint-disable-line no-unused-vars
  StateModelIF, // eslint-disable-line no-unused-vars
  UserSettingsIF // eslint-disable-line no-unused-vars
} from '@/interfaces'
import {
  registrationTableHeaders,
  AllRegistrationTypes,
  tombstoneBreadcrumbDashboard
} from '@/resources'
import {
  amendConfirmationDialog,
  dischargeConfirmationDialog,
  paymentErrorSearch,
  registrationAddErrorDialog,
  registrationAlreadyAddedDialog,
  registrationFoundDialog,
  registrationNotFoundDialog,
  registrationRestrictedDialog,
  registrationOpenDraftErrorDialog,
  renewConfirmationDialog,
  searchPdfError,
  searchResultsError,
  tableDeleteDialog,
  tableRemoveDialog
} from '@/resources/dialogOptions'
import {
  addRegistrationSummary,
  convertDate,
  deleteDraft,
  deleteRegistrationSummary,
  draftHistory,
  getFeatureFlag,
  getRegistrationSummary,
  registrationHistory,
  searchHistory,
  setupFinancingStatementDraft,
  updateUserSettings
} from '@/utils'
// local components
import { BaseSnackbar } from '@/components/common'
import { BaseDialog, RegistrationConfirmation } from '@/components/dialogs'
import { Tombstone } from '@/components/tombstone'
import { SearchBar } from '@/components/search'
import { SearchHistory, RegistrationTable } from '@/components/tables'
import { RegistrationBar } from '@/components/registration'

@Component({
  components: {
    BaseDialog,
    BaseSnackbar,
    RegistrationBar,
    RegistrationConfirmation,
    SearchHistory,
    SearchBar,
    Tombstone,
    RegistrationTable
  }
})
export default class Dashboard extends Vue {
  @Getter getSearchHistory: Array<SearchResponseIF>
  @Getter getSearchHistoryLength: Number
  @Getter getSearchResults: SearchResponseIF
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF
  @Getter getUserSettings: UserSettingsIF

  @Action resetNewRegistration: ActionBindingIF
  @Action setSearchDebtorName: ActionBindingIF
  @Action setRegistrationType: ActionBindingIF
  @Action setSearchHistory: ActionBindingIF
  @Action setSearchHistoryLength: ActionBindingIF
  @Action setSearchResults: ActionBindingIF
  @Action setSearchedType: ActionBindingIF
  @Action setSearchedValue: ActionBindingIF
  @Action setStateModel: ActionBindingIF
  @Action setLengthTrust: ActionBindingIF
  @Action setAddCollateral: ActionBindingIF
  @Action setAddSecuredPartiesAndDebtors: ActionBindingIF
  @Action setUserSettings: ActionBindingIF

  /** Whether App is ready. */
  @Prop({ default: false })
  private appReady: boolean

  @Prop({ default: false })
  private isJestRunning: boolean

  @Prop({ default: 'https://bcregistry.ca' })
  private registryUrl: string

  private loading = false
  // my reg table action stuff
  private myRegAction: TableActions = null
  private myRegActionDialog: DialogOptionsIF = dischargeConfirmationDialog
  private myRegActionDialogDisplay = false
  private myRegActionDocId = ''
  private myRegActionRegNum = ''
  private myRegActionRoute: RouteNames = null
  private myRegAdd = ''
  private myRegAddDialog: DialogOptionsIF = null
  private myRegErrDialog: DialogOptionsIF = null
  private myRegAddDialogError: StatusCodes = null
  private myRegAddDialogDisplay = false
  private myRegErrDialogDisplay = false
  private myRegDeleteDialogDisplay = false
  private myRegDeleteDialog: DialogOptionsIF = null

  // my reg table items/headers/sort info
  private myRegDataBaseRegDrafts: DraftResultIF[] = []
  private myRegDataChildDrafts: DraftResultIF[] = []
  private myRegDataHistory: RegistrationSummaryIF[] = []
  private myRegDataLoading = false
  private myRegFilter = ''
  private myRegHeaders = [...registrationTableHeaders]
  private myRegHeadersSelectable = [...registrationTableHeaders].slice(0, -1) // remove actions
  private myRegHeadersSelected = [...registrationTableHeaders]
  private myRegNoMorePages = false
  private myRegPage = 1
  private myRegSortOptions: RegistrationSortIF = {
    endDate: null,
    folNum: '',
    orderBy: 'createDateTime',
    orderVal: 'desc',
    regBy: '',
    regNum: '',
    regParty: '',
    regType: '',
    secParty: '',
    startDate: null,
    status: ''
  }

  private myRegTotalBaseRegLength = 0

  private payErrorDisplay = false
  private payErrorOptions: DialogOptionsIF = null

  private snackbarMsg = ''
  private toggleSnackbar = false
  private tooltipTxtRegSrch = 'Retrieve existing registrations you would like to ' +
    'renew, discharge or amend that are not already in your registrations table.'

  mounted () {
    // clear search data in the store
    this.setRegistrationType(null)
    this.setSearchedType(null)
    this.setSearchedValue('')
    this.setSearchResults(null)
    this.onAppReady(this.appReady)
  }

  private get breadcrumbs (): Array<BreadcrumbIF> {
    return tombstoneBreadcrumbDashboard
  }

  private get isAuthenticated (): boolean {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }

  private get myRegistrations () {
    return [...this.myRegDataBaseRegDrafts, ...this.myRegDataHistory]
  }

  private get myRegAddInvalid (): boolean {
    return ![0, 7].includes(this.myRegAdd?.trim().length || 0)
  }

  private get searchHistoryLength (): number {
    return this.getSearchHistory?.length || 0
  }

  private async addRegistration (regNum: string): Promise<void> {
    this.loading = true
    const addReg = await addRegistrationSummary(regNum)
    if (!addReg.error) {
      // set expand if its not a base reg
      if (regNum !== addReg.registrationNumber) {
        addReg.new = true
        addReg.expand = true
      }
      // add to my registrations list
      this.myRegDataHistory.unshift(addReg)
      this.snackbarMsg = 'Registration was successfully added to your table.'
      this.toggleSnackbar = !this.toggleSnackbar
    } else {
      this.myRegAddErrSetDialog(addReg.error)
    }
    this.loading = false
  }

  private editDraftAmend (docId: string, regNum: string): void {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    // Go to the Amendment first step which loads the base registration and draft data.
    this.$router.push({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': regNum, 'document-id': docId }
    })
    this.emitHaveData(false)
  }

  private async editDraftNew (documentId: string): Promise<void> {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    // Get draft details and setup store for editing the draft financing statement.
    const stateModel:StateModelIF = await setupFinancingStatementDraft(this.getStateModel, documentId)
    if (stateModel.registration.draft === undefined || stateModel.registration.draft.error !== undefined) {
      this.myRegAddDialog = { ...registrationOpenDraftErrorDialog }
      this.myRegAddDialogDisplay = true
    } else {
      this.setLengthTrust(stateModel.registration.lengthTrust)
      this.setAddCollateral(stateModel.registration.collateral)
      this.setAddSecuredPartiesAndDebtors(stateModel.registration.parties)
      // Go to the first step.
      this.$router.push({ name: RouteNames.LENGTH_TRUST })
    }
  }

  private async findRegistration (regNum: string): Promise<void> {
    if (this.myRegAddInvalid || !regNum) return

    this.loading = true
    this.myRegAddDialog = null
    regNum = regNum.trim()
    const reg = await getRegistrationSummary(regNum)
    if (!reg.error) {
      this.myRegAddFoundSetDialog(regNum, reg)
    } else {
      this.myRegAddErrSetDialog(reg.error)
    }
    this.loading = false
  }

  private myRegActionDialogHandler (proceed: boolean): void {
    // handles the response from the confirmation dialog in the amend/renew/discharge flow
    if (proceed) {
      this.startNewChildDraft(this.myRegActionRegNum, this.myRegActionRoute)
    }
    this.myRegAction = null
    this.myRegActionRegNum = ''
    this.myRegActionDialogDisplay = false
  }

  private myRegActionHandler ({ action, docId, regNum }): void {
    this.myRegAction = action as TableActions
    this.myRegActionDocId = docId as string
    this.myRegActionRegNum = regNum as string
    switch (action) {
      case TableActions.AMEND:
        this.myRegActionRoute = RouteNames.AMEND_REGISTRATION
        this.myRegActionDialog = amendConfirmationDialog
        this.myRegActionDialogDisplay = true
        break
      case TableActions.DISCHARGE:
        this.myRegActionRoute = RouteNames.REVIEW_DISCHARGE
        this.myRegActionDialog = dischargeConfirmationDialog
        this.myRegActionDialogDisplay = true
        break
      case TableActions.RENEW:
        this.myRegActionRoute = RouteNames.RENEW_REGISTRATION
        this.myRegActionDialog = renewConfirmationDialog
        this.myRegActionDialogDisplay = true
        break
      case TableActions.DELETE:
        this.myRegDeleteDialog = tableDeleteDialog
        this.myRegDeleteDialogDisplay = true
        break
      case TableActions.REMOVE:
        this.myRegDeleteDialog = tableRemoveDialog
        this.myRegDeleteDialogDisplay = true
        break
      case TableActions.EDIT_AMEND:
        this.editDraftAmend(docId, regNum)
        break
      case TableActions.EDIT_NEW:
        this.editDraftNew(docId)
        break
      default:
        this.myRegAction = null
        this.myRegActionDocId = ''
        this.myRegActionRegNum = ''
        console.error('Action not implemented.')
    }
  }

  private myRegAddErrSetDialog (error: ErrorIF): void {
    this.myRegAddDialogError = error.statusCode
    const regNum = this.myRegAdd?.trim()?.toUpperCase()
    switch (error.statusCode) {
      case StatusCodes.NOT_FOUND:
        this.myRegAddDialog = { ...registrationNotFoundDialog }
        this.myRegAddDialog.text = 'An existing registration with the ' +
          `registration number <b>${regNum}</b> was not found. Please ` +
          'check the registration number and try again.'
        break
      case StatusCodes.FORBIDDEN || StatusCodes.UNAUTHORIZED:
        this.myRegAddDialog = { ...registrationRestrictedDialog }
        this.myRegAddDialog.text = 'An existing registration was found with ' +
          `the registration number <b>${regNum}</b> but access is ` +
          'restricted and it is not available to add to your registrations ' +
          'table. Please contact us if you require assistance.'
        break
      case StatusCodes.CONFLICT:
        this.myRegAddDialog = { ...registrationAlreadyAddedDialog }
        this.myRegAddDialog.text = 'The registration with the registration number ' +
          `<b>${regNum}</b> is already in your registrations table.`
        break
      default:
        this.myRegAddDialog = { ...registrationAddErrorDialog }
    }
    this.myRegAddDialogDisplay = true
  }

  private searchError (error: ErrorIF): void {
    console.error(error)
    switch (error.type) {
      case (
        ErrorCodes.BCOL_ACCOUNT_CLOSED ||
        ErrorCodes.BCOL_USER_REVOKED ||
        ErrorCodes.BCOL_ACCOUNT_REVOKED ||
        ErrorCodes.BCOL_UNAVAILABLE
      ):
        this.payErrorOptions = { ...paymentErrorSearch }
        this.payErrorOptions.text += '<br/><br/>' + error.detail
        this.payErrorDisplay = true
        break
      case ErrorCodes.ACCOUNT_IN_PAD_CONFIRMATION_PERIOD:
        this.payErrorOptions = { ...paymentErrorSearch }
        this.payErrorOptions.text += '<br/><br/>' + error.detail +
          '<br/><br/>If this error continues after the waiting period has completed, please contact us.'
        this.payErrorOptions.hasContactInfo = true
        this.payErrorDisplay = true
        break
      default:
        if (error.type && error.type?.includes('BCOL') && error.detail) {
          // bcol generic
          this.payErrorOptions = { ...paymentErrorSearch }
          this.payErrorOptions.text += '<br/><br/>' + error.detail
          this.payErrorDisplay = true
        } else if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
          // generic pay error
          this.payErrorOptions = { ...paymentErrorSearch }
          this.payErrorOptions.text = '<b>The payment could not be completed at this time</b>' +
            '<br/><br/>If this issue persists, please contact us.'
          this.payErrorOptions.hasContactInfo = true
          this.payErrorDisplay = true
        } else {
          // generic search error
          this.myRegAddDialog = { ...searchResultsError }
          this.myRegAddDialogDisplay = true
        }
    }
  }

  private historyError (error: ErrorIF): void {
    console.error(error)
    this.myRegAddDialog = { ...searchPdfError }
    this.myRegAddDialogDisplay = true
  }

  private myRegAddFoundSetDialog (searchedRegNum: string, reg: RegistrationSummaryIF): void {
    this.myRegAddDialog = Object.assign({ ...registrationFoundDialog })
    searchedRegNum = searchedRegNum?.trim()?.toUpperCase()
    // if the searched registration is a child of the base registration
    if (searchedRegNum !== reg.baseRegistrationNumber?.trim()?.toUpperCase()) {
      this.myRegAddDialog.text = `The registration number you entered (<b>${searchedRegNum}</b>) ` +
        'is associated with the following base registration. Would you like to add this ' +
        'base registration to your registrations table? Adding the base registration to your ' +
        'registrations table will automatically include all associated registrations.'
    }
    this.myRegAddDialog.textExtra = [
      '<b>Base Registration Number:</b> ',
      '<b>Base Registration Date:</b> ',
      '<b>Registration Type:</b> ',
      '<b>Registering Party:</b> '
    ]
    this.myRegAddDialog.textExtra[0] += reg.baseRegistrationNumber
    if (reg.createDateTime) {
      const createDate = new Date(reg.createDateTime)
      this.myRegAddDialog.textExtra[1] += convertDate(createDate, false, false)
    } else {
      this.myRegAddDialog.textExtra[1] += 'N/A'
    }
    const regType = AllRegistrationTypes.find((regType: RegistrationTypeIF) => {
      if (regType.registrationTypeAPI === reg.registrationType) {
        return true
      }
    })
    if (regType) {
      this.myRegAddDialog.textExtra[2] += regType.registrationTypeUI
    } else {
      // Just in case some type gets added/changed and is not picked up by the UI.
      this.myRegAddDialog.textExtra[2] += 'Legacy'
    }
    this.myRegAddDialog.textExtra[3] += reg.registeringParty
    this.myRegAddDialogDisplay = true
  }

  private myRegAddDialogProceed (val: boolean): void {
    // add registration or not
    if (val && !this.myRegAddDialogError) {
      this.addRegistration(this.myRegAdd)
    }
    // reset values
    if (this.myRegAddDialogError !== StatusCodes.NOT_FOUND) {
      this.myRegAdd = ''
    }
    this.myRegAddDialogError = null
    this.myRegAddDialogDisplay = false
  }

  private myRegDeleteDialogProceed (val: boolean): void {
    if (val) {
      if (this.myRegAction === TableActions.DELETE) this.removeDraft(this.myRegActionRegNum, this.myRegActionDocId)
      if (this.myRegAction === TableActions.REMOVE) this.removeRegistration(this.myRegActionRegNum)
    }
    this.myRegAction = null
    this.myRegActionDocId = ''
    this.myRegActionRegNum = ''
    this.myRegDeleteDialogDisplay = false
  }

  private myRegErrDialogProceed (val: boolean): void {
    this.myRegErrDialogDisplay = false
  }

  private async myRegGetNext (): Promise<void> {
    if (this.myRegDataLoading || this.myRegNoMorePages) return
    this.myRegDataLoading = true
    this.myRegPage += 1
    const nextRegs = await registrationHistory(this.myRegSortOptions, this.myRegPage)
    if (nextRegs.error) {
      this.emitError(nextRegs.error)
    } else {
      // add child drafts to new regs if applicable
      const updatedRegs = this.myRegHistoryDraftCollapse(this.myRegDataChildDrafts, nextRegs.registrations, true)
      this.myRegDataHistory = this.myRegDataHistory.concat(updatedRegs.registrations)
    }
    if (nextRegs.registrations?.length < 100) { this.myRegNoMorePages = true }
    this.myRegDataLoading = false
  }

  private myRegHistoryDraftCollapse (
    drafts: DraftResultIF[],
    registrations: RegistrationSummaryIF[],
    sorting: boolean
  ): { drafts: DraftResultIF[], registrations: RegistrationSummaryIF[] } {
    // add child drafts to their base registration in registration history
    const parentDrafts = [] as DraftResultIF[]
    for (let i = 0; i < drafts.length; i++) {
      // check if it has a parent reg
      if (drafts[i].baseRegistrationNumber) {
        // find parent reg
        let found = false
        for (let k = 0; k < registrations.length; k++) {
          if (registrations[k].baseRegistrationNumber === drafts[i].baseRegistrationNumber) {
            // add child draft to parent reg
            if (!registrations[k].changes) registrations[k].changes = []
            registrations[k].changes.unshift(drafts[i])
            registrations[k].hasDraft = true
            found = true
            if (!sorting) this.myRegDataChildDrafts.push(drafts[i])
          }
        }
        // if sorting and the base reg is not in the list, add the draft to the parent list
        if (sorting && !found) {
          parentDrafts.push(drafts[i])
        }
      } else {
        // doesn't have a parent reg, this will be added to the normal draft results
        parentDrafts.push(drafts[i])
      }
    }
    return {
      drafts: parentDrafts,
      registrations: registrations
    }
  }

  private async myRegSort (sortOptions: RegistrationSortIF): Promise<void> {
    this.myRegDataLoading = true
    this.myRegNoMorePages = false
    this.myRegSortOptions = sortOptions
    this.myRegPage = 1
    const sortedDrafts = await draftHistory(this.myRegSortOptions)
    const sortedRegs = await registrationHistory(this.myRegSortOptions, this.myRegPage)
    // prioritize reg history error
    const error = sortedRegs.error || sortedDrafts.error
    if (error) {
      this.emitError(error)
    } else {
      if (sortedRegs.registrations?.length < 100) { this.myRegNoMorePages = true }
      // add child drafts to their base registration in registration history
      const histroyDraftsCollapsed = this.myRegHistoryDraftCollapse(sortedDrafts.drafts, sortedRegs.registrations, true)
      // only add parent drafts to draft results
      this.myRegDataBaseRegDrafts = histroyDraftsCollapsed.drafts
      this.myRegDataHistory = histroyDraftsCollapsed.registrations
    }
    this.myRegDataLoading = false
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    window.location.assign(this.registryUrl)
  }

  private async removeDraft (regNum: string, docId: string): Promise<void> {
    this.loading = true
    const deletion = await deleteDraft(docId)
    if (deletion.statusCode !== StatusCodes.NO_CONTENT) {
      // FUTURE: set dialog options / show dialog for error
      console.error('Failed to delete draft. Please try again later.')
    } else {
      // remove from table
      if (!regNum) {
        // is not a child
        this.myRegDataBaseRegDrafts = this.myRegDataBaseRegDrafts.filter(reg => reg.documentId !== docId)
      } else {
        // is a child of another base registration
        for (let i = 0; i < this.myRegDataHistory.length; i++) {
          // find base registration and filter draft out of changes array
          if (this.myRegDataHistory[i].baseRegistrationNumber === regNum) {
            const changes = this.myRegDataHistory[i].changes as any
            this.myRegDataHistory[i].changes = changes.filter(reg => reg.documentId !== docId)
            if (this.myRegDataHistory[i].changes.length === 0) {
              // remove now irrelevant fields
              delete this.myRegDataHistory[i].changes
              delete this.myRegDataHistory[i].expand
            }
            break
          }
        }
      }
    }
    this.loading = false
  }

  private async removeRegistration (regNum: string): Promise<void> {
    this.loading = true
    const removal = await deleteRegistrationSummary(regNum)
    if (removal.statusCode !== StatusCodes.NO_CONTENT) {
      // FUTURE: set dialog options / show dialog for error
      console.error('Failed to remove registration. Please try again later.')
    } else {
      // remove from table
      this.myRegDataHistory = this.myRegDataHistory.filter(reg => reg.baseRegistrationNumber !== regNum)
    }
    this.loading = false
  }

  private startNewChildDraft (regNum: string, routeName: RouteNames): void {
    this.$router.push({
      name: routeName,
      query: { 'reg-num': regNum }
    })
    this.emitHaveData(false)
  }

  /** Set registration type in the store and route to the first registration step */
  private startNewRegistration (selectedRegistration: RegistrationTypeIF): void {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    this.setRegistrationType(selectedRegistration)
    this.$router.push({ name: RouteNames.LENGTH_TRUST })
  }

  private async retrieveSearchHistory (): Promise<void> {
    // get/set search history
    const resp = await searchHistory()
    if (!resp || resp?.error) {
      this.setSearchHistory(null)
    } else {
      this.setSearchHistory(resp?.searches)
    }
  }

  /** Called when App is ready and this component can load its data. */
  @Watch('appReady')
  private async onAppReady (val: boolean): Promise<void> {
    this.loading = true
    // do not proceed if app is not ready
    if (!val) return

    // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
    if (!this.isAuthenticated || (!this.isJestRunning && !getFeatureFlag('ppr-ui-enabled'))) {
      window.alert('Personal Property Registry is under contruction. Please check again later.')
      this.redirectRegistryHome()
      return
    }
    // FUTURE: add loading for search history too
    this.myRegDataLoading = true
    this.retrieveSearchHistory()
    const myRegDrafts = await draftHistory(this.myRegSortOptions)
    const myRegHistory = await registrationHistory(this.myRegSortOptions, 1)

    if (myRegDrafts?.error || myRegHistory?.error) {
      // prioritize reg error
      const error = myRegHistory?.error || myRegDrafts?.error
      this.emitError(error)
    } else {
      if (myRegHistory.registrations?.length < 100) { this.myRegNoMorePages = true }
      // add child drafts to their base registration in registration history
      const histroyDraftsCollapsed = this.myRegHistoryDraftCollapse(
        myRegDrafts.drafts, myRegHistory.registrations, false)
      // only add parent drafts to draft results
      this.myRegDataBaseRegDrafts = histroyDraftsCollapsed.drafts
      this.myRegDataHistory = histroyDraftsCollapsed.registrations
      if (myRegHistory.registrations.length > 0) {
        this.myRegTotalBaseRegLength = myRegHistory.registrations[0].totalRegistrationCount || 0
      }
      this.myRegTotalBaseRegLength += this.myRegDataBaseRegDrafts.length
    }
    // update columns selected with user settings
    if (this.getUserSettings?.[SettingOptions.REGISTRATION_TABLE]?.columns) {
      this.myRegHeadersSelected = this.getUserSettings[SettingOptions.REGISTRATION_TABLE].columns
    } else {
      // set default headers
      const headers = []
      for (let i = 0; i < this.myRegHeadersSelected.length; i++) {
        if (this.myRegHeadersSelected[i].display) {
          headers.push(this.myRegHeadersSelected[i])
        }
      }
      this.myRegHeadersSelected = headers
    }
    this.myRegDataLoading = false

    // tell App that we're finished loading
    this.loading = false
    this.emitHaveData(true)
  }

  @Watch('getSearchHistoryLength')
  private handleSearchHistoryUpdate (newVal: number, oldVal: number): void {
    // show snackbar if oldVal was not null
    if (oldVal !== null) {
      this.snackbarMsg = 'Your search was successfully added to your table.'
      this.toggleSnackbar = !this.toggleSnackbar
    }
  }

  @Watch('getSearchResults')
  private onSearch (val: SearchResponseIF): void {
    // navigate to search page if not null/reset
    if (val) {
      this.$router.push({
        name: RouteNames.SEARCH
      })
    }
  }

  @Watch('myRegHeadersSelected')
  private async updateMyRegHeaders (val: BaseHeaderIF[]): Promise<void> {
    const headers = []
    for (let i = 0; i < registrationTableHeaders.length; i++) {
      if (registrationTableHeaders[i].value === 'actions') headers.push(registrationTableHeaders[i])
      else if (val.find(header => header.value === registrationTableHeaders[i].value)) {
        headers.push(registrationTableHeaders[i])
      }
    }
    this.myRegHeaders = headers
    // update settings
    let settings: UserSettingsIF = await updateUserSettings(
      SettingOptions.REGISTRATION_TABLE,
      { columns: val }
    )
    if (settings?.error) {
      // FUTURE: notify failure to save? - just log and continue for now
      console.error('Failed to save selected columns to user settings.')
      // save new settings to session (they won't be included in an error response)
      settings = this.getUserSettings
      settings[SettingOptions.REGISTRATION_TABLE] = { columns: val }
    }
    this.setUserSettings(settings)
  }

  @Emit('error')
  private emitError (error: ErrorIF): void {
    console.error(error)
  }

  /** Emits Have Data event. */
  @Emit('haveData')
  private emitHaveData (haveData: Boolean = true): void { }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.copy-normal {
  color: $gray7;
  font-size: 0.875rem;
}
.dashboard-title {
  background-color: $BCgovBlue0;
  color: $gray9;
  font-size: 1rem;
}
.text-input-style-above {
  label {
    font-size: 0.875rem;
    color: $gray7 !important;
    padding-left: 6px;
    margin-top: -2px;
  }
  span {
    padding-left: 6px;
    font-size: 14px;
    color: $gray7;
  }
}
.validation-msg {
  color: $error;
  font-size: 0.75rem;
  position: absolute;
}
</style>
