// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedDebtors1,
  mockedRegisteringParty1,
  mockedSecuredParties1,
  mockedSelectSecurityAgreement
} from './test-data'

// Components
import PartySummary from '@/components/parties/PartySummary.vue' // need to import like this
import { Parties } from '@/components/parties'
import { Debtors } from '@/components/parties/debtor'
import { RegisteringPartyChange, SecuredParties } from '@/components/parties/party'
import { CautionBox } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (isSummary: boolean): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((Parties as any), {
    localVue,
    propsData: { isSummary: isSummary },
    store,
    vuetify
  })
}

describe('Parties tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setAuthRoles([])
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setAddSecuredPartiesAndDebtors({
      debtors: [],
      securedParties: [],
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent(false)
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(false)
    expect(wrapper.findComponent(PartySummary).exists()).toBe(false)
    // switch to summary version
    await wrapper.setProps({ isSummary: true })
    expect(wrapper.findComponent(PartySummary).exists()).toBe(true)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(false)
    expect(wrapper.findComponent(Debtors).exists()).toBe(false)
  })

  it('does show the registering party', async () => {
    expect(wrapper.findComponent(RegisteringPartyChange).isVisible()).toBe(true)
    // show tooltip
    expect(wrapper.find('.registering-tooltip').exists()).toBeTruthy()
  })
})
