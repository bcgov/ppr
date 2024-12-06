import { createComponent } from './utils'
import { nextTick } from 'vue'
import { ExemptionDeclaration } from '@/components/exemptions'

describe('ExemptionDeclaration', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent((ExemptionDeclaration as any), { validate: false })
    await nextTick()
  })

  it('mounts the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('emits updateOption event when declaration option changes', async () => {
    const declarationOptionRadio = await wrapper.find('#destroyed-option')
    declarationOptionRadio.setChecked()
    await nextTick()
    expect(wrapper.emitted('updateOption')).toBeTruthy()
    expect(wrapper.emitted('updateOption')[0]).toEqual(['Destroyed'])
  })

  it('updates declaration reason when user selects a reason', async () => {
    const declarationOptionRadio = await wrapper.find('#destroyed-option')
    declarationOptionRadio.setChecked()
    await nextTick()

    const declarationReasonRadio = await wrapper.find('#Burnt-radio')
    await declarationReasonRadio.setChecked()
    await nextTick()

    expect(wrapper.emitted('updateReason')).toBeTruthy()
    expect(wrapper.emitted('updateReason')[0]).toEqual(['Burnt'])
  })

  it('updates declaration reason when user selects an Other reason', async () => {
    const declarationOptionRadio = await wrapper.find('#destroyed-option')
    declarationOptionRadio.setChecked()
    await nextTick()

    const declarationReasonRadio = await wrapper.find('#Other-radio')
    await declarationReasonRadio.setChecked()
    await nextTick()

    expect(wrapper.emitted('updateReason')).toBeTruthy()
    expect(wrapper.emitted('updateReason')[0]).toEqual(['Other'])
  })

  it('updates other reason text when user specifies other reason', async () => {
    const declarationOptionRadio = await wrapper.find('#destroyed-option')
    declarationOptionRadio.setChecked()
    await nextTick()

    const declarationReasonRadio = await wrapper.find('#Other-radio')
    await declarationReasonRadio.setChecked()
    await nextTick()

    const otherReasonTextField = await wrapper.find('#destroyed-other-text')
    await otherReasonTextField.setValue('Some other reason')
    await nextTick()

    expect(wrapper.emitted('updateOther')).toBeTruthy()
    expect(wrapper.emitted('updateOther')[0]).toEqual(['Some other reason'])
  })

  it('updates declaration date when user selects a date', async () => {
    const declarationOptionRadio = await wrapper.find('#destroyed-option')
    declarationOptionRadio.setChecked()
    await nextTick()

    wrapper.vm.declarationDate = '2024-04-15' // Set a date
    await nextTick()

    expect(wrapper.emitted('updateDate')).toBeTruthy()
    expect(wrapper.emitted('updateDate')[0]).toEqual(['2024-04-15'])
  })
})
