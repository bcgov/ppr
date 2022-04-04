// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { SearchedResultPpr } from '@/components/tables'

// Other
import { searchTableHeaders } from '@/resources'
import { SearchResponseIF } from '@/interfaces'
import { APISearchTypes, UISearchTypes } from '@/enums'
import { mockedSearchResponse } from './test-data'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()
const noResults: SearchResponseIF = {
  maxResultsSize: 1000,
  searchId: '1294373',
  searchDateTime: '2020-02-21T18:56:20Z',
  returnedResultsSize: 0,
  totalResultsSize: 0,
  searchQuery: {
    type: APISearchTypes.SERIAL_NUMBER,
    criteria: {
      value: 'T1234'
    }
  },
  results: []
}

// Input field selectors / buttons
const resultsTable = '#search-results-table'
const noResultsDiv = '#search-no-results-info'
const generateResult = '#btn-generate-result'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchedResultPpr, {
    localVue,
    store,
    vuetify
  })
}
describe('Test result table with no results', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setSearchResults', noResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('doesnt display table if there are no results', async () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(noResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(noResults.totalResultsSize)
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(0)
    const noResultsInfo = wrapper.findAll(noResultsDiv)
    expect(noResultsInfo.length).toBe(1)
    expect(noResultsInfo.at(0).text()).toContain('Nil Result')
    expect(noResultsInfo.at(0).text()).toContain('No registered liens or encumbrances')
    expect(wrapper.findAll(generateResult).length).toBe(1)
  })
})

describe('Serial number results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedSearchResponse[UISearchTypes.SERIAL_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with serial number results data', () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(searchTableHeaders.SERIAL_NUMBER)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
    expect(wrapper.findAll(generateResult).length).toBe(1)
  })

  it('preselects exact results', () => {
    expect(wrapper.vm.$data.exactMatchesLength).toBe(2)
    expect(wrapper.vm.$data.selected).toStrictEqual([testResults.results[0], testResults.results[1]])
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.type)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.model)
    }
  })
})

describe('Individual debtor results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedSearchResponse[UISearchTypes.INDIVIDUAL_DEBTOR]

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with individual debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(searchTableHeaders.INDIVIDUAL_DEBTOR)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
  })

  it('preselects exact results', () => {
    expect(wrapper.vm.$data.exactMatchesLength).toBe(3)
    expect(wrapper.vm.$data.selected).toStrictEqual(
      [testResults.results[0], testResults.results[1], testResults.results[2]])
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].debtor.personName.first)
      if (testResults.results[i].debtor.personName.second) {
        expect(rows.at(i + 1).text()).toContain(testResults.results[i].debtor.personName.second)
      }
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].debtor.personName.last)
      if (testResults.results[i].debtor.birthDate) {
        expect(rows.at(i + 1).text()).toContain(testResults.results[i].debtor.birthDate)
      } else {
        expect(rows.at(i + 1).text().includes('Invalid Date')).toBe(false)
      }
    }
  })
})

describe('Business debtor results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedSearchResponse[UISearchTypes.BUSINESS_DEBTOR]

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with business debtor name results data', () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(searchTableHeaders.BUSINESS_DEBTOR)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
  })

  it('preselects exact results', () => {
    expect(wrapper.vm.$data.exactMatchesLength).toBe(2)
    expect(wrapper.vm.$data.selected).toStrictEqual([testResults.results[0], testResults.results[1]])
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].debtor.businessName)
    }
  })
})

describe('Manufactured home results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedSearchResponse[UISearchTypes.MHR_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with manufactured home results data', () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(searchTableHeaders.MHR_NUMBER)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
  })

  it('preselects exact results', () => {
    expect(wrapper.vm.$data.exactMatchesLength).toBe(2)
    expect(wrapper.vm.$data.selected).toStrictEqual([testResults.results[0], testResults.results[1]])
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.serialNumber)
      expect(rows.at(i + 1).text()).toContain(
        testResults.results[i].vehicleCollateral.manufacturedHomeRegistrationNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.model)
    }
  })
})

describe('Aircraft results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedSearchResponse[UISearchTypes.AIRCRAFT]

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with aircraft results data', () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(searchTableHeaders.AIRCRAFT_DOT)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
  })

  it('preselects exact results', () => {
    expect(wrapper.vm.$data.exactMatchesLength).toBe(2)
    expect(wrapper.vm.$data.selected).toStrictEqual([testResults.results[0], testResults.results[1]])
  })

  it('displays results in the table', async () => {
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header and 2 group headers (exact / similar) so add 3
    expect(rows.length).toBe(testResults.results.length + 3)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.model)
    }
  })
})

describe('Registration number results', () => {
  let wrapper: Wrapper<any>
  const testResults = mockedSearchResponse[UISearchTypes.REGISTRATION_NUMBER]

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with registration number results data', () => {
    expect(wrapper.findComponent(SearchedResultPpr).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(searchTableHeaders.REGISTRATION_NUMBER)
    expect(wrapper.vm.$data.results).toStrictEqual(testResults.results)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(testResults.totalResultsSize)
  })

  it('preselects exact results', () => {
    expect(wrapper.vm.$data.exactMatchesLength).toBe(1)
    expect(wrapper.vm.$data.selected).toStrictEqual([testResults.results[0]])
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
