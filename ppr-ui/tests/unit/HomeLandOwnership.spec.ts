// Libraries
import { nextTick } from 'vue'

// Components
import { HomeLandOwnership } from '@/components/mhrRegistration'
import { createComponent, getTestId } from './utils'
import { useStore } from '../../src/store/store'

const store = useStore()

describe('Home Land Ownership', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(HomeLandOwnership)
  })

  it('renders base component', async () => {
    expect(wrapper.findComponent(HomeLandOwnership).exists()).toBe(true)
  })

  it('ownership checkbox performs as expected', async () => {
    expect(store.getMhrRegistrationOwnLand).toBe(false)
    expect(wrapper.find(getTestId('ownership-checkbox'))).toBeTruthy()
    wrapper.find(getTestId('ownership-checkbox')).find('input[type="checkbox"]').setValue(true)
    await nextTick()
    expect(store.getMhrRegistrationOwnLand).toBe(true)
  })
})
