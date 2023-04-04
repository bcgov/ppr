// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// local components
import { DatePicker } from '@/components/common'
import { RegistrationTable } from '@/components/tables'
import { TableRow } from '@/components/tables/common'
import { RegistrationBarTypeAheadList } from '@/components/registration'
// local types/helpers/etc.
import { AccountProductCodes, AccountProductMemberships, TableActions } from '@/enums'
import { DraftResultIF, MhRegistrationSummaryIF, RegistrationSummaryIF, RegTableNewItemI } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
// unit test data/helpers
import {
  mockedRegistration1,
  mockedDraft1,
  mockedDraft2,
  mockedDraftAmend,
  mockedRegistration3,
  mockedRegistration1Collapsed,
  mockedRegistration2Collapsed,
  mockMhrTransferDraft
} from './test-data'
import { getLastEvent, setupIntersectionObserverMock } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const regTable = '#registration-table'
const tableHeader = '.my-reg-header'
const tableFilter = '.my-reg-filter'
const tableRow = '.registration-row'
const dateFilter = '.date-filter'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationTable, {
    localVue,
    store,
    propsData: {
      setHeaders: [...registrationTableHeaders],
      setLoading: false,
      setNewRegData: { addedReg: '', addedRegParent: '' },
      setSearch: '',
      setRegistrationHistory: [],
      toggleSnackbar: false
    },
    vuetify
  })
}

