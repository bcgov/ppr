import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { QsInformation, UserAccess } from '@/pages'
import { ButtonFooter, Stepper } from '@/components/common'
import QsSelectAccess from '@/pages/userAccess/QsSelectAccess.vue'
import { MhrSubTypes, RouteNames } from '@/enums'
import { defaultFlagSet } from '@/utils'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import { nextTick } from 'vue'

const store = useStore()

describe('UserAccess', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(UserAccess, { appReady: true }, RouteNames.QS_ACCESS_TYPE)
  })

  afterEach(() => {
    store.setMhrSubProduct(null)
  })

  it('should render the default components', async () => {
    // Verify that the components are rendered
    expect(wrapper.findComponent(UserAccess).exists()).toBeTruthy()
    expect(wrapper.findComponent(QsSelectAccess).exists()).toBeTruthy()
    expect(wrapper.findComponent(ButtonFooter).exists()).toBeTruthy()

    expect(wrapper.findComponent(Stepper).exists()).toBeFalsy()
    expect(wrapper.findComponent(QsInformation).exists()).toBeFalsy()
  })

  it('restores previous selected product when Confirm Change is cancelled', async () => {
    // Confirm no previous selection
    expect(wrapper.vm.previousSelectedProduct).toBe('')

    // Set product and verify previous selection
    store.setMhrSubProduct(MhrSubTypes.LAWYERS_NOTARIES)
    await nextTick()
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.LAWYERS_NOTARIES)

    // Simulate change product type
    store.setMhrSubProduct(MhrSubTypes.MANUFACTURER)
    await nextTick()
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.MANUFACTURER)

    // Mock user response for dialog
    await wrapper.vm.handleDialogResp(false)
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.LAWYERS_NOTARIES)
  })

  it('holds product change when Confirm Change is confirmed', async () => {
    // Confirm no previous selection
    expect(wrapper.vm.previousSelectedProduct).toBe('')

    // Set product and verify previous selection
    store.setMhrSubProduct(MhrSubTypes.LAWYERS_NOTARIES)
    await nextTick()

    // Simulate change product type
    store.setMhrSubProduct(MhrSubTypes.MANUFACTURER)
    await nextTick()

    // Mock user response for dialog
    await wrapper.vm.handleDialogResp(true)
    expect(store.getMhrSubProduct).toBe(MhrSubTypes.MANUFACTURER)
  })
})

