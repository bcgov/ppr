import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
// local
import { BaseDialog } from '@/components/dialogs'
import { DialogButtons, DialogContent } from '@/components/dialogs/common'
import { DialogOptionsIF } from '@/interfaces'
import {
  dischargeCancelDialog,
  registrationAddErrorDialog,
  registrationAlreadyAddedDialog,
  registrationFoundDialog,
  registrationNotFoundDialog,
  registrationRestrictedDialog,
  renewCancelDialog,
  tableDeleteDialog,
  tableRemoveDialog
} from '@/resources/dialogOptions'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// emitted events
const proceed = 'proceed'

// Input field selectors / buttons
const title = '.dialog-title'
const closeBtn = '.close-btn'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Base Dialog tests', () => {
  let wrapper: Wrapper<any>

  const optionsList = [
    { ...dischargeCancelDialog },
    { ...registrationAddErrorDialog },
    { ...registrationAlreadyAddedDialog },
    { ...registrationFoundDialog },
    { ...registrationNotFoundDialog },
    { ...registrationRestrictedDialog },
    { ...renewCancelDialog },
    { ...tableDeleteDialog },
    { ...tableRemoveDialog }
  ]

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    wrapper = mount(BaseDialog,
      {
        localVue,
        store,
        propsData: {
          setAttach: '',
          setDisplay: true,
          setOptions: {
            acceptText: 'default accept',
            cancelText: 'default cancel',
            hasContactInfo: false,
            text: 'default text',
            textExtra: [],
            title: 'default title'
          } as DialogOptionsIF
        },
        vuetify
      })
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component with parts / hides it when needed', async () => {
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(DialogContent).exists()).toBe(true)
    expect(wrapper.findComponent(DialogButtons).exists()).toBe(true)
    expect(wrapper.findComponent(DialogContent).isVisible()).toBe(true)
    expect(wrapper.findComponent(DialogButtons).isVisible()).toBe(true)
    expect(wrapper.findComponent(DialogContent).vm.$props.setBaseText).toBe('default text')
    expect(wrapper.findComponent(DialogContent).vm.$props.setExtraText).toEqual([])
    expect(wrapper.findComponent(DialogContent).vm.$props.setHasContactInfo).toBe(false)
    expect(wrapper.findComponent(DialogButtons).vm.$props.setAcceptText).toBe('default accept')
    expect(wrapper.findComponent(DialogButtons).vm.$props.setCancelText).toBe('default cancel')
    expect(wrapper.vm.$props.setDisplay).toBe(true)
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.find(title).text()).toBe('default title')
    await wrapper.setProps({ setDisplay: false })
    expect(wrapper.vm.$props.setDisplay).toBe(false)
    expect(wrapper.find(title).isVisible()).toBe(false)
    expect(wrapper.findComponent(DialogContent).isVisible()).toBe(false)
    expect(wrapper.findComponent(DialogButtons).isVisible()).toBe(false)
  })

  it('renders base dialog with given options', async () => {
    for (let i = 0; i < optionsList.length; i++) {
      const options = optionsList[i]
      await wrapper.setProps({
        setAttach: '',
        setDisplay: true,
        setOptions: options
      })
      expect(wrapper.findComponent(BaseDialog).isVisible()).toBe(true)
      expect(wrapper.findComponent(DialogContent).isVisible()).toBe(true)
      expect(wrapper.findComponent(DialogButtons).isVisible()).toBe(true)
      expect(wrapper.findAll(title).length).toBe(1)
      expect(wrapper.find(title).text()).toBe(options.title)
      expect(wrapper.findComponent(DialogContent).vm.$props.setBaseText).toBe(options.text)
      expect(wrapper.findComponent(DialogContent).vm.$props.setExtraText).toEqual(options.textExtra || [])
      expect(wrapper.findComponent(DialogContent).vm.$props.setHasContactInfo).toBe(options.hasContactInfo || false)
      expect(wrapper.findComponent(DialogButtons).vm.$props.setAcceptText).toBe(options.acceptText)
      expect(wrapper.findComponent(DialogButtons).vm.$props.setCancelText).toBe(options.cancelText)
    }
  })

  it('Emits the button actions', async () => {
    wrapper.findComponent(DialogButtons).vm.$emit(proceed, true)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(true)
    wrapper.findComponent(DialogButtons).vm.$emit(proceed, false)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
    expect(wrapper.find(closeBtn).exists()).toBe(true)
    await wrapper.find(closeBtn).trigger('click')
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })
})
