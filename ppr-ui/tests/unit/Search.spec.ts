import { nextTick } from 'vue'
import { createComponent } from './utils'
import { Search } from '@/pages'
import { RouteNames, UISearchTypes } from '@/enums'
import { useStore } from '@/store/store'
import SearchedResultsPpr from '@/components/tables/ppr/SearchedResultsPpr.vue'
import { SearchTypes } from '@/resources'
import { mockedSearchResponse } from './test-data'

const store = useStore()

const searchMeta = '#search-meta-info'
const resultsInfo = '#results-info'
const noResultsInfo = '#no-results-info'
const folioHeader = '#results-folio-header'

describe('Search component', () => {
  let wrapper: any

  beforeEach(async () => {
    wrapper = await createComponent(Search, {}, RouteNames.SEARCH)
  })

  it('renders Search View with base components', () => {
    expect(wrapper.findComponent(Search).exists()).toBe(true)
    // doesn't render unless there are results
    expect(wrapper.vm.getSearchResults).toBeNull()
    expect(wrapper.find(searchMeta).exists()).toBe(false)
    expect(wrapper.find(resultsInfo).exists()).toBe(false)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.find(folioHeader).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultsPpr).exists()).toBe(false)
  })
  it('renders the Results component and displays search data elements with filled result set.', async () => {
    await store.setSearchedType(SearchTypes[1])
    await store.setSearchResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    wrapper = await createComponent(Search, {}, RouteNames.SEARCH)
    await nextTick()

    expect(store.getSearchResults).toStrictEqual(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    expect(store.getSearchedType).toStrictEqual(SearchTypes[1])
    await nextTick()

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
    expect(wrapper.findComponent(SearchedResultsPpr).exists()).toBe(true)
  })
  it('renders the Results component and displays search data elements with empty result set.', async () => {
    const response = mockedSearchResponse[UISearchTypes.SERIAL_NUMBER]
    response.exactResultsSize = 0
    response.totalResultsSize = 0
    response.selectedResultsSize = 0
    response.results = []
    await store.setSearchedType(SearchTypes[1])
    await store.setSearchResults(response)
    wrapper = await createComponent(Search, {}, RouteNames.SEARCH)
    await nextTick()
    expect(store.getSearchResults).toStrictEqual(response)
    expect(store.getSearchedType).toStrictEqual(SearchTypes[1])
    await nextTick()
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
    expect(wrapper.findComponent(SearchedResultsPpr).exists()).toBe(true)
  })
})
