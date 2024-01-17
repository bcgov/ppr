import { BusinessRemovalForm } from '@/components/mhrTransfers'
import { createComponent } from './utils'
import { expect } from 'vitest'
import { nextTick } from 'vue'

describe('Business Removal Form component', () => {
  let wrapper

  it('renders defaults correctly', async () => {
    wrapper = await createComponent(BusinessRemovalForm)
    await nextTick()

    // Assert that the component is rendered
    expect(wrapper.exists()).toBe(true)

    expect(wrapper.find('#corp-or-reg-num').exists()).toBe(true)
    expect(wrapper.vm.state.deathCorpNumber).toBe('')

    expect(wrapper.find('#date-of-dissolution').exists()).toBe(true)
    expect(wrapper.vm.state.deathDateTime).toBeUndefined()
  })

  it('renders with props correctly', async () => {
    wrapper = await createComponent(BusinessRemovalForm, {
      validate: false,
      historicalOwner: {
        deathCorpNumber: '123',
        deathDateTime: '2024-01-01',
        groupId: '5',
      }
    })
    await nextTick()

    expect(wrapper.exists()).toBe(true)

    expect(wrapper.find('#corp-or-reg-num').exists()).toBe(true)
    expect(wrapper.vm.state.deathCorpNumber).toBe('123')

    expect(wrapper.find('#date-of-dissolution').exists()).toBe(true)
    expect(wrapper.vm.state.dateOfDissolution).toBe('2024-01-01')
  })

  it('displays error-text with validation is prompted', async () => {
    wrapper = await createComponent(BusinessRemovalForm, {
      validate: true
    })
    await nextTick()

    const errorCount = await wrapper.findAll('.error-text').length
    expect(errorCount).toBe(2)
  })
})
