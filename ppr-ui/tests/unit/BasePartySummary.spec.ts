import {
  mockedSecuredParties1,
  mockedDebtors1,
  mockedRegisteringParty1,
  mockedSecuredPartiesAmendment,
  mockedSelectSecurityAgreement
} from './test-data'
import { createComponent } from './utils'
import { BasePartySummary } from '@/components/parties/summaries'
import { partyTableHeaders } from '@/resources'
import { RegistrationFlowType } from '@/enums'
import { useStore } from '@/store/store'

const store = useStore()

const props = {
  setHeaders: partyTableHeaders,
  setItems: mockedSecuredParties1,
  setOptions: {
    enableNoDataAction: false,
    header: 'true',
    iconColor: '',
    iconImage: '',
    isDebtorSummary: false,
    isRegisteringParty: false
  }
}

describe('Party Summary SA tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(BasePartySummary, props)
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(BasePartySummary).exists()).toBe(true)
    expect(wrapper.vm.$props.setItems.length).toBe(1)
    expect(wrapper.vm.items.length).toBe(1)
    expect(wrapper.find('.summary-header').exists()).toBeTruthy()
  })
})

describe('Secured Party list tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(BasePartySummary, props)
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.party-summary-table th').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.party-row').length
    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('SECURED PARTY COMPANY LTD.')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('test@company.com')
  })
})

describe('Debtor list tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(BasePartySummary, {
      ...props,
      setItems: mockedDebtors1,
      setOptions: {
        ...props.setOptions,
        isDebtorSummary: true
      }
    })
  })

  it('renders debtor table and headers', async () => {
    expect(wrapper.find('.party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.party-summary-table th').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.party-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('TEST 1 INDIVIDUAL DEBTOR')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('June 15, 1990')
  })
})

describe('Secured Party amendment list tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(BasePartySummary, { ...props, setItems: mockedSecuredPartiesAmendment })
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.party-summary-table th').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.party-row').length
    expect(rowCount).toEqual(3)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.party-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.party-row')[2]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ADDED')

    expect(item2.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('DELETED')
  })
})