describe('Test registration table with results', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  const registrationHistory: RegistrationSummaryIF[] = [mockedRegistration1]
  const newRegistrationHistory: (RegistrationSummaryIF | DraftResultIF)[] = [
    mockedDraft1,
    mockedDraft2,
    mockedRegistration1Collapsed,
    mockedRegistration2Collapsed,
    mockedRegistration3
  ]

  const mhrRegistrationHistoryTest: MhRegistrationSummaryIF[] = [
    mockMhrTransferDraft
  ]

  beforeEach(async () => {
    wrapper = createComponent()
    wrapper.setProps({ isPpr: true })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays with no registration history', async () => {
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // displays table
    expect(wrapper.findAll(regTable).length).toBe(1)
    // displays given headers
    expect(wrapper.vm.$props.setHeaders).toEqual(registrationTableHeaders)
    const headers = wrapper.findAll(tableHeader)
    expect(headers.length).toBe(registrationTableHeaders.length)
    for (let i = 0; i < headers.length; i++) {
      expect(headers.at(i).text()).toContain(registrationTableHeaders[i].text)
    }
    // displays table filters. FUTURE: add more to filter tests
    const filters = wrapper.findAll(tableFilter)
    expect(filters.length).toBe(headers.length)

    expect(wrapper.vm.$props.setRegistrationHistory).toEqual([])
    expect(wrapper.findComponent(TableRow).exists()).toBe(false)
    const rows = wrapper.findAll(tableRow)
    expect(rows.length).toBe(0)

    // no data text
    expect(wrapper.findAll(regTable).at(0).text()).toContain('No registrations to show.')
  })

  it('updates table headers when given new ones', async () => {
    expect(wrapper.vm.$props.setHeaders).toEqual(registrationTableHeaders)
    const newHeaders = [registrationTableHeaders[1], registrationTableHeaders[3], registrationTableHeaders[6]]
    await wrapper.setProps({ setHeaders: newHeaders })
    expect(wrapper.vm.$props.setHeaders).toEqual(newHeaders)
    await flushPromises()
    const headers = wrapper.findAll(tableHeader)
    expect(headers.length).toBe(newHeaders.length)
    for (let i = 0; i < headers.length; i++) {
      expect(headers.at(i).text()).toContain(newHeaders[i].text)
    }
    // verify table filters also updated to new length
    const filters = wrapper.findAll(tableFilter)
    expect(filters.length).toBe(headers.length)
  })

  it('updates with registration history when given', async () => {
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual([])
    expect(wrapper.findComponent(TableRow).exists()).toBe(false)
    expect(wrapper.findAll(tableRow).length).toBe(0)
    // test adding 1 row
    await wrapper.setProps({ setRegistrationHistory: registrationHistory })
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual(registrationHistory)
    expect(wrapper.findComponent(TableRow).exists()).toBe(true)
    expect(wrapper.findAllComponents(TableRow).length).toBe(1)
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setChild).toBe(false)
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setHeaders).toEqual(wrapper.vm.headers)
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setIsExpanded).toBe(false)
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setItem).toEqual(
      wrapper.vm.$props.setRegistrationHistory[0]
    )

    // test adding multiple rows + drafts
    await wrapper.setProps({ setRegistrationHistory: newRegistrationHistory })
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual(newRegistrationHistory)
    const rows = wrapper.findAllComponents(TableRow)
    expect(rows.length).toBe(newRegistrationHistory.length)
    for (let i = 0; i < rows.length; i++) {
      const reg = newRegistrationHistory[i] as RegistrationSummaryIF
      expect(rows.at(i).vm.$props.setChild).toBe(false)
      expect(rows.at(i).vm.$props.setHeaders).toEqual(wrapper.vm.headers)
      expect(rows.at(i).vm.$props.setIsExpanded).toBe(false)
      expect(rows.at(i).vm.$props.setItem).toEqual(reg)

      // expands / collapses if it has children
      if (reg.changes) {
        // expand
        rows.at(i).vm.$emit('toggleExpand', true)
        await flushPromises()
        expect(rows.at(i).vm.$props.setIsExpanded).toEqual(true)
        // child row will not be part of original rows list
        const childRow = wrapper.findAllComponents(TableRow).at(i + 1)
        expect(childRow.vm.$props.setChild).toBe(true)
        expect(childRow.vm.$props.setHeaders).toEqual(wrapper.vm.headers)
        expect(childRow.vm.$props.setIsExpanded).toBe(false)
        expect(childRow.vm.$props.setItem).toEqual(reg.changes[0])
        // collapse
        rows.at(i).vm.$emit('toggleExpand', true)
        await flushPromises()
        expect(rows.at(i).vm.$props.setIsExpanded).toEqual(false)
        // verify next row in table is not the child
        expect(wrapper.findAllComponents(TableRow).at(i + 1).vm.$props.setChild).toBe(false)
        expect(wrapper.findAllComponents(TableRow).at(i + 1).vm.$props.setItem).not.toEqual(reg.changes[0])
      }
    }
  })

  it('filters table data properly', async () => {
    // FUTURE: add tests for all filters
    await wrapper.setProps({ setRegistrationHistory: newRegistrationHistory })
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual(newRegistrationHistory)
    expect(wrapper.findAllComponents(TableRow).length).toBe(5)
    // clear filters button only shows when a filter is active
    expect(wrapper.findAll('.v-btn.registration-action').length).toBe(0)
    // filter reg number parent only match
    const parentRegNumMatch = '23'
    wrapper.vm.registrationNumber = parentRegNumMatch
    await flushPromises()
    // clear filters btn shows
    expect(wrapper.findAll('.v-btn.registration-action').length).toBe(1)
    // wait - sort will wait at least 1 second for debounce
    setTimeout(async () => {
      // emitted the new sort
      expect(getLastEvent(wrapper, 'sort')).toEqual({
        endDate: null,
        folNum: '',
        orderBy: '',
        orderVal: '',
        regBy: '',
        regNum: '23',
        regParty: '',
        regType: '',
        secParty: '',
        startDate: null,
        status: ''
      })
      // clear filters btn clears the filter
      await wrapper.find('.v-btn.registration-action').trigger('click')
      expect(wrapper.vm.registrationNumber).toBe('')
      // need to wait 1 secs due to debounce
      setTimeout(() => {
        expect(getLastEvent(wrapper, 'sort')).toEqual({
          endDate: null,
          folNum: '',
          orderBy: '',
          orderVal: '',
          regBy: '',
          regNum: '',
          regParty: '',
          regType: '',
          secParty: '',
          startDate: null,
          status: ''
        })
      }, 3000)
      expect(wrapper.findAll('.v-btn.registration-action').length).toBe(0)
    }, 3000)
  })

  it('filters mhr table data properly', async () => {
    await wrapper.setProps({ setRegistrationHistory: mhrRegistrationHistoryTest })
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual(mhrRegistrationHistoryTest)
    expect(wrapper.findAllComponents(TableRow).length).toBe(1)
    // clear filters button only shows when a filter is active
    expect(wrapper.findAll('.v-btn.registration-action').length).toBe(0)
    // filter reg number parent only match
    const parentRegNumMatch = '21'
    wrapper.vm.registrationNumber = parentRegNumMatch
    await flushPromises()
    // clear filters btn shows
    expect(wrapper.findAll('.v-btn.registration-action').length).toBe(1)
    // wait - sort will wait at least 1 second for debounce
    setTimeout(async () => {
      // emitted the new sort
      expect(getLastEvent(wrapper, 'sort')).toEqual({
        endDate: null,
        folNum: '12',
        orderBy: '',
        orderVal: '',
        regBy: 'Business',
        regNum: '23',
        regParty: 'ABC',
        regType: 'REGISTER NEW UNIT',
        secParty: '',
        startDate: null,
        status: 'Active'
      })
      // clear filters btn clears the filter
      await wrapper.find('.v-btn.registration-action').trigger('click')
      expect(wrapper.vm.registrationNumber).toBe('')
      expect(wrapper.vm.folNum).toBe('')
      expect(wrapper.vm.Status).toBe('')
      // need to wait 1 secs due to debounce
      setTimeout(() => {
        expect(getLastEvent(wrapper, 'sort')).toEqual({
          endDate: null,
          folNum: '',
          orderBy: '',
          orderVal: '',
          regBy: '',
          regNum: '',
          regParty: '',
          regType: '',
          secParty: '',
          startDate: null,
          status: ''
        })
      }, 3000)
      expect(wrapper.findAll('.v-btn.registration-action').length).toBe(0)
    }, 3000)
  })

  it('renders and displays the typeahead dropdown', async () => {
    await store.dispatch('setAccountProductSubscription', {
      [AccountProductCodes.RPPR]: {
        membership: AccountProductMemberships.MEMBER,
        roles: ['edit']
      }
    })
    await wrapper.setProps({ setRegistrationHistory: registrationHistory })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    await flushPromises()
    expect(wrapper.findComponent(RegistrationBarTypeAheadList).exists()).toBe(true)
    const autocomplete = wrapper.findComponent(RegistrationBarTypeAheadList)
    expect(autocomplete.text()).toContain('Registration Type')
  })

  it('renders and displays the date picker', async () => {
    expect(wrapper.vm.showDatePicker).toBe(false)
    expect(wrapper.findComponent(DatePicker).exists()).toBe(true)
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(false)
    expect(wrapper.findComponent(DatePicker).vm.$props.setEndDate).toBe(null)
    expect(wrapper.findComponent(DatePicker).vm.$props.setStartDate).toBe(null)
    expect(wrapper.find(dateFilter).exists()).toBe(true)
    expect(wrapper.find(dateFilter).trigger('click'))
    await flushPromises()
    await Vue.nextTick()
    expect(wrapper.vm.showDatePicker).toBe(true)
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(true)
    const startDate = '2021-10-24'
    const endDate = '2021-10-26'
    wrapper.findComponent(DatePicker).vm.$emit('submit', { endDate: endDate, startDate: startDate })
    await flushPromises()
    // wait for debounce
    setTimeout(async () => {
      expect(wrapper.vm.showDatePicker).toBe(false)
      expect(wrapper.findComponent(DatePicker).isVisible()).toBe(false)
      expect(wrapper.vm.submittedStartDate).toBe(startDate)
      expect(wrapper.vm.submittedEndDate).toBe(endDate)
    }, 2000)
  })

  it('emits button actions from TableRow', async () => {
    await wrapper.setProps({ setRegistrationHistory: [mockedRegistration1] })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findAllComponents(TableRow).length).toBeGreaterThan(0)
    // complete reg actions
    const actions = [TableActions.AMEND, TableActions.DISCHARGE, TableActions.RENEW, TableActions.REMOVE]
    for (let i = 0; i < actions.length; i++) {
      wrapper
        .findAllComponents(TableRow)
        .at(0)
        .vm.$emit('action', {
          action: actions[i],
          regNum: mockedRegistration1.baseRegistrationNumber
        })
      await flushPromises()
      expect(getLastEvent(wrapper, 'action')).toEqual({
        action: actions[i],
        docId: undefined,
        regNum: mockedRegistration1.baseRegistrationNumber,
        mhrInfo: undefined
      })
    }

    // edit new draft
    wrapper
      .findAllComponents(TableRow)
      .at(0)
      .vm.$emit('action', {
        action: TableActions.EDIT_NEW,
        docId: mockedDraft1.documentId
      })
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual({
      action: TableActions.EDIT_NEW,
      docId: mockedDraft1.documentId,
      regNum: undefined
    })
    // edit amendment draft
    wrapper
      .findAllComponents(TableRow)
      .at(0)
      .vm.$emit('action', {
        action: TableActions.EDIT_AMEND,
        docId: mockedDraftAmend.documentId,
        regNum: mockedDraftAmend.baseRegistrationNumber
      })
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual({
      action: TableActions.EDIT_AMEND,
      docId: mockedDraftAmend.documentId,
      regNum: mockedDraftAmend.baseRegistrationNumber
    })
  })

  it('works as expected for new added registrations', async () => {
    // setup
    const firstItem = newRegistrationHistory[0] as DraftResultIF
    const baseRegItem = newRegistrationHistory[2] as RegistrationSummaryIF
    const childDraftItem = baseRegItem.changes[0] as DraftResultIF
    const childRegItem = (newRegistrationHistory[3] as RegistrationSummaryIF).changes[0] as RegistrationSummaryIF
    const testItems = [firstItem, baseRegItem, childDraftItem, childRegItem]

    const newRegFirstItem: RegTableNewItemI = {
      addedReg: firstItem.documentId,
      addedRegParent: '',
      addedRegSummary: firstItem,
      prevDraft: ''
    }
    const newRegBaseItem: RegTableNewItemI = {
      addedReg: baseRegItem.registrationNumber,
      addedRegParent: '',
      addedRegSummary: baseRegItem,
      prevDraft: ''
    }
    const newRegChildDraftItem: RegTableNewItemI = {
      addedReg: childDraftItem.documentId,
      addedRegParent: childDraftItem.baseRegistrationNumber,
      addedRegSummary: childDraftItem,
      prevDraft: ''
    }
    const newRegChildItem: RegTableNewItemI = {
      addedReg: childRegItem.registrationNumber,
      addedRegParent: childRegItem.baseRegistrationNumber,
      addedRegSummary: childRegItem,
      prevDraft: ''
    }

    const emptyNewReg: RegTableNewItemI = {
      addedReg: '',
      addedRegParent: '',
      addedRegSummary: null,
      prevDraft: ''
    }

    await wrapper.setProps({ setRegistrationHistory: newRegistrationHistory })

    // verify setup
    expect(wrapper.vm.newReg).toBe(null)
    for (const i in testItems) {
      expect(wrapper.vm.isNewRegItem(testItems[i])).toBe(false)
      expect(wrapper.vm.isNewRegParentItem(testItems[i])).toBe(false)
      if (i === '0') expect(wrapper.vm.setRowRef(testItems[i])).toBe('firstItem')
      else expect(wrapper.vm.setRowRef(testItems[i])).toBe('')
    }

    // test updating the new reg (draft + first)
    await wrapper.setProps({ setNewRegItem: newRegFirstItem })
    expect(wrapper.vm.newReg).toEqual(newRegFirstItem)
    expect(wrapper.vm.isNewRegItem(firstItem)).toBe(true)
    expect(wrapper.vm.isNewRegParentItem(firstItem)).toBe(false)
    expect(wrapper.vm.setRowRef(firstItem)).toBe('newAndFirstItem')

    // test base reg + middle
    await wrapper.setProps({ setNewRegItem: newRegBaseItem })
    expect(wrapper.vm.newReg).toEqual(newRegBaseItem)
    expect(wrapper.vm.isNewRegItem(baseRegItem)).toBe(true)
    expect(wrapper.vm.isNewRegParentItem(baseRegItem)).toBe(false)
    expect(wrapper.vm.setRowRef(baseRegItem)).toBe('newRegItem')

    // test child reg
    await wrapper.setProps({ setNewRegItem: newRegChildItem })
    expect(wrapper.vm.newReg).toEqual(newRegChildItem)
    const val = wrapper.vm.isNewRegItem(childRegItem)
    await Vue.nextTick()
    expect(val).toBe(true)
    expect(wrapper.vm.isNewRegParentItem(childRegItem)).toBe(false)
    expect(wrapper.vm.isNewRegParentItem(newRegistrationHistory[3])).toBe(true)
    expect(wrapper.vm.setRowRef(childRegItem)).toBe('newRegItem')

    // test child draft reg
    await wrapper.setProps({ setNewRegItem: newRegChildDraftItem })
    expect(wrapper.vm.newReg).toEqual(newRegChildDraftItem)
    expect(wrapper.vm.isNewRegItem(childDraftItem)).toBe(true)
    expect(wrapper.vm.isNewRegParentItem(childDraftItem)).toBe(false)
    expect(wrapper.vm.isNewRegParentItem(baseRegItem)).toBe(true)
    expect(wrapper.vm.setRowRef(childDraftItem)).toBe('newRegItem')

    // setting to empty clears new reg dynamically
    await wrapper.setProps({ setNewRegItem: emptyNewReg })
    expect(wrapper.vm.newReg).toEqual(emptyNewReg)
    for (const i in testItems) {
      expect(wrapper.vm.isNewRegItem(testItems[i])).toBe(false)
      expect(wrapper.vm.isNewRegParentItem(testItems[i])).toBe(false)
      if (i === '0') expect(wrapper.vm.setRowRef(testItems[i])).toBe('firstItem')
      else expect(wrapper.vm.setRowRef(testItems[i])).toBe('')
    }
  })
})
