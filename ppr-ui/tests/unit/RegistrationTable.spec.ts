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
// local types/helpers/etc.
import { AccountProductCodes, AccountProductMemberships, TableActions } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
// unit test data/helpers
import {
  mockedRegistration1,
  mockedDraft1,
  mockedRegistration2,
  mockedRegistration2Child,
  mockedDraft2,
  mockedDraftAmend,
  mockedRegistration3
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
    // 500 days converted to year & days
    expect(wrapper.findAll(tableRow).at(0).text()).toContain('1 year 135 days')
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
          if (reg.expireDays === 500) {
            expect(rows.at(i).text()).toContain('1 year 135 days')
          } else {
            expect(rows.at(i).text()).toContain(reg.expireDays)
          }
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

  it('emits button actions properly for complete registrations', async () => {
    await wrapper.setProps({ setRegistrationHistory: [mockedRegistration1, mockedRegistration3] })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)

    // main buttons: active vs discharged/expired
    const activeRegButton = wrapper.findAll('#action-btn-0')
    expect(activeRegButton.length).toBe(1)
    expect(activeRegButton.at(0).text()).toContain('Amend')
    activeRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.AMEND, regNum: mockedRegistration1.baseRegistrationNumber }
    )

    const dischargedRegButton = wrapper.findAll('#action-btn-1')
    expect(dischargedRegButton.length).toBe(1)
    expect(dischargedRegButton.at(0).text()).toContain('Re-Register')
    // FUTURE: test it emits the correct thing here once built
    activeRegButton.at(0).trigger('click')

    // dropdown buttons
    const buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(2)

    // click dropdown for active reg
    buttons.at(0).trigger('click')
    await Vue.nextTick()

    //it renders the actions drop down
    const menuItems = wrapper.findAll(`.dropdown-btn-${0}`)
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

    // click dropdown for discharged reg
    buttons.at(1).trigger('click')
    await Vue.nextTick()
    //it renders the remove action in drop down
    const menuItemsDishcarge = wrapper.findAll(`.dropdown-btn-${1}`)
    expect(menuItemsDishcarge.length).toBe(1)
    expect(menuItemsDishcarge.at(0).text()).toContain('Remove From Table')
    await menuItemsDishcarge.at(0).trigger('click')
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.REMOVE, regNum: mockedRegistration3.baseRegistrationNumber }
    )
  })

  it('emits button actions properly for draft registrations', async () => {
    const drafts = [mockedDraft1, mockedDraftAmend]
    await wrapper.setProps({ setRegistrationHistory: drafts })
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)

    // main buttons: new vs amend
    const draftNewRegButton = wrapper.findAll('#action-btn-0')
    expect(draftNewRegButton.length).toBe(1)
    expect(draftNewRegButton.at(0).text()).toContain('Edit')
    draftNewRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.EDIT_NEW, docId: mockedDraft1.documentId }
    )

    const draftAmendRegButton = wrapper.findAll('#action-btn-1')
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

    // drop down buttons
    const buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(drafts.length)
    // amend draft: i=0, normal draft: i=1
    for (let i = 0; i < drafts.length; i++) {
      buttons.at(i).trigger('click')
      await Vue.nextTick()

      // it renders the actions drop down
      const menuItems = wrapper.findAll(`.dropdown-btn-${i}`)
      expect(menuItems.length).toBe(1)
      expect(menuItems.at(0).text()).toContain('Delete Draft')

      // click delete and check emit
      await menuItems.at(0).trigger('click')
      expect(getLastEvent(wrapper, 'action')).toEqual(
        {
          action: TableActions.DELETE,
          docId: drafts[i].documentId
        }
      )
    }
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
