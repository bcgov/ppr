// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Local
import { RegistrationOtherDialog } from '@/components/dialogs'
import { registrationOtherDialog } from '@/resources/dialogOptions'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Events
const proceed = 'proceed'

// Input field selectors / buttons
const dialogClose = '#close-btn'
const dialogCancel = '#cancel-btn'
const dialogSubmit = '#accept-btn'
const dialogTextField = '#dialog-text-field'

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
function getLastEvent (wrapper: Wrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (display: boolean): Wrapper<any> {
  const attach = '#app'
  const options = { ...registrationOtherDialog }
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((RegistrationOtherDialog as any), {
    localVue,
    propsData: { attach: attach, display: display, options: options },
    store,
    vuetify
  })
}

describe('Registration Other Dialog tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the dialog', async () => {
    expect(wrapper.findComponent(RegistrationOtherDialog).exists()).toBe(true)
    expect(wrapper.findAll('.v-dialog').length).toBe(1)
    expect(wrapper.find('.dialog-title').text()).toContain(registrationOtherDialog.title)
    expect(wrapper.find('.dialog-text').text()).toContain(registrationOtherDialog.text)
    expect(wrapper.find(dialogTextField).exists()).toBe(true)
    expect(wrapper.find(dialogSubmit).text()).toContain(registrationOtherDialog.acceptText)
    expect(wrapper.find(dialogCancel).text()).toContain(registrationOtherDialog.cancelText)
    expect(wrapper.find(dialogClose).exists()).toBe(true)
  })

  it('closes the dialog when pressing the close button', async () => {
    wrapper.find(dialogClose).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })

  it('closes the dialog when pressing the cancel button', async () => {
    wrapper.find(dialogCancel).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })

  it('validates for name of statute before submitting', async () => {
    expect(wrapper.findAll('.v-messages').length).toBe(1)
    expect(wrapper.findAll('.v-messages').at(0).text()).toBe('')
    wrapper.find(dialogSubmit).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBeNull()
    expect(wrapper.findAll('.v-messages').length).toBe(1)
    expect(wrapper.findAll('.v-messages').at(0).text()).toContain('required')
    // click modal submit
    wrapper.find(dialogTextField).setValue('test')
    wrapper.find(dialogSubmit).trigger('click')
    await flushPromises()
    // check emitted other + set other name desc
    expect(store.getStateModel.registration.registrationTypeOtherDesc).toBe('test')
    expect(getLastEvent(wrapper, proceed)).toBe(true)
  })
})
