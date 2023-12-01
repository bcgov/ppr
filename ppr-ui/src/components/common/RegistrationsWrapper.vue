<template>
  <div
    id="registrations-wrapper"
    class="mt-4"
  >
    <!-- Registration Dialogs -->
    <BaseDialog
      id="manufacturerRegSuccessDialog"
      :set-display="manufacturerRegSuccessDialogDisplay"
      :set-options="manufacturerRegSuccessDialogOptions"
      show-dismiss-dialog-checkbox
      @proceed="manufacturerRegSuccessDialogDisplay = false"
    />

    <BaseDialog
      id="myRegAddDialog"
      :setDisplay="myRegAddDialogDisplay"
      :setOptions="myRegAddDialog"
      @proceed="myRegAddDialogProceed($event)"
    />
    <BaseDialog
      id="myRegDeleteDialog"
      :setDisplay="myRegDeleteDialogDisplay"
      :setOptions="myRegDeleteDialog"
      @proceed="myRegDeleteDialogProceed($event)"
    />
    <RegistrationConfirmation
      attach=""
      :options="myRegActionDialog"
      :display="myRegActionDialogDisplay"
      :registrationNumber="myRegActionRegNum"
      @proceed="myRegActionDialogHandler($event)"
    />

    <!-- Registrations Upper Section -->
    <v-row
      class="pt-10 px-0"
      noGutters
      align="center"
    >
      <v-col
        cols="4"
        class="reg-bar-col"
      >
        <RegistrationBar
          class="soft-corners-bottom"
          :isMhr="isMhr"
          :isTabView="isTabView"
          @selectedRegistrationType="startNewRegistration($event)"
        />
      </v-col>
      <v-col cols="5">
        <p class="fs-14 float-right pr-4">
          <v-tooltip
            class="pa-2"
            contentClass="top-tooltip"
            location="top"
            transition="fade-transition"
          >
            <template #activator="{ props }">
              <v-icon
                color="primary"
                v-bind="props"
                class="mt-n1"
              >
                mdi-information-outline
              </v-icon>
            </template>
            <div>
              {{ tooltipTxtRegSrch }}
            </div>
          </v-tooltip>
          <span class="pl-1">Retrieve an existing registration to add to your table:</span>
        </p>
      </v-col>
      <v-col
        cols="3"
        class="reg-add-col"
      >
        <v-text-field
          id="my-reg-add"
          v-model="myRegAdd"
          class="reg-input rounded-all float-right"
          :class="{'column-selection': !isTabView}"
          appendInnerIcon="mdi-magnify"
          variant="filled"
          :errorMessages="myRegAddInvalid ? 'error' : ''"
          hideDetails
          singleLine
          :label="`${registrationLabel} Registration Number`"
          style="width:330px"
          density="compact"
          @keypress.enter="findRegistration(myRegAdd)"
          @click:append-inner="findRegistration(myRegAdd)"
        />
        <p
          v-if="myRegAddInvalid"
          class="validation-msg mx-3 my-1"
        >
          Registration numbers contain {{ isMhr ? '6' : '7' }} digits
        </p>
      </v-col>
    </v-row>

    <!-- Registrations Table Section -->
    <v-row
      noGutters
      class="my-10"
    >
      <v-col>
        <v-row
          id="registration-header"
          class="review-header px-6 py-2 rounded-top"
          align="center"
          noGutters
        >
          <v-col
            cols="auto"
            class="py-1"
          >
            <b>{{ registrationLabel }} Registrations </b>
            <span>({{ getRegTableTotalRowCount }})</span>
          </v-col>
          <v-col>
            <v-row
              justify="end"
              noGutters
            >
              <v-col
                class="pl-4 py-1"
                cols="3"
              >
                <v-select
                  id="column-selection"
                  v-model="myRegHeadersSelected"
                  :items="myRegHeadersSelectable"
                  hideDetails
                  itemTitle="text"
                  multiple
                  returnObject
                  density="compact"
                  placeholder="Columns to Show"
                >
                  <template #selection="{ index }">
                    <p
                      v-if="index === 0"
                      class="fs-14"
                    >
                      Columns to Show
                    </p>
                  </template>
                  <template #item="{ props, item }">
                    <v-list-item
                      v-bind="props"
                      class="py-0 my-0 fs-12 column-selection-item"
                    >
                      <template #prepend>
                        <v-checkbox
                          class="py-0 mr-n1"
                          hideDetails
                          :model-value="isActiveHeader(item.value)"
                        />
                      </template>
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row
          noGutters
          class="bg-white"
        >
          <v-col
            v-if="!appLoadingData"
            cols="12"
          >
            <RegistrationTable
              :class="{'table-border': isTabView}"
              :isPpr="isPpr"
              :isMhr="isMhr"
              :setHeaders="myRegHeaders"
              :setLoading="myRegDataLoading || myRegDataAdding"
              :setMorePages="hasMorePages"
              :setNewRegItem="getRegTableNewItem"
              :setRegistrationHistory="myRegistrations"
              :setSearch="myRegFilter"
              :setSort="getRegTableSortOptions"
              @action="myRegActionHandler($event)"
              @error="emitError($event)"
              @sort="myRegSort($event)"
              @getNext="myRegGetNext"
            />
          </v-col>
          <v-col
            v-else
            class="pa-10"
            cols="12"
          >
            <v-progress-linear
              color="primary"
              :indeterminate="true"
              rounded
              height="6"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>
