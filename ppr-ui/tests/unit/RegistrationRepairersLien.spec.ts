// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  LengthTrustIF
} from '@/interfaces'
import {
  mockedRepairersLien
} from './test-data'

// Components
import { RegistrationRepairersLien } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  isRenewal: Boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationRepairersLien, {
    localVue,
    propsData: { isRenewal },
    store,
    vuetify
  })
}

describe('RegistrationLengthTrust RL tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedRepairersLien())
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with RL values', async () => {
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.vm.surrenderDate).toBe('')
    expect(wrapper.vm.lengthTrust.showInvalid).toBe(false)
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    expect(wrapper.vm.showErrorSurrenderDate).toBe(false)
    expect(wrapper.vm.minSurrenderDate).toBeDefined()
    expect(wrapper.vm.lienAmount).toBe('')
    expect(wrapper.vm.lienAmountSummary).toBe('Not entered')
    expect(wrapper.vm.surrenderDateSummary).toBe('Not entered')
  })
  it('renders lienAmount', async () => {
    wrapper.vm.$data.lienAmount = '$1,000,000'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    wrapper.vm.$data.lienAmount = '$1'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    wrapper.vm.$data.lienAmount = 'junk'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('Lien amount must be a number greater than 0.')
    expect(wrapper.vm.showErrorLienAmount).toBe(true)
    wrapper.vm.$data.lienAmount = '$1$'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('Lien amount must be a number greater than 0.')
    expect(wrapper.vm.showErrorLienAmount).toBe(true)
  })
})

describe('RegistrationLengthTrust RL renewal test', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedRepairersLien())
    await store.dispatch('setRegistrationExpiryDate', '2021-07-28T07:59:59+00:00')
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '2021-01-21T08:00:00+00:00',
      lienAmount: ''
    })

    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.find('#length-in-years').exists()).toBe(false)
    // new expiry date (180 days)
    expect(wrapper.find('#new-expiry-rl').text()).toContain('January 23, 2022')
    // surrender date
    expect(wrapper.find('#surrender-date').text()).toContain('January 21, 2021')
  })
})
