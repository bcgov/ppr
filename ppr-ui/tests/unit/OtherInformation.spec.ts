import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { getTestId } from './utils'
import { OtherInformation } from '@/components/mhrRegistration'

Vue.use(Vuetify)
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  return mount(OtherInformation, {
    localVue,
    store
  })
}

describe('Other Information component', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(OtherInformation).exists()).toBe(true)
  })

  it('show error message for Other Information input', async () => {
    wrapper.find(getTestId('otherRemarks')).exists()
    wrapper.find(getTestId('otherRemarks')).setValue('x'.repeat(150))
    await Vue.nextTick()
    await Vue.nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 140 characters')
  })
})
