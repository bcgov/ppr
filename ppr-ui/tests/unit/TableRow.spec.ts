// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { createLocalVue, mount, Wrapper, WrapperArray } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// local components
import { TableRow } from '@/components/tables/common'
// local types/helpers/etc.
import { APIStatusTypes, TableActions } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
// unit test data/helpers
import {
  mockedRegistration1,
  mockedDraft1,
  mockedDraftAmend,
  mockedRegistration3,
  mockedRegistration1Collapsed,
  mockedRegistration2Collapsed,
  mockedRegistration2Child
} from './test-data'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const btnExpArr = '.btn-row-expand-arr'
const btnExpTxt = '.btn-row-expand-txt'
const tableRow = '.registration-row'
const tableRowBaseReg = '.base-registration-row'
const tableRowDraft = '.draft-registration-row'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (item: DraftResultIF | RegistrationSummaryIF): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(TableRow, {
    localVue,
    store,
    propsData: {
      setChild: false,
      setHeaders: [...registrationTableHeaders],
      setIsExpanded: false,
      setItem: item
    },
    vuetify
  })
}

describe('TableRow tests', () => {
  let wrapper: Wrapper<any>
  const registrationHistory: (RegistrationSummaryIF | DraftResultIF)[] = [
    mockedDraft1,
    mockedRegistration1Collapsed,
    mockedDraftAmend,
    mockedRegistration2Collapsed,
    mockedRegistration2Child,
    mockedRegistration3
  ]

  beforeEach(async () => {
    wrapper = createComponent(mockedRegistration1)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the row', async () => {
    expect(wrapper.findComponent(TableRow).exists()).toBe(true)
    expect(wrapper.vm.item).toEqual(mockedRegistration1)
    expect(wrapper.findAll(tableRow).length).toBe(1)
    expect(wrapper.findAll(tableRowBaseReg).length).toBe(1)
  })

  it('updates shown row cells when given new one headers', async () => {
    expect(wrapper.vm.$props.setHeaders).toEqual(registrationTableHeaders)
    expect(wrapper.findAll('td').length).toEqual(registrationTableHeaders.length)
    const newHeaders = [
      registrationTableHeaders[1],
      registrationTableHeaders[3],
      registrationTableHeaders[6],
      registrationTableHeaders[10]
    ]
    await wrapper.setProps({ setHeaders: newHeaders })
    expect(wrapper.vm.$props.setHeaders).toEqual(newHeaders)
    await flushPromises()
    const rowCells = wrapper.findAll('td')
    expect(rowCells.length).toBe(newHeaders.length)
  })

  it('displays properly in the row for all types of items', async () => {
    for (let i = 0; i < registrationHistory.length; i++) {
      // both below are the same variable, but typed differently
      const baseReg = registrationHistory[i] as RegistrationSummaryIF
      const draftReg = registrationHistory[i] as DraftResultIF

      const isChild = (draftReg.type && draftReg.baseRegistrationNumber) ||
        (baseReg.registrationNumber && baseReg.registrationNumber !== baseReg.baseRegistrationNumber)
      await wrapper.setProps({
        setChild: isChild,
        setItem: baseReg
      })
      expect(wrapper.vm.isChild).toBe(isChild)
      expect(wrapper.vm.item).toEqual(baseReg)

      // check things specific to state / heirarchy of the item
      if (!draftReg.type) {
        // not a draft
        let rowData: WrapperArray<Vue>
        if (!isChild) {
          // parent registration
          rowData = wrapper.findAll(tableRowBaseReg + ' td')
          expect(rowData.exists()).toBe(true)
          expect(rowData.length).toBe(11)
          // reg num
          if (baseReg.changes) {
            expect(rowData.at(0).find(btnExpArr).exists()).toBe(true)
          } else {
            expect(rowData.at(0).find(btnExpArr).exists()).toBe(false)
          }
          // base reg num
          expect(rowData.at(0).text()).not.toContain('Base Registration:')
          expect(rowData.at(0).text()).toContain(baseReg.baseRegistrationNumber)
          // reg type
          expect(rowData.at(1).text()).toContain('- Base Registration')
          if (baseReg.changes) {
            expect(rowData.at(1).find(btnExpTxt).exists()).toBe(true)
            expect(rowData.at(1).find(btnExpTxt).text()).toContain('View')
          } else {
            expect(rowData.at(1).find(btnExpTxt).exists()).toBe(false)
          }
          // status type
          expect(rowData.at(3).text()).toContain(wrapper.vm.getStatusDescription(baseReg.statusType))
          // expire days
          if ([APIStatusTypes.DISCHARGED, APIStatusTypes.EXPIRED].includes(baseReg.statusType as APIStatusTypes)) {
            expect(rowData.at(8).text()).toContain('—')
          } else {
            expect(rowData.at(8).text()).toContain(wrapper.vm.showExpireDays(baseReg))
          }
          // action btn
          if (![APIStatusTypes.DISCHARGED, APIStatusTypes.EXPIRED].includes(baseReg.statusType as APIStatusTypes)) {
            expect(rowData.at(10).text()).toContain('Amend')
          } else {
            expect(rowData.at(10).text()).toContain('RemoveFrom Table')
          }
        } else {
          // child registration
          rowData = wrapper.findAll(tableRow + ' td')
          expect(rowData.exists()).toBe(true)
          expect(rowData.length).toBe(11)
          // regNum
          expect(rowData.at(0).text()).toContain(baseReg.registrationNumber)
          expect(rowData.at(0).text()).toContain(`Base Registration: ${baseReg.baseRegistrationNumber}`)
          // reg type
          expect(rowData.at(1).text()).not.toContain('- Base Registration')
          expect(rowData.at(1).find(btnExpTxt).exists()).toBe(false)
          // status type
          expect(rowData.at(3).text()).toEqual('')
          // expiry days
          expect(rowData.at(8).text()).toEqual('')
          // action btn is not there
          expect(rowData.at(10).text()).toContain('')
        }
        // reg type
        expect(rowData.at(1).text()).toContain(wrapper.vm.getRegistrationType(baseReg.registrationType))
        // submitted date
        expect(rowData.at(2).text()).toContain(wrapper.vm.getFormattedDate(baseReg.createDateTime))
        // registering name
        expect(rowData.at(4).text()).toContain(baseReg.registeringName)
        // registering party
        expect(rowData.at(5).text()).toContain(baseReg.registeringParty)
        // secured party
        expect(rowData.at(6).text()).toContain(baseReg.securedParties)
        // pdf
        if (baseReg.path) expect(rowData.at(9).text()).toContain('PDF')
        else expect(rowData.at(9).find('.mdi-information-outline').exists()).toBe(true)
      } else {
        // draft registration
        let rowData: WrapperArray<Vue>
        if (!isChild) rowData = wrapper.findAll(tableRowDraft + ' td')
        else rowData = wrapper.findAll(tableRow + ' td')
        expect(rowData.exists()).toBe(true)
        expect(rowData.length).toBe(11)
        // reg num
        expect(rowData.at(0).text()).toBe('Pending')
        // submitted date
        expect(rowData.at(2).text()).toBe('Not Registered')
        // status type
        expect(rowData.at(3).text()).toContain(wrapper.vm.getStatusDescription(baseReg.statusType))
        // expire days
        if (isChild) expect(rowData.at(8).text()).toEqual('')
        else expect(rowData.at(8).text()).toBe('N/A')
        // pdf
        expect(rowData.at(9).text()).toEqual('')
        // action btn
        expect(rowData.at(10).text()).toContain('Edit')
      }
      // check things that apply to all items
      const rowData = wrapper.findAll(tableRow + ' td')
      expect(rowData.exists()).toBe(true)
      // folio
      expect(rowData.at(7).text()).toContain(baseReg.clientReferenceId)
    }
  })

  it('emits button actions from TableRow', async () => {
    expect(wrapper.vm.item).toEqual(mockedRegistration1)
    // main button: active reg
    const activeRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(activeRegButton.length).toBe(1)
    expect(activeRegButton.at(0).text()).toContain('Amend')
    activeRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.AMEND, regNum: mockedRegistration1.baseRegistrationNumber }
    )
    // dropdown buttons
    let buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(1)

    // click dropdown for active reg
    buttons.at(0).trigger('click')
    await Vue.nextTick()

    // it renders the actions drop down
    const menuItems = wrapper.findAll('.registration-actions .v-list-item')
    expect(menuItems.length).toBe(3)
    expect(menuItems.at(0).text()).toContain('Total Discharge')
    expect(menuItems.at(1).text()).toContain('Renew')
    expect(menuItems.at(2).text()).toContain('Remove From Table')

    // click items and check emit
    const actions = [TableActions.DISCHARGE, TableActions.RENEW, TableActions.REMOVE]
    for (let i = 0; i < actions.length; i++) {
      await menuItems.at(i).trigger('click')
      expect(getLastEvent(wrapper, 'action')).toEqual(
        { action: actions[i], regNum: mockedRegistration1.baseRegistrationNumber }
      )
    }

    // main buttons: discharged/expired
    expect(mockedRegistration3.statusType).toBe(APIStatusTypes.DISCHARGED)
    await wrapper.setProps({
      setChild: false,
      setItem: mockedRegistration3
    })
    const dischargedRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(dischargedRegButton.length).toBe(1)
    expect(dischargedRegButton.at(0).text()).toContain('RemoveFrom Table')
    // FUTURE: test it emits the correct thing here once built
    activeRegButton.at(0).trigger('click')

    // click dropdown for discharged reg
    buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(0)
    await dischargedRegButton.at(0).trigger('click')
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.REMOVE, regNum: mockedRegistration3.baseRegistrationNumber }
    )
  })

  it('emits button actions properly for draft registrations', async () => {
    // recreate wrapper with draft
    wrapper.destroy()
    wrapper = createComponent(mockedDraft1)
    await flushPromises()

    // main buttons: new
    const draftNewRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(draftNewRegButton.length).toBe(1)
    expect(draftNewRegButton.at(0).text()).toContain('Edit')
    draftNewRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.EDIT_NEW, docId: mockedDraft1.documentId }
    )

    // drop down buttons
    let dropButtons = wrapper.findAll('.actions__more-actions__btn')
    expect(dropButtons.length).toBe(1)
    dropButtons.at(0).trigger('click')
    await Vue.nextTick()
    // it renders the delete action in drop down
    let menuItems = wrapper.findAll('.registration-actions .v-list-item')
    expect(menuItems.length).toBe(1)
    expect(menuItems.at(0).text()).toContain('Delete Draft')
    await menuItems.at(0).trigger('click')
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.DELETE, docId: mockedDraft1.documentId, regNum: '' }
    )

    // main buttons: amend draft
    await wrapper.setProps({
      setChild: true,
      setItem: mockedDraftAmend
    })
    const draftAmendRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(draftAmendRegButton.length).toBe(1)
    expect(draftAmendRegButton.at(0).text()).toContain('Edit')
    draftAmendRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action'))
      .toEqual(
        {
          action: TableActions.EDIT_AMEND,
          docId: mockedDraftAmend.documentId,
          regNum: mockedDraftAmend.baseRegistrationNumber
        }
      )

    dropButtons = wrapper.findAll('.actions__more-actions__btn')
    expect(dropButtons.length).toBe(1)
    dropButtons.at(0).trigger('click')
    await Vue.nextTick()
    // it renders the delete action in drop down
    menuItems = wrapper.findAll('.registration-actions .v-list-item')
    expect(menuItems.length).toBe(1)
    expect(menuItems.at(0).text()).toContain('Delete Draft')
    await menuItems.at(0).trigger('click')
    expect(getLastEvent(wrapper, 'action')).toEqual(
      {
        action: TableActions.DELETE,
        docId: mockedDraftAmend.documentId,
        regNum: mockedDraftAmend.baseRegistrationNumber
      }
    )
  })
})
