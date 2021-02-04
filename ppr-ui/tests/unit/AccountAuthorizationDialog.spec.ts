import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { shallowMount, mount } from '@vue/test-utils'
import { AccountAuthorizationDialog } from '@/components/dialogs'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Account Authorization Dialog', () => {
  it('renders the component properly', () => {
    const wrapper = shallowMount(AccountAuthorizationDialog,
      {
        vuetify,
        store,
        propsData: { dialog: true }
      })
    expect(wrapper.attributes('contentclass')).toBe('account-authorization-dialog')
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find('#dialog-title').text()).toBe('Account Authorization')
    expect(wrapper.findAll('p').length).toBe(2)
    expect(wrapper.findAll('p').at(0).text()).toContain('There was an issue logging in')
    expect(wrapper.find('#dialog-retry-button').exists()).toBe(true)

    wrapper.destroy()
  })

  it('emits an event when retry button is clicked', async () => {
    const wrapper = mount(AccountAuthorizationDialog,
      {
        vuetify,
        store,
        propsData: { dialog: true }
      })

    expect(wrapper.emitted('retry')).toBeUndefined()

    // verify and click retry button
    const retryButton = wrapper.find('#dialog-retry-button')
    expect(retryButton.text()).toBe('Retry')
    retryButton.trigger('click')
    await Vue.nextTick()

    expect(wrapper.emitted('retry').length).toBe(1)

    wrapper.destroy()
  })
})
