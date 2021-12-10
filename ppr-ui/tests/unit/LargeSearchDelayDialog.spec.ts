import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, Wrapper } from '@vue/test-utils'
// local
import { LargeSearchDelayDialog } from '@/components/dialogs'
import {
  largeSearchReportDelay
} from '@/resources/dialogOptions'
import { getLastEvent } from './utils'

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

describe('Error Dialog', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = mount(LargeSearchDelayDialog,
      {
        vuetify,
        store,
        propsData: {
          setDisplay: true,
          setOptions: largeSearchReportDelay,
          setNumberRegistrations: 75
        }
      })
    await Vue.nextTick()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component with all error options', async () => {
      const options = largeSearchReportDelay
      wrapper.setProps({
        attach: '',
        display: true,
        options: options
      })
      await Vue.nextTick()

      expect(wrapper.findComponent(LargeSearchDelayDialog).exists()).toBe(true)
      expect(wrapper.isVisible()).toBe(true)
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
