// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { mockedRegisteringParty1, mockedSecuredParties2 } from './test-data'
import { axios as pprAxios } from '@/utils/axios-ppr'
import sinon from 'sinon'

// Components
import { EditParty } from '@/components/parties/party'
import { SecuredPartyTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-party'
const cancelButtonSelector: string = '#cancel-btn-party'
const removeButtonSelector: string = '#remove-btn-party'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (activeIndex: Number, invalidSection: boolean): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditParty, {
    localVue,
    propsData: { activeIndex, invalidSection },
    store,
    vuetify
  })
}

describe('Secured Party add individual tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    // radio button value is blank
    expect(wrapper.vm.partyType).toBe(SecuredPartyTypes.NONE)
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes('disabled')).toBe('disabled')
  })

  it('adds a secured party to the store', async () => {
    const radioInput = wrapper.findAll('input[type="radio"]')
    const radioIsIndividual = radioInput.at(0)

    await radioIsIndividual.trigger('click')
    wrapper.find('#txt-first-party').setValue('JOE')
    wrapper.find('#txt-last-party').setValue('SCHMOE')
    wrapper.find('#txt-email-party').setValue('joe@apples.com')
    // for address
    wrapper.vm.$data.currentSecuredParty.address.street = 'street'
    wrapper.vm.$data.currentSecuredParty.address.city = 'victoria'
    wrapper.vm.$data.currentSecuredParty.address.region = 'BC'
    wrapper.vm.$data.currentSecuredParty.address.country = 'CA'
    wrapper.vm.$data.currentSecuredParty.address.postalCode = 'v8r1w3'
    await Vue.nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getters.getAddSecuredPartiesAndDebtors.securedParties.length).toBe(1)
  })
})

describe('Secured Party add business tests', () => {
  let wrapper: Wrapper<any>
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    // GET autocomplete results
    const get = sandbox.stub(pprAxios, 'get')
    get.returns(
      new Promise(resolve =>
        resolve({
          data: []
        })
      )
    )
    wrapper = createComponent(-1, false)
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    expect(wrapper.vm.currentSecuredParty.businessName).toBe('')
  })

  it('adds a secured party business to the store', async () => {
    const radioInput = wrapper.findAll('input[type="radio"]')
    const radioIsBusiness = radioInput.at(1)

    await radioIsBusiness.trigger('click')
    await Vue.nextTick()
    wrapper.find('#txt-name-party').setValue('TONYS TOOLS')
    // for address
    wrapper.vm.$data.currentSecuredParty.address.street = 'street'
    wrapper.vm.$data.currentSecuredParty.address.city = 'victoria'
    wrapper.vm.$data.currentSecuredParty.address.region = 'BC'
    wrapper.vm.$data.currentSecuredParty.address.country = 'CA'
    wrapper.vm.$data.currentSecuredParty.address.postalCode = 'v8r1w3'
    await Vue.nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getters.getAddSecuredPartiesAndDebtors.securedParties[1].businessName).toBe('TONYS TOOLS')
  })
})

describe('Secured Party edit individual tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties2
    })
    wrapper = createComponent(0, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders secured party when editing', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    expect(wrapper.vm.currentSecuredParty.personName.first).toEqual('TEST')
    expect(wrapper.vm.currentSecuredParty.personName.last).toEqual('INDIVIDUAL PARTY')
    expect(wrapper.vm.currentSecuredParty.emailAddress).toEqual('test@person.com')
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
    expect(wrapper.find('.border-error-left').exists()).toBe(false)
  })

  it('shows error bar', async () => {
    await wrapper.setProps({ setShowErrorBar: true })
    await Vue.nextTick()
    expect(wrapper.find('.border-error-left').exists()).toBe(true)
  })
})

describe('Registering party test', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders registering party when editing', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    wrapper.vm.$props.setIsRegisteringParty = true
    await Vue.nextTick()
    expect(wrapper.find('.add-party-header').text()).toContain('Registering')
  })
})
