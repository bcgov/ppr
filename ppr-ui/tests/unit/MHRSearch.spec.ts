// Libraries
import { useStore } from '../../src/store/store'

// Components
import { SearchedResultMhr } from '@/components/tables'
import { MHRSearch } from '@/views'

// Other
import { mockedMHRSearchResponse } from './test-data'
import { RouteNames, UIMHRSearchTypes } from '@/enums'
import { createComponent } from './utils'

const store = useStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// input field / button selectors
const searchMeta = '#search-meta-info'
const resultsInfo = '#results-info'
const noResultsInfo = '#no-results-info'
const folioHeader = '#results-folio-header'

describe('Search component', () => {
  let wrapper: any
  const { assign } = window.location

  it('renders Search View with base components', async () => {
    wrapper = await createComponent(MHRSearch, { appReady: true }, RouteNames.MHRSEARCH)
    expect(wrapper.findComponent(MHRSearch).exists()).toBe(true)
    // doesn't render unless there are results
    expect(wrapper.find(searchMeta).exists()).toBe(false)
    expect(wrapper.find(resultsInfo).exists()).toBe(false)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.find(folioHeader).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(false)
  })

  it('renders the Results component and displays search data elements with filled result set.', async () => {
    await store.setManufacturedHomeSearchResults(mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER])
    wrapper = await createComponent(MHRSearch, { appReady: true }, RouteNames.MHRSEARCH)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
  })

  it('renders the Results component and displays search data elements with empty result set.', async () => {
    const response = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
    response.totalResultsSize = 0
    response.results = []
    await store.setManufacturedHomeSearchResults(response)
    wrapper = await createComponent(MHRSearch, { appReady: true }, RouteNames.MHRSEARCH)
    expect(wrapper.find(noResultsInfo).exists()).toBe(true)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
  })
})
