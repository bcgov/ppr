// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import { axios as vonAxios } from '@/utils/axios-von'

// Components
import { ConfirmationDialog } from '@/components/dialogs'
import { SearchBar } from '@/components/search'

// Other
import { SearchTypes } from '@/resources'
import { AutoCompleteResponseIF, SearchResponseIF, SearchTypeIF } from '@/interfaces'
import {
  mockedDefaultUserSettingsResponse,
  mockedDisableAllUserSettingsResponse,
  mockedSearchResponse,
  mockedVonResponse
} from './test-data'
import { UISearchTypes } from '@/enums'
import { FolioNumber } from '@/components/common'
import { getLastEvent } from './utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const searchError: string = 'search-error'
const searchData: string = 'search-data'

// Input field selectors / buttons
const dialogCheckbox: string = '.dialog-checkbox'
const dialogText: string = '.dialog-text'
const dialogTitle: string = '.dialog-title'
const searchButtonSelector: string = '.search-bar-btn'
const searchDropDown: string = '.search-bar-type-select'
const searchTextField: string = '.search-bar-text-field'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  attachDialog: string,
  searchTypes: Array<SearchTypeIF>
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchBar, {
    localVue,
    propsData: { attachDialog, searchTypes },
    store,
    vuetify
  })
}

describe('SearchBar component', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders SearchBar Component with basic elements', async () => {
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumber).exists()).toBe(true)
    expect(wrapper.vm.$data.searchTypes).toStrictEqual(SearchTypes)
    expect(wrapper.find(searchDropDown).exists()).toBe(true)
    expect(wrapper.find(searchTextField).exists()).toBe(true)
    expect(wrapper.find(searchButtonSelector).exists()).toBe(true)
  })
})

describe('Payment confirmation popup', () => {
  let wrapper: Wrapper<any>
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.SERIAL_NUMBER]
  const select: SearchTypeIF = SearchTypes[0]

  beforeEach(async () => {
    // GET search data
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDefaultUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('pops up with payment confirmation modal before searching', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.SERIAL_NUMBER)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'F100'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Serial numbers normally contain')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation enabled, otherwise it would skip the modal
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(true)
    expect(getLastEvent(wrapper, searchData)).toBeNull()
    expect(wrapper.findComponent(ConfirmationDialog).exists()).toBe(true)
    expect(wrapper.findComponent(ConfirmationDialog).isVisible()).toBe(true)
    expect(wrapper.find(dialogTitle).exists()).toBe(true)
    expect(wrapper.find(dialogText).exists()).toBe(true)
    expect(wrapper.find(dialogCheckbox).exists()).toBe(true)
  })
})

describe('Serial number search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.SERIAL_NUMBER]
  const select: SearchTypeIF = SearchTypes[0]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    expect(wrapper.find('.fee-text').exists()).toBeTruthy()
    expect(wrapper.find('.select-search-text').text()).toContain('Each search incurs')
    expect(select.searchTypeUI).toEqual(UISearchTypes.SERIAL_NUMBER)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'F100'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Serial numbers normally contain')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })

  it('hides and shows things for staff', async () => {
    await store.dispatch('setAuthRoles', ['staff', 'ppr_staff'])
    await store.dispatch('setStaffPayment', {
      option: 1,
      routingSlipNumber: '888555222',
      isPriority: false,
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: ''
    })
    await store.dispatch('setSearchCertified', true)
    expect(select.searchTypeUI).toEqual(UISearchTypes.SERIAL_NUMBER)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'F100'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    await flushPromises
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
    expect(wrapper.vm.$store.state.stateModel.staffPayment).toBe(null)

    const staffGroups = ['helpdesk', 'ppr_staff']
    for (let i = 0; i < staffGroups.length; i++) {
      await store.dispatch('setAuthRoles', ['staff', staffGroups[i]])
      expect(wrapper.findComponent(FolioNumber).exists()).toBeFalsy()
      expect(wrapper.find('.fee-text').exists()).toBeFalsy()
    }
    await store.dispatch('setAuthRoles', [])
    await store.dispatch('setRoleSbc', true)
    await flushPromises
    expect(wrapper.find('.fee-text').exists()).toBeTruthy()
    expect(wrapper.find('.fee-text').text()).toContain('10.00')
  })
})