<script lang="ts">
// Components
import { computed, defineComponent, onBeforeMount, reactive, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RegistrationBar } from '@/components/registration'
import { RegistrationTable } from '@/components/tables'
import { BaseDialog, RegistrationConfirmation } from '@/components/dialogs'
import {
  AllRegistrationTypes,
  mhRegistrationTableHeaders,
  MhrRegistrationType,
  registrationTableHeaders
} from '@/resources'
import {
  BaseHeaderIF,
  DialogOptionsIF,
  DraftResultIF,
  ErrorIF,
  MhrDraftIF,
  MhRegistrationSummaryIF,
  RegistrationSortIF,
  RegistrationSummaryIF,
  RegistrationTypeIF,
  RegTableNewItemI,
  StateModelIF,
  UserSettingsIF
} from '@/interfaces'
import { APIStatusTypes, ErrorCategories, RouteNames, SettingOptions, TableActions, UnitNoteDocTypes } from '@/enums'
import {
  addMHRegistrationSummary,
  addRegistrationSummary,
  convertDate,
  deleteDraft,
  deleteMhrDraft,
  deleteMhRegistrationSummary,
  deleteRegistrationSummary,
  draftHistory,
  getMHRegistrationSummary,
  getRegistrationSummary,
  hasTruthyValue,
  registrationHistory,
  setupFinancingStatementDraft,
  updateUserSettings
} from '@/utils'
import {
  amendConfirmationDialog,
  dischargeConfirmationDialog,
  manufacturerRegSuccessDialogOptions,
  mhRegistrationFoundDialog,
  mhrTableRemoveDialog,
  registrationAddErrorDialog,
  registrationAlreadyAddedDialog,
  registrationFoundDialog,
  registrationNotFoundDialog,
  registrationRestrictedDialog,
  renewConfirmationDialog,
  tableDeleteDialog,
  tableRemoveDialog
} from '@/resources/dialogOptions'
import { StatusCodes } from 'http-status-codes'
import { cloneDeep } from 'lodash'
import { useExemptions, useNewMhrRegistration } from '@/composables'

