// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { EditDebtor } from '@/components/parties/debtor'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-debtor'
const cancelButtonSelector: string = '#cancel-btn-debtor'
const removeButtonSelector: string = '#remove-btn-debtor'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<EditDebtor> object with the given parameters.
 */
function createComponent (
  activeIndex: Number,
  isBusiness: boolean,
  invalidSection: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditDebtor, {
    localVue,
    propsData: { activeIndex, isBusiness, invalidSection },
    store,
    vuetify
  })
}

describe('Debtor validation tests - business', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(-1, true, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('validates blank inputs', async () => {
    // no input added
    wrapper.find('#txt-name-debtor').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Please enter a business name')
  })
})

describe('Debtor validation tests - individual', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(-1, false, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('validates blank inputs', async () => {
    // no input added
    wrapper.find('#txt-first-debtor').setValue('')
    wrapper.find('#txt-last-debtor').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(4)
    expect(messages.at(0).text()).toBe('Please enter a first name')
    expect(messages.at(2).text()).toBe('Please enter a last name')
  })

  it('validates the birthday', async () => {
    // no input added
    wrapper.find('#txt-first-debtor').setValue('Joe')
    wrapper.find('#txt-last-debtor').setValue('Louis')
    wrapper.find('#txt-month').setValue('13')
    wrapper.find('#txt-year').setValue('1700')
    wrapper.find('#txt-day').setValue('99')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(5)
    expect(messages.at(1).text()).toBe('Please enter a valid month')
    expect(messages.at(2).text()).toBe('Please enter a valid day')
    expect(messages.at(3).text()).toBe('Please enter a valid year')
  })
})
