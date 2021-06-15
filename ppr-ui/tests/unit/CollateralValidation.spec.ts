// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { EditCollateral } from '@/components/collateral'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn'
const cancelButtonSelector: string = '#cancel-btn'
const removeButtonSelector: string = '#remove-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<EditCollateral> object with the given parameters.
 */
function createComponent (
  activeIndex: Number,
  invalidSection: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditCollateral, {
    localVue,
    propsData: { activeIndex, invalidSection },
    store,
    vuetify
  })
}

describe('Collateral validation tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('validates blank inputs', async () => {
    // no input added
    wrapper.find('#txt-serial').setValue('')
    wrapper.find('#txt-make').setValue('')
    wrapper.find('#txt-model').setValue('')
    wrapper.find('#txt-years').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(5)
    expect(messages.at(0).text()).toBe('Type is required')
    expect(messages.at(1).text()).toBe('Select a vehicle type first')
    expect(messages.at(2).text()).toBe('Enter a valid year')
    expect(messages.at(3).text()).toBe('Enter the vehicle make')
    expect(messages.at(4).text()).toBe('Enter the vehicle model')
  })

  it('validates invalid year', async () => {
    await wrapper.find('#txt-type').setValue('MV')
    wrapper.find('#txt-serial').setValue('293847298374')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(3000)
    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(1).text()).toBe('Enter a valid year')
  })

  it('validates serial number for vehicle', async () => {
    await wrapper.find('#txt-type').setValue('MV')
    await Vue.nextTick()
    wrapper.find('#txt-serial').setValue('234627834628736428734634234872364')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 25 letters')
  })

  it('validates number for manufactured home', async () => {
    wrapper.find('#txt-type').setValue('MH')
    await Vue.nextTick()
    wrapper.find('#txt-serial').setValue('ABCDEF')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Manufactured home registration number must contain 6 digits')
  })
})
