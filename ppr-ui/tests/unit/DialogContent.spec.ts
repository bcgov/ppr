import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

import flushPromises from 'flush-promises'
// local
import { ErrorContact } from '@/components/common'
import { DialogContent } from '@/components/dialogs/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const text = '.dialog-text'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Dialog Content tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const localVue = createLocalVue()

    localVue.use(Vuetify)
    wrapper = mount((DialogContent as any),
      {
        localVue,
        store,
        propsData: {},
        vuetify
      })
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component with empty props', async () => {
    expect(wrapper.findComponent(DialogContent).exists()).toBe(true)
    expect(wrapper.vm.$props.setBaseText).toBe('')
    expect(wrapper.vm.$props.setExtraText).toEqual([])
    expect(wrapper.vm.$props.setHasContactInfo).toBe(false)
    expect(wrapper.findAll(text).length).toBe(0)
    expect(wrapper.findComponent(ErrorContact).exists()).toBe(false)
  })

  it('displays text when given', async () => {
    const newBaseText = 'test base text'
    await wrapper.setProps({ setBaseText: newBaseText })
    expect(wrapper.vm.$props.setBaseText).toBe(newBaseText)
    expect(wrapper.findAll(text).length).toBe(1)
    expect(wrapper.findAll(text).at(0).text()).toContain(newBaseText)
  })

  it('Displays extra text when set', async () => {
    const extra1 = 'extra text 1'
    const extra2 = 'extra text 2'
    const extra3 = 'extra text 3'
    const newExtraText = [extra1, extra2, extra3]
    await wrapper.setProps({ setExtraText: newExtraText })
    expect(wrapper.vm.$props.setExtraText).toBe(newExtraText)
    expect(wrapper.findAll(text).length).toBe(newExtraText.length)
    for (let i = 0; i < newExtraText.length; i++) {
      expect(wrapper.findAll(text).at(i).text()).toContain(newExtraText[i])
    }
  })

  it('Displays contact info when given', async () => {
    await wrapper.setProps({ setHasContactInfo: true })
    expect(wrapper.findComponent(ErrorContact).exists()).toBe(true)
  })
})
