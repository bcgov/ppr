import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, Wrapper } from '@vue/test-utils'
// local
import { ChangeSecuredPartyDialog } from '@/components/dialogs'
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

describe('Confirmation Dialog', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = mount((ChangeSecuredPartyDialog as any), {
      vuetify,
      store,
      propsData: {
        display: true,
        securedPartyName: 'Test Company'
      }
    })
    await Vue.nextTick()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component and executes the correct events', async () => {
    expect(wrapper.findComponent(ChangeSecuredPartyDialog).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find(title).text()).toContain('Change Secured Party?')
    expect(wrapper.find(text).text()).toContain('Test Company')

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
