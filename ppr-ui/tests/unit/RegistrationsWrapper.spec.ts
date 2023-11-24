// Libraries
import { nextTick } from 'vue'
import { RegistrationsWrapper } from '@/components/common'
import { RegistrationTable } from '@/components/tables'
import { SettingOptions, TableActions } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
import {
  registrationFoundDialog,
  tableDeleteDialog,
  tableRemoveDialog
} from '@/resources/dialogOptions'
import {
  mockedRegistration1,
  mockedDraft1,
  mockedDraftAmend,
  mockedRegistration2,
} from './test-data'
import { createComponent } from './utils'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'

const store = useStore()

// Events
const selectedType = 'selected-registration-type'

// selectors
const searchHeader = '#search-header'
const historyHeader = '#search-history-header'
const myRegAddDialog = '#myRegAddDialog'
const myRegDeleteDialog = '#myRegDeleteDialog'
const myRegHeader = '#registration-header'
const myRegAddTextBox = '#my-reg-add'
const myRegTblColSelection = '#column-selection'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Ppr registration table tests', () => {
  let wrapper

  const myRegDrafts: DraftResultIF[] = [{ ...mockedDraft1 }, { ...mockedDraftAmend }]
  const myRegHistory: RegistrationSummaryIF[] = [{ ...mockedRegistration1 }]
  const parentDrafts: DraftResultIF[] = [{ ...mockedDraft1 }]
  // setup baseReg with added child draft
  const baseReg = { ...mockedRegistration1 }
  baseReg.changes = [{ ...mockedDraftAmend }]
  baseReg.expand = false
  const myRegHistoryWithChildren = [baseReg]
  const newColumnSelection = [...registrationTableHeaders].slice(3)

  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    // set base selected columns
    await store.setUserInfo(
      { settings: { [SettingOptions.REGISTRATION_TABLE]: { columns: registrationTableHeaders } } }
    )
    wrapper = await createComponent(RegistrationsWrapper, { appReady: true, isPpr: true })
    await store.setRegTableDraftsBaseReg(parentDrafts)
    await store.setRegTableBaseRegs(myRegHistoryWithChildren)
    await flushPromises()
    await nextTick()
  })

  it('displays my registration header and content', async () => {
    expect(wrapper.findComponent(RegistrationsWrapper).exists()).toBe(true)
    // myRegDrafts contains a child that will be put into a baseReg
    expect(store.getRegTableDraftsBaseReg).toStrictEqual(parentDrafts)
    expect(store.getRegTableBaseRegs).toStrictEqual(myRegHistoryWithChildren)
    const header = await wrapper.findAll(myRegHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain(
      `Personal Property Registrations (${parentDrafts.length + myRegHistoryWithChildren.length})`
    )
    // expect(wrapper.find(myRegTblFilter).exists()).toBe(true)
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryWithChildren])
  })

  it('updates the registration table with new headers', async () => {
    // ensure original is based off settings patch stub
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(registrationTableHeaders)
    // update dashboard headers variable directly
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    wrapper.vm.myRegHeaders = newColumnSelection
    await flushPromises()
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(newColumnSelection)
  })

  it('updates the registration table with new headers from column selection', async () => {
    // ensure original selection is based off settings patch stub
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(registrationTableHeaders)
    // update column selection
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)

    wrapper.vm.myRegHeadersSelected = newColumnSelection
    await flushPromises()
    await nextTick()

    // verify dashboard values updated
    expect(wrapper.vm.myRegHeadersSelected).toEqual(newColumnSelection)
    expect(wrapper.vm.myRegHeaders).toEqual(newColumnSelection)

    await store.setUserInfo(
      { settings: { [SettingOptions.REGISTRATION_TABLE]: { columns: newColumnSelection } } }
    )
    await nextTick()
    // // verify store updated with patch response
    expect(store.getStateModel.userInfo.settings[SettingOptions.REGISTRATION_TABLE].columns)
      .toEqual(newColumnSelection)
    // verify table props updated
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(newColumnSelection)
  })

  it('deletes parent drafts', async () => {
    const myRegDraftsCopy = [...parentDrafts]
    // check setup
    expect(store.getRegTableDraftsBaseReg).toEqual(myRegDraftsCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...myRegDraftsCopy, ...myRegHistoryWithChildren])
    // emit delete action
    wrapper.findComponent(RegistrationTable).vm.$emit(
      'action', { action: TableActions.DELETE, docId: myRegDraftsCopy[0].documentId }
    )
    await flushPromises()
    // dialog shows
    const myRegDeleteDialogComponent = await wrapper.find(myRegDeleteDialog)
    expect(myRegDeleteDialogComponent.exists()).toBe(true)
    expect(wrapper.vm.myRegDeleteDialogDisplay).toBe(true)
    expect(wrapper.vm.myRegDeleteDialog).toEqual(tableDeleteDialog)

    // emit proceed with delete
    wrapper.vm.myRegDeleteDialogProceed(true)
    await flushPromises()
    await nextTick()

    expect(store.getRegTableDraftsBaseReg).toEqual(myRegDraftsCopy)

    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...myRegDraftsCopy, ...myRegHistoryWithChildren])
  })

  it('deletes child drafts', async () => {
    const myRegDraftsCopy = myRegHistoryWithChildren[0].changes[0] as DraftResultIF
    // check setup
    expect(store.getRegTableDraftsBaseReg).toEqual(parentDrafts)
    expect(store.getRegTableBaseRegs).toEqual(myRegHistoryWithChildren)
    expect(store.getRegTableBaseRegs[0].changes[0]).toEqual(myRegDraftsCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryWithChildren])
    // emit delete action
    wrapper.findComponent(RegistrationTable).vm.$emit(
      'action',
      {
        action: TableActions.DELETE,
        docId: myRegDraftsCopy.documentId,
        regNum: myRegDraftsCopy.baseRegistrationNumber
      }
    )
    await flushPromises()
    await nextTick()
    // dialog shows
    const myRegDeleteDialogComponent = await wrapper.find(myRegDeleteDialog)
    expect(myRegDeleteDialogComponent.exists()).toBe(true)
    expect(wrapper.vm.myRegDeleteDialogDisplay).toBe(true)
    expect(wrapper.vm.myRegDeleteDialog).toEqual(tableDeleteDialog)

    // emit proceed with delete
    wrapper.vm.myRegDeleteDialogProceed(true)
    await flushPromises()
    await nextTick()

    // draft is removed from table
    expect(wrapper.vm.myRegistrations).toEqual([...parentDrafts, ...myRegHistoryWithChildren])
  })

  it('removes complete registrations', async () => {
    const myRegHistoryCopy = [...myRegHistoryWithChildren]
    // check setup
    expect(store.getRegTableBaseRegs).toEqual(myRegHistoryCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryCopy])

    // emit delete action
    wrapper.findComponent(RegistrationTable).vm.$emit(
      'action', { action: TableActions.REMOVE, regNum: myRegHistoryCopy[0].baseRegistrationNumber }
    )
    await flushPromises()
    await nextTick()

    const myRegDeleteDialogComponent = await wrapper.find(myRegDeleteDialog)
    expect(myRegDeleteDialogComponent.exists()).toBe(true)
    expect(wrapper.vm.myRegDeleteDialogDisplay).toBe(true)
    expect(wrapper.vm.myRegDeleteDialog).toEqual(tableRemoveDialog)
    await flushPromises()

    // emit proceed with delete
    wrapper.vm.myRegDeleteDialogProceed(true)
    await flushPromises()

    expect(store.getRegTableBaseRegs).toEqual(myRegHistoryCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryCopy])
  })
})

