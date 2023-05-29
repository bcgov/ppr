// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import flushPromises from 'flush-promises'

// Components
import { SearchHistory } from '@/components/tables'

// Other
import { mockedSearchHistory, mockedMHRSearchHistory } from './test-data'
import { axios } from '@/utils/axios-ppr'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const historyTable: string = '#search-history-table'
const noResultsInfo: string = '#no-history-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchHistory, {
    localVue,
    store,
    vuetify
  })
}
describe('Test result table with no results', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setSearchHistory([])
    wrapper = createComponent()
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays correct elements for no results', async () => {
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.historyLength).toBe(0)
    expect(wrapper.find(historyTable).exists()).toBe(true)
    const noResultsDisplay = wrapper.findAll(noResultsInfo)
    expect(noResultsDisplay.length).toBe(1)
    expect(noResultsDisplay.at(0).text()).toContain('Your search history will display here')
    expect(wrapper.find('#retry-search-history').exists()).toBe(false)
  })
})

describe('Test result table with results', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    // GET search pdf
    get.returns(new Promise(resolve => resolve({
      data: { test: 'pdf' }
    })))
    await store.setSearchHistory(mockedSearchHistory.searches)
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders and displays correct elements with results', async () => {
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.historyLength).toBe(mockedSearchHistory.searches.length)
    expect(wrapper.vm.searchHistory).toStrictEqual(mockedSearchHistory.searches)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    const historyTableDisplay = wrapper.findAll(historyTable)
    expect(historyTableDisplay.length).toBe(1)
    const downloadMock = jest.fn()
    wrapper.vm.downloadPDF = downloadMock
    const rows = wrapper.findAll('tr')
    // includes header so add 1
    expect(rows.length).toBe(mockedSearchHistory.searches.length + 1)
    mockedSearchHistory.searches.sort((a, b) => {
      if (a.searchDateTime > b.searchDateTime) {
        return -1
      } else if (a.searchDateTime < b.searchDateTime) {
        return 1
      } else {
        return 0
      }
    })
    for (let i = 0; i < mockedSearchHistory.searches.length; i++) {
      const searchQuery = mockedSearchHistory.searches[i].searchQuery
      const searchDate = mockedSearchHistory.searches[i].searchDateTime
      const totalResultsSize = String(mockedSearchHistory.searches[i].totalResultsSize)
      const exactResultsSize = String(mockedSearchHistory.searches[i].exactResultsSize)
      const selectedResultsSize = String(mockedSearchHistory.searches[i].selectedResultsSize)
      const searchId = mockedSearchHistory.searches[i].searchId
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displaySearchValue(searchQuery))
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displayType(searchQuery.type))
      expect(rows.at(i + 1).text()).toContain(searchQuery.clientReferenceId)
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displayDate(searchDate))
      expect(rows.at(i + 1).text()).toContain(totalResultsSize)
      expect(rows.at(i + 1).text()).toContain(exactResultsSize)
      expect(rows.at(i + 1).text()).toContain(selectedResultsSize)
      // PDF only shows for selected result size < 76
      if (Number(selectedResultsSize) < 76) {
        if (!wrapper.vm.isPDFAvailable(mockedSearchHistory.searches[i])) {
          expect(rows.at(i + 1).text()).not.toContain('PDF')
        } else {
          expect(rows.at(i + 1).text()).toContain('PDF')
          wrapper.find(`#pdf-btn-${searchId}`).trigger('click')
          await nextTick()
          expect(downloadMock).toHaveBeenCalledWith(mockedSearchHistory.searches[i])
        }
      }
    }
  })
})

describe('Test result table with results', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    // GET search pdf
    get.returns(new Promise(resolve => resolve({
      data: { test: 'pdf' }
    })))
    await store.setSearchHistory(mockedMHRSearchHistory.searches)
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders and displays correct elements with results', async () => {
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.historyLength).toBe(mockedMHRSearchHistory.searches.length)
    expect(wrapper.vm.searchHistory).toStrictEqual(mockedMHRSearchHistory.searches)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    const historyTableDisplay = wrapper.findAll(historyTable)
    expect(historyTableDisplay.length).toBe(1)
    const downloadMock = jest.fn()
    wrapper.vm.downloadPDF = downloadMock
    const rows = wrapper.findAll('tr')
    // includes header so add 1
    expect(rows.length).toBe(mockedMHRSearchHistory.searches.length + 1)
    mockedMHRSearchHistory.searches.sort((a, b) => {
      if (a.searchDateTime > b.searchDateTime) {
        return -1
      } else if (a.searchDateTime < b.searchDateTime) {
        return 1
      } else {
        return 0
      }
    })
    for (let i = 0; i < mockedMHRSearchHistory.searches.length; i++) {
      const searchQuery = mockedMHRSearchHistory.searches[i].searchQuery
      const searchDate = mockedMHRSearchHistory.searches[i].searchDateTime
      const totalResultsSize = String(mockedMHRSearchHistory.searches[i].totalResultsSize)
      const selectedResultsSize = String(mockedMHRSearchHistory.searches[i].selectedResultsSize)
      const searchId = mockedMHRSearchHistory.searches[i].searchId
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displaySearchValue(searchQuery))
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displayType(searchQuery.type))
      expect(rows.at(i + 1).text()).toContain(searchQuery.clientReferenceId)
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displayDate(searchDate))
      expect(rows.at(i + 1).text()).toContain(totalResultsSize)
      expect(rows.at(i + 1).text()).toContain(selectedResultsSize)
      // PDF only shows for selected result size < 76
      if (Number(selectedResultsSize) < 76) {
        if (!wrapper.vm.isPDFAvailable(mockedMHRSearchHistory.searches[i])) {
          expect(rows.at(i + 1).text()).not.toContain('PDF')
        } else {
          expect(rows.at(i + 1).text()).toContain('PDF')
          wrapper.find(`#pdf-btn-${searchId}`).trigger('click')
          await nextTick()
          expect(downloadMock).toHaveBeenCalledWith(mockedMHRSearchHistory.searches[i])
        }
      }
    }
  })
})

describe('Test result table with error', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setSearchHistory(null)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays correct elements for no results', async () => {
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.historyLength).toBe(0)
    expect(wrapper.find(historyTable).exists()).toBe(true)
    const noResultsDisplay = wrapper.findAll(noResultsInfo)
    expect(noResultsDisplay.at(0).text()).toContain('We were unable to retrieve your search history.')
    expect(wrapper.find('#retry-search-history').exists()).toBe(true)
  })
})

describe('Test table headers', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setSearchHistory(mockedSearchHistory.searches)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('headers for ppr only', async () => {
    await store.setAuthRoles(['ppr'])
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.headers.length).toBe(9)
  })

  it('headers for both mhr and ppr', async () => {
    await store.setAuthRoles(['ppr', 'mhr'])
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.headers.length).toBe(9)
  })
})
