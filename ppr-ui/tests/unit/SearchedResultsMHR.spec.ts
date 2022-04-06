// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { SearchedResultMhr } from '@/components/tables'

// Other
import { manufacturedHomeSearchTableHeaders } from '@/resources'
import { ManufacturedHomeSearchResponseIF } from '@/interfaces'
import { APIMHRSearchTypes, UIMHRSearchTypes } from '@/enums'
import { mockedMHRSearchResponse } from './test-data'

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
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchedResultMhr, {
    localVue,
    store,
    vuetify
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
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (active / exempt) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].registrationNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].model)
    }
  })
})

describe('Owner name debtor results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
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
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].registrationNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].model)
    }
  })
})

describe('Business debtor results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
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
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].registrationNumber)
    }
  })
})

describe('Manufactured home results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setManufacturedHomeSearchResults', testResults)
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
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
  })


  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].registrationNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].model)
    }
  })
})



