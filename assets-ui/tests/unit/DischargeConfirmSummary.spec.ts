import { nextTick } from 'vue'
import { DischargeConfirmSummary } from '@/components/common'
import { UIRegistrationTypes } from '@/enums'
import { createComponent, getLastEvent } from './utils'

// selectors
const summaryInfo = '.summary-info'
const checkboxTxtNormal = '.copy-normal'
const checkboxTxtError = '.check-box-error'
const checkboxId1 = '#discharge-confirm-checkbox-1'
const checkboxId2 = '#discharge-confirm-checkbox-2'
const checkboxId3 = '#discharge-confirm-checkbox-3'

describe('Discharge confirm summary component tests', () => {
  let wrapper: any
  const regNum = '123456B'
  const regType = UIRegistrationTypes.SECURITY_AGREEMENT
  const colSummary = 'General Collateral and 3 Vehicles'
  const showErrors = false

  beforeEach(async () => {
    wrapper = await createComponent(DischargeConfirmSummary, {
      setRegNum: regNum,
      setRegType: regType,
      setCollateralSummary: colSummary,
      setShowErrors: showErrors
    })
  })

  it('renders component with given props', () => {
    expect(wrapper.findComponent(DischargeConfirmSummary).exists()).toBe(true)
    expect(wrapper.vm.checkbox1).toBe(false)
    expect(wrapper.vm.checkbox2).toBe(false)
    expect(wrapper.vm.checkbox3).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    const info = wrapper.findAll(summaryInfo)
    expect(info.length).toBe(1)
    expect(info.at(0).text()).toContain(`Base Registration Number: ${regNum}`)
    expect(info.at(0).text()).toContain(`Registration Type: ${regType}`)
    expect(info.at(0).text()).toContain(`Collateral: ${colSummary}`)
    expect(wrapper.findAll(checkboxId1).length).toBe(1)
    expect(wrapper.findAll(checkboxId2).length).toBe(1)
    expect(wrapper.findAll(checkboxId3).length).toBe(1)
    const checkboxTxt = wrapper.findAll(checkboxTxtNormal)
    expect(checkboxTxt.length).toBe(3)
    expect(checkboxTxt.at(0).text()).toContain('discharge this registration.')
    expect(checkboxTxt.at(1).text()).toContain('all collateral on this registration will be released.')
    expect(checkboxTxt.at(2).text()).toContain('all Secured Parties will be notified.')
    expect(wrapper.findAll(checkboxTxtError).length).toBe(0)
  })

  it('validates with checkboxes', async () => {
    const checkbox1 = await wrapper.find(checkboxId1)
    const checkbox2 = await wrapper.find(checkboxId2)
    const checkbox3 = await wrapper.find(checkboxId3)

    // Verify defaults
    expect(wrapper.vm.checkbox1).toBe(false)
    expect(wrapper.vm.checkbox2).toBe(false)
    expect(wrapper.vm.checkbox3).toBe(false)
    // not valid yet

    // Mock model change due to vuetify limitations
    checkbox1.setValue(true)
    await nextTick()
    expect(wrapper.vm.checkbox1).toBe(true)
    // still not valid (1/3)
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBeNull()

    // Mock model change due to vuetify limitations
    checkbox2.setValue(true)
    await nextTick()
    expect(wrapper.vm.checkbox2).toBe(true)
    // still not valid (2/3)
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBeNull()

    // Mock model change due to vuetify limitations
    checkbox3.setValue(true)
    await nextTick()
    expect(wrapper.vm.checkbox3).toBe(true)
    // should be valid now (3/3)
    expect(wrapper.vm.valid).toBe(true)
    expect(getLastEvent(wrapper, 'valid')).toBe(true)

    // Mock model change due to vuetify limitations
    checkbox1.setValue(false)
    await nextTick()
    expect(wrapper.vm.checkbox3).toBe(true)
    // should be invalid again
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBe(false)
  })

  it('shows validation when asked by prop', async () => {
    wrapper = await createComponent(DischargeConfirmSummary, {
      setRegNum: regNum,
      setRegType: regType,
      setCollateralSummary: colSummary,
      setShowErrors: true
    })
    const normalCheckboxes = await wrapper.findAll(checkboxTxtNormal)
    const errorCheckboxes = await wrapper.findAll(checkboxTxtError)

    expect(normalCheckboxes.length).toBe(0)
    expect(errorCheckboxes.length).toBe(3)

    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(0)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(3)
    const checkbox1 = wrapper.find(checkboxId1)
    checkbox1.setValue(true)
    await nextTick()

    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(1)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(2)
    const checkbox2 = wrapper.find(checkboxId2)
    checkbox2.setValue(true)
    await nextTick()

    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(2)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(1)
    const checkbox3 = wrapper.find(checkboxId3)
    checkbox3.setValue(true)
    await nextTick()

    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(3)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(0)

    checkbox2.setValue(false)
    await nextTick()

    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(2)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(1)
    expect(wrapper.findAll(checkboxTxtError).at(0).text()).toContain(
      'all collateral on this registration will be released.'
    )
  })
})
