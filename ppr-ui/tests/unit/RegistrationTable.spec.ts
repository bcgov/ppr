// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// local components
import { RegistrationTable } from '@/components/tables'
import { RegistrationBarTypeAheadList } from '@/components/registration'
import { RegistrationConfirmation } from '@/components/dialogs'
// local types/helpers/etc.
import { AccountProductCodes, AccountProductMemberships } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
// unit test data/helpers
import {
  mockedRegistration1,
  mockedDraft1,
  mockedRegistration2,
  mockedRegistration2Child,
  mockedDraft2
} from './test-data'

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
    mockedRegistration1,
    mockedRegistration2,
    mockedRegistration2Child
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
    expect(wrapper.findAll(tableRow).length).toBe(0)
    // test adding 1 row
    await wrapper.setProps({ setRegistrationHistory: registrationHistory })
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual(registrationHistory)
    expect(wrapper.findAll(tableRow).length).toBe(1)
    expect(wrapper.findAll(tableRow).at(0).text()).toContain(registrationHistory[0].baseRegistrationNumber)
    expect(wrapper.findAll(tableRow).at(0).text()).toContain(registrationHistory[0].expireDays)
    expect(wrapper.findAll(tableRow).at(0).text()).toContain(registrationHistory[0].registeringParty)
    expect(wrapper.findAll(tableRow).at(0).text()).toContain(registrationHistory[0].securedParties)
    // test adding multiple rows + drafts
    await wrapper.setProps({ setRegistrationHistory: newRegistrationHistory })
    expect(wrapper.vm.$props.setRegistrationHistory).toEqual(newRegistrationHistory)
    const rows = wrapper.findAll(tableRow)
    expect(rows.length).toBe(newRegistrationHistory.length)
    for (let i = 0; i < rows.length; i++) {
      if (newRegistrationHistory[i].baseRegistrationNumber) {
        // not a draft
        const reg = newRegistrationHistory[i] as RegistrationSummaryIF
        expect(rows.at(i).text()).toContain(reg.baseRegistrationNumber)
        if (reg.registrationNumber && reg.registrationNumber !== reg.baseRegistrationNumber) {
          // child registration
          expect(rows.at(i).text()).toContain('N/A')
        } else {
          expect(rows.at(i).text()).toContain(reg.expireDays)
        }
        expect(rows.at(i).text()).toContain(reg.registeringParty)
        expect(rows.at(i).text()).toContain(reg.securedParties)
        expect(rows.at(i).text()).toContain('PDF')
      } else {
        // draft
        expect(rows.at(i).text()).toContain('Pending')
        expect(rows.at(i).text()).toContain('Draft')
      }
    }
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
    // the api is going to be called twice, once for drafts and once for registrations
    // the tests can't tell the difference, so the same one is called twice
    await flushPromises()
    expect(wrapper.findComponent(RegistrationBarTypeAheadList).exists()).toBe(true)
    const autocomplete = wrapper.findComponent(RegistrationBarTypeAheadList)
    expect(autocomplete.text()).toContain('Registration Type')

  })

  it('shows the discharge modal', async () => {
    await wrapper.setProps({ setRegistrationHistory: registrationHistory })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // the api is going to be called twice, once for drafts and once for registrations
    // the tests can't tell the difference, so the same one is called twice
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    const buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(1)

    buttons.at(0).trigger('click')
    await Vue.nextTick()

    //it renders the actions drop down
    const menuItems = wrapper.findAll('.v-list-item__subtitle')
    expect(menuItems.length).toBe(4)
    expect(menuItems.at(1).text()).toContain('Total Discharge')

    //click the discharge
    menuItems.at(1).trigger('click')
    await flushPromises()
    const dialog = wrapper.findComponent(RegistrationConfirmation)
    expect(dialog.isVisible()).toBe(true)
  })

  it('shows the amendment modal', async () => {
    await wrapper.setProps({ setRegistrationHistory: registrationHistory })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    const buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(1)

    buttons.at(0).trigger('click')
    await Vue.nextTick()

    //it renders the actions drop down
    const menuItems = wrapper.findAll('.v-list-item__subtitle')
    expect(menuItems.length).toBe(4)
    expect(menuItems.at(0).text()).toContain('Amend')

    //click the amendment
    menuItems.at(0).trigger('click')
    await flushPromises()
    const dialog = wrapper.findComponent(RegistrationConfirmation)
    
    expect(dialog.isVisible()).toBe(true)
  })

  it('shows the renewal modal', async () => {
    await wrapper.setProps({ setRegistrationHistory: registrationHistory })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    const buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(1)

    buttons.at(0).trigger('click')
    await Vue.nextTick()

    //it renders the actions drop down
    const menuItems = wrapper.findAll('.v-list-item__subtitle')
    expect(menuItems.length).toBe(4)
    expect(menuItems.at(2).text()).toContain('Renew')

    //click the renewal
    menuItems.at(2).trigger('click')
    await flushPromises()
    const dialog = wrapper.findComponent(RegistrationConfirmation)
    
    expect(dialog.isVisible()).toBe(true)
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
