import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import {
  mockedGeneralCollateral1,
  mockedVehicleCollateral1,
  mockedSelectSecurityAgreement,
  mockedMarriageMH
} from './test-data'
import { APIVehicleTypes } from '@/enums'
import { EditCollateral } from '@/components/collateral/vehicle'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const doneButtonSelector: string = '#done-btn-collateral'
const cancelButtonSelector: string = '#cancel-btn-collateral'
const removeButtonSelector: string = '#remove-btn-collateral'
const vehicleTypeDrop: string = '#txt-type-drop'

const store = useStore()

describe('Collateral add tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    wrapper = await createComponent(EditCollateral, { activeIndex: -1, invalidSection: false })
    await flushPromises()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.vm.currentVehicle.serialNumber).toBe('')
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes().disabled).toBeDefined()
  })

  it('adds a vehicle to the store', async () => {
    wrapper.find(vehicleTypeDrop).setValue(APIVehicleTypes.MOTOR_VEHICLE)
    await nextTick()
    wrapper.vm.currentVehicle.type = APIVehicleTypes.MOTOR_VEHICLE
    const serialInput = await wrapper.find('#txt-serial')
    serialInput.setValue('293847298374')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    await nextTick()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getAddCollateral.vehicleCollateral.length).toBe(1)
  })
})

describe('Collateral tests for MH', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedMarriageMH())
    wrapper = await createComponent(EditCollateral, { activeIndex: -1, invalidSection: false })
    await flushPromises()
  })

  it('renders with readonly type and manufactured home input', async () => {
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.find('#txt-type').exists()).toBe(true)
    // show read only text box
    expect(wrapper.find('#txt-man').exists()).toBe(true)

    // no drop down
    expect(wrapper.find(vehicleTypeDrop).exists()).toBe(false)
  })
})

describe('Collateral edit tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddCollateral({
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: mockedVehicleCollateral1
    })
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    wrapper = await createComponent(EditCollateral, { activeIndex: 0, invalidSection: false })
    await flushPromises()
  })

  it('renders vehicle collateral when editing', async () => {
    expect(wrapper.findComponent(EditCollateral).exists()).toBe(true)
    expect(wrapper.vm.currentVehicle.serialNumber).toEqual('KM8J3CA46JU622994')
    expect(wrapper.vm.currentVehicle.year).toEqual(2018)
    expect(wrapper.vm.currentVehicle.make).toEqual('HYUNDAI')
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
    expect(wrapper.find('.border-error-left').exists()).toBe(false)
  })

  it('shows error bar', async () => {
    wrapper = await createComponent(EditCollateral, { activeIndex: -1, invalidSection: false, setShowErrorBar: true })
    await nextTick()
    expect(wrapper.find('.border-error-left').exists()).toBe(true)
  })
})
