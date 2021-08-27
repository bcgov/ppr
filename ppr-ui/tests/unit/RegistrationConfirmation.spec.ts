import sinon from 'sinon'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, Wrapper } from '@vue/test-utils'
// local
import { RegistrationConfirmation } from '@/components/dialogs'
import { SettingOptions } from '@/enums'
import { dischargeConfirmationDialog } from '@/resources'
import { axios } from '@/utils/axios-ppr'
import { mockedDebtorNames } from './test-data'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// emitted events
const proceed: string = 'proceed'

// Input field selectors / buttons
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'
const checkbox: string = '.dialog-checkbox'
const text: string = '.dialog-text'
const title: string = '.dialog-title'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Registration Confirmation Dialog', () => {
  let wrapper: Wrapper<any>
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const patch = sandbox.stub(axios, 'patch')
    patch.returns(new Promise(resolve => resolve({
      data: mockedDebtorNames
    })))
    wrapper = mount(RegistrationConfirmation,
      {
        vuetify,
        store,
        propsData: {
          attach: '',
          display: false,
          options: {
            acceptText: '',
            cancelText: '',
            text: '',
            title: ''
          },
          settingOptions: ''
        }
      })
    await Vue.nextTick()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders the component with all error options', async () => {
    const confirmationOptions = [dischargeConfirmationDialog]
    for (let i = 0; i < confirmationOptions.length; i++) {
      const options = confirmationOptions[i]
      wrapper.setProps({
        attach: '',
        display: true,
        options: options
      })
      await Vue.nextTick()

      expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
      expect(wrapper.isVisible()).toBe(true)
      expect(wrapper.find(title).text()).toBe(options.title)
      expect(wrapper.find(text).text()).toContain(options.text.replace('<i>', '').replace('</i>', ''))
      expect(wrapper.find(checkbox).exists()).toBe(true)
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
    }
  })

  it('updates user settings when checkbox is selected', async () => {
    wrapper.setProps({
      attach: '',
      display: true,
      options: dischargeConfirmationDialog
    })
    await Vue.nextTick()
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(true)
    expect(wrapper.vm.preventDialog).toBe(false)
    wrapper.vm.preventDialog = true
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.updateFailed).toBe(false)
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
  })
})
