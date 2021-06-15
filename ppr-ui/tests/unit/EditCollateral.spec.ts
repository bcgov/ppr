// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedGeneralCollateral1,
  mockedVehicleCollateral1
} from './test-data'

// Components
import { EditCollateral } from '@/components/collateral'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn'
const cancelButtonSelector: string = '#cancel-btn'
const removeButtonSelector: string = '#remove-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  activeIndex: Number,
  invalidSection: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditCollateral, {
    localVue,
    propsData: { activeIndex, invalidSection },
    store,
    vuetify
  })
}

describe('Collateral add tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.vm.currentVehicle.serialNumber).toBe('')
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes('disabled')).toBe('disabled')
  })

  it('adds a vehicle to the store', async () => {
    wrapper.find('#txt-type').setValue('MV')
    await Vue.nextTick()
    wrapper.vm.$data.currentVehicle.type = 'MV'
    wrapper.find('#txt-serial').setValue('293847298374')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    // expect(messages.at(0).text()).toBe('Type is required')
    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getters.getAddCollateral.vehicleCollateral.length).toBe(1)
  })
})

describe('Collateral edit tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddCollateral', {
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: mockedVehicleCollateral1
    })
    wrapper = createComponent(0, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders vehicle collateral when editing', async () => {
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.vm.currentVehicle.serialNumber).toEqual('KM8J3CA46JU622994')
    expect(wrapper.vm.currentVehicle.year).toEqual(2018)
    expect(wrapper.vm.currentVehicle.make).toEqual('HYUNDAI')
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
  })
})
