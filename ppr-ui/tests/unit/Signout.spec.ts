import { createComponent } from './utils'
import { Signout } from '@/pages'
import flushPromises from 'flush-promises'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'
import KeyCloakService from '@sbc/services/keycloak.services'

// mock keycloak service to prevent errors in the test
const mockLogout = vi.fn();
KeyCloakService.logout = mockLogout;

describe('Signout component', () => {
  let wrapper: any
  const baseURL = 'myhost/basePath'
  sessionStorage.setItem('REGISTRY_URL', baseURL)

  beforeEach(async () => {
    wrapper = await createComponent(Signout)
    await flushPromises()
  })

  it('renders with signout component', () => {
    expect(wrapper.vm.logoutURL).toBe(`${baseURL}?logout=true`)
    expect(wrapper.findComponent(Signout).exists()).toBe(true)
    expect(wrapper.findComponent(SbcSignout).exists()).toBe(true)
    expect(mockLogout).toHaveBeenCalled();
  })
})
