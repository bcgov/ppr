// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

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
setActivePinia(createPinia())
const store = useStore()

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

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((RegisteringParty as any), {
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
    await store.setAddSecuredPartiesAndDebtors({
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
    await store.setAddSecuredPartiesAndDebtors({
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
          businessName: 'ANOTHER COMPANY'
        }
      })))
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)

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
    const dropButtons = wrapper.findAll('.edit-btn')
    expect(dropButtons.length).toBe(1)
    dropButtons.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'setRegisteringParty')).toBe(null)
  })
})

describe('Test result table with error', () => {
  let wrapper: Wrapper<any>
  let sandbox
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null
    })

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(
      new Promise(resolve => resolve({
        data: null
      })))
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays correct elements for no results', async () => {
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
    expect(wrapper.vm.registeringParty.length).toBe(0)
    expect(wrapper.find('.registering-table').exists()).toBe(true)
    const noResultsDisplay = wrapper.findAll('tr td')
    expect(noResultsDisplay.at(0).text()).toContain('We were unable to retrieve Registering Party')
    expect(wrapper.find('#retry-registering-party').exists()).toBe(true)
  })
})
