// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'


// Components
import { StaffPayment as StaffPaymentComponent } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentDialog, BaseDialog } from '@/components/dialogs'
import { getLastEvent } from './utils'
import {
  staffPaymentDialog
} from '@/resources/dialogOptions'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

document.body.setAttribute('data-app', 'true')

// emitted events
const proceed = 'proceed'

// Input field selectors / buttons
const title = '.dialog-title'

describe('Payment component', () => {
  let wrapper: any

  beforeEach(async () => {
    const localVue = createLocalVue()

    localVue.use(Vuetify)
    wrapper = mount((StaffPaymentDialog as any),
      {
        localVue,
        store,
        propsData: {
          setOptions: staffPaymentDialog,
          setDisplay: true,
          setShowCertifiedCheckbox: true
        },
        vuetify
      })

    // wait for all queries to complete
    await flushPromises()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with staff payment component', () => {
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPaymentComponent).exists()).toBe(true)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.find(title).text()).toBe('Staff Payment')
  })

  it('Emits the cancel action', async () => {
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, false)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
  })

  it('Emits the submit action', async () => {
    wrapper.vm.valid = true

    wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(true)
  })

  it('updates search certified when checkbox is selected', async () => {
    expect(wrapper.vm.$store.state.stateModel.search.searchCertified).toBe(false)
    wrapper.find('#certify-checkbox').trigger('click')
    wrapper.vm.$data.valid = true
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
    await flushPromises()
    expect(wrapper.vm.$store.state.stateModel.search.searchCertified).toBe(true)
  })

  it('updates store payment info', async () => {
    wrapper.findComponent(StaffPaymentComponent).vm.$emit('update:staffPaymentData', {
      option: 1,
      routingSlipNumber: '999888777',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    })
    await flushPromises()
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
    await flushPromises()
    expect(wrapper.vm.$store.state.stateModel.staffPayment.routingSlipNumber).toBe('999888777')
  })

  it('Clears the payment data on cancel', async () => {
    wrapper.findComponent(StaffPaymentComponent).vm.$emit('update:staffPaymentData', {
      option: 1,
      routingSlipNumber: '999888777',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    })
    await flushPromises()
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, false)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
    expect(wrapper.vm.$store.state.stateModel.staffPayment.routingSlipNumber).toBe('')
  })
})
