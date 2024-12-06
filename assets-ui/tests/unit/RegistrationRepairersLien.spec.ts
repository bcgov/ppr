import Vue, { nextTick } from 'vue'
import {
  mockedRepairersLien
} from './test-data'
import { RegistrationRepairersLien } from '@/components/registration'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const store = useStore()

describe('RegistrationLengthTrust RL tests', () => {
  let wrapper
  beforeEach(async () => {
    await store.setRegistrationType(mockedRepairersLien())
    wrapper = await createComponent(RegistrationRepairersLien, { isRenewal: false })
  })

  it('renders with RL values', async () => {
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.vm.surrenderDate).toBe('')
    expect(wrapper.vm.lengthTrust.showInvalid).toBe(false)
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    expect(wrapper.vm.showErrorSurrenderDate).toBe(false)
    expect(wrapper.vm.minSurrenderDate).toBeDefined()
    expect(wrapper.vm.lienAmount).toBe('')
    expect(wrapper.vm.lienAmountSummary).toBe('Not entered')
    expect(wrapper.vm.surrenderDateSummary).toBe('Not entered')
  })
  it('renders lienAmount', async () => {
    wrapper.vm.lienAmount = '$1,000,000'
    await nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    wrapper.vm.lienAmount = '$1'
    await nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    wrapper.vm.lienAmount = 'junk'
    await nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('Lien amount must be a number greater than 0.')
    expect(wrapper.vm.showErrorLienAmount).toBe(true)
    wrapper.vm.lienAmount = '$1$'
    await nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('Lien amount must be a number greater than 0.')
    expect(wrapper.vm.showErrorLienAmount).toBe(true)
  })
})

describe('RegistrationLengthTrust RL renewal test', () => {
  let wrapper
  beforeEach(async () => {
    await store.setRegistrationType(mockedRepairersLien())
    await store.setRegistrationExpiryDate('2021-07-28T07:59:59+00:00')
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '2021-01-21T08:00:00+00:00',
      lienAmount: ''
    })

    wrapper = await createComponent(RegistrationRepairersLien, { isRenewal: true })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.find('#length-in-years').exists()).toBe(false)
    // new expiry date (180 days)
    expect(wrapper.find('#new-expiry-rl').text()).toContain('January 23, 2022')
    // surrender date
    expect(wrapper.find('#surrender-date').text()).toContain('January 21, 2021')
  })
})
