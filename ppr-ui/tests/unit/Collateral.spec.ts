// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { TiptapVuetifyPlugin } from 'tiptap-vuetify'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedGeneralCollateral1,
  mockedVehicleCollateral1,
  mockedSelectSecurityAgreement,
  mockedOtherCarbon,
  mockedLienUnpaid,
  mockedRepairersLien
} from './test-data'

// Components
import { Collateral, GeneralCollateral, VehicleCollateral } from '@/components/collateral'
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
Vue.use(TiptapVuetifyPlugin, {
  // the next line is important! You need to provide the Vuetify Object to this place.
  vuetify, // same as "vuetify: vuetify"
  // optional, default to 'md' (default vuetify icons before v2.0.0)
  iconsGroup: 'mdi'
})
const store = getVuexStore()

// Input field selectors / buttons
const collateralEdit = '#collateral-edit'
const collateralSummary = '#collateral-summary'
const goToCollateralBtn = '#router-link-collateral'
const validCollateralIcon = '.agreement-valid-icon'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  isSummary: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(Collateral, {
    localVue,
    propsData: {
      isSummary: isSummary
    },
    store,
    vuetify
  })
}

describe('Collateral SA tests (covers workflow for most registration types)', () => {
  let wrapper: Wrapper<any>
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders summary properly in error view when no collateral exists', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.invalid-message').length).toBe(2)
    expect(wrapper.findAll('.invalid-message').at(1).text()).toContain('This step is unfinished.')
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(true)
  })

  it('renders summary view properly when vehicle collateral exists', async () => {
    await store.dispatch('setAddCollateral', {
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
    expect(wrapper.findAll('.invalid-message').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
  })

  it('renders summary view properly when general collateral exists', async () => {
    await store.dispatch('setAddCollateral', {
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
    expect(wrapper.findAll('.invalid-message').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(true)
  })

  it('renders summary view properly when vehicle + general collateral exists', async () => {
    await store.dispatch('setAddCollateral', {
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
    expect(wrapper.findAll('.invalid-message').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).vm.$props.showInvalid).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(true)
  })

  it('renders edit view properly when no collateral exists', async () => {
    await wrapper.setProps({ isSummary: false })
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
    await wrapper.setProps({ isSummary: false })
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: mockedVehicleCollateral1,
      valid: true,
      showInvalid: false
    })
    expect(wrapper.vm.valid).toBe(true)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain(
      'At least one form of collateral (vehicle or general)'
    )
    expect(wrapper.findAll(validCollateralIcon).length).toBe(1)
    expect(wrapper.vm.$data.generalCollateralLength).toBe(0)
    expect(wrapper.vm.$data.vehicleCollateralLength).toBe(2)
  })

  it('updates description in edit view when general collateral is added', async () => {
    await wrapper.setProps({ isSummary: false })
    await store.dispatch('setAddCollateral', {
      generalCollateral: mockedGeneralCollateral1,
      vehicleCollateral: [],
      valid: true,
      showInvalid: false
    })
    expect(wrapper.vm.valid).toBe(true)
    // description
    expect(wrapper.findAll('#collateral-edit-description').length).toBe(1)
    expect(wrapper.findAll('#collateral-edit-description').at(0).text()).toContain(
      'At least one form of collateral (vehicle or general)'
    )
    expect(wrapper.findAll(validCollateralIcon).length).toBe(1)
    expect(wrapper.vm.$data.generalCollateralLength).toBe(1)
    expect(wrapper.vm.$data.vehicleCollateralLength).toBe(0)
  })
})

describe('Collateral Lien unpaid wages summary test', () => {
  let wrapper: Wrapper<any>
  const registrationType = mockedLienUnpaid()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })
  it('renders summary view with general collateral when none is given', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.invalid-message').length).toBe(2)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(true)
    expect(wrapper.vm.$data.generalCollateralLength).toBe(0)
  })
})

describe('Collateral Lien unpaid wages edit tests', () => {
  let wrapper: Wrapper<any>
  const registrationType = mockedLienUnpaid()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })
  it('renders edit view with general collateral when none is given', async () => {
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
    expect(wrapper.vm.$data.generalCollateralLength).toBe(1)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(false)
  })

  it('renders summary view without general collateral when none is given and it is in the discharge flow', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.DISCHARGE)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    const wrapper2 = createComponent(true)
    expect(wrapper2.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper2.findComponent(GeneralCollateral).exists()).toBe(false)
    wrapper2.destroy()
  })

  it('renders summary view without general collateral when none is given and it is in the renew flow', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.RENEWAL)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    const wrapper2 = createComponent(true)
    expect(wrapper2.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper2.findComponent(GeneralCollateral).exists()).toBe(false)
    wrapper2.destroy()
  })
})

describe('Collateral Carbon Tax summary test', () => {
  let wrapper: Wrapper<any>
  const registrationType = mockedOtherCarbon()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })
  it('renders summary view with general collateral when none is given', async () => {
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(VehicleCollateral).exists()).toBe(false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(wrapper.findAll(collateralSummary).length).toBe(1)
    expect(wrapper.findAll(collateralEdit).length).toBe(0)
    expect(wrapper.findAll('.invalid-message').length).toBe(0)
    expect(wrapper.find(goToCollateralBtn).exists()).toBe(false)
    expect(wrapper.vm.$data.generalCollateralLength).toBe(1)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(true)
  })
})

describe('Collateral Carbon Tax edit tests', () => {
  let wrapper: Wrapper<any>
  const registrationType = mockedOtherCarbon()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })


  it('renders edit view with general collateral when none is given', async () => {
    await wrapper.setProps({ isSummary: false })
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
    expect(wrapper.vm.$data.generalCollateralLength).toBe(1)
    expect(wrapper.findComponent(GeneralCollateral).vm.$props.isSummary).toBe(false)
  })

  it('renders summary view without general collateral when none is given and it is in the discharge flow', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.DISCHARGE)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    const wrapper2 = createComponent(true)
    expect(wrapper2.findComponent(GeneralCollateral).exists()).toBe(false)
    wrapper2.destroy()
  })

  it('renders summary view without general collateral when none is given and it is in the renew flow', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.RENEWAL)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    const wrapper2 = createComponent(true)
    expect(wrapper2.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper2.findComponent(GeneralCollateral).exists()).toBe(false)
    wrapper2.destroy()
  })
})

describe('Collateral SA tests for amendments', () => {
  let wrapper: Wrapper<any>
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
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
  let wrapper: Wrapper<any>
  const registrationType = mockedRepairersLien()

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    await store.dispatch('setAddCollateral', {
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })

    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
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
