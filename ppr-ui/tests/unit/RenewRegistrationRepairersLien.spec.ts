import { RenewRegistration } from '@/views'
import { RegistrationRepairersLien } from '@/components/registration'
import { CourtOrder, StickyContainer } from '@/components/common'
import { RouteNames } from '@/enums'
import {
  mockedDebtorNames, mockedFinancingStatementRepairers,
} from './test-data'
import flushPromises from 'flush-promises'
import { createComponent } from './utils'
import { useStore } from '@/store/store'

const store = useStore()

describe('Renew registration component for repairers lien', () => {
  let wrapper: any

  vi.mock('@/utils/ppr-api-helper', () => ({
    getFinancingStatement: vi.fn(() =>
      Promise.resolve({ ...mockedFinancingStatementRepairers })),
  }))

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    wrapper = await createComponent(
      RenewRegistration,
      { appReady: true },
      RouteNames.RENEW_REGISTRATION,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('renders Renew Registration View with child components', async () => {
    expect(wrapper.findComponent(RenewRegistration).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 1
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Review and Complete')
  })

  it('proceeds if valid court order', async () => {
    wrapper.findComponent(CourtOrder).vm.$emit('setCourtOrderValid', true)
    await flushPromises()
    expect(wrapper.vm.registrationValid).toBe(true)
  })

  it('doesnt proceed if validation errors', async () => {
    wrapper.findComponent(CourtOrder).vm.$emit('setCourtOrderValid', false)
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.showInvalid).toBe(true)
  })
})
