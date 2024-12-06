// Libraries
import { useStore } from '../../src/store/store'

// Components
import { AddEditHomeSections, HomeSections } from '@/components/mhrRegistration'
import { mockedHomeSections } from './test-data/mock-home-sections'
import { createComponent } from './utils'
import { HomeSectionsTable } from '@/components/tables/mhr'

const store = useStore()

const addEditHomeSectionBtn = '.add-home-section-btn'
const sectionCounter = '#section-count'
const errorText = '.error-text'

describe('Home Sections', () => {
  let wrapper

  beforeEach(async () => {
    // Set home sections default
    await store.setMhrHomeDescription({ key: 'sections', value: [] })
    wrapper = await createComponent(HomeSections)
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
    expect(wrapper.find(addEditHomeSectionBtn).getCurrentComponent().props.disabled).toBe(true)
  })

  it('counts the added Home Sections', async () => {
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 0')
    await store.setMhrHomeDescription({ key: 'sections', value: mockedHomeSections })

    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 4')
  })

  it('disables the Add/Edit btn when max sections added and displays error msg', async () => {
    // Verify Default state
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 0')
    expect(wrapper.find(errorText).exists()).toBe(false)

    // Set homeSections
    await store.setMhrHomeDescription({ key: 'sections', value: mockedHomeSections })

    // Verify sections added
    expect(wrapper.find(sectionCounter).text()).toBe('Number of Sections: 4')

    // Display Error msg when trying to add more sections
    await wrapper.find(addEditHomeSectionBtn).trigger('click')
    expect(wrapper.find(errorText).text()).toBe('Your registration cannot contain more than four sections')
  })
})
