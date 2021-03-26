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
import { SearchBar } from '@/components/search'

// Other
import { SearchTypes } from '@/resources'
import { AutoCompleteResponseIF, SearchResponseIF, SearchTypeIF } from '@/interfaces'
import { mockedSearchResponse, mockedVonResponse } from './test-data'
import { UISearchTypes } from '@/enums'
import { FolioNumber } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const searchError: string = 'search-error'
const searchData: string = 'search-data'

// Input field selectors / buttons
const searchButtonSelector: string = '.search-bar-btn'
const searchDropDown: string = '.search-bar-type-select'
const searchTextField: string = '.search-bar-text-field'

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
function getLastEvent (wrapper: Wrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  searchTypes: Array<SearchTypeIF>
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchBar, {
    localVue,
    propsData: { searchTypes },
    store,
    vuetify
  })
}

describe('SearchBar component', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
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
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('searches when fields are filled', async () => {
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
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
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
    wrapper = createComponent(SearchTypes)
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
    wrapper = createComponent(SearchTypes)
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
    wrapper = createComponent(SearchTypes)
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
    wrapper = createComponent(SearchTypes)
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
    expect(messages.at(0).text()).toContain('Up to 25 letters')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
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
    wrapper = createComponent(SearchTypes)
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
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})
