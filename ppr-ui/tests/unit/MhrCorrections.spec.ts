import { useStore } from '@/store/store'

import { createComponent, getTestId } from './utils'
import { ActionTypes, AuthRoles, RouteNames } from '@/enums'
import { defaultFlagSet } from '@/utils/feature-flags'
import { MhrCorrectionStaff } from '@/resources'
import { useNewMhrRegistration } from '@/composables'
import { mockedMhrRegistration } from './test-data'
import MhrRegistration from '@/views/newMhrRegistration/MhrRegistration.vue'
import { Stepper } from '@/components/common'
import { nextTick } from 'vue'
import HomeSections from '@/components/mhrRegistration/YourHome/HomeSections.vue'
import AddEditHomeSections from '@/components/mhrRegistration/YourHome/AddEditHomeSections.vue'
import flushPromises from 'flush-promises'
import InfoChip from '@/components/common/InfoChip.vue'
import YourHomeReview from '@/components/mhrRegistration/ReviewConfirm/YourHomeReview.vue'

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
    await store.setMhrBaseline(mockedMhrRegistration)
    await useNewMhrRegistration().initDraftOrCurrentMhr(mockedMhrRegistration)

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
    expect(wrapper.vm.$route.name).toBe(RouteNames.YOUR_HOME)

    // no Corrected badges showing
    expect(wrapper.findAll('#updated-badge-component').length).toBe(0)

    // update the fields to trigger Corrected badges
    await wrapper.find('#manufacturer-name').setValue('x')
    await wrapper.find('#manufacturer-year').setValue('2020')
    await wrapper.find('#manufacturer-make').setValue('x')
    await wrapper.find('#manufacturer-model').setValue('x')

    await nextTick()
    expect(wrapper.findAll('#updated-badge-component').length).toBe(4)

    await wrapper.find('#csa-number').setValue('CSA-123')
    await wrapper.find('#rebuilt-status-text').setValue('x')
    await wrapper.find('#other-remarks').setValue('x')

    await nextTick()
    expect(wrapper.findAll('#updated-badge-component').length).toBe(7)

    // reset manufacturer name field to original so the Corrected badge can be cleared
    await wrapper.find('#manufacturer-name').setValue(mockedMhrRegistration.description.manufacturer)
    await nextTick()

    expect(wrapper.findAll('#updated-badge-component').length).toBe(6)
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

    // Number of Sections should be still 2 (Deleted and Added sections)
    expect(homeSections.find('#section-count').text()).toContain(2)
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

})
