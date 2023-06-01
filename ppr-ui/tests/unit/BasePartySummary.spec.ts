// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { useStore } from '@/store/store'
import { createPinia, setActivePinia } from 'pinia'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedSecuredParties1,
  mockedDebtors1,
  mockedRegisteringParty1,
  mockedSecuredPartiesAmendment,
  mockedSelectSecurityAgreement
} from './test-data'

// Components
import { BasePartySummary } from '@/components/parties/summaries'
import { BaseHeaderIF, PartyIF, PartySummaryOptionsI } from '@/interfaces'
import { partyTableHeaders } from '@/resources'
import { RegistrationFlowType } from '@/enums'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Debtors> object with the given parameters.
 */
function createComponent (
  setHeaders: Array<BaseHeaderIF>,
  setItems: Array<PartyIF>,
  setOptions: PartySummaryOptionsI
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((BasePartySummary as any), {
    localVue,
    propsData: { setHeaders, setItems, setOptions },
    store,
    vuetify
  })
}

describe('Party Summary SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = createComponent(partyTableHeaders, mockedSecuredParties1, {
      enableNoDataAction: false,
      header: 'true',
      iconColor: '',
      iconImage: '',
      isDebtorSummary: false,
      isRegisteringParty: false
    })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(BasePartySummary).exists()).toBe(true)
    expect(wrapper.vm.$props.setItems.length).toBe(1)
    expect(wrapper.vm.items.length).toBe(1)
    expect(wrapper.find('.summary-header').exists()).toBeTruthy()
  })
})

describe('Secured Party list tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent(partyTableHeaders, mockedSecuredParties1, {
      enableNoDataAction: false,
      header: 'true',
      iconColor: '',
      iconImage: '',
      isDebtorSummary: false,
      isRegisteringParty: false
    })
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
    wrapper = createComponent(partyTableHeaders, mockedDebtors1, {
      enableNoDataAction: false,
      header: 'true',
      iconColor: '',
      iconImage: '',
      isDebtorSummary: true,
      isRegisteringParty: false
    })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders debtor table and headers', async () => {
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

    expect(item1.querySelectorAll('td')[0].textContent).toContain('TEST 1 INDIVIDUAL DEBTOR')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[3].textContent).toContain('June 15, 1990')
  })
})

describe('Secured Party amendment list tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = createComponent(partyTableHeaders, mockedSecuredPartiesAmendment, {
      enableNoDataAction: false,
      header: 'true',
      iconColor: '',
      iconImage: '',
      isDebtorSummary: false,
      isRegisteringParty: false
    })
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
    expect(rowCount).toEqual(3)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[2]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ADDED')

    expect(item2.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('DELETED')
  })
})
