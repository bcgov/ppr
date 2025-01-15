import { Exemptions } from '@/pages'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { createComponent } from './utils'
import { nextTick } from 'vue'
import { RouteNames } from '@/enums/routeNames'
import { defaultFlagSet } from '@/utils'

describe('Exemptions.vue', () => {
  let wrapper

  beforeEach(async () => {
    defaultFlagSet['mhr-exemption-enabled'] = true
    wrapper = await createComponent(Exemptions, { appReady: true }, RouteNames.EXEMPTION_DETAILS)
    wrapper.vm.dataLoaded = true
    await nextTick()
  })

  it('mounts the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders Stepper component', () => {
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
  })

  it('renders ButtonFooter component', () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
  })

  it('renders StickyContainer component', () => {
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })

  it('checks reactive property dataLoaded value', () => {
    expect(wrapper.vm.dataLoaded).toBe(true)
  })

  it('checks reactive property loading value', () => {
    expect(wrapper.vm.loading).toBe(true)
  })

  // Additional tests can go here...
})
