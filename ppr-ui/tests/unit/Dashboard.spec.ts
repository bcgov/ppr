// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { Dashboard } from '@/views'
import { Tombstone } from '@/components/common'
import { SearchBar } from '@/components/search'
import { SearchHistory } from '@/components/tables'

// Other
import mockRouter from './MockRouter'
import { mockedSearchResponse, mockedSearchHistory } from './test-data'
import { UISearchTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const searchHeader: string = '#search-header'
const historyHeader: string = '#search-history-header'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Dashboard component', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = shallowMount(Dashboard, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Dashboard View with child components', () => {
    expect(wrapper.findComponent(Dashboard).exists()).toBe(true)
    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
  })
  it('displays the search header', () => {
    const header = wrapper.findAll(searchHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Personal Property Search')
  })
  it('displays default search history header', () => {
    expect(wrapper.vm.getSearchHistory).toBeNull // eslint-disable-line no-unused-expressions
    expect(wrapper.vm.searchHistoryLength).toBe(0)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Searches (0)')
  })
  it('updates the search history header based on history data', async () => {
    wrapper.vm.setSearchHistory(mockedSearchHistory.searches)
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.getSearchHistory?.length).toBe(5)
    expect(wrapper.vm.searchHistoryLength).toBe(5)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Searches (5)')
  })
  it('routes to search after getting a search response', async () => {
    wrapper.vm.setSearchResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe('search')
  })
})
