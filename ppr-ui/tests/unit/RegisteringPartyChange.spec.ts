import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import {
  mockedDebtors1,
  mockedRegisteringParty1,
  mockedSecuredParties1,
  mockedSelectSecurityAgreement
} from './test-data'
import { EditParty, PartySearch, RegisteringParty, RegisteringPartyChange } from '@/components/parties/party'
import { createComponent } from './utils'

const store = useStore()

describe('Parties tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAuthRoles([])
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setAddSecuredPartiesAndDebtors({
      debtors: [],
      securedParties: [],
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(RegisteringPartyChange)
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
    // does not show party search and edit when not change
    expect(wrapper.findComponent(PartySearch).exists()).toBe(false)
    expect(wrapper.findComponent(EditParty).exists()).toBe(false)
  })

  it('shows the search on change', async () => {
    wrapper.vm.openChangeScreen = true
    await nextTick()
    // does not show party search and edit when not change
    expect(wrapper.findComponent(PartySearch).exists()).toBe(true)
    expect(wrapper.findComponent(EditParty).exists()).toBe(false)
  })

  it('handles address country change in registering party', async () => {
    const newRegParty = {
      ...mockedRegisteringParty1
    }
    // default is saved properly in store
    expect(wrapper.vm.registeringParty).toEqual(newRegParty)

    // update address
    const addressChange1 = {
      street: 'test change 1',
      streetAdditional: '1',
      city: 'Vancouver',
      region: 'BC',
      country: 'CA',
      postalCode: 'V0N 1G0',
      deliveryInstructions: ''
    }
    newRegParty.address = addressChange1
    await store.setAddSecuredPartiesAndDebtors(
      { registeringParty: newRegParty, debtors: [], securedParties: [] }
    )
    expect(store.getStateModel.registration.parties.registeringParty.address).toEqual(addressChange1)
    expect(wrapper.vm.registeringParty).toEqual(newRegParty)

    // update address again - change country
    const addressChange2 = {
      street: 'test change 2',
      streetAdditional: '1',
      city: 'Philadelphia',
      region: 'PA',
      country: 'US',
      postalCode: '19132-4594',
      deliveryInstructions: ''
    }
    newRegParty.address = addressChange2
    await store.setAddSecuredPartiesAndDebtors(
      { registeringParty: newRegParty, debtors: [], securedParties: [] }
    )
    expect(
      store.getStateModel.registration.parties.registeringParty.address
    ).toEqual(addressChange2)
    expect(wrapper.vm.registeringParty).toEqual(newRegParty)
  })

  it('trigger change registering party edit', async () => {
    wrapper.vm.changeRegisteringParty()
    await nextTick()
    // show cancel button
    expect(wrapper.find('#cancel-btn-chg-reg-party').exists()).toBeTruthy()
  })
})

describe('Parties sbc user tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)
    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtors1,
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    store.setRoleSbc(true)
    wrapper = await createComponent(RegisteringPartyChange)
  })

  it('shows the party search screen for sbc', async () => {
    expect(wrapper.findComponent(PartySearch).isVisible()).toBe(true)
    // no tooltip
    expect(wrapper.find('.registering-tooltip').exists()).toBeFalsy()
    // no cancel button
    expect(wrapper.find('#cancel-btn-chg-reg-party').exists()).toBeFalsy()
  })
})
