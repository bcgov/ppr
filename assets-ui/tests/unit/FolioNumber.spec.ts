import { nextTick } from 'vue'
import { FolioNumber } from '@/components/common'
import { createComponent } from './utils'

// Input field selectors / buttons
const folioEditTxt: string = '#folio-edit-txt'

describe('Folio number tests', () => {
  let wrapper
  const defaultFolio = 't123'

  beforeEach(async () => {
    wrapper = await createComponent(FolioNumber, { defaultFolioNumber: defaultFolio })
  })

  it('renders with default folio set', async () => {
    expect(wrapper.findComponent(FolioNumber).exists()).toBe(true)
    expect(wrapper.vm.folioNumber).toBe(defaultFolio)
    expect(wrapper.vm.folioEditNumber).toBe(defaultFolio)
    const folioInput = <HTMLInputElement>wrapper.find(folioEditTxt).element
    expect(folioInput.value).toBe('t123')
  })

  it('allows the user to edit the folio', async () => {
    const newFolio = '12'
    wrapper.vm.folioEditNumber = newFolio
    await nextTick()
    const newEdit = wrapper.findAll(folioEditTxt)
    expect(newEdit.length).toBe(1)
  })

  it('validates the folio number', async () => {
    wrapper.find(folioEditTxt).setValue('Test File Number that is too long')
    await nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 15 characters reached')
  })
})
