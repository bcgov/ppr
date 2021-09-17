// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedGeneralCollateral1,
  mockedVehicleCollateral1,
  mockedSelectSecurityAgreement,
  mockedOtherCarbon,
  mockedLienUnpaid,
  generalCollateralText
} from './test-data'

// Components
import { Collateral, EditCollateral } from '@/components/collateral'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const addButtonSelector: string = '#btn-add-collateral'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(Collateral, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Collateral SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())

    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditCollateral).exists()).toBeFalsy()
    expect(wrapper.vm.generalCollateralDesc).toBe('')
  })

  it('add collateral button shows the add vehicle form', async () => {
    expect(wrapper.find(addButtonSelector).exists()).toBe(true)
    wrapper.find(addButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(EditCollateral).exists()).toBeTruthy()
    expect(wrapper.findComponent(EditCollateral).isVisible()).toBe(true)
  })
})

describe('Collateral Lien unpaid wages tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedLienUnpaid())
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })
  it('renders with default values', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // won't show vehicle collateral
    expect(wrapper.find('.collateral-table').exists()).toBeFalsy()
    expect(wrapper.vm.generalCollateralDesc).toContain('All the personal property of the debtor')
  })


})

describe('Collateral Carbon tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedOtherCarbon())
    await store.dispatch('setAddCollateral', {
      generalCollateral: null,
      vehicleCollateral: []
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // won't show vehicle collateral
    expect(wrapper.find('.collateral-table').exists()).toBeFalsy()
    expect(wrapper.vm.generalCollateralDesc).toContain(generalCollateralText)
  })


})

describe('Collateral store tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddCollateral', {
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: mockedVehicleCollateral1
    })
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders general collateral when set', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.vm.generalCollateralDesc).toEqual('TEST1 GENERAL COLLATERAL')
  })
  it('renders vehicle collateral table and headers', async () => {
    expect(wrapper.find('.collateral-table').exists()).toBeTruthy()
    // column header class is text-start
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



