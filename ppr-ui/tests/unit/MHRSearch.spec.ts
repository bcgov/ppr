// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { SearchedResultMhr } from '@/components/tables'
import { MHRSearch } from '@/views'

// Other
import mockRouter from './MockRouter'
import { mockedMHRSearchResponse } from './test-data'
import { UIMHRSearchTypes } from '@/enums'
import { MHRSearchTypes } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// input field / button selectors
const searchMeta = '#search-meta-info'
const resultsInfo = '#results-info'
const noResultsInfo = '#no-results-info'
const folioHeader = '#results-folio-header'

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
    await router.push({ name: 'mhr-search' })
    wrapper = shallowMount((MHRSearch as any), { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Search View with base components', () => {
    expect(wrapper.findComponent(MHRSearch).exists()).toBe(true)
    // doesn't render unless there are results
    expect(wrapper.find(searchMeta).exists()).toBe(false)
    expect(wrapper.find(resultsInfo).exists()).toBe(false)
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.find(folioHeader).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(false)
  })
  it('renders the Results component and displays search data elements with filled result set.', async () => {
    await store.dispatch('setManufacturedHomeSearchResults', mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER])
    expect(wrapper.find(noResultsInfo).exists()).toBe(false)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
  })
  it('renders the Results component and displays search data elements with empty result set.', async () => {
    const response = mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER]
    response.totalResultsSize = 0
    response.results = []
    await store.dispatch('setManufacturedHomeSearchResults', response)
    expect(wrapper.find(noResultsInfo).exists()).toBe(true)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
  })
})
