// Libraries
import { nextTick } from 'vue'
import { EditDebtor } from '@/components/parties/debtor'
import { createComponent } from './utils'

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
