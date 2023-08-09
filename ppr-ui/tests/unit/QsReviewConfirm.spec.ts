import { QsReviewConfirm } from '@/views'
import { createComponent, setupMockUser } from './utils'
import { Wrapper } from '@vue/test-utils'
import { defaultFlagSet } from '@/utils'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
import { MhrSubTypes } from '@/enums'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'

setActivePinia(createPinia())
const store = useStore()

describe('QsInformation', () => {
  let wrapper: Wrapper<any> | any
  const submittingPartyInfo = {
    name: 'John Doe',
    email: 'john@example.com'
  }

  beforeAll(async () => {
    defaultFlagSet['mhr-user-access-enabled'] = true
    await store.setMhrSubProduct(MhrSubTypes.LAWYERS_NOTARIES)
    await store.setMhrQsSubmittingParty(submittingPartyInfo)
    await setupMockUser()
    await flushPromises()
    await nextTick()
  })

  beforeEach(async () => {
    wrapper = await createComponent(QsReviewConfirm)
    await flushPromises()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the AccountInfo component with the correct props', () => {
    const accountInfoComponent = wrapper.findComponent({ name: 'AccountInfo' })
    expect(accountInfoComponent.exists()).toBe(true)

    // Verify that the props are passed correctly
    expect(accountInfoComponent.props('title')).toBe('Submitting Party for this Application')
    expect(accountInfoComponent.props('tooltipContent'))
      .toContain('The default Submitting Party is based on your BC Registries user account information.')
    expect(accountInfoComponent.props('accountInfo')).toBe(submittingPartyInfo)
  })

  // Add more tests for specific behaviors and interactions if needed.
})
