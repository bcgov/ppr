import { createComponent, getLastEvent } from './utils'
import { RegistrationFlowType, RouteNames, UIRegistrationTypes } from '@/enums'
import { mockedGeneralCollateral1, mockedSelectSecurityAgreement } from './test-data'
import flushPromises from 'flush-promises'
import { ReviewConfirm } from '@/views'
import { ButtonFooter, CertifyInformation, FolioNumberSummary, Stepper, StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { Parties } from '@/components/parties'
import { Collateral } from '@/components/collateral'
import { LengthTrustIF } from '@/interfaces'
import { RegistrationTypes } from '@/resources'
import { useStore } from '@/store/store'

const store = useStore()

const header = '#registration-header'
const title: string = '.generic-label'
const titleInfo: string = '.sub-header-info'

describe('Review Confirm new registration component', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(null)
    await store.setRegistrationFlowType(null)
  })

  it('redirects to dashboard when store is not set', async () => {
    wrapper = await createComponent(ReviewConfirm, { appReady: true }, RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('renders Add Parties View with child components when store is set', async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(ReviewConfirm, { appReady: true }, RouteNames.REVIEW_CONFIRM)
    await flushPromises()

    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
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
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStepName).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(Parties).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(Collateral).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.find(header).exists()).toBe(true)
    expect(wrapper.find(title).exists()).toBe(true)
    expect(wrapper.find(titleInfo).exists()).toBe(true)
  })

  it('updates fee summary with registration length changes', async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(ReviewConfirm, { appReady: true }, RouteNames.REVIEW_CONFIRM)
    await flushPromises()
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

  it('displays correct info based on registration type', async () => {
    for (let i = 0; i < RegistrationTypes.length; i++) {
      // skip dividers + other
      if (
        !RegistrationTypes[i].registrationTypeUI ||
        RegistrationTypes[i].registrationTypeUI === UIRegistrationTypes.OTHER
      ) {
        continue
      }
      await store.setRegistrationType(RegistrationTypes[i])
      await store.setRegistrationFlowType(RegistrationFlowType.NEW)
      await flushPromises()
      expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
        RegistrationTypes[i].registrationTypeUI
      )
      // header
      expect(wrapper.find(header).text()).toContain(RegistrationTypes[i].registrationTypeUI)
      // title
      expect(wrapper.find(title).text()).toContain('Review and Confirm')
      // message
      expect(wrapper.find(titleInfo).text()).toContain(
        'Review the information in your registration. If you need to change'
      )
    }
  })

  it('show error message in Collateral Summary section when description is empty', async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({ generalCollateral: mockedGeneralCollateral1 })
    wrapper = await createComponent(ReviewConfirm, { appReady: true }, RouteNames.REVIEW_CONFIRM)
    await flushPromises()

    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    const invalidMessages = await wrapper.findComponent(Collateral).findAll('.error-text')
    expect(invalidMessages.length).toBe(0)

    // Go back to Collateral step
    await wrapper.find('#reg-back-btn').trigger('click')
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_COLLATERAL)

    // Delete text from General Collateral as leave just html styling tag (as per current behavior)
    await store.setAddCollateral({
      generalCollateral:
      {
        addedDateTime: '2021-09-16T05:56:20Z',
        description: '<p></p>'
      }
    }
    )

    // Go Next to Review page and check that Collateral sections has invalid message(s)
    await wrapper.find('#reg-next-btn').trigger('click')
    expect(wrapper.vm.stepName).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.find(title).text()).toContain('Review and Confirm')
    expect(wrapper.findComponent(Collateral).findAll('.error-text').length).toBe(1)
  })

  it('emits error', async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await flushPromises()
    const error = { statusCode: 404 }
    expect(getLastEvent(wrapper, 'error')).not.toEqual(error)
    await wrapper.findComponent(ButtonFooter).vm.$emit('error', error)
    await flushPromises()
    expect(getLastEvent(wrapper, 'error')).toEqual(error)
  })
})
