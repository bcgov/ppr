import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { Wrapper } from '@vue/test-utils'
import { createComponent, getTestId } from './utils'
import { EffectiveDate } from '@/components/unitNotes'
import { SharedDatePicker } from '@/components/common'
import { useStore } from '@/store/store'

Vue.use(Vuetify)
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
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(EffectiveDate, props)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('should render the component', () => {
    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDate)

    expect(EffectiveDateTimeComponent.exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.findComponent(SharedDatePicker).exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.find(getTestId('date-summary-label')).exists()).toBeFalsy()

    const immediateDate = <HTMLInputElement>(
      EffectiveDateTimeComponent.find(getTestId('immediate-date-radio'))).element

    const pastDate = <HTMLInputElement>(
      EffectiveDateTimeComponent.find(getTestId('past-date-radio'))).element

    expect(immediateDate.checked).toBeTruthy()
    expect(pastDate.checked).toBeFalsy()
  })

  it('should set the Effective and Expiry Date Times', async () => {
    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDate)

    expect(wrapper.vm.effectiveDate).toBe('')

    EffectiveDateTimeComponent.find(getTestId('past-date-radio')).trigger('click')
    EffectiveDateTimeComponent.findComponent(SharedDatePicker).vm.$emit('emitDate', '2023-07-01')
    expect(wrapper.vm.selectedPastDate).toBeTruthy()

    await Vue.nextTick()

    const dateSummaryLabel = EffectiveDateTimeComponent.find(getTestId('date-summary-label'))
    expect(dateSummaryLabel.exists()).toBeTruthy()
    expect(dateSummaryLabel.text()).toContain('July 1, 2023')
  })
})
