// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { EditParty } from '@/components/parties/party'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-party'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<EditParty> object with the given parameters.
 */
function createComponent (activeIndex: Number, invalidSection: boolean): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((EditParty as any), {
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
    // click business
    const radios = wrapper.findAll('input[type=radio]')
    expect(radios.length).toBe(2)
    radios.at(1).trigger('click')
    await nextTick()

    // no input added
    wrapper.find('#txt-name-party').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Please enter a business name')
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
    await nextTick()

    // no input added
    wrapper.find('#txt-first-party').setValue('')
    wrapper.find('#txt-last-party').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(3)
    expect(messages.at(0).text()).toBe('Please enter a first name')
    expect(messages.at(1).text()).toBe('Please enter a last name')
  })

  it('validates the email', async () => {
    // click individual
    const radios = wrapper.findAll('input[type=radio]')
    expect(radios.length).toBe(2)
    radios.at(0).trigger('click')
    await nextTick()
    wrapper.find('#txt-first-party').setValue('first')
    wrapper.find('#txt-last-party').setValue('person')

    wrapper.find('#txt-email-party').setValue('person@')
    wrapper.find('#txt-email-party').trigger('blur')

    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Please enter a valid email address')
    expect(messages.at(1).text()).toBe('Street address, PO box, rural route, or general delivery address')
  })
})
