// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { HomeLandOwnership } from '@/components/mhrRegistration'
import flushPromises from 'flush-promises'
import { getTestId } from './utils'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()
/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  document.body.setAttribute('data-app', 'true')
  return mount((HomeLandOwnership as any), {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Home Land Ownership', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
    await nextTick()
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders base component', async () => {
    expect(wrapper.findComponent(HomeLandOwnership).exists()).toBe(true)
  })

  it('ownership radio group performs as expected', async () => {
    expect(store.getMhrRegistrationOwnLand).toBe(null)
    expect(wrapper.find(getTestId('ownership-radios'))).toBeTruthy()

    //no instructional paragraph should be displayed initially
    expect(wrapper.find(getTestId('yes-paragraph')).exists()).toBe(false)
    expect(wrapper.find(getTestId('no-paragraph')).exists()).toBe(false)

    const yesRadioBtn = <HTMLInputElement>(
      wrapper.find(getTestId('yes-ownership-radiobtn'))).element
    const noRadioBtn = <HTMLInputElement>(
      wrapper.find(getTestId('no-ownership-radiobtn'))).element

    //no button should be selected initially
    expect(yesRadioBtn.checked).toBeFalsy()
    expect(noRadioBtn.checked).toBeFalsy()

    //click yes button
    wrapper.find(getTestId('yes-ownership-radiobtn')).trigger('click')
    await nextTick()
    expect(store.getMhrRegistrationOwnLand).toBe(true)
    expect(wrapper.find(getTestId('yes-paragraph')).exists()).toBe(true)
    expect(wrapper.find(getTestId('no-paragraph')).exists()).toBe(false)

    //click no button
    wrapper.find(getTestId('no-ownership-radiobtn')).trigger('click')
    await nextTick()
    expect(store.getMhrRegistrationOwnLand).toBe(false)
    expect(wrapper.find(getTestId('yes-paragraph')).exists()).toBe(false)
    expect(wrapper.find(getTestId('no-paragraph')).exists()).toBe(true)
  })
})
