// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'
import CompositionApi from '@vue/composition-api'

// Components
import { StaffPayment as StaffPaymentComponent } from '@bcrs-shared-components/staff-payment'
import { StaffPaymentDialog } from '@/components/dialogs'
import { getLastEvent } from './utils'

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
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    wrapper = mount(StaffPaymentDialog,
      {
        localVue,
        store,
        propsData: {
          setAttach: '',
          setDisplay: true
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
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.find(title).text()).toBe('Staff Payment')
    
  })

  it('Emits the cancel action', async () => {
    expect(wrapper.find('#cancel-btn').exists()).toBe(true)
    await wrapper.find('#cancel-btn').trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })

  it('Emits the submit action', async () => {
    wrapper.vm.valid = true
    
    await wrapper.find('#accept-btn').trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(true)
  })  
})
