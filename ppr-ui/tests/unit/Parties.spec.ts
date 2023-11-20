import { nextTick } from 'vue'
import PartySummary from '@/components/parties/PartySummary.vue' // need to import like this
import { Parties } from '@/components/parties'
import { Debtors } from '@/components/parties/debtor'
import { RegisteringPartyChange, SecuredParties } from '@/components/parties/party'
import { CautionBox } from '@/components/common'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import {
  mockedRegisteringParty1,
  mockedSelectSecurityAgreement
} from './test-data'
import flushPromises from 'flush-promises'

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
    wrapper = await createComponent(Parties, { isSummary: false })
    await nextTick()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(false)
    expect(wrapper.findComponent(PartySummary).exists()).toBe(false)
  })

  it.only('does show the registering party', async () => {
    expect(wrapper.vm.isRoleStaffSbc).toBe(false)
    expect(wrapper.findComponent(RegisteringPartyChange).isVisible()).toBe(true)
  })

  it('renders in summary mode', async () => {
    wrapper = await createComponent(Parties, { isSummary: true })
    await nextTick()
    await flushPromises()

    expect(wrapper.vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(false)
    expect(wrapper.findComponent(Debtors).exists()).toBe(false)
  })
})
