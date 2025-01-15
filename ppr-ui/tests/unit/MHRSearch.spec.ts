// Libraries
import { useStore } from '../../src/store/store'

// Components
import { SearchedResultsMhr } from '@/components/tables/mhr'
import { MHRSearch } from '@/pages'

// Other
import { mockedMHRSearchResponse } from './test-data'
import { RouteNames, UIMHRSearchTypes } from '@/enums'
import { createComponent } from './utils'
import { nextTick } from 'vue'

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

  beforeEach(async () => {
    wrapper = await createComponent(MHRSearch, { appReady: true }, RouteNames.MHRSEARCH)
  })

  it('renders Search View with base components', async () => {
    expect(wrapper.findComponent(MHRSearch).exists()).toBe(true)
    // doesn't render unless there are results
    expect(wrapper.find(searchMeta).exists()).toBe(false)
    expect(wrapper.find(resultsInfo).exists()).toBe(false)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.find(folioHeader).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultsMhr).exists()).toBe(false)
  })

  it('renders the Results component and displays search data elements with filled result set.', async () => {
    await store.setManufacturedHomeSearchResults(mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER])
    await nextTick()
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultsMhr).exists()).toBe(true)
  })

  it('renders the Results component and displays search data elements with empty result set.', async () => {
    await store.setManufacturedHomeSearchResults({ ...mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER], totalResultsSize: 0, results: [] })
    await nextTick()
    expect(wrapper.find(noResultsInfo).exists()).toBe(true)
    expect(wrapper.findComponent(SearchedResultsMhr).exists()).toBe(true)
  })
})
