// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import { axios as vonAxios } from '@/utils/axios-von'

// Components
import { AutoComplete } from '@/components/search'

// Other
import { SearchTypes } from '@/resources'
import { AutoCompleteResponseIF, SearchResponseIF, SearchTypeIF } from '@/interfaces'
import { mockedSearchResponse, mockedVonResponse } from './test-data'
import { UISearchTypes } from '@/enums'
import { getLastEvent } from './utils'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const hideDetails: string = 'hide-details'
const searchValue: string = 'search-value'

// Input field selectors / buttons
const closeButtonSelector: string = '.auto-complete-close-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<AutoComplete> object with the given parameters.
 */
function createComponent (
  setAutoCompleteIsActive: boolean,
  searchValue: string
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(AutoComplete, {
    localVue,
    propsData: { setAutoCompleteIsActive, searchValue },
    store,
    vuetify
  })
}

describe('AutoComplete component', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('VON_API_URL', 'mock-url-von')
  let sandbox
  const resp: SearchResponseIF = mockedSearchResponse[UISearchTypes.BUSINESS_DEBTOR]
  const vonResp: AutoCompleteResponseIF = mockedVonResponse
  const select: SearchTypeIF = SearchTypes[2]

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    // GET autocomplete results
    const get = sandbox.stub(vonAxios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: vonResp
    })))
    wrapper = createComponent(true, '')
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('initially does not display anything with empty search value', async () => {
    wrapper.setProps({ searchValue: '' })
    // 3 ticks: watcher update, method run, results update
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    const autoCompleteNames = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNames.length).toBe(0)
    expect(getLastEvent(wrapper, hideDetails)).toBeFalsy()
    expect(getLastEvent(wrapper, searchValue)).toBeNull()
  })

  it('gets results and displays them when active + searchValue is not empty', async () => {
    wrapper.setProps({ searchValue: 'test' })
    // 3 ticks: watcher update, method run, results update
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
    expect(getLastEvent(wrapper, hideDetails)).toBeTruthy()
    expect(getLastEvent(wrapper, searchValue)).toBeNull()
  })
  it('does not display when inactive', async () => {
    wrapper.setProps({ setAutoCompleteIsActive: false })
    wrapper.setProps({ searchValue: 'test' })
    // 3 ticks: watcher update, method run, results update
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    const autoCompleteNames = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNames.length).toBe(0)
    expect(getLastEvent(wrapper, hideDetails)).toBeFalsy()
    expect(getLastEvent(wrapper, searchValue)).toBeNull()

  })
  it('does closes display when outside clicked', async () => {
    wrapper.setProps({ searchValue: 'test' })
    // 3 ticks: watcher update, method run, results update
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    const autoCompleteNames = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNames.length).toBe(5)
    //simulate clicking outside the autocomplete
    wrapper.vm.$data.autoCompleteIsActive = false
    await Vue.nextTick()
    expect(wrapper.vm.$data.autoCompleteResults).toEqual([])
    expect(wrapper.vm.$data.showAutoComplete).toBeFalsy()
    expect(getLastEvent(wrapper, hideDetails)).toBeFalsy()
    const autoCompleteNamesAfterClose = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNamesAfterClose.length).toBe(0)
  })
  it('emits the search value and closes the list after a name in the list is clicked', async () => {
    wrapper.setProps({ searchValue: 'test' })
    // 3 ticks: watcher update, method run, results update
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    const autoCompleteNames = wrapper.findAll('.auto-complete-item')
    expect(autoCompleteNames.length).toBe(5)
    const selectedText = autoCompleteNames.at(0).text()
    autoCompleteNames.at(0).trigger('click')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchValue)).toEqual(selectedText)
  })
})
