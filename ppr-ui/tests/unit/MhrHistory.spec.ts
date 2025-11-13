import { MhrHistory } from '@/pages'
import { nextTick } from 'vue'
import { createComponent, setupMockStaffUser } from './utils'
import { pacificDate } from '@/utils'
import { expect, vi } from 'vitest'
import { RouteNames } from '@/enums'
import { createPinia, setActivePinia } from 'pinia'

describe('HistoricalManufacturedHomeInfo', () => {
  let wrapper, store, pinia

  vi.mock('@/utils/mhr-api-helper', () => ({
    getMhrHistory: vi.fn(() =>
      Promise.resolve({ }))
  }))

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    setupMockStaffUser(store)
    wrapper = await createComponent(MhrHistory, {
     appReady: true
    }, RouteNames.MHR_HISTORY, null,[pinia])
    await nextTick()
  })

  it.skip('renders correctly when data is loaded', async () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h1').text()).toBe('Historical Manufactured Home Information')
    expect(wrapper.find('p').text()).toContain('This is the current information for this registration as of')
    expect(wrapper.find('.font-weight-bold').text()).toBe(pacificDate(new Date()))
    expect(wrapper.vm.$route.name).toBe('mhr-history')
  })

  it('shows the loading overlay when loading', async () => {
    wrapper.vm.loading = true
    await nextTick()

    expect(document.querySelector('.v-overlay__content')).toBeTruthy()
  })

  it('does not proceed if app is not ready', async () => {
    wrapper = await createComponent(MhrHistory, {
      appReady: false
    }, RouteNames.MHR_HISTORY, null, [pinia])
    await nextTick()

    expect(wrapper.vm.$route.name).toBe('dashboard')
  })

  it('navigates to dashboard if feature flag is disabled', async () => {
    wrapper = await createComponent(MhrHistory, {
      appReady: true
    }, RouteNames.MHR_HISTORY, null, [pinia])
    await nextTick()

    expect(wrapper.vm.$route.name).toBe('dashboard')
  })
})

