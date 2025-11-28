import { nextTick } from 'vue'
import { createComponent, getTestId } from './utils'
import { EffectiveDate } from '@/components/unitNotes'
import { useStore } from '@/store/store'
import { InputFieldDatePicker } from '@/components/common'
import { dataTestId } from './plugins/data-test-id'
const store = useStore()

const props = {
  content: {
    title: 'Effective Date',
    description: 'Select the effective date for this note',
    sideLabel: 'Effective Date'
  },
  validate: false
}

describe('EffectiveDate', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EffectiveDate, props)
  })

  it('should render the component', () => {
    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDate)

    expect(EffectiveDateTimeComponent.exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.findComponent(InputFieldDatePicker).exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.find(getTestId('date-summary-label')).exists()).toBeFalsy()

    const immediateDate = <HTMLInputElement>(
      dataTestId(EffectiveDateTimeComponent).findInputByTestId('immediate-date-radio')).element

    const pastDate = <HTMLInputElement>(
      dataTestId(EffectiveDateTimeComponent).findInputByTestId('past-date-radio')).element

    expect(immediateDate.checked).toBeTruthy()
    expect(pastDate.checked).toBeFalsy()
  })

  it('should set the Effective and Expiry Date Times', async () => {
    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDate)

    expect(wrapper.vm.effectiveDate).toBe('')

    dataTestId(EffectiveDateTimeComponent).findInputByTestId('past-date-radio').setValue(true)
    EffectiveDateTimeComponent.findComponent(InputFieldDatePicker).vm.$emit('emitDate', '2023-07-01')
    expect(wrapper.vm.selectedPastDate).toBeTruthy()

    await nextTick()

    const dateSummaryLabel = EffectiveDateTimeComponent.find(getTestId('date-summary-label'))
    expect(dateSummaryLabel.exists()).toBeTruthy()
    expect(dateSummaryLabel.text()).toContain('July 1, 2023')
  })
})
