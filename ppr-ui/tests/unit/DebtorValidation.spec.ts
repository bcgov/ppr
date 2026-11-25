// Libraries
import { nextTick } from 'vue'
import { EditDebtor } from '@/components/parties/debtor'
import { createComponent } from './utils'
import { useDebtorValidation } from '@/composables/parties/useDebtorValidation'

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-debtor'
const ERROR_MSG = '.v-messages__message'

describe('Debtor validation tests - business', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditDebtor, { activeIndex: -1, isBusiness: true, invalidSection: false })
  })

  it('validates blank inputs', async () => {
    // no input added
    const txtName = await wrapper.find('#txt-name-debtor')
    txtName.setValue('')
    await nextTick()
    const btn = await wrapper.find(doneButtonSelector)
    btn.trigger('click')
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Please enter a business name')
  })
})

describe('Debtor validation tests - individual', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditDebtor, { activeIndex: -1, isBusiness: false, invalidSection: false })
  })

  it('validates blank inputs', async () => {
    // no input added
    const txtName = await wrapper.find('#txt-first-debtor')
    txtName.setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(4)
    expect(messages.at(0).text()).toBe('Please enter a first name')
    expect(messages.at(1).text()).toBe('Required if person has middle name')
  })

  it('validates the birthday', async () => {
    // no input added
    wrapper.find('#txt-first-debtor').setValue('Joe')
    wrapper.find('#txt-middle-debtor').setValue('Boxer')
    wrapper.find('#txt-last-debtor').setValue('Louis')
    wrapper.find('#txt-month').setValue('13')
    wrapper.find('#txt-year').setValue('1700')
    wrapper.find('#txt-day').setValue('99')
    wrapper.find(doneButtonSelector).trigger('click')
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(5)
    expect(messages.at(1).text()).toBe('Please enter a valid month')
    expect(messages.at(2).text()).toBe('Please enter a valid day')
    expect(messages.at(3).text()).toBe('Please enter a valid year')
  })
})

describe('Debtor birthdate live validation', () => {
  it('flags an impossible date as soon as all three fields are entered', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('1990', 2, '30')
    expect(errors.value.day.message).toBe('Please enter a valid day')
    expect(errors.value.month.succeeded).toBe(true)
    expect(errors.value.year.succeeded).toBe(true)
  })

  it('flags a day the month never has, before the year is entered', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('', 2, '30')
    expect(errors.value.day.message).toBe('Please enter a valid day')
    validateBirthdateLive('', 4, '31')
    expect(errors.value.day.message).toBe('Please enter a valid day')
  })

  it('allows Feb 29 until the year shows it is not a leap year', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('', 2, '29')
    expect(errors.value.day.succeeded).toBe(true)
    validateBirthdateLive('2001', 2, '29')
    expect(errors.value.day.message).toBe('Please enter a valid day')
    validateBirthdateLive('2000', 2, '29')
    expect(errors.value.day.succeeded).toBe(true)
  })

  it('does not flag fields the user has not filled in yet', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('', 4, '')
    expect(errors.value.year.succeeded).toBe(true)
    expect(errors.value.day.succeeded).toBe(true)
    expect(errors.value.month.succeeded).toBe(true)
  })

  it('flags an out-of-range day right away', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('', 0, '45')
    expect(errors.value.day.message).toBe('Please enter a valid day')
  })

  it('waits for a 4-digit year while typing, but checks it on blur', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('19', 4, '10')
    expect(errors.value.year.succeeded).toBe(true)
    validateBirthdateLive('19', 4, '10', true)
    expect(errors.value.year.message).toBe('Please enter a valid year')
  })

  it('clears the error once the date is corrected', () => {
    const { errors, validateBirthdateLive } = useDebtorValidation()
    validateBirthdateLive('1990', 4, '31')
    expect(errors.value.day.message).toBe('Please enter a valid day')
    validateBirthdateLive('1990', 4, '30')
    expect(errors.value.day.succeeded).toBe(true)
  })
})
