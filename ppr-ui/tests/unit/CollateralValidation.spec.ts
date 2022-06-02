// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import {
  mockedSelectSecurityAgreement
} from './test-data'

// Components
import { EditCollateral } from '@/components/collateral'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-collateral'
const cancelButtonSelector: string = '#cancel-btn-collateral'
const removeButtonSelector: string = '#remove-btn-collateral'

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
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
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
    expect(messages.length).toBe(4)
    expect(messages.at(0).text()).toBe('Type is required')
    expect(messages.at(2).text()).toBe('Enter the vehicle make')
    expect(messages.at(3).text()).toBe('Enter the vehicle model')
  })

  it('validates invalid year', async () => {
    await wrapper.find('#txt-type-drop').setValue('MV')
    wrapper.find('#txt-serial').setValue('293847298374')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(3000)
    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a valid year')
  })

  it('validates serial number for vehicle', async () => {
    await wrapper.find('#txt-type-drop').setValue('MV')
    await Vue.nextTick()
    wrapper.find('#txt-serial').setValue('234627834628736428734634234872364')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe(
      'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
    )
  })

  it('validates number is correct for manufactured home', async () => {
    wrapper.find('#txt-type-drop').setValue('MH')
    await Vue.nextTick()
    wrapper.find('#txt-man').setValue('444555')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    // messages length is one when correct (because of the YYYY hint for year)
    expect(messages.length).toBe(1)
  })

  it('validates numbers only for manufactured home', async () => {
    wrapper.find('#txt-type-drop').setValue('MH')
    await Vue.nextTick()
    wrapper.find('#txt-man').setValue('123$a')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe(
      'Manufactured Home Registration Number must contain 6 digits'
    )
  })

  it('validates serial number max length for manufactured home', async () => {
    wrapper.find('#txt-type-drop').setValue('MH')
    await Vue.nextTick()
    wrapper.find('#txt-man').setValue('123456')
    wrapper.find('#txt-serial').setValue('123456789012345678901234567890')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe(
      'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
    )
  })

  it('validates serial number max length for manufactured home', async () => {
    wrapper.find('#txt-type-drop').setValue('MH')
    await Vue.nextTick()
    wrapper.find('#txt-man').setValue('123456')
    wrapper.find('#txt-serial').setValue('123456789012345678901234567890')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe(
      'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
    )
  })

  it('validates max lengths', async () => {
    wrapper.find('#txt-type-drop').setValue('MV')
    await Vue.nextTick()
    wrapper.find('#txt-serial').setValue('ABC123')
    wrapper.find('#txt-make').setValue(
      'This is a very long make for a car or any vehicle for that matter but is it too long'
    )
    wrapper.find('#txt-model').setValue(
      'This is a very long model for a car or any vehicle for that matter but is it too long'
    )
    wrapper.find('#txt-years').setValue(2016)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(3)
    expect(messages.at(1).text()).toBe('Maximum 60 characters')
    expect(messages.at(2).text()).toBe('Maximum 60 characters')
  })
})