export default defineComponent({
  name: 'RegistrationsWrapper',
  components: {
    BaseDialog,
    RegistrationConfirmation,
    RegistrationBar,
    RegistrationTable
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    appLoadingData: {
      type: Boolean,
      default: false
    },
    isPpr: {
      type: Boolean,
      default: false
    },
    isMhr: {
      type: Boolean,
      default: false
    },
    isTabView: {
      type: Boolean,
      default: false
    }
  },
  emits: ['error', 'haveData', 'snackBarMsg'],
  setup (props, context) {
    const router = useRouter()
    const {
      // Actions
      resetNewRegistration, setRegistrationType, setRegTableCollapsed, setRegTableNewItem, setLengthTrust,
      setAddCollateral, setAddSecuredPartiesAndDebtors, setUnsavedChanges, setRegTableDraftsBaseReg,
      setRegTableDraftsChildReg, setRegTableTotalRowCount, setRegTableBaseRegs,
      setRegTableSortHasMorePages, setRegTableSortOptions, setUserSettings, resetRegTableData, setMhrInformation,
      setMhrTableHistory, setEmptyMhr, getUserMiscSettingsByKey, setRegTableSortPage
    } = useStore()
    const {
      // Getters
      getRegTableBaseRegs, getRegTableDraftsBaseReg, isMhrRegistration, isMhrManufacturerRegistration,
      getRegTableTotalRowCount, getStateModel, getRegTableDraftsChildReg, hasMorePages, getRegTableNewItem,
      getRegTableSortOptions, getRegTableSortPage, getUserSettings, getMhRegTableBaseRegs, isRoleStaffReg
    } = storeToRefs(useStore())

    const {
      initNewMhr,
      initNewManufacturerMhr,
      fetchMhRegistrations
    } = useNewMhrRegistration()
    const { goToExemptions } = useExemptions()

    const localState = reactive({
      loading: false,
      myRegAdd: '',
      myRegAction: null as TableActions,
      myRegActionDocId: '',
      myRegActionRegNum: '',
      myRegFilter: '',
      myRegActionRoute: null as RouteNames,
      myRegAddDialog: null as DialogOptionsIF,
      myRegAddDialogError: null as StatusCodes,
      dialogPermanentlyHidden: false,
      manufacturerRegSuccessDialogDisplay: false,
      manufacturerRegSuccessDialogOptions: manufacturerRegSuccessDialogOptions,
      hideSuccessDialog: false,
      myRegAddDialogDisplay: false,
      myRegActionDialogDisplay: false,
      myRegDeleteDialogDisplay: false,
      myRegDeleteDialog: null as DialogOptionsIF,
      myRegActionDialog: dischargeConfirmationDialog as DialogOptionsIF,
      myRegDataLoading: false,
      myRegDataAdding: false,
      pprColumnSettings: [],
      mhrColumnSettings: [],
      myRegHeaders: props.isPpr ? [...registrationTableHeaders] : [...mhRegistrationTableHeaders],
      myRegHeadersSelected: props.isPpr ? [...registrationTableHeaders] : [...mhRegistrationTableHeaders],
      myRegHeadersSelectable: props.isPpr
        ? [...registrationTableHeaders].slice(0, -1) // remove actions
        : [...mhRegistrationTableHeaders].slice(0, -1), // remove actions
      myRegistrations: computed(() => {
        if (props.isPpr && !!getRegTableDraftsBaseReg.value && !!getRegTableBaseRegs.value) {
          return [...getRegTableDraftsBaseReg.value, ...getRegTableBaseRegs.value]
        }
        if (props.isMhr) {
          return [...getMhRegTableBaseRegs.value]
        }
        return []
      }),
      myRegAddInvalid: computed((): boolean => {
        const maxLength = props.isMhr ? 6 : 7
        return ![0, maxLength].includes(
          localState.myRegAdd?.trim().length || 0) || (localState.myRegAdd && !localState.myRegAdd?.trim()
        )
      }),
      registrationLabel: computed((): string => {
        return props.isMhr ? 'Manufactured Home' : 'Personal Property'
      })
    })

    const tooltipTxtRegSrch: string = 'Retrieve existing registrations you would like to ' +
      'make changes to that are not already in your registrations table.'

    onBeforeMount(async (): Promise<void> => {
      localState.loading = true
      // do not proceed if app is not ready
      if (!props.appReady) return

      localState.dialogPermanentlyHidden =
        getUserMiscSettingsByKey(SettingOptions.SUCCESSFUL_REGISTRATION_DIALOG_HIDE) || false

      resetNewRegistration(null) // Clear store data from any previous registration.
      // FUTURE: add loading for search history too
      localState.myRegDataLoading = true
      if (getRegTableNewItem.value?.addedReg) {
        // new reg was added so don't reload the registrations + trigger new item handler
        await handleRegTableNewItem(getRegTableNewItem.value)
      } else if (props.isPpr) {
        // load in registrations from scratch
        resetRegTableData(null)
        const myRegDrafts = await draftHistory(cloneDeep(getRegTableSortOptions.value))
        const myRegHistory = await registrationHistory()

        if (myRegDrafts?.error || myRegHistory?.error) {
          // prioritize reg error
          const error = myRegHistory?.error || myRegDrafts?.error
          emitError(error)
        } else {
          if (myRegHistory.registrations?.length < 1) setRegTableSortHasMorePages(false)
          // add child drafts to their base registration in registration history
          const historyDraftsCollapsed = myRegHistoryDraftCollapse(
            myRegDrafts.drafts, myRegHistory.registrations, false)
          // only add parent drafts to draft results
          setRegTableDraftsBaseReg(historyDraftsCollapsed.drafts)
          setRegTableBaseRegs(historyDraftsCollapsed.registrations)
          if (myRegHistory.registrations?.length > 0) {
            setRegTableTotalRowCount(myRegHistory.registrations[0].totalRegistrationCount || 0)
          }
          // add base reg drafts length to total reg length
          setRegTableTotalRowCount(getRegTableTotalRowCount.value + historyDraftsCollapsed.drafts.length)
        }
      } else if (props.isMhr && !props.isTabView) { // If Tab view, Mhr Data will be loaded in dashboardTabs component
        await fetchMhRegistrations()
      }


      if (props.isPpr) {
        // update columns selected with user settings
        localState.pprColumnSettings = getUserSettings.value[SettingOptions.REGISTRATION_TABLE]?.columns?.length >= 1
          ? getUserSettings.value[SettingOptions.REGISTRATION_TABLE]?.columns
          : [...registrationTableHeaders] // Default to all selections for initialization

        localState.myRegHeadersSelected = localState.pprColumnSettings
      } else if (props.isMhr) {
        localState.mhrColumnSettings = getUserSettings.value[SettingOptions.REGISTRATION_TABLE]?.mhrColumns?.length >= 1
          ? getUserSettings.value[SettingOptions.REGISTRATION_TABLE]?.mhrColumns
          : [...mhRegistrationTableHeaders] // Default to all selections for initialization

        localState.myRegHeadersSelected = localState.mhrColumnSettings
      } else {
        // set default headers
        const headers = []
        for (const item of localState.myRegHeadersSelected) {
          if (item.display) {
            headers.push(item)
          }
        }
        localState.myRegHeadersSelected = headers
      }
      localState.myRegDataLoading = false
      localState.loading = false
    })

    /** Set registration type in the store and route to the first registration step */
    const startNewRegistration = async (selectedRegistration: RegistrationTypeIF, draftNumber: string = ''):
      Promise<void> => {
      // Clear store data for MHR
      await setEmptyMhr({ ...initNewMhr(), draftNumber })

      resetNewRegistration(null) // Clear store data from the previous registration.
      setRegistrationType(selectedRegistration)
      setRegTableCollapsed(null)

      if (!draftNumber && isMhrManufacturerRegistration.value) {
        await initNewManufacturerMhr()
      }

      const route = isMhrRegistration.value ? RouteNames.YOUR_HOME : RouteNames.LENGTH_TRUST
      await router.replace({ name: route })
    }

    const findRegistration = async (regNum: string): Promise<void> => {
      if (localState.myRegAddInvalid || !regNum) return

      localState.loading = true
      localState.myRegAddDialog = null
      regNum = regNum.trim()
      const reg = props.isMhr
        ? await getMHRegistrationSummary(regNum, false)
        : await getRegistrationSummary(regNum, false)
      if (!reg.error) {
        props.isMhr
          ? myMHRegAddFoundSetDialog(regNum, reg as MhRegistrationSummaryIF)
          : myRegAddFoundSetDialog(regNum, reg as RegistrationSummaryIF)
      } else {
        myRegAddErrSetDialog(reg.error)
      }
      localState.loading = false
    }

    // PPR Found Dialog
    const myRegAddFoundSetDialog = (searchedRegNum: string, reg: RegistrationSummaryIF): void => {
      localState.myRegAddDialog = Object.assign({ ...registrationFoundDialog })
      searchedRegNum = searchedRegNum?.trim()?.toUpperCase()
      // if the searched registration is a child of the base registration
      if (searchedRegNum !== reg.baseRegistrationNumber?.trim()?.toUpperCase()) {
        localState.myRegAddDialog.text = `The registration number you entered (<b>${searchedRegNum}</b>) ` +
          'is associated with the following base registration. Would you like to add this ' +
          'base registration to your registrations table? Adding the base registration to your ' +
          'registrations table will automatically include all associated registrations.'
      }
      localState.myRegAddDialog.textExtra = [
        '<b>Base Registration Number:</b> ',
        '<b>Base Registration Date:</b> ',
        '<b>Registration Type:</b> ',
        '<b>Registering Party:</b> '
      ]
      localState.myRegAddDialog.textExtra[0] += reg.baseRegistrationNumber
      if (reg.createDateTime) {
        const createDate = new Date(reg.createDateTime)
        localState.myRegAddDialog.textExtra[1] += convertDate(createDate, false, false)
      } else {
        localState.myRegAddDialog.textExtra[1] += 'N/A'
      }
      const regType = AllRegistrationTypes.find((regType: RegistrationTypeIF) => {
        if (regType.registrationTypeAPI === reg.registrationType) {
          return true
        }
      })
      if (regType) {
        localState.myRegAddDialog.textExtra[2] += regType.registrationTypeUI
      } else {
        // Just in case some type gets added/changed and is not picked up by the UI.
        localState.myRegAddDialog.textExtra[2] += 'Legacy'
      }
      localState.myRegAddDialog.textExtra[3] += reg.registeringParty
      localState.myRegAddDialogDisplay = true
    }

    // MHR Found Dialog
    const myMHRegAddFoundSetDialog = (searchedRegNum: string, reg: MhRegistrationSummaryIF): void => {
      localState.myRegAddDialog = Object.assign({ ...mhRegistrationFoundDialog })
      // if the searched registration is a child of the base registration
      if (searchedRegNum !== reg.mhrNumber) {
        localState.myRegAddDialog.text = `The registration number you entered (<b>${searchedRegNum}</b>) ` +
          'is associated with the following MHR number. Would you like to add this MHR registration to ' +
          'your table? Adding the MHR registration to your table will automatically include all ' +
          'associated registrations.'
      }
      localState.myRegAddDialog.textExtra = [
        '<b>MHR Number:</b> ',
        '<b>MH Registration Date:</b> ',
        '<b>Registration Type:</b> ',
        '<b>Submitting Party:</b> '
      ]
      localState.myRegAddDialog.textExtra[0] += reg.mhrNumber
      if (reg.createDateTime) {
        const createDate = new Date(reg.createDateTime)
        localState.myRegAddDialog.textExtra[1] += convertDate(createDate, false, false)
      } else {
        localState.myRegAddDialog.textExtra[1] += 'N/A'
      }
      localState.myRegAddDialog.textExtra[2] +=
        reg.registrationDescription?.length > 0 ? reg.registrationDescription : 'N/A'
      localState.myRegAddDialog.textExtra[3] += reg.submittingParty
      localState.myRegAddDialogDisplay = true
    }

    const myRegAddErrSetDialog = (error: ErrorIF): void => {
      localState.myRegAddDialogError = error.statusCode
      const regNum = localState.myRegAdd?.trim()?.toUpperCase()
      switch (error.statusCode) {
        case StatusCodes.NOT_FOUND:
          localState.myRegAddDialog = { ...registrationNotFoundDialog }
          localState.myRegAddDialog.text = 'An existing registration with the ' +
            `registration number <b>${regNum}</b> was not found. Please ` +
            'check the registration number and try again.'
          break
        case StatusCodes.FORBIDDEN || StatusCodes.UNAUTHORIZED:
          localState.myRegAddDialog = { ...registrationRestrictedDialog }
          localState.myRegAddDialog.text = 'An existing registration was found with ' +
            `the registration number <b>${regNum}</b> but access is ` +
            'restricted and it is not available to add to your registrations ' +
            'table. Please contact us if you require assistance.'
          break
        case StatusCodes.CONFLICT:
          localState.myRegAddDialog = { ...registrationAlreadyAddedDialog }
          localState.myRegAddDialog.text = 'The registration with the registration number ' +
            `<b>${regNum}</b> is already in your registrations table.`
          break
        default:
          localState.myRegAddDialog = { ...registrationAddErrorDialog }
      }
      localState.myRegAddDialogDisplay = true
    }

    const myRegAddDialogProceed = (val: boolean): void => {
      // add registration or not
      if (val && !localState.myRegAddDialogError &&
        (localState.myRegAddDialog.title === 'Registration Found')) {
        props.isMhr ? addMHRegistration(localState.myRegAdd) : addRegistration(localState.myRegAdd)
      }
      // reset values
      if (localState.myRegAddDialogError !== StatusCodes.NOT_FOUND) {
        localState.myRegAdd = ''
      }
      localState.myRegAddDialogError = null
      localState.myRegAddDialogDisplay = false
      localState.hideSuccessDialog = true
    }

    // Add PPR summary to registration table
    const addRegistration = async (regNum: string): Promise<void> => {
      localState.loading = true
      const addReg = await addRegistrationSummary(regNum)
      if (addReg.error) {
        myRegAddErrSetDialog(addReg.error)
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
        setRegTableNewItem(newRegItem)
      }
      localState.loading = false
    }

    // Add MHR summary to registration table
    const addMHRegistration = async (regNum: string): Promise<void> => {
      localState.loading = true
      const addReg = await addMHRegistrationSummary(regNum)
      if (addReg.error) {
        myRegAddErrSetDialog(addReg.error)
      } else {
        let parentRegNum = ''
        if (regNum.toUpperCase() !== addReg.mhrNumber.toUpperCase()) {
          // not a base registration so add parent reg num
          parentRegNum = addReg.mhrNumber.toUpperCase()
        }

        const newRegItem: RegTableNewItemI = {
          addedReg: regNum,
          addedRegParent: parentRegNum,
          addedRegSummary: addReg,
          prevDraft: ''
        }
        setRegTableNewItem(newRegItem)
        await fetchMhRegistrations()
      }
      localState.loading = false
    }

    const myRegActionHandler = ({ action, docId, regNum, mhrInfo }): void => {
      localState.myRegAction = action as TableActions
      localState.myRegActionDocId = docId as string
      localState.myRegActionRegNum = regNum as string
      switch (action) {
        case TableActions.AMEND:
          localState.myRegActionRoute = RouteNames.AMEND_REGISTRATION
          localState.myRegActionDialog = amendConfirmationDialog
          localState.myRegActionDialogDisplay = true
          break
        case TableActions.DISCHARGE:
          localState.myRegActionRoute = RouteNames.REVIEW_DISCHARGE
          localState.myRegActionDialog = dischargeConfirmationDialog
          localState.myRegActionDialogDisplay = true
          break
        case TableActions.RENEW:
          localState.myRegActionRoute = RouteNames.RENEW_REGISTRATION
          localState.myRegActionDialog = renewConfirmationDialog
          localState.myRegActionDialogDisplay = true
          break
        case TableActions.DELETE:
          localState.myRegDeleteDialog = tableDeleteDialog
          localState.myRegDeleteDialogDisplay = true
          break
        case TableActions.REMOVE:
          localState.myRegDeleteDialog = props.isMhr ? mhrTableRemoveDialog : tableRemoveDialog
          localState.myRegDeleteDialogDisplay = true
          break
        case TableActions.EDIT_AMEND:
          editDraftAmend(docId, regNum)
          break
        case TableActions.EDIT_NEW:
          editDraftNew(docId)
          break
        case TableActions.EDIT_NEW_MHR:
          openMhrDraft(mhrInfo)
          break
        case TableActions.OPEN_MHR:
          openMhr(mhrInfo)
          break
        case UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER:
        case UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION:
          openMhrExemption(mhrInfo, action)
          break
        default:
          localState.myRegAction = null
          localState.myRegActionDocId = ''
          localState.myRegActionRegNum = ''
          console.error('Action not implemented.')
      }
    }

    const editDraftAmend = (docId: string, regNum: string): void => {
      resetNewRegistration(null) // Clear store data from the previous registration.
      // Go to the Amendment first step which loads the base registration and draft data.
      setRegTableCollapsed(null)
      router.replace({
        name: RouteNames.AMEND_REGISTRATION,
        query: { 'reg-num': regNum, 'document-id': docId }
      })
      context.emit('haveData', false)
    }

    const editDraftNew = async (documentId: string): Promise<void> => {
      resetNewRegistration(null) // Clear store data from the previous registration.
      // Get draft details and setup store for editing the draft financing statement.
      const stateModel: StateModelIF = await setupFinancingStatementDraft(getStateModel.value, documentId)
      if (stateModel.registration.draft.error) {
        emitError(stateModel.registration.draft.error)
      } else {
        setLengthTrust(stateModel.registration.lengthTrust)
        setAddCollateral(stateModel.registration.collateral)
        setAddSecuredPartiesAndDebtors(stateModel.registration.parties)
        // reset unsaved changes
        setUnsavedChanges(false)
        // Go to the first step.
        setRegTableCollapsed(null)
        await router.replace({ name: RouteNames.LENGTH_TRUST })
      }
    }

    const openMhrDraft = async (mhrInfo: MhrDraftIF): Promise<void> => {
      await startNewRegistration(MhrRegistrationType, mhrInfo.draftNumber)
    }

    const openMhr = async (mhrSummary: MhRegistrationSummaryIF): Promise<void> => {
      setMhrInformation(mhrSummary)
      await router.replace({ name: RouteNames.MHR_INFORMATION })
    }

    const openMhrExemption = async (mhrSummary: MhRegistrationSummaryIF, type: UnitNoteDocTypes): Promise<void> => {
      await setMhrInformation(mhrSummary)
      await goToExemptions(type)
    }

    const removeMhrDraft = async (mhrNumber: string): Promise<void> => {
      localState.myRegDataLoading = true
      await deleteMhrDraft(mhrNumber)
      await fetchMhRegistrations() // Refresh the table with update Registration History
      localState.myRegDataLoading = false
    }

    const myRegActionDialogHandler = (proceed: boolean): void => {
      // handles the response from the confirmation dialog in the amend/renew/discharge flow
      if (proceed) {
        startNewChildDraft(localState.myRegActionRegNum, localState.myRegActionRoute)
      }
      localState.myRegAction = null
      localState.myRegActionRegNum = ''
      localState.myRegActionDialogDisplay = false
    }

    const startNewChildDraft = (regNum: string, routeName: RouteNames): void => {
      setRegTableCollapsed(null)
      router.replace({
        name: routeName,
        query: { 'reg-num': regNum }
      })
      context.emit('haveData', false)
    }

    const myRegDeleteDialogProceed = (val: boolean): void => {
      if (val) {
        if (localState.myRegAction === TableActions.DELETE) {
          props.isPpr
            ? removeDraft(localState.myRegActionRegNum, localState.myRegActionDocId)
            : removeMhrDraft(localState.myRegActionRegNum)
        }
        if (localState.myRegAction === TableActions.REMOVE) {
          props.isPpr
            ? removeRegistration(localState.myRegActionRegNum)
            : removeMhRegistration(localState.myRegActionRegNum)
        }
      }
      localState.myRegAction = null
      localState.myRegActionDocId = ''
      localState.myRegActionRegNum = ''
      localState.myRegDeleteDialogDisplay = false
    }

    const myRegGetNext = async (): Promise<void> => {
      if (localState.myRegDataLoading || !hasMorePages.value) return
      localState.myRegDataLoading = true
      const page = getRegTableSortPage.value + 1
      setRegTableSortPage(page)
      const nextRegs = await registrationHistory(cloneDeep(getRegTableSortOptions.value), page)
      if (nextRegs.error) {
        emitError(nextRegs.error)
      } else {
        // add child drafts to new regs if applicable
        const updatedRegs = myRegHistoryDraftCollapse(
            cloneDeep(getRegTableDraftsChildReg.value), cloneDeep(nextRegs.registrations), true)
        const newBaseRegs = getRegTableBaseRegs.value.concat(updatedRegs.registrations)
        setRegTableBaseRegs(newBaseRegs)
      }
      if (nextRegs.registrations?.length < 1) setRegTableSortHasMorePages(false)
      localState.myRegDataLoading = false
    }

    const removeDraft = async (regNum: string, docId: string): Promise<void> => {
      localState.loading = true
      const deletion = await deleteDraft(docId)
      if (deletion.statusCode !== StatusCodes.NO_CONTENT) {
        emitError(deletion)
      } else {
        // remove from table
        setRegTableDraftsBaseReg(getRegTableDraftsBaseReg.value.filter(reg => reg.documentId !== docId))
        setRegTableDraftsChildReg(getRegTableDraftsChildReg.value.filter(reg => reg.documentId !== docId))
        if (!regNum) {
          // is not a child
          setRegTableTotalRowCount(getRegTableTotalRowCount.value - 1)
        } else {
          // is a child of another base registration
          const baseRegs = getRegTableBaseRegs.value
          // find parent base registration and filter draft out of changes array
          const parentIndex = baseRegs.findIndex(reg => reg.baseRegistrationNumber === regNum)
          const changes = baseRegs[parentIndex].changes as any
          baseRegs[parentIndex].changes = changes.filter(reg => reg.documentId !== docId)
          if (baseRegs[parentIndex].changes.length === 0) {
            // no longer a parent reg so remove irrelevant fields
            delete baseRegs[parentIndex].changes
            delete baseRegs[parentIndex].expand
          }
          setRegTableBaseRegs(baseRegs)
        }
      }
      localState.loading = false
    }

    const removeRegistration = async (regNum: string): Promise<void> => {
      localState.loading = true
      const removal = await deleteRegistrationSummary(regNum)
      if (removal.statusCode !== StatusCodes.NO_CONTENT) {
        emitError(removal)
      } else {
        // remove from table
        setRegTableBaseRegs(getRegTableBaseRegs.value.filter(reg => reg.baseRegistrationNumber !== regNum))
        setRegTableTotalRowCount(getRegTableTotalRowCount.value - 1)
      }
      localState.loading = false
    }

    const removeMhRegistration = async (mhrNum: string): Promise<void> => {
      localState.loading = true
      const removal = await deleteMhRegistrationSummary(mhrNum)
      if (removal.statusCode !== StatusCodes.NO_CONTENT) {
        emitError(removal)
      } else {
        // remove from table
        setMhrTableHistory(getMhRegTableBaseRegs.value.filter(reg => reg.mhrNumber !== mhrNum))
      }
      localState.loading = false
    }

    const myRegHistoryDraftCollapse = (
      drafts: DraftResultIF[],
      registrations: RegistrationSummaryIF[],
      sorting: boolean
    ): { drafts: DraftResultIF[], registrations: RegistrationSummaryIF[] } => {
      // add child drafts to their base registration in registration history
      const parentDrafts = [] as DraftResultIF[]
      let childDrafts = getRegTableDraftsChildReg.value
      // reset child drafts if not sorting
      if (!sorting) childDrafts = []
      for (let i = 0; i < drafts?.length; i++) {
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
      setRegTableDraftsChildReg(childDrafts)
      return {
        drafts: parentDrafts,
        registrations
      }
    }

    const myRegSort = async (args: { sortOptions: RegistrationSortIF, sorting: boolean }): Promise<void> => {
      localState.myRegDataLoading = true
      setRegTableSortOptions(args.sortOptions)

      const sorting = args.sorting
      let sortedDrafts = { drafts: [] as DraftResultIF[], error: null }
      if (props.isPpr) {
        // Filtering Ppr Registrations
        // all drafts return from the api no matter the status value so prevent it here
        if (!args.sortOptions.status || args.sortOptions.status === APIStatusTypes.DRAFT) {
          sortedDrafts = await draftHistory(cloneDeep(args.sortOptions))
        }
        // Destructure to omit orderBy and orderVal from condition
        const { ...sortvalues } = args.sortOptions
        const sortedRegs = hasTruthyValue(sortvalues)
          ? await registrationHistory(cloneDeep(args.sortOptions))
          : await registrationHistory()

        // prioritize reg history error
        const error = sortedRegs.error || sortedDrafts.error
        if (error) {
          emitError(error)
        } else {
          if (sortedRegs.registrations?.length < 1) setRegTableSortHasMorePages(false)
          // parent drafts from sorted list
          const draftsCollapsed = myRegHistoryDraftCollapse(
            cloneDeep(sortedDrafts.drafts), cloneDeep(sortedRegs.registrations), sorting)
          // add child drafts from original list to sorted base registrations
          const updatedRegs = myRegHistoryDraftCollapse(
            cloneDeep(getRegTableDraftsChildReg.value), cloneDeep(sortedRegs.registrations), sorting)
          // only add parent drafts to draft results
          setRegTableDraftsBaseReg(draftsCollapsed.drafts)
          setRegTableBaseRegs(updatedRegs.registrations)
        }
      } else if (props.isMhr) {
        await fetchMhRegistrations(cloneDeep(args.sortOptions))
      }
      localState.myRegDataLoading = false
    }

    const handleRegTableNewItem = async (val: RegTableNewItemI) => {
      if (val.addedReg) {
        localState.myRegDataAdding = true

        // PPR Handling
        if (props.isPpr) {
          if (!val.addedRegSummary) {
            // attempt to get the summary info from the api
            if (val.addedReg[0] !== 'D') {
              // its a normal reg - get reg summary
              const regSummary = await getRegistrationSummary(val.addedReg, true)
              if (regSummary.error) {
                emitError(regSummary.error) // dialog and will reload the dash after
                localState.myRegDataAdding = false
                return
              }
              val.addedRegSummary = regSummary
            } else {
              // its a draft - get draft summary
              const drafts = await draftHistory(null)
              if (drafts.error) {
                emitError(drafts.error) // dialog and will reload the dash after
                localState.myRegDataAdding = false
                return
              } else {
                val.addedRegSummary = drafts.drafts.find(d => d.documentId === val.addedReg)
                if (!val.addedRegSummary) {
                  emitError({
                    category: ErrorCategories.HISTORY_REGISTRATIONS,
                    statusCode: StatusCodes.NOT_FOUND,
                    message: 'Error finding new draft summary.'
                  })
                  localState.myRegDataAdding = false
                  return
                }
              }
            }
          }

          const baseRegs = getRegTableBaseRegs.value
          if (val.prevDraft) {
            // remove previous draft item from the store (child drafts also exist under parent - removed later)
            setRegTableDraftsBaseReg(getRegTableDraftsBaseReg.value.filter(reg => reg.documentId !== val.prevDraft))
            setRegTableDraftsChildReg(getRegTableDraftsChildReg.value.filter(reg => reg.documentId !== val.prevDraft))
          }
          // for masking the type of the new summary
          const newDraftSummary = val.addedRegSummary as DraftResultIF
          const newRegSummary = val.addedRegSummary as RegistrationSummaryIF
          if (val.addedRegParent && props.isPpr) {
            // new child reg. Find parent + update it with new summary
            const parentIndex = baseRegs.findIndex(reg => reg.baseRegistrationNumber === val.addedRegParent)
            if (parentIndex === -1) {
              // reg was a child of a new base reg so we are adding the full base reg
              newRegSummary.expand = true
              baseRegs.unshift({ ...newRegSummary, expand: false })
              setRegTableBaseRegs([...baseRegs])
              setRegTableTotalRowCount(getRegTableTotalRowCount.value + 1)
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
              setRegTableBaseRegs(cloneDeep(baseRegs))
            }
          } else if (newDraftSummary?.documentId) {
            // new draft base reg
            const draftBaseRegs = getRegTableDraftsBaseReg.value
            draftBaseRegs.unshift(newDraftSummary)
            setRegTableDraftsBaseReg(draftBaseRegs)
            if (!val.prevDraft) {
              // new draft so increase
              setRegTableTotalRowCount(getRegTableTotalRowCount.value + 1)
            }
          } else {
            // Safety check: Prevent duplicate Registrations in UI
            if (baseRegs.some(reg => reg.registrationNumber === newRegSummary.registrationNumber)) return

            // new base reg
            baseRegs.unshift({ ...newRegSummary, expand: false })
            setRegTableBaseRegs([...baseRegs])
            if (!val.prevDraft) {
              // not from a draft so increase
              setRegTableTotalRowCount(getRegTableTotalRowCount.value + 1)
            }
          }
        }

        localState.myRegDataAdding = false

        // check if success registration dialog for Manufacturers is permanently hidden (via user settings)
        localState.manufacturerRegSuccessDialogDisplay =
          !localState.dialogPermanentlyHidden && !isRoleStaffReg.value && !localState.hideSuccessDialog && props.isMhr

        // trigger snackbar
        context.emit('snackBarMsg', 'Registration was successfully added to your table.')
        // set to empty strings after 6 seconds
        setTimeout(() => {
          // only reset if it hasn't changed since
          if (val.addedReg === getRegTableNewItem.value.addedReg) {
            const emptyItem: RegTableNewItemI = {
              addedReg: '', addedRegParent: '', addedRegSummary: null, prevDraft: ''
            }
            setRegTableNewItem(emptyItem)
          }
        }, 6000)
      }
    }

    const updateMyRegHeaders = async (val: BaseHeaderIF[]): Promise<void> => {
      const headers = []
      const baseHeaders = props.isPpr ? registrationTableHeaders : mhRegistrationTableHeaders
      const columnSettings = props.isPpr
        ? { columns: val, mhrColumns: localState.mhrColumnSettings }
        : { columns: localState.pprColumnSettings, mhrColumns: val }

      for (let i = 0; i < baseHeaders.length; i++) {
        if (baseHeaders[i].value === 'actions') headers.push(baseHeaders[i])
        else if (val.find(header => header.value === baseHeaders[i].value)) {
          headers.push(baseHeaders[i])
        }
      }
      localState.myRegHeaders = headers
      // update settings
      let settings: UserSettingsIF = await updateUserSettings(
        SettingOptions.REGISTRATION_TABLE,
        columnSettings
      )
      if (settings?.error) {
        // FUTURE: notify failure to save? - just log and continue for now
        console.error('Failed to save selected columns to user settings.')
        // save new settings to session (they won't be included in an error response)
        settings = getUserSettings.value
        settings[SettingOptions.REGISTRATION_TABLE] = columnSettings
      }
      setUserSettings(settings)
    }

    /** Returns True when the header is selected */
    const isActiveHeader = (headerType: string): boolean => {
      return localState.myRegHeadersSelected.some(header => header.value === headerType)
    }

    const emitError = (error): void => {
      context.emit('error', error)
    }

    watch(() => getRegTableNewItem.value, (val: RegTableNewItemI) => {
      handleRegTableNewItem(val)
    })

    watch(() => localState.myRegHeadersSelected, (val: BaseHeaderIF[]) => {
      updateMyRegHeaders(val)
    })

    return {
      isActiveHeader,
      myRegGetNext,
      addRegistration,
      emitError,
      findRegistration,
      getRegTableNewItem,
      getRegTableTotalRowCount,
      getRegTableSortOptions,
      getMhRegTableBaseRegs,
      hasMorePages,
      myRegSort,
      myRegActionHandler,
      myRegActionDialogHandler,
      myRegDeleteDialogProceed,
      myRegAddFoundSetDialog,
      myRegAddErrSetDialog,
      myRegAddDialogProceed,
      startNewRegistration,
      tooltipTxtRegSrch,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.reg-input {
  :deep(.v-field) {
    background-color: white;

    .v-field-label {
      font-size: .875rem;
    }
  }
}

.validation-msg {
  color: $error;
  font-size: 0.75rem;
  position: absolute;
}

.table-border {
  border: 1px solid $gray3
}

.column-selection-item {
  height: 15px;
  padding: 0!important;
}
</style>
