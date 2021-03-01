// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { Result } from '@/components/results'

// Other
import { SearchTypes, tableHeaders } from '@/resources'
import { SearchResponseIF, SearchTypeIF } from '@/interfaces'
import { APISearchTypes } from '@/enums'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()
const testResults: SearchResponseIF = {
  maxResultsSize: 1000,
  searchId: '1294373',
  searchDateTime: '2020-02-21T18:56:20Z',
  returnedResultsSize: 8,
  totalResultsSize: 8,
  searchQuery: {
    type: APISearchTypes.SERIAL_NUMBER,
    criteria: {
      value: 'T1234'
    }
  },
  results: [
    {
      matchType: 'EXACT',
      baseRegistrationNumber: '023001B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622994', year: 2018, make: 'HYUNDAI', model: 'TUCSON' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B2',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622995', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B8',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622996', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B7',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622997', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B6',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622998', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B5',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622999', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B4',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU623000', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    },
    {
      matchType: 'SIMILAR',
      baseRegistrationNumber: '023001B3',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: { type: 'MV', serialNumber: 'KM8J3CA46JU622992', year: 2018, make: 'TOYOTA', model: 'COROLLA' }
    }
  ]
}
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
const resultsTable: string = '.results-table'
const noResultsDiv: string = '.no-results-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Search> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(Result, {
    localVue,
    store,
    vuetify
  })
}

describe('Test result table with results', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setSearchResults', testResults)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Results Component with serial number results data', () => {
    expect(wrapper.findComponent(Result).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(testResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.headers).toStrictEqual(tableHeaders.SERIAL_NUMBER)
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
    // includes header so add 1
    expect(rows.length).toBe(testResults.results.length + 1)
    for (let i; i < testResults.results; i++) {
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.serialNumber)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.type)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.year)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.make)
      expect(rows.at(i + 1).text()).toContain(testResults.results[i].vehicleCollateral.model)
    }
  })
})
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
    expect(wrapper.findComponent(Result).exists()).toBe(true)
    expect(wrapper.vm.$data.searched).toBeTruthy()
    expect(wrapper.vm.$data.searchValue).toEqual(noResults.searchQuery.criteria.value)
    expect(wrapper.vm.$data.totalResultsLength).toEqual(noResults.totalResultsSize)
    const datatable = wrapper.findAll(resultsTable)
    expect(datatable.length).toBe(0)
    const noResultsInfo = wrapper.findAll(noResultsDiv)
    expect(noResultsInfo.length).toBe(1)
    expect(noResultsInfo.at(0).text()).toContain('No registrations were found for the Serial Number:')
    expect(noResultsInfo.at(0).text()).toContain(noResults.searchQuery.criteria.value)
  })
})
