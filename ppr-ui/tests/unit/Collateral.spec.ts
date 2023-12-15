import { useStore } from '@/store/store'
import {
  mockedGeneralCollateral1,
  mockedVehicleCollateral1,
  mockedSelectSecurityAgreement,
  mockedOtherCarbon,
  mockedLienUnpaid,
  mockedRepairersLien,
  mockedIncomeTax
} from './test-data'

// Components
import { Collateral, GeneralCollateral, VehicleCollateral } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { createComponent } from './utils'
import { nextTick } from 'vue'

const store = useStore()

// Input field selectors / buttons
const collateralEdit = '#collateral-edit'
const collateralSummary = '#collateral-summary'
const goToCollateralBtn = '#router-link-collateral'
const validCollateralIcon = '.agreement-valid-icon'

describe('Collateral SA tests (covers workflow for most registration types) in Summary Mode', () => {
  let wrapper
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: true })
    await nextTick()
  })

  it('renders summary properly in error view when no collateral exists', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.error-text').length).toBe(1)
    expect(wrapper.findAll('.error-text').at(0).text()).toContain('This step is unfinished.')
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(true)
  })

  it('renders summary view properly when vehicle collateral exists', async () => {
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: mockedVehicleCollateral1,
      valid: true,
      showInvalid: false
    })
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.error-text').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
  })

  it('renders summary view properly when general collateral exists', async () => {
    await store.setAddCollateral({
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: [],
      valid: true,
      showInvalid: false
    })
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.error-text').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(true)
  })

  it('renders summary view properly when vehicle + general collateral exists', async () => {
    await store.setAddCollateral({
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: mockedVehicleCollateral1,
      valid: true,
      showInvalid: false
    })
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.error-text').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(true)
  })
})

describe('Collateral SA tests (covers workflow for most registration types)', () => {
  let wrapper
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: true,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: false })
    await nextTick()
  })

  it('renders edit view properly when no collateral exists', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(0)
    expect(wrapper.findAll(collateralEdit).length).toBe(1)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain(
      'At least one form of collateral (vehicle or general)'
    )
    expect(wrapper.findAll(validCollateralIcon).length).toBe(0)
    // vehicle collateral
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
    // general collateral
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(false)
  })

  it('updates description in edit view when vehicle collateral is added', async () => {
    await store.setAddCollateral({
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: mockedVehicleCollateral1,
      valid: true,
      showInvalid: false
    })
    await nextTick()

    expect(wrapper.vm.valid).toBe(true)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain(
      'At least one form of collateral (vehicle or general)'
    )
    expect(wrapper.findAll(validCollateralIcon).length).toBe(1)
    expect(wrapper.vm.generalCollateralLength).toBe(1)
    expect(wrapper.vm.vehicleCollateralLength).toBe(2)
  })

  it('updates description in edit view when general collateral is added', async () => {
    await store.setAddCollateral({
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: [],
      valid: true,
      showInvalid: false
    })
    await nextTick()

    expect(wrapper.vm.valid).toBe(true)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain(
      'At least one form of collateral (vehicle or general)'
    )
    expect(wrapper.findAll(validCollateralIcon).length).toBe(1)
    expect(wrapper.vm.generalCollateralLength).toBe(1)
    expect(wrapper.vm.vehicleCollateralLength).toBe(0)
  })
})

describe('Collateral Lien unpaid wages summary test', () => {
  let wrapper
  const registrationType = mockedLienUnpaid()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: true })
    await nextTick()
  })

  it('renders summary view with general collateral when none is given', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.error-text').length).toBe(1)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(true)
    expect(wrapper.vm.generalCollateralLength).toBe(0)
  })
})

describe('Collateral Lien unpaid wages edit tests', () => {
  let wrapper
  const registrationType = mockedLienUnpaid()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: true })
    await nextTick()
  })

  it('renders edit view with general collateral when none is given', async () => {
    wrapper = await createComponent(Collateral, { isSummary: false })
    await nextTick()

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(collateralSummary).length).toBe(0)
    expect(wrapper.findAll(collateralEdit).length).toBe(1)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain('General Collateral')
    expect(wrapper.findAll(validCollateralIcon).length).toBe(1)
    // vehicle collateral
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
    // general collateral
    expect(wrapper.vm.generalCollateralLength).toBe(1)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(false)
  })

  it('renders summary view without general collateral when none is given and it is in the discharge flow', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.DISCHARGE)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
  })

  it('renders summary view without general collateral when none is given and it is in the renew flow', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.RENEWAL)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
  })
})

describe('Collateral Carbon Tax summary test', () => {
  let wrapper
  const registrationType = mockedOtherCarbon()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: true })
    await nextTick()
  })

  it('renders summary view with general collateral when none is given', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.error-text').length).toBe(1)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(true)
    expect(wrapper.vm.generalCollateralLength).toBe(0)
  })
})

describe('Collateral Carbon Tax edit tests', () => {
  let wrapper
  const registrationType = mockedOtherCarbon()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: true })
    await nextTick()
  })

  it('renders edit view with general collateral when none is given', async () => {
    wrapper = await createComponent(Collateral, { isSummary: false })
    await nextTick()

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(collateralSummary).length).toBe(0)
    expect(wrapper.findAll(collateralEdit).length).toBe(1)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain('General Collateral')
    expect(wrapper.findAll(validCollateralIcon).length).toBe(1)
    // vehicle collateral
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
    // general collateral
    expect(wrapper.vm.generalCollateralLength).toBe(1)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(false)
  })

  it('renders summary view without general collateral when none is given and it is in the discharge flow', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.DISCHARGE)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    await nextTick()

    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
  })

  it('renders summary view without general collateral when none is given and it is in the renew flow', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.RENEWAL)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    await nextTick()

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
  })
})

describe('Collateral SA tests for amendments', () => {
  let wrapper
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: false })
    await nextTick()
  })

  it('vehicle collateral and general collateral properly for amendments', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // should still render for amendments
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)

    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
  })
})

describe('Collateral RL tests for amendments', () => {
  let wrapper
  const registrationType = mockedRepairersLien()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = await createComponent(Collateral, { isSummary: false })
    await nextTick()
  })

  it('vehicle collateral and general collateral properly for amendments', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // should still render for amendments
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    // should not render for repairers lien
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)

    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
  })
})

describe('Collateral for Crown Charge - Income Tax Act', () => {
  let wrapper
  const registrationType = mockedIncomeTax()

  beforeEach(async () => {
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)

    wrapper = await createComponent(Collateral, { isSummary: true })
  })

  it('should have vehicle collateral optional and general collateral required', async () => {
    const emptyCollateral = {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    }
    await store.setAddCollateral(emptyCollateral)

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)

    // add vehicle collateral
    await store.setAddCollateral({
      ...emptyCollateral,
      vehicleCollateral: mockedVehicleCollateral1
    })

    // for this reg type vehicle collateral is optional therefore valid is still false
    expect(wrapper.vm.valid).toBe(false)

    // add vehicle collateral and general collateral
    await store.setAddCollateral({
      ...emptyCollateral,
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: mockedVehicleCollateral1
    })

    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)

    // by adding general collateral the valid should be updated to true
    expect(wrapper.vm.valid).toBe(true)
  })
})
