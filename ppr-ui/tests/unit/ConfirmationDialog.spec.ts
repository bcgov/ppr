import sinon from 'sinon'
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
// local
import { BaseDialog, ConfirmationDialog } from '@/components/dialogs'
import { DialogContent } from '@/components/dialogs/common'
import { SettingOptions } from '@/enums'
import { paymentConfirmaionDialog, selectionConfirmaionDialog } from '@/resources/dialogOptions'
import { axios } from '@/utils/axios-ppr'
import { mockedDefaultUserSettingsResponse, mockedDisablePayUserSettingsResponse } from './test-data'
import { getLastEvent } from './utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// emitted events
const proceed = 'proceed'

// Input field selectors / buttons
const checkbox = '.dialog-checkbox'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Confirmation Dialog', () => {
  let wrapper: Wrapper<any>
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const patch = sandbox.stub(axios, 'patch')
    patch.returns(new Promise(resolve => resolve({
      data: mockedDisablePayUserSettingsResponse
    })))
    await store.dispatch('setUserInfo', {
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDefaultUserSettingsResponse
    })

    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    wrapper = mount(ConfirmationDialog,
      {
        localVue,
        vuetify,
        store,
        propsData: {
          setDisplay: false,
          setOptions: {
            acceptText: '',
            cancelText: '',
            text: '',
            title: ''
          },
          setSettingOption: null
        }
      })
    await flushPromises()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders the component with all error options', async () => {
    const confirmationOptions = [paymentConfirmaionDialog, selectionConfirmaionDialog]
    const settingOptions = [SettingOptions.PAYMENT_CONFIRMATION_DIALOG, SettingOptions.SELECT_CONFIRMATION_DIALOG]
    for (let i = 0; i < confirmationOptions.length; i++) {
      const options = confirmationOptions[i]
      const settingOption = settingOptions[i]
      wrapper.setProps({
        setDisplay: true,
        setOptions: options,
        setSettingOption: settingOption
      })
      await flushPromises()

      expect(wrapper.findComponent(ConfirmationDialog).exists()).toBe(true)
      expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
      expect(wrapper.findComponent(DialogContent).exists()).toBe(true)
      expect(wrapper.isVisible()).toBe(true)
      expect(wrapper.findComponent(BaseDialog).text()).toContain(options.title)
      expect(wrapper.findComponent(DialogContent).text()).toContain(options.text)
      expect(wrapper.find(checkbox).exists()).toBe(true)

      wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
      await flushPromises()
      expect(getLastEvent(wrapper, proceed)).toEqual(true)

      wrapper.findComponent(BaseDialog).vm.$emit(proceed, false)
      await flushPromises()
      expect(getLastEvent(wrapper, proceed)).toEqual(false)
    }
  })

  it('updates user settings when checkbox is selected', async () => {
    wrapper.setProps({
      attach: '',
      display: true,
      options: paymentConfirmaionDialog,
      settingOption: SettingOptions.PAYMENT_CONFIRMATION_DIALOG
    })
    await flushPromises()
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(true)
    expect(wrapper.vm.preventDialog).toBe(false)
    wrapper.vm.preventDialog = true
    await flushPromises()
    expect(wrapper.vm.updateFailed).toBe(false)
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
  })
})
