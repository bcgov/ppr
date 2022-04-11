// Libraries
// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { SearchResultSummary } from '@/components/mhr'

// enums, etc.
import { UIMHRSearchTypes } from '@/enums'

// test stuff
import { getLastEvent } from './utils'
import { mockedMHRSearchResults } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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

  return mount(SearchResultSummary, {
    localVue,
    store,
    vuetify
  })
}

describe('Discharge confirm summary component tests', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.dispatch('setSelectedManufacturedHome', mockedMHRSearchResults[UIMHRSearchTypes.MHRMHR_NUMBER][0])
    
    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders component with search result data', () => {
    const component = wrapper.findComponent(SearchResultSummary)
    const result = mockedMHRSearchResults[UIMHRSearchTypes.MHRMHR_NUMBER][0]
    expect(component.exists()).toBe(true)
    expect(wrapper.vm.$el.querySelectorAll('#registrationNumber')[0].textContent).toContain(result.registrationNumber)
    expect(wrapper.vm.$el.querySelectorAll('#ownerName')[0].textContent).toContain(result.ownerName.first)
    expect(wrapper.vm.$el.querySelectorAll('#ownerName')[0].textContent).toContain(result.ownerName.last)
    expect(wrapper.vm.$el.querySelectorAll('#status')[0].textContent).toContain(result.status)
    expect(wrapper.vm.$el.querySelectorAll('#yearMakeModel')[0].textContent).toContain(result.year)
    expect(wrapper.vm.$el.querySelectorAll('#yearMakeModel')[0].textContent).toContain(result.make)
    expect(wrapper.vm.$el.querySelectorAll('#yearMakeModel')[0].textContent).toContain(result.model)
    expect(wrapper.vm.$el.querySelectorAll('#serialNumber')[0].textContent).toContain(result.serialNumber)
    expect(wrapper.vm.$el.querySelectorAll('#homeLocation')[0].textContent).toContain(result.homeLocation)
    
    expect(wrapper.findAll('#includeLien').length).toBe(1)
  })

 })
