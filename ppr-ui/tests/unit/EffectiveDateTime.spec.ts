import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { Wrapper } from '@vue/test-utils'
import { createComponent, getTestId } from './utils'
import { EffectiveDateTime } from '@/components/unitNotes'
import { SharedDatePicker } from '@/components/common'
import { useStore } from '@/store/store'
import { PeriodTypes } from '@/enums'

Vue.use(Vuetify)
const store = useStore()

const props = {
  content: {
    title: 'Effective Date and Time',
    description: 'Select the effective date and time for',
    sideLabel: 'Effective Date and Time'
  },
  validate: false
}

describe('EffectiveDateTime', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(EffectiveDateTime, props)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('should render the component', () => {
    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDateTime)

    expect(EffectiveDateTimeComponent.exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.findComponent(SharedDatePicker).exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.find(getTestId('time-picker-fields')).exists()).toBeTruthy()
    expect(EffectiveDateTimeComponent.find(getTestId('date-summary-label')).exists()).toBeFalsy()

    const immediateDate = <HTMLInputElement>(
      EffectiveDateTimeComponent.find(getTestId('immediate-date-radio'))).element

    const pastDate = <HTMLInputElement>(
      EffectiveDateTimeComponent.find(getTestId('past-date-radio'))).element

    expect(immediateDate.checked).toBeTruthy()
    expect(pastDate.checked).toBeFalsy()
  })

  it('should set the Effective and Expiry Date Times', async () => {
    const EffectiveDateTimeComponent = wrapper.findComponent(EffectiveDateTime)

    expect(wrapper.vm.effectiveDate).toBe('')

    EffectiveDateTimeComponent.find(getTestId('past-date-radio')).trigger('click')
    EffectiveDateTimeComponent.findComponent(SharedDatePicker).vm.$emit('emitDate', '2023-07-01')
    expect(wrapper.vm.selectedPastDate).toBeTruthy()

    wrapper.vm.selectHour = '10'
    wrapper.vm.selectMinute = '25'

    await Vue.nextTick()

    const dateSummaryLabel = EffectiveDateTimeComponent.find(getTestId('date-summary-label'))
    expect(dateSummaryLabel.exists()).toBeTruthy()
    expect(dateSummaryLabel.text()).toContain('July 1, 2023 at 10:25 am')

    wrapper.vm.selectHour = '12'
    wrapper.vm.selectMinute = '00'

    await Vue.nextTick()

    expect(dateSummaryLabel.text()).toContain('July 1, 2023 at 12:00 am')

    wrapper.vm.selectHour = '9'
    wrapper.vm.selectMinute = '45'
    wrapper.vm.selectPeriod = PeriodTypes.PM

    await Vue.nextTick()

    expect(dateSummaryLabel.text()).toContain('July 1, 2023 at 9:45 pm')
  })
})
