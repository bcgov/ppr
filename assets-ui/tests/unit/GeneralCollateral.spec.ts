import { nextTick } from 'vue'
import { GenColEdit, GenColSummary, GeneralCollateral, GenColAmend } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
const store = useStore()

describe('General Collateral tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
    wrapper = await createComponent(GeneralCollateral, { isSummary: false, setShowInvalid: false })
  })

  it('renders summary view when prop set', async () => {
    wrapper = await createComponent(GeneralCollateral, { isSummary: true, setShowInvalid: false })
    await nextTick()

    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.findComponent(GenColEdit).exists()).toBe(false)
  })

  it('renders edit view and invalid when prop set', async () => {
    wrapper = await createComponent(GeneralCollateral, { isSummary: true, setShowInvalid: true })
    await nextTick()

    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.findComponent(GenColEdit).exists()).toBe(false)
    expect(wrapper.vm.showInvalid).toBe(true)
  })

  it('renders amendment view for amendments', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(GeneralCollateral, { isSummary: true, setShowInvalid: false })
    await nextTick()

    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.findComponent(GenColAmend).exists()).toBe(false)
  })
})
