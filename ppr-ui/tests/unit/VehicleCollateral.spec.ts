// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedVehicleCollateral1,
  mockedSelectSecurityAgreement
} from './test-data'

// Components
import { EditCollateral, VehicleCollateral } from '@/components/collateral'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const addButtonSelector: string = '#btn-add-collateral'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  isSummary: boolean,
  showInvalid: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(VehicleCollateral, {
    localVue,
    propsData: {
      isSummary: isSummary,
      showInvalid: showInvalid
    },
    store,
    vuetify
  })
}

describe('Vehicle collateral summary tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.dispatch('setRegistrationType', registrationType)

    wrapper = createComponent(true, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with summary version with empty collateral', async () => {
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(false)
    expect(wrapper.find('.collateral-table').exists()).toBe(false)
  })

  it('renders with summary version with vehicle collateral', async () => {
    await store.dispatch('setVehicleCollateral', mockedVehicleCollateral1)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(false)
    expect(wrapper.find('.collateral-table').exists()).toBe(true)
  })
})

describe('Vehicle collateral edit tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setVehicleCollateral', mockedVehicleCollateral1)
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    wrapper = createComponent(false, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('add collateral button shows the add vehicle form', async () => {
    expect(wrapper.find(addButtonSelector).exists()).toBe(true)
    wrapper.find(addButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(EditCollateral).isVisible()).toBe(true)
  })

  it('renders vehicle collateral table and headers', async () => {
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(false)
    expect(wrapper.find('.collateral-table').exists()).toBe(true)
    expect(wrapper.findAll('.text-start').length).toBe(6)
  })

  it('displays the correct vehicle rows when data is present', () => {
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row').length
    expect(vehicleRowCount).toEqual(2)
  })

  it('displays the correct data in the vehicle table rows', () => {
    const vehicleItem1 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[0]
    expect(vehicleItem1.querySelectorAll('td')[0].textContent).toContain('MV')
    expect(vehicleItem1.querySelectorAll('td')[1].textContent).toContain('2018')
    expect(vehicleItem1.querySelectorAll('td')[2].textContent).toContain('HYUNDAI')
    expect(vehicleItem1.querySelectorAll('td')[3].textContent).toContain('TUSCON')
    expect(vehicleItem1.querySelectorAll('td')[4].textContent).toContain('KM8J3CA46JU622994')
  })
})
