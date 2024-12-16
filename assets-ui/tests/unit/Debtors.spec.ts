import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { mockedDebtors1, mockedDebtorsAmendment, mockedDebtorsDeleted } from './test-data'

// Components
import { Debtors, EditDebtor } from '@/components/parties/debtor'
import { RegistrationFlowType } from '@/enums'
import { createComponent, getLastEvent } from './utils'

const store = useStore()

// Input field selectors / buttons
const addIndividualSelector: string = '#btn-add-individual'
const addBusinessSelector: string = '#btn-add-business'

describe('Debtor SA tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(Debtors)
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditDebtor).exists()).toBeFalsy()
  })

  it('add debtor button shows the add form', async () => {
    expect(wrapper.find(addIndividualSelector).exists()).toBe(true)
    expect(wrapper.find(addBusinessSelector).exists()).toBe(true)
    wrapper.find(addIndividualSelector).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(EditDebtor).exists()).toBeTruthy()
    expect(wrapper.findComponent(EditDebtor).isVisible()).toBe(true)
  })
})

describe('Debtor store tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtors1
    })
    wrapper = await createComponent(Debtors)
  })

  it('renders debtor table and headers', async () => {
    expect(wrapper.find('.debtor-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('th').length).toBe(5)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.debtor-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.debtor-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('TEST 1 INDIVIDUAL DEBTOR')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[3].textContent).toContain('June 15, 1990')
  })
})

describe('Debtor amendment tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtorsAmendment
    })
    await store.setOriginalAddSecuredPartiesAndDebtors({
      debtors: mockedDebtorsAmendment
    })
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(Debtors)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.debtor-row').length
    // three debtors, three rows
    expect(rowCount).toEqual(3)
  })

  it('displays the correct chips in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.debtor-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.debtor-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.debtor-row')[2]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('DELETED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('ADDED')
  })

  it('displays the correct actions in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.debtor-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.debtor-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.debtor-row')[2]
    expect(item1.querySelectorAll('td')[4].textContent).toContain('Undo')
    const dropDowns = await wrapper.findAll('.smaller-actions')
    // 2 drop downs
    expect(dropDowns.length).toBe(2)
    // click the drop down arrow
    dropDowns.at(0).trigger('click')
    await nextTick()
    expect(item2.querySelectorAll('td')[4].textContent).toContain('Undo')
    expect(item3.querySelectorAll('td')[4].textContent).toContain('Edit')
  })

  it('fires the open event', async () => {
    wrapper.vm.initEdit(1)
    expect(getLastEvent(wrapper, 'debtorOpen')).toBeTruthy()
  })
})

describe('Debtor validation tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtorsDeleted
    })
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(Debtors)
  })

  it('displays the correct rows', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.debtor-row').length
    // one greyed out row
    expect(rowCount).toEqual(1)
    const item1 = wrapper.vm.$el.querySelectorAll('.debtor-row')[0]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('DELETED')
  })

  it('displays the error', async () => {
    wrapper = await createComponent(Debtors, { setShowInvalid: true })
    expect(wrapper.vm.getDebtorValidity()).toBe(false)
    wrapper.vm.showErrorDebtors = true
    await nextTick()
    expect(wrapper.findAll('.border-error-left').length).toBe(1)
  })

  it('goes from valid to invalid', async () => {
    wrapper.vm.debtors = mockedDebtors1
    await nextTick()
    expect(wrapper.vm.getDebtorValidity()).toBe(true)
    // remove said debtor
    wrapper.vm.debtors = []
    await nextTick()
    expect(wrapper.vm.getDebtorValidity()).toBe(false)
  })
})
