// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { HomeSections } from '@/components/mhrRegistration'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
import HomeSectionsTable from '@/components/tables/mhr/HomeSectionsTable.vue'
import { mockedHomeSections } from './test-data/mock-home-sections'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const addEditHomeSectionBtn = '.add-home-section-btn'
const sectionCounter = '#section-count'
const errorText = '.error-text'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(HomeSections, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Home Sections', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    // Set home sections default
    await store.dispatch('setMhrHomeDescription', { key: 'sections', value: [] })

    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders base component with sub components', async () => {
    expect(wrapper.findComponent(HomeSections).exists()).toBe(true)
    expect(wrapper.findComponent(AddEditHomeSections).exists()).toBe(false) // Hidden by default
    expect(wrapper.findComponent(HomeSectionsTable).exists()).toBe(true)
  })

  it('renders with default values', async () => {
    // Verify Add Section btn
    expect(wrapper.find(addEditHomeSectionBtn).text()).toBe('Add a Section')
    // Verify Section Counter
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 0')
  })

  it('opens the Add Home Section Component when btn is clicked', async () => {
    // Verify hidden by default
    expect(wrapper.findComponent(AddEditHomeSections).exists()).toBe(false)

    // Click the btn
    await wrapper.find(addEditHomeSectionBtn).trigger('click')

    // Verify Add Edit Home Sections component
    expect(wrapper.findComponent(AddEditHomeSections).exists()).toBe(true)
  })

  it('disables the Add/Edit btn when the Add Home Section form is open', async () => {
    // Verify hidden by default
    expect(wrapper.findComponent(AddEditHomeSections).exists()).toBe(false)
    await wrapper.find(addEditHomeSectionBtn).trigger('click')

    expect(wrapper.find(addEditHomeSectionBtn).attributes('disabled')).toBe('disabled')
  })

  it('counts the added Home Sections', async () => {
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 0')
    await store.dispatch('setMhrHomeDescription', { key: 'sections', value: mockedHomeSections })

    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 4')
  })

  it('disables the Add/Edit btn when max sections added and displays error msg', async () => {
    // Verify Default state
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 0')
    expect(wrapper.find(errorText).exists()).toBe(false)

    // Set homeSections
    await store.dispatch('setMhrHomeDescription', { key: 'sections', value: mockedHomeSections })

    // Verify sections added
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 4')

    // Display Error msg when trying to add more sections
    await wrapper.find(addEditHomeSectionBtn).trigger('click')
    expect(wrapper.find(errorText).text()).toBe('Your registration cannot contain more than four sections')
  })
})
