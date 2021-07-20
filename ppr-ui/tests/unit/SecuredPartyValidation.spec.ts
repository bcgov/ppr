// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { EditParty } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<EditParty> object with the given parameters.
 */
function createComponent (
  activeIndex: Number,
  invalidSection: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditParty, {
    localVue,
    propsData: { activeIndex, invalidSection },
    store,
    vuetify
  })
}

describe('Secured Party validation tests - business', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('validates blank inputs', async () => {
    //click business
    const radios = wrapper.findAll('input[type=radio]')
    expect(radios.length).toBe(2)
    radios.at(1).trigger('click')
    await Vue.nextTick()
    
    // no input added
    wrapper.find('#txt-name').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(6)
    expect(messages.at(0).text()).toBe('Please enter a business name')
    expect(messages.at(1).text()).toBe('This field is required')
  })

  
})

describe('Secured Party validation tests - individual', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('validates blank inputs', async () => {
    // click individual
    const radios = wrapper.findAll('input[type=radio]')
    expect(radios.length).toBe(2)
    radios.at(0).trigger('click')
    await Vue.nextTick()
    
    // no input added
    wrapper.find('#txt-first').setValue('')
    wrapper.find('#txt-last').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(7)
    expect(messages.at(0).text()).toBe('Please enter a first name')
    expect(messages.at(1).text()).toBe('Please enter a last name')
    expect(messages.at(3).text()).toBe('This field is required')
  })

  it('validates the email', async () => {
    // click individual
    const radios = wrapper.findAll('input[type=radio]')
    expect(radios.length).toBe(2)
    radios.at(0).trigger('click')
    await Vue.nextTick()
    wrapper.find('#txt-first').setValue('first')
    wrapper.find('#txt-last').setValue('person')
    
    wrapper.find('#txt-email').setValue('person@')
    wrapper.find('#txt-email').trigger('blur')
    
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Please enter a valid email address.')
  })
  
})

