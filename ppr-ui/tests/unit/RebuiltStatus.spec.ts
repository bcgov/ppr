import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { getTestId } from './utils'
import { RebuiltStatus } from '@/components/mhrRegistration'

Vue.use(Vuetify)
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()

  return mount((RebuiltStatus as any), {
    localVue,
    store
  })
}

describe('Rebuilt Status component', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(RebuiltStatus).exists()).toBe(true)
  })

  it('show error message for text area input', async () => {
    wrapper.find('#rebuilt-status-text').exists()
    wrapper.find('#rebuilt-status-text').setValue('x'.repeat(290))
    await nextTick()
    await nextTick()

    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 280 characters')
  })
})
