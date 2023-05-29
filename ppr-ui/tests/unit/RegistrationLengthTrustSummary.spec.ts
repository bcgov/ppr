// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  LengthTrustIF
} from '@/interfaces'
import {
  mockedSelectSecurityAgreement,
  mockedRepairersLien,
  mockedSaleOfGoods,
  mockedMarriageMH,
  mockedLengthTrust1,
  mockedLengthTrust2,
  mockedLengthTrust3
} from './test-data'

// Components
import { RegistrationLengthTrustSummary } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const selectDropDown: string = '.registration-bar-type-select'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  isRenewal: Boolean
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((RegistrationLengthTrustSummary as any), {
    localVue,
    propsData: { isRenewal },
    store,
    vuetify
  })
}

describe('RegistrationLengthTrust SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setLengthTrust(mockedLengthTrust1)
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
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
  let wrapper: Wrapper<any>
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
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
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
  let wrapper: Wrapper<any>
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
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
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
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.setRegistrationType(mockedMarriageMH())
    await store.setLengthTrust(mockedLengthTrust2)
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default infinite values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.find('#registration-length').text()).toContain('Infinite')
    expect(wrapper.find('#trust-indenture-summary').exists()).toBeFalsy()
  })
})
