// Libraries
import { nextTick } from 'vue'
import {
  mockedSelectSecurityAgreement,
  mockedRepairersLien,
  mockedSaleOfGoods,
  mockedMarriageMH,
  mockedLengthTrust1,
  mockedLengthTrust2,
  mockedLengthTrust3
} from './test-data'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const store = useStore()

describe('RegistrationLengthTrust SA tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setLengthTrust(mockedLengthTrust1)
    wrapper = await createComponent(RegistrationLengthTrustSummary, { isSummary: false })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // show trust indenture will be true for security agreement only
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('')
    expect(wrapper.vm.trustIndenture).toBe(true)
    expect(wrapper.find('#registration-length').text()).toContain('5 Years')
    expect(wrapper.find('#trust-indenture-summary').text()).toContain('Yes')
  })
})

describe('RegistrationLengthTrust RL tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setRegistrationType(mockedRepairersLien())
    // await store.setLengthTrust(mockedLengthTrust2)
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '2021-01-21'
    })
    wrapper = await createComponent(RegistrationLengthTrustSummary, { isSummary: false })
  })

  it('renders with RL values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.vm.lifeInfinite).toBe('false')
    expect(wrapper.vm.surrenderDate).toBe('2021-01-21')
    expect(wrapper.vm.lengthSummary).toBe('180 Days')
    expect(wrapper.vm.surrenderDateSummary).toBe('January 21, 2021')
    expect(wrapper.find('#registration-length').text()).toContain('180 Days')
    expect(wrapper.find('#trust-indenture-summary').exists()).toBeFalsy()
  })
})

describe('RegistrationLengthTrust SG tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setLengthTrust({
      valid: false,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 3,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setRegistrationType(mockedSaleOfGoods())
    wrapper = wrapper = await createComponent(RegistrationLengthTrustSummary, { isSummary: false })
  })

  it('renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // show trust indenture will be true for security agreement only
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.find('#registration-length').text()).toContain('3 Years')
    expect(wrapper.find('#trust-indenture-summary').exists()).toBeFalsy()
  })
})

describe('RegistrationLengthTrust Crown tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setRegistrationType(mockedMarriageMH())
    await store.setLengthTrust(mockedLengthTrust2)
    wrapper = wrapper = await createComponent(RegistrationLengthTrustSummary, { isSummary: false })
  })

  it('renders with default infinite values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.find('#registration-length').text()).toContain('Infinite')
    expect(wrapper.find('#trust-indenture-summary').exists()).toBeFalsy()
  })
})
