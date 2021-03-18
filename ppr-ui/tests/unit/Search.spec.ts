// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { SearchedResult } from '@/components/results'
import { Search } from '@/views'
import { SearchBar } from '@/components/search'

// Other
import mockRouter from './MockRouter'
import { mockedSearchResponse } from './test-data'
import { UISearchTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// input field / button selectors
const doneButton = '.search-done-btn'

describe('Search component', () => {
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
    await router.push({ name: 'search' })
    wrapper = shallowMount(Search, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Search View with base components', () => {
    expect(wrapper.findComponent(Search).exists()).toBe(true)
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    // doesn't render unless there are results
    expect(wrapper.vm.getSearchResults).toBeNull()
    expect(wrapper.find(doneButton).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResult).exists()).toBe(false)
    wrapper.vm.setSearchResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
  })
  it('renders the Results component when there are results.', async () => {
    wrapper.vm.setSearchResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    await Vue.nextTick()
    expect(wrapper.vm.getSearchResults).toStrictEqual(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    expect(wrapper.find(doneButton).exists()).toBe(true)
    expect(wrapper.findComponent(SearchedResult).exists()).toBe(true)
  })
})
