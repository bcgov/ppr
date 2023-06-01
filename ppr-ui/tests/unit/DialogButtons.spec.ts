import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

import flushPromises from 'flush-promises'
// local
import { DialogButtons } from '@/components/dialogs/common'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// emitted events
const proceed: string = 'proceed'

// Input field selectors / buttons
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Dialog Button tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const localVue = createLocalVue()

    localVue.use(Vuetify)
    wrapper = mount((DialogButtons as any),
      {
        localVue,
        store,
        propsData: {
          setAcceptText: '',
          setCancelText: ''
        },
        vuetify
      })
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(DialogButtons).exists()).toBe(true)
    expect(wrapper.vm.$props.setAcceptText).toBe('')
    expect(wrapper.vm.$props.setCancelText).toBe('')
    expect(wrapper.findAll(accept).length).toBe(0)
    expect(wrapper.findAll(cancel).length).toBe(0)
  })

  it('shows buttons when given', async () => {
    const newAcceptText = 'accept'
    const newCancelText = 'cancel'
    await wrapper.setProps({ setAcceptText: newAcceptText })
    expect(wrapper.vm.$props.setAcceptText).toBe(newAcceptText)
    expect(wrapper.vm.$props.setCancelText).toBe('')
    expect(wrapper.findAll(accept).length).toBe(1)
    expect(wrapper.find(accept).text()).toContain(newAcceptText)
    expect(wrapper.findAll(cancel).length).toBe(0)
    await wrapper.setProps({ setCancelText: newCancelText })
    expect(wrapper.vm.$props.setAcceptText).toBe(newAcceptText)
    expect(wrapper.vm.$props.setCancelText).toBe(newCancelText)
    expect(wrapper.findAll(accept).length).toBe(1)
    expect(wrapper.find(accept).text()).toContain(newAcceptText)
    expect(wrapper.findAll(cancel).length).toBe(1)
    expect(wrapper.find(cancel).text()).toContain(newCancelText)
  })

  it('Emits the button actions', async () => {
    await wrapper.setProps({
      setAcceptText: 'accept',
      setCancelText: 'cancel'
    })
    expect(wrapper.find(accept).exists()).toBe(true)
    await wrapper.find(accept).trigger('click')
    expect(getLastEvent(wrapper, proceed)).toEqual(true)
    expect(wrapper.find(cancel).exists()).toBe(true)
    await wrapper.find(cancel).trigger('click')
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
  })
})
