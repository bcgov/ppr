// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedSecuredParties1,
  mockedDebtors1,
  mockedRegisteringParty1
} from './test-data'

// Components
import { PartySummary } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
  return mount(PartySummary, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Party Summary SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(PartySummary).exists()).toBe(true)
    expect(wrapper.find('#party-summary').exists()).toBeTruthy()
  })
})

describe('Secured Party list tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.party-summary-table .text-start').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row').length
    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('SECURED PARTY COMPANY LTD.')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('test@company.com')
  })
})

describe('Debtor list tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders debtor table and headers', async () => {
    expect(wrapper.find('.debtor-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.debtor-summary-table .text-start').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .debtor-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .debtor-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('TEST 1 INDIVIDUAL DEBTOR')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[3].textContent).toContain('June 16, 1990')
  })
})

describe('Registering Party tests', () => {
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
    // column header class is text-start
    expect(wrapper.findAll('.registering-table .text-start').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .registering-row').length
    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .registering-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ABC REGISTERING')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
  })
})
