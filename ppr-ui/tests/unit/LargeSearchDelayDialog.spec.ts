import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
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
const text: string = '.dialog-text'
const title: string = '.dialog-title'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Delay Dialog', () => {
  let wrapper: Wrapper<any>
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)

  beforeEach(async () => {
    wrapper = mount(LargeSearchDelayDialog,
      {
        localVue,
        store,
        propsData: {
          setDisplay: true,
          setOptions: largeSearchReportDelay,
          setNumberRegistrations: 75
        },
        vuetify
      })
    await Vue.nextTick()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component with the options', async () => {
      const options = largeSearchReportDelay

      expect(wrapper.findComponent(LargeSearchDelayDialog).exists()).toBe(true)
      expect(wrapper.isVisible()).toBe(true)
      expect(wrapper.find(title).text()).toBe(options.title)
      expect(wrapper.find(text).text()).toContain(options.text)
      expect(wrapper.find(accept).exists()).toBe(true)
      wrapper.find(accept).trigger('click')
      await Vue.nextTick()
      expect(getLastEvent(wrapper, proceed)).toEqual(true)
      
  })
})
