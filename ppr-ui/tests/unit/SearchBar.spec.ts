// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import { axios as vonAxios } from '@/utils/axios-von'

// Components
import { ConfirmationDialog } from '@/components/dialogs'
import { BusinessSearchAutocomplete, SearchBar } from '@/components/search'

// Other
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { AutoCompleteResponseIF, ManufacturedHomeSearchResponseIF, SearchResponseIF, SearchTypeIF } from '@/interfaces'
import {
  mockedDefaultUserSettingsResponse,
  mockedDisableAllUserSettingsResponse, mockedMHRSearchResponse,
  mockedSearchResponse,
  mockedVonResponse
} from './test-data'
import { APIMHRSearchTypes, UIMHRSearchTypes, UISearchTypes } from '@/enums'
import { FolioNumber } from '@/components/common'
import { getLastEvent, getTestId } from './utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

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
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((SearchBar as any), {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('SearchBar component basic tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders SearchBar Component with basic elements', async () => {
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumber).exists()).toBe(true)
    expect(wrapper.find(searchDropDown).exists()).toBe(true)
    expect(wrapper.find(searchTextField).exists()).toBe(true)
    expect(wrapper.find(searchButtonSelector).exists()).toBe(true)
    // check the default is the regular fee
    expect(wrapper.vm.$props.isNonBillable).toBe(false)
    expect(wrapper.vm.fee).toBe('8.50')
    // update to non billable and see fee change
    await wrapper.setProps({ isNonBillable: true, serviceFee: 3 })
    expect(wrapper.vm.$props.isNonBillable).toBe(true)
    expect(wrapper.vm.$props.serviceFee).toBe(3)
    expect(wrapper.vm.fee).toBe('3.00')
  })
})

describe('Payment confirmation popup', () => {
  let wrapper: Wrapper<any>
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.SERIAL_NUMBER]
  const select: SearchTypeIF = SearchTypes[1]

  beforeEach(async () => {
    // GET search data
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDefaultUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('pops up with payment confirmation modal before searching', async () => {
    wrapper.vm.returnSearchSelection(select)
    await nextTick()
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = 'F100'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Serial numbers normally contain')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation enabled, otherwise it would skip the modal
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(true)
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
  const select: SearchTypeIF = SearchTypes[1]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    await store.setAuthRoles(['ppr'])
    await store.setUserProductSubscriptionsCodes(['PPR'])

    expect(wrapper.find('.fee-text').exists()).toBeTruthy()
    const searchText = wrapper.find('.search-info').text()
    expect(searchText).toContain('Select a search category and then enter a criteria to search')
    expect(searchText).not.toContain('$8.50')
    // PPR info should be displayed for PPR only roles
    expect(wrapper.find(getTestId('ppr-search-info')).exists()).toBeTruthy()
    wrapper.vm.returnSearchSelection(select)
    await nextTick()
    wrapper.vm.selectedSearchType = select
    await nextTick()
    expect(wrapper.find(getTestId('ppr-search-info')).exists()).toBeTruthy()
    wrapper.vm.searchValue = 'F100'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Serial numbers normally contain')
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })

  it('hides and shows things for staff', async () => {
    await store.setAuthRoles(['staff', 'ppr_staff'])
    await store.setUserProductSubscriptionsCodes([''])

    const searchText = wrapper.find('.search-info').text()
    expect(searchText).toContain('Select a search category and then enter a criteria to search')
    await store.setStaffPayment({
      option: 1,
      routingSlipNumber: '888555222',
      isPriority: false,
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: ''
    })
    await store.setSearchCertified(true)
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    expect(wrapper.find(getTestId('ppr-search-info')).exists()).toBeFalsy()
    expect(wrapper.find(getTestId('mhr-search-info')).exists()).toBeFalsy()
    wrapper.vm.searchValue = 'F100'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    await flushPromises
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
    expect(store.getStateModel.staffPayment).toBe(null)

    const staffGroups = ['helpdesk', 'ppr_staff']
    for (let i = 0; i < staffGroups.length; i++) {
      await store.setAuthRoles(['staff', staffGroups[i]])
      expect(wrapper.findComponent(FolioNumber).exists()).toBeTruthy()
      expect(wrapper.find('.fee-text').exists()).toBeFalsy()
    }
    await store.setAuthRoles([])
    await store.setRoleSbc(true)
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
  const select: SearchTypeIF = SearchTypes[2]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValueFirst = 'test'
    wrapper.vm.searchValueSecond = 'tester'
    wrapper.vm.searchValueLast = 'testing'
    wrapper.vm.folioNumber = '123'
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
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
  it('Middle name is optional', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValueFirst = 'test'
    wrapper.vm.searchValueLast = 'testing'
    wrapper.vm.folioNumber = '123'
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
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
  it('special characters are being replaced', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValueFirst = 'Apostrophe’'
    wrapper.vm.searchValueSecond = '‘Single Quotes’'
    wrapper.vm.searchValueLast = '“Double Quotes”'
    wrapper.vm.folioNumber = '123'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: select.searchTypeAPI,
      criteria: {
        debtorName: {
          first: 'Apostrophe\'',
          second: '\'Single Quotes\'',
          last: '"Double Quotes"'
        }
      },
      clientReferenceId: '123'
    })
  })
})

describe('Business debtor search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  sessionStorage.setItem('VON_API_URL', 'mock-url-von')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.BUSINESS_DEBTOR]
  const vonResp: AutoCompleteResponseIF = mockedVonResponse
  const select: SearchTypeIF = SearchTypes[3]

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
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = 'test business debtor'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    if (messages) {
      expect(messages.length).toBe(1)
      // ensure its the hint message not a validation message
      expect(messages.at(0).text()).toContain('Business names must contain')
    }
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
  it('shows business dropdown after 3 characters', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = 'Abc'
    await nextTick()

    expect(wrapper.findComponent(BusinessSearchAutocomplete).exists()).toBe(true)
    expect(wrapper.find('#business-search-autocomplete').exists()).toBe(true)
    expect(wrapper.vm.autoCompleteSearchValue).toBe('Abc')
  })
  it('special characters are being replaced', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = 'Apostrophe’ ‘Single Quotes’ “Double Quotes”'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: select.searchTypeAPI,
      criteria: {
        debtorName: {
          business: 'Apostrophe\' \'Single Quotes\' "Double Quotes"'
        }
      },
      clientReferenceId: ''
    })
  })
})

