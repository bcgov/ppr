import { nextTick } from 'vue'
import { RegistrationLengthTrust } from '@/components/registration'
import { createComponent, getLastEvent } from './utils'
import {
  mockedSelectSecurityAgreement,
  mockedSaleOfGoods,
  mockedMarriageMH
} from './test-data'
import { useStore } from '@/store/store'
const store = useStore()

describe('RegistrationLengthTrust SA tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    wrapper = await createComponent(RegistrationLengthTrust, { isRenewal: false })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // show trust indenture will be true for security agreement only
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('')
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.lifeYearsEdit).toBe('')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
    expect(wrapper.vm.maxYears).toBe('25')
  })

  it('renders trustIndenture', async () => {
    wrapper.vm.trustIndenture = true
    expect(wrapper.vm.trustIndenture).toBe(true)
  })

  it('renders lifeYears', async () => {
    wrapper.vm.lifeInfinite = 'false'
    wrapper.vm.lifeYearsEdit = '3'
    expect(wrapper.vm.trustIndenture).toBe(true)
    await nextTick()
    wrapper.vm.lifeYearsEdit = 'XX'
    await nextTick()
    expect(wrapper.vm.lifeYearsMessage).toBe('Registration length must be a number between 1 and 25')
    const state = store.getStateModel
    expect(state.registration.lengthTrust.valid).toBe(false)

    // more tests for year validations
    wrapper.vm.lifeYearsEdit = '3.0'
    await nextTick()
    expect(state.registration.lengthTrust.valid).toBe(true)

    wrapper.vm.lifeYearsEdit = '3.5'
    await nextTick()
    expect(wrapper.vm.lifeYearsMessage).toBe('Registration length must be a number between 1 and 25')
    expect(state.registration.lengthTrust.valid).toBe(false)
  })

  it('renders lifeInfinite', async () => {
    wrapper.find('#length-infinite').trigger('click')
    await nextTick()
    wrapper.vm.lifeYearsEdit = ''
    expect(wrapper.vm.lifeInfinite).toBe('')
    expect(store.getStateModel.registration.lengthTrust.valid).toBe(true)
  })
})

describe('RegistrationLengthTrust SG tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 3,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setRegistrationType(mockedSaleOfGoods())
    wrapper = await createComponent(RegistrationLengthTrust, { isRenewal: false })
  })

  it('renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // show trust indenture will be true for security agreement only
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.vm.lifeInfinite).toBe('false')
    expect(wrapper.vm.lifeYearsEdit).toBe('3')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
    expect(wrapper.vm.trustIndenture).toBe(false)
    await nextTick()
    expect(store.getStateModel.registration.lengthTrust.lifeYears).toBe(3)
    expect(store.getStateModel.registration.lengthTrust.lifeInfinite).toBe(false)
    expect(store.getStateModel.registration.lengthTrust.valid).toBe(true)
  })
})

describe('RegistrationLengthTrust life infinite tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    wrapper = await createComponent(RegistrationLengthTrust, { isRenewal: false })
  })

  it('life infinite renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('true')
    expect(wrapper.vm.lifeYearsEdit).toBe('')
    expect(wrapper.vm.lifeYearsDisabled).toBe(true)
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(store.getStateModel.registration.lengthTrust.valid).toBe(true)
  })
})

describe('RegistrationLengthTrust Crown tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setRegistrationType(mockedMarriageMH())
    wrapper = await createComponent(RegistrationLengthTrust, { isRenewal: false })
  })

  it('renders with default infinite values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.find('#trust-indenture-checkbox').exists()).toBe(false)
    expect(wrapper.find('#length-in-years').exists()).toBe(false)

    expect(wrapper.find('#lien-amount').exists()).toBe(false)

    expect(wrapper.vm.infinityPreselected()).toBe(true)
    expect(store.getStateModel.registration.lengthTrust.valid).toBe(true)
  })
})

describe('RegistrationLengthTrust SA renewal test', () => {
  let wrapper
  beforeEach(async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationExpiryDate('2021-03-31T06:59:59+00:00')

    wrapper = await createComponent(RegistrationLengthTrust, { isRenewal: true })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.find('#length-in-years').exists()).toBe(true)
    // set renewal length to 1 year
    wrapper.vm.lifeYearsEdit = '1'
    await nextTick()
    const expiryDate = await wrapper.find('#new-expiry')
    expect(expiryDate.text()).toContain('March 30, 2022')
    expect(store.getStateModel.registration.lengthTrust.lifeYears).toBe(1)
    expect(store.getStateModel.registration.lengthTrust.valid).toBe(true)
    // also emits if valid
    expect(getLastEvent(wrapper, 'lengthTrustValid')).toBeTruthy()
  })

  it('emits if invalid', async () => {
    // set renewal length to bad value
    wrapper.vm.lifeYearsEdit = 'a'
    await nextTick()
    expect(wrapper.vm.lengthTrust.valid).toBe(false)
    expect(getLastEvent(wrapper, 'lengthTrustValid')).toBeFalsy()
  })
})
