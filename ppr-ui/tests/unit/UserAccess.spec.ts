import { QsInformation, UserAccess } from '@/views'
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { ButtonFooter, Stepper } from '@/components/common'
import QsSelectAccess from '@/views/userAccess/QsSelectAccess.vue'
import { createComponent, setupMockUser } from './utils'
import { Wrapper } from '@vue/test-utils'
import { RouteNames } from '@/enums'
import { defaultFlagSet } from '@/utils'

Vue.use(Vuetify)

describe('UserAccess', () => {
  let wrapper: Wrapper<any>
  defaultFlagSet['mhr-user-access-enabled'] = true
  setupMockUser()

  beforeEach(async () => {
    wrapper = await createComponent(UserAccess,
      { appReady: true },
      RouteNames.QS_ACCESS_TYPE
    )
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('should render the default components', async () => {
    // Wait for the next tick to allow time for the component to render
    await nextTick()

    // Verify that the components are rendered
    expect(wrapper.findComponent(UserAccess).exists()).toBe(true)
    expect(wrapper.findComponent(QsSelectAccess).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)

    expect(wrapper.findComponent(Stepper).exists()).toBe(false)
    expect(wrapper.findComponent(QsInformation).exists()).toBe(false)
  })
})
