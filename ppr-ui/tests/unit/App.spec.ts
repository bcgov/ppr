import { describe, it, expect, beforeEach } from 'vitest'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import App from '@/app.vue'
import ConnectHeader from '@sbc-connect/nuxt-core-layer-beta/app/components/Connect/Header/index.vue'
import ConnectFooter from '@sbc-connect/nuxt-core-layer-beta/app/components/Connect/Footer.vue'
import { Tombstone } from '@/components/tombstones'
import { Breadcrumb, SkipToMainContent } from '@/components/common'
import { axe } from 'vitest-axe'

const store = useStore()

describe('App component basic rendering normal account', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAuthRoles(['ppr'])
    const currentUser = {
      id: 'test_id',
      firstname: 'first',
      lastname: 'last',
      username: 'username'
    }
    await store.setUserInfo(currentUser)

    wrapper = await createComponent(App, {
      appReady: true
    })

    // Mock present token service to prevent running in test env
    wrapper.vm.tokenService = true

    // Wait for the component and subcomponents to render
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve()
      }, 1000)
    })
  })

  it.skip('should have no accessibility violations', async () => {
    // Run the axe-core accessibility check on the component's HTML
    const results = await axe(wrapper.html())
    // Use the custom vitest-axe matcher to check for violations
    expect(results).toHaveNoViolations()
  })

  it('renders the sub-components properly', async () => {
    expect(wrapper.findComponent(App).exists()).toBe(true)
    expect(wrapper.findComponent(SkipToMainContent).exists()).toBe(true)
    expect(wrapper.findComponent(ConnectHeader).exists()).toBe(true)
    expect(wrapper.findComponent(ConnectFooter).exists()).toBe(true)
    expect(wrapper.findComponent(Tombstone).exists()).toBe(false)
    expect(wrapper.findComponent(Breadcrumb).exists()).toBe(false)
  })

  it('gets auth and user info/settings properly', async () => {
    expect(store.getStateModel.authorization.authRoles).toContain('ppr')
    expect(store.getStateModel.userInfo).not.toBeNull()
    expect(store.getStateModel.userInfo.firstname).toBe('first')
    expect(store.getStateModel.userInfo.lastname).toBe('last')
    expect(store.getStateModel.userInfo.username).toBe('username')
  })
})
