import { useStore } from '@/store/store'
import { createComponent, getTestId } from './utils'
import {
  ActionTypes,
  ApiHomeTenancyTypes,
  APIRegistrationTypes,
  AuthRoles,
  HomeTenancyTypes,
  RouteNames
} from '@/enums'
import { defaultFlagSet } from '@/utils/feature-flags'
import { MhrCorrectionStaff } from '@/resources'
import { useMhrCorrections, useNewMhrRegistration } from '@/composables'
import { mockedMhrRegistration } from './test-data'
import MhrRegistration from '@/views/newMhrRegistration/MhrRegistration.vue'
import { StaffPayment, Stepper } from '@/components/common'
import { nextTick } from 'vue'
import HomeSections from '@/components/mhrRegistration/YourHome/HomeSections.vue'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
import flushPromises from 'flush-promises'
import InfoChip from '@/components/common/InfoChip.vue'
import YourHomeReview from '@/components/mhrRegistration/ReviewConfirm/YourHomeReview.vue'
import { cloneDeep } from 'lodash'
import { expect } from 'vitest'

const store = useStore()

describe('Mhr Corrections', async () => {
  let wrapper

  // navigate to a step of the Mhr Corrections flow
  const goToStep = async (stepNum: number) => {
    wrapper.findAll('.step').at(stepNum-1).trigger('click')
    await nextTick()
  }

  beforeEach(async () => {
    defaultFlagSet['mhr-staff-correction-enabled'] = true
    defaultFlagSet['mhr-registration-enabled'] = true

    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    await store.setRegistrationType(MhrCorrectionStaff)
    await store.setMhrBaseline(cloneDeep(mockedMhrRegistration))
    await useNewMhrRegistration().initDraftOrCurrentMhr(cloneDeep(mockedMhrRegistration))

    wrapper = await createComponent(
      MhrRegistration,
      { appReady: true },
      RouteNames.SUBMITTING_PARTY
    )
    wrapper.vm.dataLoaded = true
  })

  it('Submitting Party step: renders initial step of Mhr Registry Corrections', async () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('#registration-correction-header').text()).toBe('Registry Correction - Staff Error or Omission')
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findAll('.step').length).toBe(5)

    // no Corrected badges showing
    expect(wrapper.findAll('#updated-badge-component').length).toBe(0)
    expect(wrapper.vm.$route.name).toBe(RouteNames.SUBMITTING_PARTY)

  })

  it('Describe Your Home step: renders corrected badges', async () => {
    goToStep(2)
    // Since we are mounting from parent view, isolate selector to specific step to prevent Review Confirm Badge Counts
    const correctedBadge = '#mhr-describe-your-home #updated-badge-component'
    expect(wrapper.vm.$route.name).toBe(RouteNames.YOUR_HOME)

    // no Corrected badges showing
    expect(wrapper.findAll(correctedBadge).length).toBe(0)

    // update the fields to trigger Corrected badges
    await wrapper.find('#manufacturer-name').setValue('x')
    await wrapper.find('#manufacturer-year').setValue('2020')
    await wrapper.find('#manufacturer-make').setValue('x')
    await wrapper.find('#manufacturer-model').setValue('x')

    await nextTick()
    expect(wrapper.findAll(correctedBadge).length).toBe(4)

    await wrapper.find('#csa-number').setValue('CSA-123')
    await wrapper.find('#rebuilt-status-text').setValue('x')
    await wrapper.find('#other-remarks').setValue('x')

    await nextTick()
    expect(wrapper.findAll(correctedBadge).length).toBe(7)

    // reset manufacturer name field to original so the Corrected badge can be cleared
    await wrapper.find('#manufacturer-name').setValue(mockedMhrRegistration.description.manufacturer)
    await nextTick()

    expect(wrapper.findAll(correctedBadge).length).toBe(6)
  })

  it('Describe Your Home step: renders corrected badges for Home Sections table and Review page', async () => {
    goToStep(2)
    expect(wrapper.vm.$route.name).toBe(RouteNames.YOUR_HOME)

    const homeSections = wrapper.findComponent(HomeSections)
    expect(homeSections.findAll('.info-chip-badge').length).toBe(0)
    expect(homeSections.find('#section-count').text()).toContain(mockedMhrRegistration.description.sections.length)
    expect(homeSections.find('.home-sections-table tbody tr').find('.v-btn').text()).toContain('Correct')

    homeSections.find('.home-sections-table tbody tr').find('.v-btn').trigger('click')
    await nextTick()

    // Edit a section to show Corrected badge (infoChip)
    let addEditHomeSection = homeSections.findComponent(AddEditHomeSections)
    addEditHomeSection.find('#serial-number').setValue('SN123123')
    addEditHomeSection.find('#done-btn-party').trigger('click')
    await flushPromises()

    expect(addEditHomeSection.exists()).toBeFalsy()
    expect(homeSections.findAll('.info-chip-badge').length).toBe(1)
    expect(homeSections.findAll('.info-chip-badge')[0].text()).toContain('CORRECTED')
    expect(store.getMhrRegistration.description.sections[0].action).toBe(ActionTypes.CORRECTED)
    expect(homeSections.find(getTestId('undo-btn-section-0')).exists()).toBeTruthy()

    // Add a new section to show Corrected badge (infoChip)
    homeSections.find('.add-home-section-btn').trigger('click')
    await nextTick()

    addEditHomeSection = homeSections.findComponent(AddEditHomeSections)
    addEditHomeSection.find('#serial-number').setValue('SN123123')
    addEditHomeSection.find('#length-feet').setValue('20')
    addEditHomeSection.find('#width-feet').setValue('10')
    addEditHomeSection.find('#done-btn-party').trigger('click')
    await flushPromises()
    expect(homeSections.findAll('.info-chip-badge').length).toBe(2)
    expect(homeSections.findAll('.info-chip-badge')[1].text()).toContain('ADDED')
    expect(store.getMhrRegistration.description.sections[1].action).toBe(ActionTypes.ADDED)

    // Undo the first section to remove the Corrected badge
    homeSections.find(getTestId('undo-btn-section-0')).trigger('click')
    await nextTick()
    expect(homeSections.findAll('.info-chip-badge').length).toBe(1)
    expect(store.getMhrRegistration.description.sections[0].action).toBe(null)
    await nextTick()

    // Delete first section to show Deleted badge
    homeSections.find(getTestId('edit-btn-section-0')).trigger('click')
    await nextTick()
    homeSections.findComponent(AddEditHomeSections).find('#remove-btn-party').trigger('click')
    await flushPromises()
    expect(store.getMhrRegistration.description.sections[0].action).toBe(ActionTypes.REMOVED)

    // Number of Sections should be 1 (Added sections only, not Deleted)
    expect(homeSections.find('#section-count').text()).toContain(1)
    expect(homeSections.findAllComponents(InfoChip).length).toBe(2)

    // Review and Confirm step
    goToStep(5)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    const homeSectionsReview = wrapper.findComponent(YourHomeReview)
    const homeSectionsBadges = homeSectionsReview.findAllComponents(InfoChip)
    expect(homeSectionsBadges.length).toBe(2)
    expect(homeSectionsBadges[0].text()).toContain(ActionTypes.REMOVED)
    expect(homeSectionsBadges[1].text()).toContain(ActionTypes.ADDED)
  })

  it('Home Location step: renders corrected badges', async () => {
    goToStep(4)
    // Since we are mounting from parent view, isolate selector to specific step to prevent Review Confirm Badge Counts
    const correctedBadge = '#mhr-home-location #updated-badge-component'
    expect(wrapper.vm.$route.name).toBe(RouteNames.HOME_LOCATION)

    // no Corrected badges showing
    expect(wrapper.findAll(correctedBadge).length).toBe(0)

    // Verify a Location Type Change
    await wrapper.find('#dealer-manufacturer-name').setValue('x')
    await nextTick()

    expect(wrapper.findAll(correctedBadge).length).toBe(1)

    // Verify a Civic Address Change
    await wrapper.find('#city').setValue('Vancouver')
    await nextTick()

    expect(wrapper.findAll(correctedBadge).length).toBe(2)

    // Verify a Land Details Change
    // Do so manually, as radio options in test dom are not reactive in my experience
    await store.setMhrRegistrationOwnLand(true)
    await nextTick()

    expect(wrapper.findAll(correctedBadge).length).toBe(3)
  })

  it('Review Confirm step: renders corrected badges', async () => {
    goToStep(5)
    const correctedBadge = '#mhr-review-confirm #updated-badge-component'
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    // no Corrected badges showing
    expect(wrapper.findAll(correctedBadge).length).toBe(0)

    // Correct YourHome Step
    await wrapper.find('#manufacturer-name').setValue('x')
    await wrapper.find('#manufacturer-year').setValue('2020')
    await wrapper.find('#manufacturer-make').setValue('x')
    await wrapper.find('#manufacturer-model').setValue('x')
    await wrapper.find('#csa-number').setValue('CSA-123')
    await wrapper.find('#rebuilt-status-text').setValue('x')
    await wrapper.find('#other-remarks').setValue('x')

    // Correct HomeLocation
    await wrapper.find('#dealer-manufacturer-name').setValue('x')
    await wrapper.find('#city').setValue('Victoria')
    await store.setMhrRegistrationOwnLand(true)
    await nextTick()

    expect(wrapper.findAll(correctedBadge).length).toBe(10)
  })

  it('Review Confirm step: Hides Staff Payment component for REGC_STAFF', async () => {
    goToStep(5)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)
    expect(wrapper.findComponent(StaffPayment).exists()).toBe(false)
  })

  it('Review Confirm step: validates that corrections have been made', async () => {
    goToStep(5)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    // Doesn't display until prompted
    expect(wrapper.find('#invalid-correction-msg').exists()).toBe(false)

    // Prompt Submission
    const submitBtn = await wrapper.find('#reg-next-btn')
    submitBtn.trigger('click')
    await nextTick()

    // At least one change is required validation will appear
    expect(wrapper.find('#invalid-correction-msg').exists()).toBe(true)
    expect(wrapper.find('#invalid-correction-msg').text())
      .toContain('At least one change to the home’s registration information is required')
  })

  it('Correction Payload: Includes Description', async () => {
    goToStep(5)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    // Correct YourHome Step
    await wrapper.find('#manufacturer-name').setValue('x')

    // Build Correction
    const mhrData = useNewMhrRegistration().buildApiData()
    const mhrCorrection = useMhrCorrections().buildCorrectionPayload(mhrData)

    // Verify the inclusion of Corrected and root payload data
    // Submitting Party
    expect(mhrCorrection.submittingParty).toBeTruthy()
    expect(mhrCorrection.submittingParty.businessName).toBe(mockedMhrRegistration.submittingParty.businessName)

    // Doc Id
    expect(mhrCorrection.documentId).toBeTruthy()
    expect(mhrCorrection.documentId).toBe(mockedMhrRegistration.documentId)

    // Doc Type
    expect(mhrCorrection.documentType).toBeTruthy()
    expect(mhrCorrection.documentType).toBe(APIRegistrationTypes.MHR_CORRECTION_STAFF)

    // Description
    expect(mhrCorrection.description).toBeTruthy()
    expect(mhrCorrection.description).toContain({ manufacturer: 'x' })

    // Verify sections that are not corrected are not included
    expect(mhrCorrection.location).toBeFalsy()
    expect(mhrCorrection.addOwnerGroups).toBeFalsy()
    expect(mhrCorrection.deleteOwnerGroups).toBeFalsy()
    expect(mhrCorrection.ownLand).toBeFalsy()
  })

  it('Correction Payload: Includes Location', async () => {
    goToStep(5)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    // Correct Home Location Step
    await wrapper.find('#city').setValue('Victoria')

    // Build Correction
    const mhrData = useNewMhrRegistration().buildApiData()
    const mhrCorrection = useMhrCorrections().buildCorrectionPayload(mhrData)

    // Verify the inclusion of Corrected and root payload data
    // Submitting Party
    expect(mhrCorrection.submittingParty).toBeTruthy()
    expect(mhrCorrection.submittingParty.businessName).toBe(mockedMhrRegistration.submittingParty.businessName)

    // Doc Id
    expect(mhrCorrection.documentId).toBeTruthy()
    expect(mhrCorrection.documentId).toBe(mockedMhrRegistration.documentId)

    // Doc Type
    expect(mhrCorrection.documentType).toBeTruthy()
    expect(mhrCorrection.documentType).toBe(APIRegistrationTypes.MHR_CORRECTION_STAFF)

    // Location
    expect(mhrCorrection.location).toBeTruthy()
    expect(mhrCorrection.location.address).toContain({ city: 'Victoria' })

    // Verify sections that are not corrected are not included
    expect(mhrCorrection.description).toBeFalsy()
    expect(mhrCorrection.addOwnerGroups).toBeFalsy()
    expect(mhrCorrection.deleteOwnerGroups).toBeFalsy()
    expect(mhrCorrection.ownLand).toBeFalsy()
  })

  it('Correction Payload: Includes Home Owners', async () => {
    goToStep(5)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    // Correct HomeOwners
    const correctedOwnerGroups = cloneDeep([
      ...mockedMhrRegistration.ownerGroups.map((group, index) =>
        index === 0 ? { ...group, action: ActionTypes.CORRECTED } : group
      )
    ])
    store.setMhrRegistrationHomeOwnerGroups(correctedOwnerGroups)
    await nextTick()

    // Build Correction
    const mhrData = useNewMhrRegistration().buildApiData()
    const mhrCorrection = useMhrCorrections().buildCorrectionPayload(mhrData)

    // Verify the inclusion of Corrected and root payload data
    // Submitting Party
    expect(mhrCorrection.submittingParty).toBeTruthy()
    expect(mhrCorrection.submittingParty.businessName).toBe(mockedMhrRegistration.submittingParty.businessName)

    // Doc Id
    expect(mhrCorrection.documentId).toBeTruthy()
    expect(mhrCorrection.documentId).toBe(mockedMhrRegistration.documentId)

    // Doc Type
    expect(mhrCorrection.documentType).toBeTruthy()
    expect(mhrCorrection.documentType).toBe(APIRegistrationTypes.MHR_CORRECTION_STAFF)

    // Home Owners
    expect(mhrCorrection.addOwnerGroups).toBeTruthy()
    expect(mhrCorrection.deleteOwnerGroups).toBeTruthy()
    expect(mhrCorrection.addOwnerGroups[0]).toStrictEqual({ ...correctedOwnerGroups[0], type: ApiHomeTenancyTypes.NA })

    // Verify sections that are not corrected are not included
    expect(mhrCorrection.description).toBeFalsy()
    expect(mhrCorrection.location).toBeFalsy()
    expect(mhrCorrection.ownLand).toBeFalsy()
  })

})
