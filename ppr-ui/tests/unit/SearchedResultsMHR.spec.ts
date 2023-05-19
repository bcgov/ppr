// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { nextTick } from 'vue'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
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
import { mockedMHRSearchResponse, mockedMHRSearchResultsSorted, mockedMHRSearchSelections } from './test-data'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()
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
function createComponent (propsData: any = null): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((SearchedResultMhr as any), {
    localVue,
    store,
    vuetify,
    propsData: { ...propsData }
  })
}

function getUniqueSelectedPPRLienSearches (
  searchResults: ManufacturedHomeSearchResultIF[]
): ManufacturedHomeSearchResultIF[] {
  return uniqBy(searchResults, UIMHRSearchTypeValues.MHRMHR_NUMBER).filter(
    item => item.selected && item.includeLienInfo
  )
}

describe('Test result table with no results', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', noResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('doesnt display table if there are no results', async () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(noResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(noResults.totalResultsSize)
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(0)
    const noResultsInfo = wrapper.findAll(noResultsDiv)
    expect(noResultsInfo.length).toBe(1)
    expect(noResultsInfo.at(0).text()).toContain('No registered homes')
  })
})

describe('Serial number results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRSERIAL_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSearchedType', MHRSearchTypes[4])
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with serial number results data', async () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchSerialNumberHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

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
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }

    // Row with consolidated serial numbers (serial numbers that are identical in search results table)
    const consolidatedRow = 3 // row where activeCount is grater than 1
    expect(rows.at(consolidatedRow).text()).toContain(`(${testResults.results[consolidatedRow - 1].activeCount})`)
  })
})

describe('Serial number results in Review Mode', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRSERIAL_NUMBER]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRSERIAL_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', selectedResults)
    await store.dispatch('setSearchedType', MHRSearchTypes[4])

    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with Serial number data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchSerialNumberHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

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
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', [])
    await store.dispatch('setSearchedType', MHRSearchTypes[2])

    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with individual debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchNameHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

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
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }
  })
})

describe('Owner name name in Review Mode', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHROWNER_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', selectedResults)
    await store.dispatch('setSearchedType', MHRSearchTypes[2])

    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with Owner name data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchNameHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

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
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', [])
    await store.dispatch('setSearchedType', MHRSearchTypes[3])

    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with business debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchNameHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

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
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', selectedResults)
    await store.dispatch('setSearchedType', MHRSearchTypes[3])

    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with business debtor name data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchNameHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

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
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', [])
    await store.dispatch('setSearchedType', MHRSearchTypes[1])

    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchMhrNumberHeaders)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

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
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }
  })
})

describe('Manufactured home results in Review Mode', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRMHR_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', selectedResults)
    await store.dispatch('setSearchedType', MHRSearchTypes[1])

    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(mhSearchMhrNumberHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

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
