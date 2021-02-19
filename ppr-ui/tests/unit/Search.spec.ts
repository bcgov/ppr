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

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const searchError: string = 'search-error'
const searchData: string = 'search-data'

// Input field selectors / buttons
const searchButtonSelector: string = '#search-btn'
const searchDropDown: string = '#search-type-select'

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
function getLastEvent (wrapper: Wrapper<Search>, name: string): any {
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
): Wrapper<Search> {
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

describe('App component', () => {
  let wrapper: Wrapper<Search>
  sessionStorage.setItem('PPR_API_URL', 'mock-url')
  const post = sinon.stub(axios, 'post')

  const resp: SearchResponseIF = {
    searchId: '1',
    maxResultsSize: 1,
    totalResultsSize: 1,
    returnedResultsSize: 1,
    searchQuery: {
      type: 'SERIAL_NUMBER',
      criteria: {
        value: 'F100'
      }
    },
    results: null
  }

  // GET NR data
  post.returns(new Promise(resolve => resolve({
      data: resp
    })))
  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Search Component with search types', () => {
    // const wrapper: Wrapper<Search> = createComponent(SearchTypes)
    expect(wrapper.findComponent(Search).exists()).toBe(true)
    expect(wrapper.vm.$data.searchTypes).toStrictEqual(SearchTypes)
    expect(wrapper.find(searchButtonSelector).attributes('disabled')).toBeUndefined()
  })

  it('prevents searching and gives validation when category is not selected', async () => {
    expect(wrapper.vm.$data.selectedSearchType).toBeUndefined()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchTypes).toStrictEqual(SearchTypes)
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
    expect(wrapper.vm.$data.validations.category?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Please select a category')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeUndefined()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a serial number to search')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('searches when fields are filled', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    wrapper.vm.$data.selectedSearchType = select1
    wrapper.vm.$data.searchValue = 'F100'
    await Vue.nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations).toBeNull()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(0)
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toEqual(resp)
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'F10'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.popUp).toBeDefined()
    await Vue.nextTick()
    const popUpMessages = wrapper.findAll('.v-tooltip__content')
    expect(popUpMessages.length).toBe(1)
    wrapper.vm.$data.searchValue = 'F10@'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
  })
})
