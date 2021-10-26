// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// local components
import { RegistrationTable } from '@/components/tables'
import { TableRow } from '@/components/tables/common'
import { RegistrationBarTypeAheadList } from '@/components/registration'
// local types/helpers/etc.
import { AccountProductCodes, AccountProductMemberships, TableActions } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
// unit test data/helpers
import {
  mockedRegistration1,
  mockedDraft1,
  mockedDraft2,
  mockedDraftAmend,
  mockedRegistration3,
  mockedRegistration1Collapsed,
  mockedRegistration2Collapsed
} from './test-data'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const regTable = '#registration-table'
const tableHeader = '.my-reg-header'
const tableFilter = '.my-reg-filter'
const tableRow = '.registration-row'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationTable, {
    localVue,
    store,
    propsData: {
      setHeaders: [...registrationTableHeaders],
      setLoading: false,
      setSearch: '',
      setRegistrationHistory: [],
      toggleSnackbar: false
    },
    vuetify
  })
}

describe('Test registration table with results', () => {
  let wrapper: Wrapper<any>
  const registrationHistory: RegistrationSummaryIF[] = [mockedRegistration1]
  const newRegistrationHistory: (RegistrationSummaryIF | DraftResultIF)[] = [
    mockedDraft1,
    mockedDraft2,
    mockedRegistration1Collapsed,
    mockedRegistration2Collapsed,
    mockedRegistration3
  ]

  beforeEach(async () => {
    wrapper = createComponent()
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
    expect(wrapper.findAll(regTable).at(0).text()).toContain('No registrations created yet.')
  })

  it('updates table headers when given new ones', async () => {
    expect(wrapper.vm.$props.setHeaders).toEqual(registrationTableHeaders)
    const newHeaders = [
      registrationTableHeaders[1],
      registrationTableHeaders[3],
      registrationTableHeaders[6]
    ]
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
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setItem).toEqual(wrapper.vm.$props.setRegistrationHistory[0])

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
        const childRow = wrapper.findAllComponents(TableRow).at(i+1)
        expect(childRow.vm.$props.setChild).toBe(true)
        expect(childRow.vm.$props.setHeaders).toEqual(wrapper.vm.headers)
        expect(childRow.vm.$props.setIsExpanded).toBe(false)
        expect(childRow.vm.$props.setItem).toEqual(reg.changes[0])
        // collapse
        rows.at(i).vm.$emit('toggleExpand', true)
        await flushPromises()
        expect(rows.at(i).vm.$props.setIsExpanded).toEqual(false)
        // verify next row in table is not the child 
        expect(wrapper.findAllComponents(TableRow).at(i+1).vm.$props.setChild).toBe(false)
        expect(wrapper.findAllComponents(TableRow).at(i+1).vm.$props.setItem).not.toEqual(reg.changes[0])
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
    expect(wrapper.findAllComponents(TableRow).length).toBe(2)
    for (let i = 0; i < wrapper.findAllComponents(TableRow).length; i++) {
      expect(wrapper.findAllComponents(TableRow).at(i)
        .vm.$props.setItem.baseRegistrationNumber).toContain(parentRegNumMatch)
      expect(wrapper.findAllComponents(TableRow).at(i).vm.$props.setChild).toBe(false)
      expect(wrapper.findAllComponents(TableRow).at(i).vm.$props.setIsExpanded).toBe(false)
    }
    // clear filters btn clears the filter
    await wrapper.find('.v-btn.registration-action').trigger('click')
    await flushPromises()
    expect(wrapper.vm.registrationNumber).toBe('')
    expect(wrapper.findAllComponents(TableRow).length).toBe(5)
    expect(wrapper.findAll('.v-btn.registration-action').length).toBe(0)

    // filter reg number child only match -> parent should show expanded
    const childRegNumMatch = 'BC456789'
    wrapper.vm.registrationNumber = childRegNumMatch
    await flushPromises()
    expect(wrapper.findAllComponents(TableRow).length).toBe(2)
    // first item should be parent
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setChild).toBe(false)
    expect(wrapper.findAllComponents(TableRow).at(0)
      .vm.$props.setItem.baseRegistrationNumber).not.toContain(childRegNumMatch)
    expect(wrapper.findAllComponents(TableRow).at(0)
      .vm.$props.setItem.changes[0].registrationNumber).toContain(childRegNumMatch)
    expect(wrapper.findAllComponents(TableRow).at(0).vm.$props.setIsExpanded).toBe(true)
    // second item should be child
    const parentRegNum = wrapper.findAllComponents(TableRow).at(0).vm.$props.setItem.baseRegistrationNumber
    expect(wrapper.findAllComponents(TableRow).at(1).vm.$props.setChild).toBe(true)
    expect(wrapper.findAllComponents(TableRow).at(1)
      .vm.$props.setItem.baseRegistrationNumber).toBe(parentRegNum)
    expect(wrapper.findAllComponents(TableRow).at(1)
      .vm.$props.setItem.registrationNumber).toContain(childRegNumMatch)
  })

  it('renders and displays the typeahead dropdown', async () => {
    await store.dispatch('setAccountProductSubscribtion', {
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

  it('emits button actions from TableRow', async () => {
    await wrapper.setProps({ setRegistrationHistory: [mockedRegistration1] })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findAllComponents(TableRow).length).toBeGreaterThan(0)
    // complete reg actions
    const actions = [TableActions.AMEND, TableActions.DISCHARGE, TableActions.RENEW, TableActions.REMOVE]
    for (let i = 0; i < actions.length; i++) {
      wrapper.findAllComponents(TableRow).at(0).vm.$emit(
        'action',
        { action: actions[i], regNum: mockedRegistration1.baseRegistrationNumber }
      )
      await flushPromises()
      expect(getLastEvent(wrapper, 'action')).toEqual(
        { action: actions[i], docId: undefined, regNum: mockedRegistration1.baseRegistrationNumber }
      )
    }

    // edit new draft
    wrapper.findAllComponents(TableRow).at(0).vm.$emit(
      'action',
      { action: TableActions.EDIT_NEW, docId: mockedDraft1.documentId }
    )
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.EDIT_NEW, docId: mockedDraft1.documentId, regNum: undefined }
    )
    // edit amendment draft
    wrapper.findAllComponents(TableRow).at(0).vm.$emit(
      'action',
      {
        action: TableActions.EDIT_AMEND,
        docId: mockedDraftAmend.documentId,
        regNum: mockedDraftAmend.baseRegistrationNumber
      }
    )
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      {
        action: TableActions.EDIT_AMEND,
        docId: mockedDraftAmend.documentId,
        regNum: mockedDraftAmend.baseRegistrationNumber
      }
    )
  })

  it('shows the snackbar when toggled', async () => {
    // toggle show snackbar
    await wrapper.setProps({ toggleSnackBar: true })
    expect(wrapper.find('.v-snack__wrapper').exists()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').text()).toContain(
      'Registration was successfully added to your table'
    )
    // close snackbar
    expect(wrapper.find('.snackbar-btn-close').exists()).toBe(true)
    await wrapper.find('.snackbar-btn-close').trigger('click')
    expect(wrapper.vm.$data.showSnackbar).toBe(false)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(false)
    // verify toggle works again after the first time
    await wrapper.setProps({ toggleSnackBar: false })
    expect(wrapper.vm.$data.showSnackbar).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').text()).toContain(
      'Registration was successfully added to your table'
    )
  })
})
