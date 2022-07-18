// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { SearchedResultMhr } from '@/components/tables'

// Other
import { manufacturedHomeSearchTableHeaders, manufacturedHomeSearchTableHeadersReview } from '@/resources'
import { ManufacturedHomeSearchResponseIF } from '@/interfaces'
import { APIMHRSearchTypes, UIMHRSearchTypes } from '@/enums'
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
    type: APIMHRSearchTypes.MHRSERIAL_NUMBER,
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
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchedResultMhr, {
    localVue,
    store,
    vuetify,
    propsData: { ...propsData }
  })
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
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with serial number results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('5 homes found')
    expect(wrapper.find('#active-results-count').text()).toBe('2 active homes')
    expect(wrapper.find('#selected-results-count').text()).toBe('0 homes selected + 0 lien search')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (Active, Exempt, Historical) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)

    const groupHeaders = wrapper.findAll('.group-header')
    expect(groupHeaders.at(0).text()).toBe('ACTIVE OWNERS (2)')
    expect(groupHeaders.at(1).text()).toBe('EXEMPT OWNERS (2)')

    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].mhrNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].baseInformation.model)
    }
  })
})

describe('Serial number results in Review Mode', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRSERIAL_NUMBER]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRSERIAL_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', selectedResults)
    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with Serial number data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toBe('2 Manufactured Homes')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes group categories (Active)
    expect(rows.length).toBe(selectedResults.length + 2)
  })
})

describe('Owner name debtor results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', [])
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with individual debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('5 homes found')
    expect(wrapper.find('#active-results-count').text()).toBe('2 active homes')
    expect(wrapper.find('#selected-results-count').text()).toBe('0 homes selected + 0 lien search')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (Active, Exempt, Historical) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)

    const groupHeaders = wrapper.findAll('.group-header')
    expect(groupHeaders.at(0).text()).toBe('ACTIVE OWNERS (2)')
    expect(groupHeaders.at(1).text()).toBe('EXEMPT OWNERS (2)')

    for (let i; i < testResults.results; i++) {
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
    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with Owner name data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toBe('1 Manufactured Homes')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes group categories (Active)
    expect(rows.length).toBe(selectedResults.length + 2)
  })
})

describe('Business debtor results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', [])
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with business debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('5 homes found')
    expect(wrapper.find('#active-results-count').text()).toBe('2 active homes')
    expect(wrapper.find('#selected-results-count').text()).toBe('0 homes selected + 0 lien search')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (Active, Exempt) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)

    const groupHeaders = wrapper.findAll('.group-header')
    expect(groupHeaders.at(0).text()).toBe('ACTIVE OWNERS (2)')
    expect(groupHeaders.at(1).text()).toBe('EXEMPT OWNERS (2)')

    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].mhrNumber)
    }
  })
})

describe('Business debtor results in Review Mode', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]
  const selectedResults = mockedMHRSearchSelections[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', selectedResults)
    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with business debtor name data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toBe('2 Manufactured Homes')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes group categories (Active, Exempt)
    expect(rows.length).toBe(selectedResults.length + 3)
  })
})

describe('Manufactured home results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
  const sortedResults = mockedMHRSearchResultsSorted[UIMHRSearchTypes.MHRMHR_NUMBER]
  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
    await store.dispatch('setSelectedManufacturedHomes', [])
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeaders)
    expect(wrapper.vm.$data.results).toStrictEqual(sortedResults)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(true)
    expect(wrapper.find('#home-results-count').text()).toBe('5 homes found')
    expect(wrapper.find('#active-results-count').text()).toBe('2 active homes')
    expect(wrapper.find('#selected-results-count').text()).toBe('0 homes selected + 0 lien search')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(true)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(true)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(true)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (active / exempt / historical) so add 3
    expect(rows.length).toBe(testResults.results.length + 4)

    const groupHeaders = wrapper.findAll('.group-header')
    expect(groupHeaders.at(0).text()).toBe('ACTIVE OWNERS (2)')
    expect(groupHeaders.at(1).text()).toBe('EXEMPT OWNERS (2)')
    expect(groupHeaders.at(2).text()).toBe('HISTORIC OWNERS (1)')

    for (let i; i < testResults.results; i++) {
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
    wrapper = createComponent({ isReviewMode: true })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
    expect(wrapper.vm.$data.headers).toStrictEqual(manufacturedHomeSearchTableHeadersReview)
    expect(wrapper.vm.$data.results).toStrictEqual(selectedResults)

    // Verify base mode features
    expect(wrapper.find('#search-summary-info').exists()).toBe(false)
    expect(wrapper.find('#review-results-count').text()).toBe('3 Manufactured Homes')
    expect(wrapper.find('#review-confirm-btn').exists()).toBe(false)
    expect(wrapper.find('#select-all-checkbox').exists()).toBe(false)
    expect(wrapper.find('#select-all-lien-checkbox').exists()).toBe(false)
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes group categories (Active, Exempt, Historical)
    expect(rows.length).toBe(selectedResults.length + 3)
  })
})
