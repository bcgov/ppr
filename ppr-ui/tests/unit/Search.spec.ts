// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { SearchedResultPpr } from '@/components/tables'
import { Search } from '@/views'

// Other
import mockRouter from './MockRouter'
import { mockedSearchResponse } from './test-data'
import { UISearchTypes } from '@/enums'
import { SearchTypes } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// input field / button selectors
const doneButton = '.search-done-btn'
const searchMeta = '#search-meta-info'
const resultsInfo = '#results-info'
const noResultsInfo = '#no-results-info'
const folioHeader = '#results-folio-header'

describe('Search component', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'search' })
    wrapper = shallowMount(Search, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Search View with base components', () => {
    expect(wrapper.findComponent(Search).exists()).toBe(true)
    // doesn't render unless there are results
    expect(wrapper.vm.getSearchResults).toBeNull()
    expect(wrapper.find(searchMeta).exists()).toBe(false)
    expect(wrapper.find(resultsInfo).exists()).toBe(false)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.find(folioHeader).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(false)
  })
  it('renders the Results component and displays search data elements with filled result set.', async () => {
    wrapper.vm.setSearchedType(SearchTypes[1])
    wrapper.vm.setSearchResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    await Vue.nextTick()
    expect(wrapper.vm.getSearchResults).toStrictEqual(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    expect(wrapper.vm.getSearchedType).toStrictEqual(SearchTypes[1])
    await Vue.nextTick()
    expect(wrapper.vm.folioNumber).toBe(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER].searchQuery.clientReferenceId)
    expect(wrapper.vm.searchType).toBe(SearchTypes[1].searchTypeUI)
    expect(wrapper.vm.searchValue).toBe(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER].searchQuery.criteria.value)
    expect(wrapper.vm.searchTime).toBeDefined()
    const searchMetaDisplay = wrapper.findAll(searchMeta)
    expect(searchMetaDisplay.length).toBe(1)
    expect(searchMetaDisplay.at(0).text()).toContain(wrapper.vm.searchType)
    expect(searchMetaDisplay.at(0).text()).toContain(wrapper.vm.searchValue)
    expect(searchMetaDisplay.at(0).text()).toContain(wrapper.vm.searchTime.trim())
    const resultInfoDisplay = wrapper.findAll(resultsInfo)
    expect(resultInfoDisplay.length).toBe(1)
    expect(resultInfoDisplay.at(0).text()).toContain('Select the registrations you want to include')
    const folioDisplay = wrapper.findAll(folioHeader)
    expect(folioDisplay.length).toBe(1)
    expect(folioDisplay.at(0).text()).toContain(wrapper.vm.folioNumber)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
  })
  it('renders the Results component and displays search data elements with empty result set.', async () => {
    const response = mockedSearchResponse[UISearchTypes.SERIAL_NUMBER]
    response.exactResultsSize = 0
    response.totalResultsSize = 0
    response.selectedResultsSize = 0
    response.results = []
    wrapper.vm.setSearchedType(SearchTypes[1])
    wrapper.vm.setSearchResults(response)
    await Vue.nextTick()
    expect(wrapper.vm.getSearchResults).toStrictEqual(response)
    expect(wrapper.vm.getSearchedType).toStrictEqual(SearchTypes[1])
    await Vue.nextTick()
    expect(wrapper.vm.folioNumber).toBe(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER].searchQuery.clientReferenceId)
    expect(wrapper.vm.searchType).toBe(SearchTypes[1].searchTypeUI)
    expect(wrapper.vm.searchValue).toBe(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER].searchQuery.criteria.value)
    expect(wrapper.vm.searchTime).toBeDefined()
    const searchMetaDisplay = wrapper.findAll(searchMeta)
    expect(searchMetaDisplay.length).toBe(1)
    expect(searchMetaDisplay.at(0).text()).toContain(wrapper.vm.searchType)
    expect(searchMetaDisplay.at(0).text()).toContain(wrapper.vm.searchValue)
    expect(searchMetaDisplay.at(0).text()).toContain(wrapper.vm.searchTime.trim())
    expect(wrapper.find(resultsInfo).exists()).toBe(false)
    const noResultInfoDisplay = wrapper.findAll(noResultsInfo)
    expect(noResultInfoDisplay.length).toBe(1)
    expect(noResultInfoDisplay.at(0).text()).toContain('No Registrations were found.')
    const folioDisplay = wrapper.findAll(folioHeader)
    expect(folioDisplay.length).toBe(1)
    expect(folioDisplay.at(0).text()).toContain(wrapper.vm.folioNumber)
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
  })
})
