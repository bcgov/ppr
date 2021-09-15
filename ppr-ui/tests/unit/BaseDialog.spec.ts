import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'
// local
import { BaseDialog } from '@/components/dialogs'
import { getLastEvent } from './utils'
import { dischargeCancelDialog } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// emitted events
const proceed: string = 'proceed'

// Input field selectors / buttons
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'
const text: string = '.dialog-text'
const title: string = '.dialog-title'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Base Dialog tests', () => {
  let wrapper: Wrapper<any>

  const options = { ...dischargeCancelDialog }

  beforeEach(async () => {
    wrapper = mount(BaseDialog,
      {
        vuetify,
        store,
        propsData: {
          attach: '',
          display: false,
          options: {
            acceptText: 'default accept',
            cancelText: 'default cancel',
            text: 'default text',
            title: 'default title'
          }
        }
      })
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.vm.$props.display).toBe(false)
    expect(wrapper.findAll(title).length).toBe(0)
    expect(wrapper.findAll(text).length).toBe(0)
    expect(wrapper.findAll(accept).length).toBe(0)
    expect(wrapper.findAll(cancel).length).toBe(0)
    await wrapper.setProps({
      attach: '',
      display: true,
      options: options
    })
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.findAll(text).length).toBe(1)
    expect(wrapper.findAll(accept).length).toBe(1)
    expect(wrapper.findAll(cancel).length).toBe(1)
    expect(wrapper.find(title).text()).toBe(options.title)
    expect(wrapper.find(text).text()).toContain(options.text)
    if (options.acceptText) {
      expect(wrapper.find(accept).exists()).toBe(true)
      wrapper.find(accept).trigger('click')
      await Vue.nextTick()
      expect(getLastEvent(wrapper, proceed)).toEqual(true)
    } else {
      expect(wrapper.find(accept).exists()).toBe(false)
    }
    if (options.cancelText) {
      expect(wrapper.find(cancel).exists()).toBe(true)
      wrapper.find(cancel).trigger('click')
      await Vue.nextTick()
      expect(getLastEvent(wrapper, proceed)).toEqual(false)
    } else {
      expect(wrapper.find(cancel).exists()).toBe(false)
    }
  })
})