describe('Dashboard add registration tests', () => {
  let wrapper
  const myRegAdd: RegistrationSummaryIF = { ...mockedRegistration1, expand: false }
  const mockAddDialogContent = { ...registrationFoundDialog,
    textExtra:
      [
      "<b>Base Registration Number:</b> GOV2343",
      "<b>Base Registration Date:</b> July 20, 2021",
      "<b>Registration Type:</b> Security Agreement",
      "<b>Registering Party:</b> John Doe"
      ]
  }

  beforeEach(async () => {
    wrapper = await createComponent(RegistrationsWrapper, { appReady: true, isPpr: true })
    await store.setRegTableBaseRegs([mockedRegistration2])
    await flushPromises()
  })

  it('displays the add registration text box + shows dialog + adds it to table', async () => {
    // FUTURE: add all cases (i.e. simulate error flows etc.)
    expect(wrapper.find(myRegAddTextBox).exists()).toBe(true)
    expect(wrapper.vm.myRegAdd).toBe('')
    await wrapper.find(myRegAddTextBox).setValue('123')
    expect(wrapper.vm.myRegAdd).toBe('123')
    expect(wrapper.vm.myRegAddInvalid).toBe(true)
    // set to lowercase to test it gets uppercase reg num
    const regAdd = await wrapper.find(myRegAddTextBox)
    regAdd.setValue(myRegAdd.baseRegistrationNumber.toLowerCase())
    expect(wrapper.vm.myRegAddInvalid).toBe(false)
    // simulate add
    await wrapper.vm.findRegistration(myRegAdd.baseRegistrationNumber.toLowerCase())
    await flushPromises()
    await nextTick()
    expect(wrapper.vm.myRegAddDialogDisplay).toBe(true)
    expect(wrapper.vm.loading).toBe(false)

    const myRegAddDialogComponent = await wrapper.find(myRegAddDialog)
    expect(myRegAddDialogComponent.exists()).toBe(true)
    expect(wrapper.vm.myRegAddDialogDisplay).toBe(true)

    await wrapper.vm.myRegAddFoundSetDialog(myRegAdd.baseRegistrationNumber.toLowerCase(), myRegAdd)
    await nextTick()

    expect(wrapper.vm.myRegAddDialog).toEqual(mockAddDialogContent)
    wrapper.vm.myRegAdd = myRegAdd.baseRegistrationNumber.toLowerCase()
    await nextTick()
    await wrapper.vm.myRegAddDialogProceed(true)
    await nextTick()
    expect(store.getRegTableBaseRegs).toEqual([mockedRegistration2])
    await flushPromises()
    await store.setRegTableBaseRegs([myRegAdd, mockedRegistration2])
    await flushPromises()

    expect(store.getRegTableBaseRegs).toEqual([myRegAdd, mockedRegistration2])
    expect(wrapper.vm.myRegAddDialogDisplay).toBe(false)
    expect(wrapper.vm.myRegAdd).toBe('')
  })
})
