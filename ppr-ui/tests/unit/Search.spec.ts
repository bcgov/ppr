// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'

// Components
import { Search } from '@/components/search'

// Other
import { SearchTypes } from '@/resources'
import { SearchResponseIF, SearchTypeIF } from '@/interfaces'
import { mockResponse } from './test-data'
import { UISearchTypes } from '@/enums'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const searchError: string = 'search-error'
const searchData: string = 'search-data'

// Input field selectors / buttons
const searchButtonSelector: string = '#search-btn'

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
 * @returns a Wrapper<Search> object with the given parameters.
 */
function createComponent (
  searchTypes: Array<SearchTypeIF>
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(Search, {
    localVue,
    propsData: { searchTypes },
    store,
    vuetify
  })
}

describe('Search component', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Search Component with search types', () => {
    expect(wrapper.findComponent(Search).exists()).toBe(true)
    expect(wrapper.vm.$data.searchTypes).toStrictEqual(SearchTypes)
    expect(wrapper.find(searchButtonSelector).attributes('disabled')).toBeUndefined()
  })
})

describe('Serial number search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox;
  const resp: SearchResponseIF = mockResponse[UISearchTypes.SERIAL_NUMBER]

  beforeEach(async () => {
    sandbox = sinon.createSandbox();
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
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    wrapper.vm.$data.selectedSearchType = select1
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
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Business debtor search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox;
  const resp: SearchResponseIF = mockResponse[UISearchTypes.BUSINESS_DEBTOR]

  beforeEach(async () => {
    sandbox = sinon.createSandbox();
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
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[2]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'test business debtor'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    // ensure its the hint message not a validation message
    expect(messages.at(0).text()).toContain('Business names must contain')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('MHR search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox;
  const resp: SearchResponseIF = mockResponse[UISearchTypes.MHR_NUMBER]

  beforeEach(async () => {
    sandbox = sinon.createSandbox();
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
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[4]
    wrapper.vm.$data.selectedSearchType = select1
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
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Aircraft search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox;
  const resp: SearchResponseIF = mockResponse[UISearchTypes.AIRCRAFT]

  beforeEach(async () => {
    sandbox = sinon.createSandbox();
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
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[5]
    wrapper.vm.$data.selectedSearchType = select1
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
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})

describe('Registration number search', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  let sandbox;
  const resp: SearchResponseIF = mockResponse[UISearchTypes.REGISTRATION_NUMBER]

  beforeEach(async () => {
    sandbox = sinon.createSandbox();
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
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[6]
    wrapper.vm.$data.selectedSearchType = select1
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
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })
})