describe('MHR search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('MHR_API_URL', 'mock-url')
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
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = '123456'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Manufactured home registration numbers normally contain up to 6 digits')
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Mhr Owner name search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('MHR_API_URL', 'mock-url')
  let sandbox
  const resp: ManufacturedHomeSearchResponseIF = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]
  const select: SearchTypeIF = MHRSearchTypes[2]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')

    // GET search data
    post.returns(new Promise(resolve => resolve({
      data: resp
    })))
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    const searchText = wrapper.find('.search-info').text()
    expect(searchText).not.toContain('Each search will incur a fee')
    wrapper.vm.searchValueFirst = 'test first'
    wrapper.vm.searchValueSecond = 'test middle'
    wrapper.vm.searchValueLast = 'test last'
    wrapper.vm.folioNumber = '123'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: APIMHRSearchTypes.MHROWNER_NAME,
      criteria: {
        ownerName: {
          first: 'test first',
          middle: 'test middle',
          last: 'test last'
        }
      },
      clientReferenceId: '123'
    })
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await nextTick()
    await nextTick()

    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })

  it('searches when fields are filled as Staff', async () => {
    await store.setAuthRoles(['staff', 'ppr_staff'])
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValueFirst = 'test first'
    wrapper.vm.searchValueSecond = 'test middle'
    wrapper.vm.searchValueLast = 'test last'
    wrapper.vm.folioNumber = '123'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: APIMHRSearchTypes.MHROWNER_NAME,
      criteria: {
        ownerName: {
          first: 'test first',
          middle: 'test middle',
          last: 'test last'
        }
      },
      clientReferenceId: '123'
    })
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await nextTick()
    await nextTick()

    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })

  it('Middle name is optional', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValueFirst = 'test first'
    wrapper.vm.searchValueLast = 'test last'
    wrapper.vm.folioNumber = '123'
    expect(wrapper.vm.getSearchApiParams()).toStrictEqual({
      type: APIMHRSearchTypes.MHROWNER_NAME,
      criteria: {
        ownerName: {
          first: 'test first',
          middle: undefined,
          last: 'test last'
        }
      },
      clientReferenceId: '123'
    })
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    expect(wrapper.find('.v-messages__message').exists()).toBe(false)
    await nextTick()
    await nextTick()

    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
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
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = 'abcd-efgh-fhgh' // dashes allowed
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Up to 25 characters')
    await nextTick()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
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
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
    wrapper.vm.returnSearchSelection(select)
    wrapper.vm.selectedSearchType = select
    await nextTick()
    wrapper.vm.searchValue = '123456A'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    await nextTick()
    expect(wrapper.vm.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Registration numbers contain')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    // verify payment confirmation disabled, otherwise it would not have gotten the response yet
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Staff and Client search buttons', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('should show/hide Staff and Client search buttons', async () => {
    await store.setRoleSbc(false)

    // Staff Roles
    await store.setAuthRoles(['staff', 'mhr'])
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(true)

    await store.setAuthRoles(['staff', 'ppr_staff', 'ppr'])
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(true)

    await store.setAuthRoles(['helpdesk', 'ppr'])
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(true)

    await store.setAuthRoles(['helpdesk', 'mhr'])
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(true)

    await store.setAuthRoles(['mhr'])
    await store.setRoleSbc(true)
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(false)

    await store.setAuthRoles(['ppr'])
    await store.setRoleSbc(true)
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(false)

    // Client Roles

    await store.setAuthRoles(['ppr'])
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(false)

    await store.setAuthRoles(['mhr'])
    expect(wrapper.find(getTestId('client-search-bar-btn')).exists()).toBe(false)
  })
})
