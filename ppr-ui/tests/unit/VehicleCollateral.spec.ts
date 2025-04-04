import { useStore } from '@/store/store'
import {
  mockedForestrySubcontractor,
  mockedOtherCarbon,
  mockedRepairersLien,
  mockedSelectSecurityAgreement,
  mockedVehicleCollateral1,
  mockedVehicleCollateralAmendment,
  mockedVehicleCollateralAmendment2
} from './test-data'
import { createComponent } from './utils'
import { EditCollateral, VehicleCollateral } from '@/components/collateral/vehicle'
import { nextTick } from 'vue'
import { RegistrationFlowType } from '@/enums'

const store = useStore()

// Input field selectors / buttons
const addButtonSelector: string = '#btn-add-collateral'

describe('Vehicle collateral summary tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)

    wrapper = await createComponent(VehicleCollateral, { isSummary: true, showInvalid: false })
    await nextTick()
  })

  it('renders with summary version with empty collateral', async () => {
    await store.setVehicleCollateral(null)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(false)
    expect(wrapper.vm.vehicleCollateral.length).toBe(0)
    expect(wrapper.find('.collateral-table').exists()).toBe(false)
  })

  it('renders with summary version with vehicle collateral', async () => {
    await store.setVehicleCollateral(mockedVehicleCollateral1)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(false)
    expect(wrapper.find('.collateral-table').exists()).toBe(true)
  })
})

describe('Vehicle collateral edit tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setVehicleCollateral(mockedVehicleCollateral1)
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    wrapper = await createComponent(VehicleCollateral, { isSummary: false, showInvalid: false })
    await nextTick()
  })

  it('add collateral button shows the add vehicle form', async () => {
    expect(wrapper.find(addButtonSelector).exists()).toBe(true)
    wrapper.find(addButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(EditCollateral).isVisible()).toBe(true)
  })

  it('renders vehicle collateral table and headers', async () => {
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(false)
    expect(wrapper.find('.collateral-table').exists()).toBe(true)
    expect(wrapper.findAll('th').length).toBe(6)
  })

  it('displays the correct vehicle rows when data is present', () => {
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.vehicle-row').length
    expect(vehicleRowCount).toEqual(2)
  })

  it('displays the correct data in the vehicle table rows', () => {
    const vehicleItem1 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[0]
    expect(vehicleItem1.querySelectorAll('td')[0].textContent).toContain('MV')
    expect(vehicleItem1.querySelectorAll('td')[1].textContent).toContain('2018')
    expect(vehicleItem1.querySelectorAll('td')[2].textContent).toContain('HYUNDAI')
    expect(vehicleItem1.querySelectorAll('td')[3].textContent).toContain('TUSCON')
    expect(vehicleItem1.querySelectorAll('td')[4].textContent).toContain('KM8J3CA46JU622994')
  })
})

describe('Vehicle Collateral amendment tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setVehicleCollateral(mockedVehicleCollateralAmendment)
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(VehicleCollateral, { isSummary: false, showInvalid: false })
    await nextTick()
  })

  it('displays the correct vehicle rows when data is present', () => {
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.vehicle-row').length
    expect(vehicleRowCount).toEqual(3)
  })

  it('displays the correct chips in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[2]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('DELETED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('ADDED')
  })

  it('displays the correct actions in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[2]
    expect(item1.querySelectorAll('td')[6].textContent).toContain('Undo')
    const dropDowns = wrapper.findAll('.vehicle-row .actions__more-actions__btn')
    // 2 drop downs
    expect(dropDowns.length).toBe(2)
    // click the drop down arrow
    dropDowns.at(0).trigger('click')
    await nextTick()

    // TODO: Currently TBD on how to access overlay context items outside the component wrapper
    // expect(wrapper.findAll('.actions__more-actions .v-list-item__subtitle').length).toBe(2)
    // expect(item2.querySelectorAll('td')[6].textContent).toContain('Undo')
    // expect(item3.querySelectorAll('td')[6].textContent).toContain('Edit')
    // // click the second drop down
    // dropDowns.at(1).trigger('click')
    // await nextTick()
    // const options = wrapper.findAll('.actions__more-actions .v-list-item__subtitle')
    // // options from first drop down
    // expect(options.at(0).text()).toContain('Amend')
    // expect(options.at(1).text()).toContain('Delete')
    // // option from second drop down
    // expect(options.at(2).text()).toContain('Remove')
  })
})

describe('Vehicle Collateral summary amendment tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setVehicleCollateral(mockedVehicleCollateralAmendment)
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(VehicleCollateral, { isSummary: true, showInvalid: false })
    await nextTick()
  })

  it('displays the correct vehicle rows when data is present', () => {
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.collateral-table tr').length
    expect(wrapper.vm.summaryView).toBe(true)
    // 3 rows plus header
    expect(vehicleRowCount).toEqual(4)
  })

  it('displays the correct chips in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.collateral-table tr')[1]
    const item2 = wrapper.vm.$el.querySelectorAll('.collateral-table tr')[2]
    const item3 = wrapper.vm.$el.querySelectorAll('.collateral-table tr')[3]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('DELETED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('ADDED')
  })
})

describe('Vehicle Collateral repairers lien amendment tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setVehicleCollateral(mockedVehicleCollateralAmendment2)
    await store.setRegistrationType(mockedRepairersLien())
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(VehicleCollateral, { isSummary: false, showInvalid: false })
    await nextTick()
  })

  it('displays the correct vehicle rows when data is present', () => {
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.vehicle-row').length
    expect(vehicleRowCount).toEqual(2)
  })

  it('displays the correct chips in the table rows', () => {
    const item2 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[1]
    expect(item2.querySelectorAll('td')[0].textContent).toContain('DELETED')
  })

  it('displays the correct actions in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.vehicle-row')[1]
    expect(item1.querySelectorAll('td')[5].textContent).toContain('Delete')
    expect(item2.querySelectorAll('td')[5].textContent).toContain('Undo')
  })
})

describe('Vehicle Collateral crown charge tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setVehicleCollateral(mockedVehicleCollateralAmendment2)
    await store.setRegistrationType(mockedOtherCarbon())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(VehicleCollateral, { isSummary: false, showInvalid: false })
    await nextTick()
  })

  it('displays the add button and the vehicles', () => {
    expect(wrapper.find(addButtonSelector).exists()).toBe(true)
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.vehicle-row').length
    expect(vehicleRowCount).toEqual(2)
  })

  it('displays the data for the amendment', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    const vehicleRowCount = wrapper.vm.$el.querySelectorAll('.vehicle-row').length
    expect(vehicleRowCount).toEqual(2)
  })
})

describe('Vehicle Collateral forestry subcontractor tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setVehicleCollateral(mockedVehicleCollateralAmendment2)
    await store.setRegistrationType(mockedForestrySubcontractor())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(VehicleCollateral, { isSummary: false, showInvalid: false })
    await nextTick()
  })

  it('displays no vehicle data for the forestry subcontractor', async () => {
    expect(wrapper.find(addButtonSelector).exists()).toBe(false)
    expect(wrapper.find('.vehicle-row').exists()).toBe(false)
  })
})
