import { QsInformation, UserAccess } from '@/views'
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { ButtonFooter, Stepper } from '@/components/common'
import QsSelectAccess from '@/views/userAccess/QsSelectAccess.vue'
import { createComponent, setupMockUser } from './utils'
import { Wrapper } from '@vue/test-utils'
import { MhrSubTypes, RouteNames } from '@/enums'
import { defaultFlagSet } from '@/utils'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'

Vue.use(Vuetify)
setActivePinia(createPinia())
const store = useStore()

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
    store.setMhrSubProduct(null)
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

  it('restores previous selected product when Confirm Change is cancelled', async () => {
    // Confirm no previous selection
    expect(wrapper.vm.previousSelectedProduct).toBe('')

    // Set product and verify previous selection
    await store.setMhrSubProduct(MhrSubTypes.LAWYERS_NOTARIES)
    await nextTick()
    expect(wrapper.vm.previousSelectedProduct).toBe(MhrSubTypes.LAWYERS_NOTARIES)

    // Simulate change product type
    await store.setMhrSubProduct(MhrSubTypes.MANUFACTURER)
    await nextTick()
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.MANUFACTURER)

    // Verify restoration of previous selection on Confirm Change Cancel
    wrapper.vm.handleDialogResp(false)
    await nextTick()
    expect(wrapper.vm.previousSelectedProduct).toBe(MhrSubTypes.LAWYERS_NOTARIES)
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.LAWYERS_NOTARIES)
  })

  it('holds product change when product when Confirm Change is confirmed', async () => {
    // Confirm no previous selection
    expect(wrapper.vm.previousSelectedProduct).toBe('')

    // Set product and verify previous selection
    await store.setMhrSubProduct(MhrSubTypes.LAWYERS_NOTARIES)
    await nextTick()

    // Simulate change product type
    await store.setMhrSubProduct(MhrSubTypes.MANUFACTURER)
    expect(wrapper.vm.previousSelectedProduct).toBe(MhrSubTypes.LAWYERS_NOTARIES)
    await nextTick()

    // Verify restoration of previous selection on Confirm Change Cancel
    wrapper.vm.handleDialogResp(true)
    await nextTick()
    expect(wrapper.vm.previousSelectedProduct).toBe(MhrSubTypes.MANUFACTURER)
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.MANUFACTURER)
  })
})
