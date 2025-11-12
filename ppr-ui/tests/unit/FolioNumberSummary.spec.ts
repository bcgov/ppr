import { nextTick } from 'vue'
import { FolioNumberSummary } from '@/components/common'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import flushPromises from 'flush-promises'

const store = useStore()

describe('Folio number on the summary page', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setFolioOrReferenceNumber('ABC123')
    wrapper = await createComponent(FolioNumberSummary)
  })

  it('renders the view with text box', () => {
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    expect(wrapper.find('#txt-folio').exists()).toBe(true)
  })

  it('renders the folio data from the store', async () => {
    expect(wrapper.vm.folioNumber).toEqual('ABC123')
    expect(wrapper.find('#txt-folio').element.value).toBe('ABC123')
  })

  it('is valid and emits the valid event', async () => {
    wrapper.find('#txt-folio').setValue('MY TEST')
    await nextTick()
    expect(wrapper.vm.isValid).toBeTruthy()
  })

  it('sets the validity to false for > 50 characters', async () => {
    const mockData =
      'MY TEST THAT IS VERY LONG IN FACT TOO LONG SKDJFA ASKDJFL ASDKFJL ASDKJFL ALKSJDFLKJ ALSDKFJ AKSDJF'
    await store.setFolioOrReferenceNumber(mockData)
    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()

    expect(wrapper.vm.folioNumber).toEqual(mockData)
    expect(wrapper.vm.isValid).toBeFalsy()
    expect(wrapper.emitted().folioValid).toBeFalsy()
  })
})
