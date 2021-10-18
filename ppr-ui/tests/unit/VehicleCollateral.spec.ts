// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedVehicleCollateral1,
  mockedSelectSecurityAgreement,
  mockedVehicleCollateralAmendment
} from './test-data'

// Components
import { EditCollateral, VehicleCollateral } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'

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

describe('Vehicle Collateral amendment tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setVehicleCollateral', mockedVehicleCollateralAmendment)
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    wrapper = createComponent(false, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('displays the correct vehicle rows when data is present', () => {
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row').length
    expect(vehicleRowCount).toEqual(3)
  })

  it('displays the correct chips in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[2]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('DELETED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('ADDED')
  })

  it('displays the correct actions in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.v-data-table .vehicle-row')[2]
    expect(item1.querySelectorAll('td')[6].textContent).toContain('Undo')
    const dropDowns = wrapper.findAll('.v-data-table .vehicle-row .actions__more-actions__btn')
    // 2 drop downs
    expect(dropDowns.length).toBe(2)
    // click the drop down arrow
    dropDowns.at(0).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findAll('.actions__more-actions .v-list-item__subtitle').length).toBe(2)
    expect(item2.querySelectorAll('td')[6].textContent).toContain('Undo')
    expect(item3.querySelectorAll('td')[6].textContent).toContain('Edit')
    // click the second drop down
    dropDowns.at(1).trigger('click')
    await Vue.nextTick()
    const options = wrapper.findAll('.actions__more-actions .v-list-item__subtitle')
    // options from first drop down
    expect(options.at(0).text()).toContain('Amend')
    expect(options.at(1).text()).toContain('Delete')
    // option from second drop down
    expect(options.at(2).text()).toContain('Remove')
  })

})
