// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { mockedRegisteringParty1 } from './test-data'

// Components
import { RegisteringParty } from '@/components/parties/party'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Debtors> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegisteringParty, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('RegisteringParty tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
  })
})

describe('RegisteringParty store tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders registering party table and headers', async () => {
    expect(wrapper.find('.registering-table').exists()).toBeTruthy()
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .registering-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .registering-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ABC REGISTERING')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    
    expect(wrapper.find('.actions-cell').exists()).toBeTruthy()
  })
})


describe('RegisteringParty store undo test', () => {
  let wrapper: Wrapper<any>
  let sandbox
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {

    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: 
      {
        businessName: 'ABC REGISTERING COMPANY LTD.',
        address: {
          street: '1234 Fort St.',
          streetAdditional: '2nd floor',
          city: 'Victoria',
          region: 'BC',
          country: 'CA',
          postalCode: 'V8R1L2',
          deliveryInstructions: ''
        },
        action: ActionTypes.EDITED
      }
    })

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(
      new Promise(resolve => resolve({
        data: {
          businessName: 'ANOTHER COMPANY',
        }
      })))
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })



  it('displays the correct data in the table rows', async () => {
    
    
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .registering-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ABC REGISTERING')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    
    expect(item1.querySelectorAll('td')[4].textContent).toContain('Undo')
  })

  it('displays the correct data in the table rows', async () => {
    let dropButtons = wrapper.findAll('.edit-btn')
    expect(dropButtons.length).toBe(1)
    dropButtons.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'setRegisteringParty')).toBe(null)
  })
})
