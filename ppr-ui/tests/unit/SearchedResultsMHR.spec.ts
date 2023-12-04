// Libraries
import { useStore } from '../../src/store/store'
import { uniqBy } from 'lodash'
// Components
import { SearchedResultMhr } from '@/components/tables'
// Other
import {
  MHRSearchTypes,
  mhSearchMhrNumberHeaders,
  mhSearchMhrNumberHeadersReview,
  mhSearchNameHeaders,
  mhSearchNameHeadersReview,
  mhSearchSerialNumberHeaders,
  mhSearchSerialNumberHeadersReview
} from '@/resources'
import { ManufacturedHomeSearchResponseIF, ManufacturedHomeSearchResultIF } from '@/interfaces'
import { APIMHRSearchTypes, UIMHRSearchTypes, UIMHRSearchTypeValues } from '@/enums'
import { mockedMHRSearchResponse, mockedMHRSearchSelections } from './test-data'
import { createComponent } from './utils'

const store = useStore()

const noResults: ManufacturedHomeSearchResponseIF = {
  searchId: '1294373',
  searchDateTime: '2020-02-21T18:56:20Z',
  totalResultsSize: 0,
  searchQuery: {
    type: APIMHRSearchTypes.MHROWNER_NAME,
    criteria: {
      value: 'T1234'
    }
  },
  results: []
}

// Input field selectors / buttons
const resultsTable = '#mh-search-results-table'
const noResultsDiv = '#search-no-results-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultMhr> object with the given parameters.
 */
// function createComponent (propsData: any = null) {
//   const localVue = createLocalVue()
//   localVue.use(Vuetify)
//   document.body.setAttribute('data-app', 'true')
//   return mount((SearchedResultMhr as any), {
//     localVue,
//     store,
//     vuetify,
//     propsData: { ...propsData }
//   })
// }

function getUniqueSelectedPPRLienSearches (
  searchResults: ManufacturedHomeSearchResultIF[]
): ManufacturedHomeSearchResultIF[] {
  return uniqBy(searchResults, UIMHRSearchTypeValues.MHRMHR_NUMBER).filter(
    item => item.selected && item.includeLienInfo
  )
}

describe('Test result table with no results', () => {
  let wrapper

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(noResults)
    wrapper = await createComponent(SearchedResultMhr)
  })

  it('does not display table if there are no results', async () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.searched).toBeTruthy()
    expect(wrapper.vm.searchValue).toEqual(noResults.searchQuery.criteria.value)
    expect(wrapper.vm.totalResultsLength).toEqual(noResults.totalResultsSize)
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(0)
    const noResultsInfo = wrapper.findAll(noResultsDiv)
    expect(noResultsInfo.length).toBe(1)
    expect(noResultsInfo.at(0).text()).toContain('No registered homes')
  })
})

describe('Serial number results', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRSERIAL_NUMBER]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSearchedType(MHRSearchTypes[4])
    wrapper = await createComponent(SearchedResultMhr)
  })

  it('renders Results Component with serial number results data', async () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.searched).toBeTruthy()
    expect(wrapper.vm.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchSerialNumberHeaders)
    expect(wrapper.vm.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('Matches Found: 5')
    expect(wrapper.find('#selected-results-count').text()).toBe('Matches Selected: 0')
    expect(wrapper.find('#selected-lien-count').text()).toBe('PPR Lien Searches Selected: 0')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    expect(wrapper.findAll(resultsTable).length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(testResults.results.length + 1)

    for (let i = 0; i < testResults.results.length; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].mhrNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(String(testResults.results[i].baseInformation.year))
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }

    // Row with consolidated serial numbers (serial numbers that are identical in search results table)
    const consolidatedRow = 3 // row where activeCount is grater than 1
    expect(rows.at(consolidatedRow).text()).toContain(`(${testResults.results[consolidatedRow - 1].activeCount})`)
  })
})

describe('Serial number results in Review Mode', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRSERIAL_NUMBER]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRSERIAL_NUMBER]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes(selectedResults)
    await store.setSearchedType(MHRSearchTypes[4])

    wrapper = await createComponent(SearchedResultMhr, { isReviewMode: true })

  })

  it('renders Results Component with Serial number data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchSerialNumberHeadersReview)
    expect(wrapper.vm.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toContain('Matches Selected: 2')
    expect(wrapper.find('#review-results-count').text()).toContain('Registrations: 1')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(selectedResults).length
    expect(wrapper.find('#review-results-count').text()).toContain('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(selectedResults.length + 1)
  })
})

