import { MhrHistory } from '@/views'
import { nextTick } from 'vue'
import { createComponent, setupMockStaffUser } from './utils'
import { defaultFlagSet, pacificDate } from '@/utils'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { expect } from 'vitest'
import { RouteNames } from '@/enums'

describe('HistoricalManufacturedHomeInfo', () => {
  let wrapper: any
  let mock: MockAdapter

  defaultFlagSet['mhr-history-enabled'] = true

  beforeEach(async () => {
    mock = new MockAdapter(axios)
    mock.onGet(/\/registrations\/history\/\d+/).reply(200, {
      mhrNumber: '123456',
      descriptions: [],
      locations: [],
      owners: [],
      registrations: [],
      statusType: 'ACTIVE'
    })

    setupMockStaffUser()
    wrapper = await createComponent(MhrHistory, {
     appReady: true
    }, RouteNames.MHR_HISTORY)
    await nextTick()
  })

  afterEach(() => {
    mock.restore()
  })

  it('renders correctly when data is loaded', async () => {
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
    }, RouteNames.MHR_HISTORY)
    await nextTick()

    expect(wrapper.vm.$route.name).toBe('dashboard')
  })

  it('navigates to dashboard if feature flag is disabled', async () => {
    defaultFlagSet['mhr-history-enabled'] = false
    wrapper = await createComponent(MhrHistory, {
      appReady: true
    }, RouteNames.MHR_HISTORY)
    await nextTick()

    expect(wrapper.vm.$route.name).toBe('dashboard')
  })
})