describe('Individual debtor search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.INDIVIDUAL_DEBTOR]
  const select: SearchTypeIF = SearchTypes[1]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.INDIVIDUAL_DEBTOR)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValueFirst = 'test'
    wrapper.vm.$data.searchValueSecond = 'tester'
    wrapper.vm.$data.searchValueLast = 'testing'
    wrapper.vm.$data.folioNumber = '123'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: select.searchTypeAPI,
      criteria: {
        debtorName: {
          first: 'test',
          second: 'tester',
          last: 'testing'
        }
      },
      clientReferenceId: '123'
    })
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
  it('Middle name is optional', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.INDIVIDUAL_DEBTOR)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValueFirst = 'test'
    wrapper.vm.$data.searchValueLast = 'testing'
    wrapper.vm.$data.folioNumber = '123'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: select.searchTypeAPI,
      criteria: {
        debtorName: {
          first: 'test',
          second: undefined,
          last: 'testing'
        }
      },
      clientReferenceId: '123'
    })
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Business debtor search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  sessionStorage.setItem('VON_API_URL', 'mock-url-von')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.BUSINESS_DEBTOR]
  const vonResp: AutoCompleteResponseIF = mockedVonResponse
  const select: SearchTypeIF = SearchTypes[2]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    // GET search data
    const post = sandbox.stub(axios, 'post')
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    // GET autocomplete
    const get = sandbox.stub(vonAxios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: vonResp
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.BUSINESS_DEBTOR)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'test business debtor'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    if (messages) {
      expect(messages.length).toBe(1)
      // ensure its the hint message not a validation message
      expect(messages.at(0).text()).toContain('Business names must contain')
    }
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
  it('shows von api results while typing', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.BUSINESS_DEBTOR)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 't'
    // takes 4 ticks before displayed
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    const autoCompleteNames = wrapper.findAll('.auto-complete-item')
    // 6 in the response, but should only display up to 5
    expect(autoCompleteNames.length).toBe(5)
    expect(autoCompleteNames.at(0).text()).toEqual(mockedVonResponse.results[0].value)
    expect(autoCompleteNames.at(1).text()).toEqual(mockedVonResponse.results[1].value)
    expect(autoCompleteNames.at(2).text()).toEqual(mockedVonResponse.results[2].value)
    expect(autoCompleteNames.at(3).text()).toEqual(mockedVonResponse.results[3].value)
    expect(autoCompleteNames.at(4).text()).toEqual(mockedVonResponse.results[4].value)
  })
  it('updates the search value and removes the autocomplete list after a name is selected', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.BUSINESS_DEBTOR)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'test'
    // takes 4 ticks before displayed
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    const autoCompleteNames = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNames.length).toBe(5)
    const selectedText = autoCompleteNames.at(3).text()
    autoCompleteNames.at(3).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toEqual(selectedText)
    const autoCompleteNamesAfterClose = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNamesAfterClose.length).toBe(0)
  })
})

describe('MHR search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.MHR_NUMBER]
  const select: SearchTypeIF = SearchTypes[4]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.MHR_NUMBER)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = '123456'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Manufactured home registration number must contain')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Aircraft search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.AIRCRAFT]
  const select: SearchTypeIF = SearchTypes[5]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.AIRCRAFT)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'abcd-efgh-fhgh' // dashes allowed
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Up to 25 characters')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Registration number search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.REGISTRATION_NUMBER]
  const select: SearchTypeIF = SearchTypes[6]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent('', SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    expect(select.searchTypeUI).toEqual(UISearchTypes.REGISTRATION_NUMBER)
    wrapper.vm.$data.selectedSearchType = select
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = '123456A'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Registration numbers contain')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})
