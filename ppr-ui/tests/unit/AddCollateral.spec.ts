import { createComponent } from './utils'
import { useStore } from '@/store/store'
import { RegistrationFlowType, RouteNames, UIRegistrationTypes } from '@/enums'
import { AddCollateral } from '@/views'
import { mockedSelectSecurityAgreement } from './test-data'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { Collateral } from '@/components/collateral'
import flushPromises from 'flush-promises'
import { LengthTrustIF } from '@/interfaces'
import { RegistrationTypes } from '@/resources'

const store = useStore()

// Input field selectors / buttons
const header = '#registration-header'
const title: string = '.generic-label'
const titleInfo: string = '.sub-header-info'

describe('Redirects when Add Collateral is not ready', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setRegistrationType(null)
    await store.setRegistrationFlowType(null)

    wrapper = await createComponent(AddCollateral, { appReady: true }, RouteNames.ADD_COLLATERAL)
  })

  it('redirects to dashboard when store is not set', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
})

describe('Add Collateral new registration component', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)

    wrapper = await createComponent(AddCollateral, { appReady: true }, RouteNames.ADD_COLLATERAL)
  })

  it('renders Add Collateral View with child components when store is set', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(AddCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 0
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
      UIRegistrationTypes.SECURITY_AGREEMENT
    )
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStepName).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)

    expect(wrapper.find(header).exists()).toBe(true)
    expect(wrapper.find(title).exists()).toBe(true)
    expect(wrapper.find(titleInfo).exists()).toBe(true)
  })

  it('updates fee summary with registration length changes', async () => {
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 0
    })
    const newLengthTrust1: LengthTrustIF = {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0
    }
    await store.setLengthTrust(newLengthTrust1)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust1.lifeInfinite,
      lifeYears: newLengthTrust1.lifeYears
    })
    const newLengthTrust2: LengthTrustIF = {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0
    }
    await store.setLengthTrust(newLengthTrust2)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust2.lifeInfinite,
      lifeYears: newLengthTrust2.lifeYears
    })
  })

  for (let i = 0; i < RegistrationTypes.length; i++) {
    if (
      !RegistrationTypes[i].registrationTypeUI ||
      RegistrationTypes[i].registrationTypeUI === UIRegistrationTypes.OTHER
    ) {
      continue
    }

    it(`displays correct info based on registration type: ${RegistrationTypes[i].registrationTypeUI}`, async () => {
      // skip dividers + other
      await store.setRegistrationType(RegistrationTypes[i])
      await store.setRegistrationFlowType(RegistrationFlowType.NEW)
      await flushPromises()
      expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
        RegistrationTypes[i].registrationTypeUI
      )
      // header
      expect(wrapper.find(header).text()).toContain(RegistrationTypes[i].registrationTypeUI)
      // title
      expect(wrapper.find(title).text()).toContain('Add Collateral')
      // message
      expect(wrapper.find(titleInfo).text()).toContain(
        `Add the collateral for this ${RegistrationTypes[i].registrationTypeUI} registration.`
      )
    })
  }
})
