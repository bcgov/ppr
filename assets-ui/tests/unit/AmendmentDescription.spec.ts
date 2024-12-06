import { useStore } from '@/store/store'
import { createComponent, getLastEvent } from './utils'
import { AmendmentDescription } from '@/components/registration'

const store = useStore()

// Input field selectors / buttons
const amendmentDescrption = '#amendment-detail-description'
const descriptionTxt = '#amendment-description'
const errorMsg = '.v-messages__message'
const showError = '.error-text'

describe('Amendment Detail Description tests', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setAmendmentDescription('')
    wrapper = await createComponent(AmendmentDescription, { setShowErrors: false, isSummary: false })
  })

  it('renders default with no existing description', async () => {
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    expect(wrapper.vm.detailDescription).toBe('')
    expect(wrapper.vm.amendmentDescription).toBe('')
    expect(wrapper.vm.showErrorComponent).toBe(false)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(descriptionTxt).length).toBe(1)
    expect(wrapper.findAll(errorMsg).length).toBe(0)
    expect(wrapper.findAll(showError).length).toBe(0)
  })

  it('updates amendment with new description text valid length', async () => {
    await wrapper.find(descriptionTxt).setValue('valid amendment description')
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.detailDescription).toBe('valid amendment description')
    expect(wrapper.vm.amendmentDescription).toBe('valid amendment description')
    expect(wrapper.vm.valid).toBe(true)
    expect(getLastEvent(wrapper, 'valid')).toBe(true)
  })

  it('updates amendment with new description text invalid length', async () => {
    const invalidLengthTxt = 'x'.repeat(4001)
    await wrapper.find(descriptionTxt).setValue(invalidLengthTxt)
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBe(false)
    await wrapper.find(descriptionTxt).setValue('valid amendment description')
    expect(wrapper.vm.detailDescription).toBe('valid amendment description')
    expect(wrapper.vm.valid).toBe(true)
    expect(getLastEvent(wrapper, 'valid')).toBe(true)
  })
})

describe('Amendment Detail Description summary view tests', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setAmendmentDescription('test')
    wrapper = await createComponent(AmendmentDescription, { setShowErrors: false, isSummary: true })
  })

  it('renders the summary view of the amendment description', async () => {
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    expect(wrapper.vm.summaryView).toBe(true)
    expect(wrapper.vm.detailDescription).toBe('test')
    expect(wrapper.vm.amendmentDescription).toBe('test')
    expect(wrapper.vm.showErrorComponent).toBe(false)
    expect(wrapper.vm.valid).toBe(true)
  })
})
