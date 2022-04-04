<template>
  <v-container id="dashboard" class="view-container px-15 py-10 ma-0" fluid>
    <v-overlay :value="pageLoader">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <base-dialog
      id="myRegAddDialog"
      :setDisplay="myRegAddDialogDisplay"
      :setOptions="myRegAddDialog"
      @proceed="myRegAddDialogProceed($event)"
    />
    <base-dialog
      id="myRegDeleteDialog"
      :setDisplay="myRegDeleteDialogDisplay"
      :setOptions="myRegDeleteDialog"
      @proceed="myRegDeleteDialogProceed($event)"
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
              <b v-if="hasPprRole && hasMhrRole">Asset Search</b>
              <b v-else-if="hasPprRole">Personal Property Search</b>
              <b v-else-if="hasMhrRole">Manufactured Home Search</b>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-bar
              class="soft-corners-bottom"
              :isNonBillable="isNonBillable"
              :serviceFee="getUserServiceFee"
              @debtor-name="setSearchDebtorName"
              @searched-type="setSearchedType"
              @searched-value="setSearchedValue"
              @search-data="setSearchResults"
              @toggleStaffPaymentDialog="staffPaymentDialogDisplay = true"
              @search-error="emitError($event)"
            />
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
            <v-col v-if="!appLoadingData" cols="12">
              <search-history class="soft-corners-bottom" @retry="retrieveSearchHistory" @error="emitError"/>
            </v-col>
            <v-col v-else class="pa-10" cols="12">
              <v-progress-linear color="primary" indeterminate rounded height="6" />
            </v-col>
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
              <b>Registrations</b> ({{ getRegTableTotalRowCount }})
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
            <v-col v-if="!appLoadingData" cols="12">
              <registration-table
                :setHeaders="myRegHeaders"
                :setLoading="myRegDataLoading || myRegDataAdding"
                :setMorePages="hasMorePages"
                :setNewRegItem="getRegTableNewItem"
                :setRegistrationHistory="myRegistrations"
                :setSearch="myRegFilter"
                :setSort="getRegTableSortOptions"
                @action="myRegActionHandler($event)"
                @error="emitError($event)"
                @getNext="myRegGetNext()"
                @sort="myRegSort($event)"
              />
            </v-col>
            <v-col v-else class="pa-10" cols="12">
              <v-progress-linear color="primary" indeterminate rounded height="6" />
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
import { cloneDeep } from 'lodash'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local helpers/enums/interfaces/resources
import {
  APIStatusTypes, ErrorCategories, RouteNames, SettingOptions, TableActions // eslint-disable-line no-unused-vars
} from '@/enums'
import {
  ActionBindingIF, // eslint-disable-line no-unused-vars
  BaseHeaderIF, // eslint-disable-line no-unused-vars
  BreadcrumbIF, // eslint-disable-line no-unused-vars
  DialogOptionsIF, // eslint-disable-line no-unused-vars
  DraftResultIF, // eslint-disable-line no-unused-vars
  ErrorIF, // eslint-disable-line no-unused-vars
  RegistrationSortIF, // eslint-disable-line no-unused-vars
  RegistrationSummaryIF, // eslint-disable-line no-unused-vars
  RegistrationTypeIF, RegTableDataI, RegTableNewItemI, // eslint-disable-line no-unused-vars
  SearchResponseIF, SearchTypeIF, // eslint-disable-line no-unused-vars
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
  registrationAddErrorDialog,
  registrationAlreadyAddedDialog,
  registrationFoundDialog,
  registrationNotFoundDialog,
  registrationRestrictedDialog,
  renewConfirmationDialog,
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
  updateUserSettings,
  navigate
} from '@/utils'
// local components
import { BaseSnackbar } from '@/components/common'
import { BaseDialog, RegistrationConfirmation } from '@/components/dialogs'
import { Tombstone } from '@/components/tombstone'
import { SearchBar } from '@/components/search'
import { SearchHistory, RegistrationTable } from '@/components/tables'
import { RegistrationBar } from '@/components/registration'
import { useSearch } from '@/composables/useSearch'

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
  @Getter getRegTableBaseRegs: RegistrationSummaryIF[]
  @Getter getRegTableDraftsBaseReg: DraftResultIF[]
  @Getter getRegTableDraftsChildReg: DraftResultIF[]
  @Getter getRegTableNewItem: RegTableNewItemI
  @Getter getRegTableSortOptions: RegistrationSortIF
  @Getter getRegTableSortPage: number
  @Getter getRegTableTotalRowCount: number
  @Getter getSearchHistory: Array<SearchResponseIF>
  @Getter getSearchHistoryLength: number
  @Getter getSearchResults: SearchResponseIF
  @Getter getSearchedType: SearchTypeIF
  @Getter getRegistrationType: RegistrationTypeIF
  @Getter getStateModel: StateModelIF
  @Getter getUserServiceFee!: number
  @Getter getUserSettings: UserSettingsIF
  @Getter hasMorePages: boolean
  @Getter isNonBillable!: boolean
  @Getter hasPprRole: boolean
  @Getter hasMhrRole: boolean

  @Action resetNewRegistration: ActionBindingIF
  @Action resetRegTableData: ActionBindingIF
  @Action setRegTableBaseRegs: ActionBindingIF
  @Action setRegTableCollapsed: ActionBindingIF
  @Action setRegTableDraftsBaseReg: ActionBindingIF
  @Action setRegTableDraftsChildReg: ActionBindingIF
  @Action setRegTableNewItem: ActionBindingIF
  @Action setRegTableSortHasMorePages: ActionBindingIF
  @Action setRegTableSortOptions: ActionBindingIF
  @Action setRegTableSortPage: ActionBindingIF
  @Action setRegTableTotalRowCount: ActionBindingIF
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
  @Action setUnsavedChanges: ActionBindingIF
  @Action setUserSettings: ActionBindingIF

  @Prop({ default: false })
  private appLoadingData: boolean

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
  private myRegAddDialogError: StatusCodes = null
  private myRegAddDialogDisplay = false
  private myRegDeleteDialogDisplay = false
  private myRegDeleteDialog: DialogOptionsIF = null
  private isMHRSearchType = useSearch().isMHRSearchType
  private isPPRSearchType = useSearch().isPPRSearchType

  private myRegDataLoading = false
  private myRegDataAdding = false
  private myRegFilter = ''
  private myRegHeaders = [...registrationTableHeaders]
  private myRegHeadersSelectable = [...registrationTableHeaders].slice(0, -1) // remove actions
  private myRegHeadersSelected = [...registrationTableHeaders]

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
    if (!!this.getRegTableDraftsBaseReg && !!this.getRegTableBaseRegs) {
      return [...this.getRegTableDraftsBaseReg, ...this.getRegTableBaseRegs]
    }
    return []
  }

  private get myRegAddInvalid (): boolean {
    return ![0, 7].includes(this.myRegAdd?.trim().length || 0) || (this.myRegAdd && !this.myRegAdd?.trim())
  }

  private get pageLoader (): boolean {
    return this.loading || this.myRegDataAdding
  }

  private get searchHistoryLength (): number {
    return this.getSearchHistory?.length || 0
  }

  private async addRegistration (regNum: string): Promise<void> {
    this.loading = true
    const addReg = await addRegistrationSummary(regNum)
    if (addReg.error) {
      this.myRegAddErrSetDialog(addReg.error)
    } else {
      // set new item (watcher will add it etc.)
      let parentRegNum = ''
      if (regNum.toUpperCase() !== addReg.registrationNumber.toUpperCase()) {
        // not a base registration so add parent reg num
        parentRegNum = addReg.registrationNumber.toUpperCase()
      }
      const newRegItem: RegTableNewItemI = {
        addedReg: regNum.toUpperCase(),
        addedRegParent: parentRegNum,
        addedRegSummary: addReg,
        prevDraft: ''
      }
      this.setRegTableNewItem(newRegItem)
    }
    this.loading = false
  }

  private editDraftAmend (docId: string, regNum: string): void {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    // Go to the Amendment first step which loads the base registration and draft data.
    this.setRegTableCollapsed(null)
    this.$router.replace({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': regNum, 'document-id': docId }
    })
    this.emitHaveData(false)
  }

  private async editDraftNew (documentId: string): Promise<void> {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    // Get draft details and setup store for editing the draft financing statement.
    const stateModel:StateModelIF = await setupFinancingStatementDraft(this.getStateModel, documentId)
    if (stateModel.registration.draft.error) {
      this.emitError(stateModel.registration.draft.error)
    } else {
      this.setLengthTrust(stateModel.registration.lengthTrust)
      this.setAddCollateral(stateModel.registration.collateral)
      this.setAddSecuredPartiesAndDebtors(stateModel.registration.parties)
      // reset unsaved changes
      this.setUnsavedChanges(false)
      // Go to the first step.
      this.setRegTableCollapsed(null)
      this.$router.replace({ name: RouteNames.LENGTH_TRUST })
    }
  }

  private async findRegistration (regNum: string): Promise<void> {
    if (this.myRegAddInvalid || !regNum) return

    this.loading = true
    this.myRegAddDialog = null
    regNum = regNum.trim()
    const reg = await getRegistrationSummary(regNum, false)
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
    if (val && !this.myRegAddDialogError &&
      (this.myRegAddDialog.title === 'Registration Found')) {
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

  private async myRegGetNext (): Promise<void> {
    if (this.myRegDataLoading || !this.hasMorePages) return
    this.myRegDataLoading = true
    const page = this.getRegTableSortPage + 1
    this.setRegTableSortPage(page)
    const nextRegs = await registrationHistory(cloneDeep(this.getRegTableSortOptions), page)
    if (nextRegs.error) {
      this.emitError(nextRegs.error)
    } else {
      // add child drafts to new regs if applicable
      const updatedRegs = this.myRegHistoryDraftCollapse(
        cloneDeep(this.getRegTableDraftsChildReg), cloneDeep(nextRegs.registrations), true)
      const newBaseRegs = this.getRegTableBaseRegs.concat(updatedRegs.registrations)
      this.setRegTableBaseRegs(newBaseRegs)
    }
    if (nextRegs.registrations?.length < 1) this.setRegTableSortHasMorePages(false)
    this.myRegDataLoading = false
  }

  private myRegHistoryDraftCollapse (
    drafts: DraftResultIF[],
    registrations: RegistrationSummaryIF[],
    sorting: boolean
  ): { drafts: DraftResultIF[], registrations: RegistrationSummaryIF[] } {
    // add child drafts to their base registration in registration history
    const parentDrafts = [] as DraftResultIF[]
    let childDrafts = this.getRegTableDraftsChildReg
    // reset child drafts if not sorting
    if (!sorting) childDrafts = []
    for (let i = 0; i < drafts.length; i++) {
      // check if it has a parent reg
      if (drafts[i].baseRegistrationNumber) {
        if (!sorting) childDrafts.push(drafts[i])
        // find parent reg
        let found = false
        const parentIndex = registrations.findIndex(
          reg => reg.baseRegistrationNumber === drafts[i].baseRegistrationNumber)
        if (parentIndex !== -1) {
          // add child draft to parent reg
          if (!registrations[parentIndex].changes) registrations[parentIndex].changes = []
          registrations[parentIndex].changes.unshift(drafts[i])
          registrations[parentIndex].hasDraft = true
          found = true
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
    // set store child drafts to new list
    this.setRegTableDraftsChildReg(childDrafts)
    return {
      drafts: parentDrafts,
      registrations: registrations
    }
  }

  private async myRegSort (args: { sortOptions: RegistrationSortIF, sorting: boolean }): Promise<void> {
    this.myRegDataLoading = true
    this.setRegTableSortHasMorePages(true)
    this.setRegTableSortOptions(args.sortOptions)
    this.setRegTableSortPage(1)
    const sorting = args.sorting
    let sortedDrafts = { drafts: [] as DraftResultIF[], error: null }
    // all drafts return from the api no matter the status value so prevent it here
    if (!args.sortOptions.status || args.sortOptions.status === APIStatusTypes.DRAFT) {
      sortedDrafts = await draftHistory(cloneDeep(args.sortOptions))
    }
    const sortedRegs = await registrationHistory(cloneDeep(args.sortOptions), 1)
    // prioritize reg history error
    const error = sortedRegs.error || sortedDrafts.error
    if (error) {
      this.emitError(error)
    } else {
      if (sortedRegs.registrations?.length < 1) this.setRegTableSortHasMorePages(false)
      // parent drafts from sorted list
      const draftsCollapsed = this.myRegHistoryDraftCollapse(
        cloneDeep(sortedDrafts.drafts), cloneDeep(sortedRegs.registrations), sorting)
      // add child drafts from original list to sorted base registrations
      const updatedRegs = this.myRegHistoryDraftCollapse(
        cloneDeep(this.getRegTableDraftsChildReg), cloneDeep(sortedRegs.registrations), sorting)
      // only add parent drafts to draft results
      this.setRegTableDraftsBaseReg(draftsCollapsed.drafts)
      this.setRegTableBaseRegs(updatedRegs.registrations)
    }
    this.myRegDataLoading = false
  }

  /** Redirects browser to Business Registry home page. */
  private redirectRegistryHome (): void {
    navigate(this.registryUrl)
  }

  private async removeDraft (regNum: string, docId: string): Promise<void> {
    this.loading = true
    const deletion = await deleteDraft(docId)
    if (deletion.statusCode !== StatusCodes.NO_CONTENT) {
      this.emitError(deletion)
    } else {
      // remove from table
      this.setRegTableDraftsBaseReg(this.getRegTableDraftsBaseReg.filter(reg => reg.documentId !== docId))
      this.setRegTableDraftsChildReg(this.getRegTableDraftsChildReg.filter(reg => reg.documentId !== docId))
      if (!regNum) {
        // is not a child
        this.setRegTableTotalRowCount(this.getRegTableTotalRowCount - 1)
      } else {
        // is a child of another base registration
        const baseRegs = this.getRegTableBaseRegs
        // find parent base registration and filter draft out of changes array
        const parentIndex = baseRegs.findIndex(reg => reg.baseRegistrationNumber === regNum)
        const changes = baseRegs[parentIndex].changes as any
        baseRegs[parentIndex].changes = changes.filter(reg => reg.documentId !== docId)
        if (baseRegs[parentIndex].changes.length === 0) {
          // no longer a parent reg so remove irrelevant fields
          delete baseRegs[parentIndex].changes
          delete baseRegs[parentIndex].expand
        }
        this.setRegTableBaseRegs(baseRegs)
      }
    }
    this.loading = false
  }

  private async removeRegistration (regNum: string): Promise<void> {
    this.loading = true
    const removal = await deleteRegistrationSummary(regNum)
    if (removal.statusCode !== StatusCodes.NO_CONTENT) {
      this.emitError(removal)
    } else {
      // remove from table
      this.setRegTableBaseRegs(this.getRegTableBaseRegs.filter(reg => reg.baseRegistrationNumber !== regNum))
      this.setRegTableTotalRowCount(this.getRegTableTotalRowCount - 1)
    }
    this.loading = false
  }

  private startNewChildDraft (regNum: string, routeName: RouteNames): void {
    this.setRegTableCollapsed(null)
    this.$router.replace({
      name: routeName,
      query: { 'reg-num': regNum }
    })
    this.emitHaveData(false)
  }

  /** Set registration type in the store and route to the first registration step */
  private startNewRegistration (selectedRegistration: RegistrationTypeIF): void {
    this.resetNewRegistration(null) // Clear store data from the previous registration.
    this.setRegistrationType(selectedRegistration)
    this.setRegTableCollapsed(null)
    this.$router.replace({ name: RouteNames.LENGTH_TRUST })
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
    this.emitHaveData(false)
    this.resetNewRegistration(null) // Clear store data from any previous registration.
    // FUTURE: add loading for search history too
    this.myRegDataLoading = true
    this.retrieveSearchHistory()
    if (this.getRegTableNewItem?.addedReg) {
      // new reg was added so don't reload the registrations + trigger new item handler
      this.handleRegTableNewItem(this.getRegTableNewItem)
    } else {
      // load in registrations from scratch
      this.resetRegTableData(null)
      const myRegDrafts = await draftHistory(cloneDeep(this.getRegTableSortOptions))
      const myRegHistory = await registrationHistory(cloneDeep(this.getRegTableSortOptions), 1)

      if (myRegDrafts?.error || myRegHistory?.error) {
        // prioritize reg error
        const error = myRegHistory?.error || myRegDrafts?.error
        this.emitError(error)
      } else {
        if (myRegHistory.registrations?.length < 1) this.setRegTableSortHasMorePages(false)
        // add child drafts to their base registration in registration history
        const histroyDraftsCollapsed = this.myRegHistoryDraftCollapse(
          myRegDrafts.drafts, myRegHistory.registrations, false)
        // only add parent drafts to draft results
        this.setRegTableDraftsBaseReg(histroyDraftsCollapsed.drafts)
        this.setRegTableBaseRegs(histroyDraftsCollapsed.registrations)
        if (myRegHistory.registrations.length > 0) {
          this.setRegTableTotalRowCount(myRegHistory.registrations[0].totalRegistrationCount || 0)
        }
        // add base reg drafts length to total reg length
        this.setRegTableTotalRowCount(this.getRegTableTotalRowCount + histroyDraftsCollapsed.drafts.length)
      }
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

  @Watch('getRegTableNewItem')
  private async handleRegTableNewItem (val: RegTableNewItemI) {
    if (val.addedReg) {
      this.myRegDataAdding = true
      if (!val.addedRegSummary) {
        // atttempt to get the summary info from the api
        if (val.addedReg[0] !== 'D') {
          // its a normal reg - get reg summary
          const regSummary = await getRegistrationSummary(val.addedReg, true)
          if (regSummary.error) {
            this.emitError(regSummary.error) // dialog and will reload the dash after
            this.myRegDataAdding = false
            return
          }
          val.addedRegSummary = regSummary
        } else {
          // its a draft - get draft summary
          const drafts = await draftHistory(null)
          if (drafts.error) {
            this.emitError(drafts.error) // dialog and will reload the dash after
            this.myRegDataAdding = false
            return
          } else {
            val.addedRegSummary = drafts.drafts.find(d => d.documentId === val.addedReg)
            if (!val.addedRegSummary) {
              this.emitError({
                category: ErrorCategories.HISTORY_REGISTRATIONS,
                statusCode: StatusCodes.NOT_FOUND,
                message: 'Error finding new draft summary.'
              })
              this.myRegDataAdding = false
              return
            }
          }
        }
      }

      const baseRegs = this.getRegTableBaseRegs
      if (val.prevDraft) {
        // remove previous draft item from the store (child drafts also exist under parent - removed later)
        this.setRegTableDraftsBaseReg(this.getRegTableDraftsBaseReg.filter(reg => reg.documentId !== val.prevDraft))
        this.setRegTableDraftsChildReg(this.getRegTableDraftsChildReg.filter(reg => reg.documentId !== val.prevDraft))
      }
      // for masking the type of the new summary
      const newDraftSummary = val.addedRegSummary as DraftResultIF
      const newRegSummary = val.addedRegSummary as RegistrationSummaryIF
      if (val.addedRegParent) {
        // new child reg. Find parent + update it with new summary
        const parentIndex = baseRegs.findIndex(reg => reg.baseRegistrationNumber === val.addedRegParent)
        if (parentIndex === -1) {
          // reg was a child of a new base reg so we are adding the full base reg
          newRegSummary.expand = true
          baseRegs.unshift(newRegSummary)
          this.setRegTableBaseRegs([...baseRegs])
          this.setRegTableTotalRowCount(this.getRegTableTotalRowCount + 1)
        } else {
          if (val.prevDraft) {
            // remove draft
            const changes = baseRegs[parentIndex].changes as DraftResultIF[]
            if (changes) baseRegs[parentIndex].changes = changes.filter(reg => reg.documentId !== val.prevDraft)
            // update hasDraft value if removed draft was the only child draft
            const draftIndex = changes.findIndex(
              reg => reg.documentId !== val.prevDraft && reg.documentId !== undefined)
            if (!draftIndex) baseRegs[parentIndex].hasDraft = false
          }
          if (newDraftSummary.documentId) {
            // slot draft into parent changes
            if (!baseRegs[parentIndex].changes) baseRegs[parentIndex].changes = []
            baseRegs[parentIndex].changes.unshift(newDraftSummary)
          } else {
            // replace with new summary + then add drafts back on
            const changes = baseRegs[parentIndex].changes as DraftResultIF[]
            baseRegs[parentIndex] = newRegSummary
            if (changes) {
              const drafts = changes.filter(draft => !!draft.documentId)
              for (let i = drafts.length; i > 0; i--) {
                baseRegs[parentIndex].changes.unshift(drafts[i - 1])
                baseRegs[parentIndex].hasDraft = true
              }
            }
          }
          // expand row
          baseRegs[parentIndex].expand = true
          // update store
          this.setRegTableBaseRegs(cloneDeep(baseRegs))
        }
      } else if (newDraftSummary.documentId) {
        // new draft base reg
        const draftBaseRegs = this.getRegTableDraftsBaseReg
        draftBaseRegs.unshift(newDraftSummary)
        this.setRegTableDraftsBaseReg(draftBaseRegs)
        if (!val.prevDraft) {
          // new draft so increase
          this.setRegTableTotalRowCount(this.getRegTableTotalRowCount + 1)
        }
      } else {
        // new base reg
        baseRegs.unshift(newRegSummary)
        this.setRegTableBaseRegs([...baseRegs])
        if (!val.prevDraft) {
          // not from a draft so increase
          this.setRegTableTotalRowCount(this.getRegTableTotalRowCount + 1)
        }
      }
      this.myRegDataAdding = false
      // trigger snackbar
      this.snackbarMsg = 'Registration was successfully added to your table.'
      this.toggleSnackbar = !this.toggleSnackbar
      // set to empty strings after 5 seconds
      setTimeout(() => {
        // only reset if it hasn't changed since
        if (val.addedReg === this.getRegTableNewItem.addedReg) {
          const emptyItem: RegTableNewItemI = { addedReg: '', addedRegParent: '', addedRegSummary: null, prevDraft: '' }
          this.setRegTableNewItem(emptyItem)
        }
      }, 4000)
    }
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
      if (this.isMHRSearchType(this.getSearchedType.searchTypeAPI)) {
        // 'replace' resets the state so window.onbeforeunload event is fired when the browser 'back' btn is pressed
        this.$router.replace({
          name: RouteNames.MHRSEARCH
        })
      } else {
        // 'replace' resets the state so window.onbeforeunload event is fired when the browser 'back' btn is pressed
        this.$router.replace({
          name: RouteNames.SEARCH
        })
      }
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

  /** Emits error to app.vue for handling */
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
