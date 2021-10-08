// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'

// Components
import { CourtOrder } from '@/components/common'
import { getLastEvent } from './utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Court Order component', () => {
  let wrapper: any

  beforeEach(async () => {
    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    document.body.setAttribute('data-app', 'true')
    await store.dispatch('setCourtOrderInformation', 
    {
      courtName: 'ABC',
      courtRegistry: '123',
      orderDate: '2021-10-07',
      fileNumber: 'DEF',
      effectOfOrder: 'Good'
    })
    wrapper = mount(CourtOrder, {
      localVue,
      propsData: {},
      store,
      vuetify
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the view with text boxes', () => {
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(true)
    expect(wrapper.find('#txt-court-name').exists()).toBe(true)
    expect(wrapper.find('#txt-court-registry').exists()).toBe(true)
    expect(wrapper.find('#txt-court-file-number').exists()).toBe(true)
    expect(wrapper.find('#court-date-text-field').exists()).toBe(true)
    expect(wrapper.find('#effect-of-order').exists()).toBe(true)
  })

  it('renders the court order data from the store', async () => {
  
    await flushPromises()
    expect(wrapper.find('#txt-court-name').element.value).toBe('ABC')
    expect(wrapper.find('#txt-court-registry').element.value).toBe('123')
    expect(wrapper.find('#txt-court-file-number').element.value).toBe('DEF')
    expect(wrapper.find('#effect-of-order').element.value).toBe('Good')
  })

  it('sets the validity to true when filled in', async () => {
    wrapper.find('#txt-court-name').setValue('Test Court')
    wrapper.find('#txt-court-registry').setValue('Test Registry')
    wrapper.find('#txt-court-file-number').setValue('Test File Number')
    wrapper.vm.$data.orderDate = 'October 7, 2021'
    wrapper.find('#effect-of-order').setValue('Test Effect')

    await flushPromises()
    expect(getLastEvent(wrapper, 'setCourtOrderValid')).toBe(true)
    
  })

  it('sets the validity to false for blank fields', async () => {
    wrapper.vm.$data.courtName = ' '
    await flushPromises()
    expect(getLastEvent(wrapper, 'setCourtOrderValid')).toBe(false)
    
  })
})
