import { mockedRegisteringParty1 } from './test-data'
import { RegisteringParty } from '@/components/parties/party'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import flushPromises from 'flush-promises'
import { createComponent, getLastEvent } from './utils'
import { useStore } from '@/store/store'

const store = useStore()

describe('RegisteringParty tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(RegisteringParty)
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
  })
})

describe('RegisteringParty store tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(RegisteringParty)
  })

  it('renders registering party table and headers', async () => {
    expect(wrapper.find('.registering-table').exists()).toBeTruthy()
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.registering-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.registering-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('ABC REGISTERING')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')

    expect(wrapper.find('.actions').exists()).toBeTruthy()
  })
})

describe('RegisteringParty store undo test', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty:
      {
        partyId: '1',
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

    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(RegisteringParty)
  })

  it('displays the correct data in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.registering-row')[0]

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
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null
    })

    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(RegisteringParty)
  })


  it('renders and displays correct elements for no results', async () => {
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
    expect(wrapper.vm.registeringParty.length).toBe(1)
    expect(wrapper.vm.registeringParty).toStrictEqual([{}])
    expect(wrapper.find('.registering-table').exists()).toBe(true)
    const noResultsDisplay = wrapper.findAll('tr td')
    expect(noResultsDisplay.at(0).text()).toContain('We were unable to retrieve Registering Party')
    expect(wrapper.find('#retry-registering-party').exists()).toBe(true)
  })
})
