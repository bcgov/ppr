import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
// local
import { LargeSearchResultDialog, BaseDialog } from '@/components/dialogs'
import {
  largeSearchReportError
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

describe('Large Search Result Dialog', () => {
  let wrapper: Wrapper<any>
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)

  beforeEach(async () => {
    wrapper = mount(LargeSearchResultDialog,
      {
        localVue,
        store,
        propsData: {
          setDisplay: true,
          setOptions: largeSearchReportError,
          setNumberRegistrations: 75
        },
        vuetify
      })
    await Vue.nextTick()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component with all options', async () => {
      const options = largeSearchReportError

      expect(wrapper.findComponent(LargeSearchResultDialog).exists()).toBe(true)
      expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
      expect(wrapper.isVisible()).toBe(true)
      expect(wrapper.find(title).text()).toBe(options.title)
      // number of registrations
      expect(wrapper.find(text).text()).toContain('75 registrations')
      expect(wrapper.find(accept).exists()).toBe(true)
      wrapper.find(accept).trigger('click')
      await Vue.nextTick()
      expect(getLastEvent(wrapper, proceed)).toEqual(true)
    
      expect(wrapper.find(cancel).exists()).toBe(true)
      wrapper.find(cancel).trigger('click')
      await Vue.nextTick()
      expect(getLastEvent(wrapper, proceed)).toEqual(false)
  
  })
})