describe('Owner name debtor results', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes([])
    await store.setSearchedType(MHRSearchTypes[2])

    wrapper = await createComponent(SearchedResultMhr)
  })

  it('renders Results Component with individual debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.searched).toBeTruthy()
    expect(wrapper.vm.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchNameHeaders)
    expect(wrapper.vm.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('Matches Found: 5')
    expect(wrapper.find('#selected-results-count').text()).toBe('Matches Selected: 0')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(testResults.results).length
    expect(wrapper.find('#selected-lien-count').text()).toBe('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(testResults.results.length + 1)

    for (let i = 0; i < testResults.results.length; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].mhrNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(String(testResults.results[i].baseInformation.year))
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }
  })
})

describe('Owner name name in Review Mode', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHROWNER_NAME]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes(selectedResults)
    await store.setSearchedType(MHRSearchTypes[2])

    wrapper = await createComponent(SearchedResultMhr, { isReviewMode: true })
  })

  it('renders Results Component with Owner name data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchNameHeadersReview)
    expect(wrapper.vm.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toContain('Matches Selected: 1')
    expect(wrapper.find('#review-results-count').text()).toContain('Registrations: 1')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(selectedResults).length
    expect(wrapper.find('#review-results-count').text()).toContain('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(selectedResults.length + 1)
  })
})

describe('Business organization results', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes([])
    await store.setSearchedType(MHRSearchTypes[3])

    wrapper = await createComponent(SearchedResultMhr)
  })

  it('renders Results Component with business debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.searched).toBeTruthy()
    expect(wrapper.vm.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchNameHeaders)
    expect(wrapper.vm.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('Matches Found: 5')
    expect(wrapper.find('#selected-results-count').text()).toBe('Matches Selected: 0')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(testResults.results).length
    expect(wrapper.find('#selected-lien-count').text()).toBe('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(testResults.results.length + 1)

    for (let i = 0; i < testResults.results.length; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].mhrNumber)
    }
  })
})

describe('Business organization results in Review Mode', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes(selectedResults)
    await store.setSearchedType(MHRSearchTypes[3])

    wrapper = await createComponent(SearchedResultMhr, { isReviewMode: true })
  })

  it('renders Results Component with business debtor name data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchNameHeadersReview)
    expect(wrapper.vm.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toContain('Matches Selected: 2')
    expect(wrapper.find('#review-results-count').text()).toContain('Registrations: 1')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(selectedResults).length
    expect(wrapper.find('#review-results-count').text()).toContain('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(selectedResults.length + 1)
  })
})

describe('Manufactured home results', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes([])
    await store.setSearchedType(MHRSearchTypes[1])

    wrapper = await createComponent(SearchedResultMhr)
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.searched).toBeTruthy()
    expect(wrapper.vm.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchMhrNumberHeaders)
    expect(wrapper.vm.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('Matches Found: 5')
    expect(wrapper.find('#selected-results-count').text()).toBe('Matches Selected: 0')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(testResults.results).length
    expect(wrapper.find('#selected-lien-count').text()).toBe('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(testResults.results.length + 1)

    for (let i = 0; i < testResults.results.length; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].mhrNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(String(testResults.results[i].baseInformation.year))
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }
  })
})

describe('Manufactured home results in Review Mode', () => {
  let wrapper
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRMHR_NUMBER]

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(testResults)
    await store.setSelectedManufacturedHomes(selectedResults)
    await store.setSearchedType(MHRSearchTypes[1])

    wrapper = await createComponent(SearchedResultMhr, { isReviewMode: true })
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.headers).toStrictEqual(mhSearchMhrNumberHeadersReview)
    expect(wrapper.vm.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toContain('Matches Selected: 3')
    expect(wrapper.find('#review-results-count').text()).toContain('Registrations: 1')
    const pprLiensLength = getUniqueSelectedPPRLienSearches(selectedResults).length
    expect(wrapper.find('#review-results-count').text()).toContain('PPR Lien Searches Selected: ' + pprLiensLength)
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(selectedResults.length + 1)
  })
})
