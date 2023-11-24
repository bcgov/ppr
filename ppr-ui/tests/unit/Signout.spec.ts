import { createComponent } from './utils'
import { Signout } from '@/views'
import flushPromises from 'flush-promises'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'

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
  })
})
