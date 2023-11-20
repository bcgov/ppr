// Libraries
import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import {
  mockedSecuredParties1,
  mockedDebtors1,
  mockedRegisteringParty1,
  mockedSelectSecurityAgreement
} from './test-data'
import { PartySummary } from '@/components/parties'
import { createComponent } from './utils/helper-functions'
const store = useStore()

describe('Party Summary SA tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(PartySummary)
    await nextTick()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(PartySummary).exists()).toBe(true)
    expect(wrapper.find('.secured-party-summary').exists()).toBeTruthy()
  })
})

describe('Secured Party list tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(PartySummary)
    await nextTick()
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.secured-party-summary .party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.secured-party-summary .party-summary-table th').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.secured-party-summary .party-row').length
    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.secured-party-summary .party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('SECURED PARTY COMPANY LTD.')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('test@company.com')
  })
})

describe('Debtor list tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)

    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtors1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(PartySummary)
  })

  it('renders debtor table and headers', async () => {
    expect(wrapper.find('.debtor-summary .party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.debtor-summary .party-summary-table th').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.debtor-summary .party-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.debtor-summary .party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('TEST 1 INDIVIDUAL DEBTOR')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[3].textContent).toContain('June 15, 1990')
  })
})

describe('Registering Party tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(PartySummary)
  })

  it('renders registering party table and headers', async () => {
    expect(wrapper.find('.registering-party-summary .party-summary-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.registering-party-summary .party-summary-table th').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.registering-party-summary .party-row').length
    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.registering-party-summary .party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ABC REGISTERING')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
  })
})
