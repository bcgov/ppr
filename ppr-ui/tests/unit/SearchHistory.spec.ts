import { nextTick } from 'vue'
import { SearchHistory } from '@/components/tables'
import { createComponent } from './utils'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'
import { mockedMHRSearchHistory, mockedSearchHistory } from './test-data'
import { axe } from 'vitest-axe'
import { createPinia, setActivePinia } from 'pinia'

// Input field selectors / buttons
const historyTable: string = '#search-history-table'
const noResultsInfo: string = '#no-history-info'

describe('Test result table with no results', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    await store.setSearchHistory([])
    wrapper = await createComponent(SearchHistory, null, null, null, [pinia])
    await flushPromises()
  })

  it.skip('should have no accessibility violations', async () => {
    // Run the axe-core accessibility check on the component's HTML
    const results = await axe(wrapper.html())

    expect(results).toBeDefined()
    expect(results.violations).toBeDefined()
    expect(results.violations).toHaveLength(0)
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
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    await store.setSearchHistory(mockedSearchHistory.searches)
    wrapper = await createComponent(SearchHistory, null, null, null, [pinia])
  })

  it('renders and displays correct elements with results', async () => {
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.historyLength).toBe(mockedSearchHistory.searches.length)
    expect(wrapper.vm.searchHistory).toStrictEqual(mockedSearchHistory.searches)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    const historyTableDisplay = wrapper.findAll(historyTable)
    expect(historyTableDisplay.length).toBe(1)
    const downloadMock = vi.fn()
    wrapper.vm.downloadPDF = downloadMock
    const rows = wrapper.findAll('tr')
    // includes header so add 1
    expect(rows.length).toBe(mockedSearchHistory.searches.length + 3)
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
      expect(rows.at(i + 3).text()).toContain(wrapper.vm.displaySearchValue(searchQuery))
      expect(rows.at(i + 3).text()).toContain(wrapper.vm.displayType(searchQuery.type))
      expect(rows.at(i + 3).text()).toContain(searchQuery.clientReferenceId)
      expect(rows.at(i + 3).text()).toContain(wrapper.vm.displayDate(searchDate))
      expect(rows.at(i + 3).text()).toContain(totalResultsSize)
      expect(rows.at(i + 3).text()).toContain(exactResultsSize)
      expect(rows.at(i + 3).text()).toContain(selectedResultsSize)
      // PDF only shows for selected result size < 76
      if (Number(selectedResultsSize) < 76) {
        if (!wrapper.vm.isPDFAvailable(mockedSearchHistory.searches[i])) {
          expect(rows.at(i + 3).text()).not.toContain('PDF')
        } else {
          expect(rows.at(i + 3).text()).toContain('PDF')
          wrapper.find(`#pdf-btn-${searchId}`).trigger('click')
          await nextTick()
          expect(downloadMock).toHaveBeenCalledWith(mockedSearchHistory.searches[i])
        }
      }
    }
  })
})

describe('Test result table with results', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    await store.setSearchHistory(mockedMHRSearchHistory.searches)
    wrapper = await createComponent(SearchHistory, null, null, null, [pinia])
  })

  it('renders and displays correct elements with results', async () => {
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.historyLength).toBe(mockedMHRSearchHistory.searches.length)
    expect(wrapper.vm.searchHistory).toStrictEqual(mockedMHRSearchHistory.searches)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    const historyTableDisplay = wrapper.findAll(historyTable)
    expect(historyTableDisplay.length).toBe(1)
    const downloadMock = vi.fn()
    wrapper.vm.downloadPDF = downloadMock
    const rows = wrapper.findAll('tr')
    // includes header so add 1
    expect(rows.length).toBe(mockedMHRSearchHistory.searches.length + 3)
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
      expect(rows.at(i + 3).text()).toContain(wrapper.vm.displaySearchValue(searchQuery))
      expect(rows.at(i + 3).text()).toContain(wrapper.vm.displayType(searchQuery.type))
      expect(rows.at(i + 3).text()).toContain(searchQuery.clientReferenceId)
      expect(rows.at(i + 3).text()).toContain(wrapper.vm.displayDate(searchDate))
      expect(rows.at(i + 3).text()).toContain(totalResultsSize)
      expect(rows.at(i + 3).text()).toContain(selectedResultsSize)
      // PDF only shows for selected result size < 76
      if (Number(selectedResultsSize) < 76) {
        if (!wrapper.vm.isPDFAvailable(mockedMHRSearchHistory.searches[i])) {
          expect(rows.at(i + 3).text()).not.toContain('PDF')
        } else {
          expect(rows.at(i + 3).text()).toContain('PDF')
          wrapper.find(`#pdf-btn-${searchId}`).trigger('click')
          await nextTick()
          expect(downloadMock).toHaveBeenCalledWith(mockedMHRSearchHistory.searches[i])
        }
      }
    }
  })
})

describe('Test result table with error', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    await store.setSearchHistory(null)
    wrapper = await createComponent(SearchHistory, null, null, null, [pinia])
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
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    await store.setSearchHistory(mockedSearchHistory.searches)
    wrapper = await createComponent(SearchHistory, null, null, null, [pinia])
  })

  it('headers for ppr only', async () => {
    await store.setAuthRoles(['ppr'])
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.headers.length).toBe(6)
  })

  it('headers for both mhr and ppr', async () => {
    await store.setAuthRoles(['ppr', 'mhr'])
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.vm.headers.length).toBe(6)
  })
})
