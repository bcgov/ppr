import { useStore } from '@/store/store'

import { createComponent } from './utils'
import { AuthRoles, RouteNames } from '@/enums'
import { defaultFlagSet } from '@/utils/feature-flags'
import { MhrCorrectionStaff } from '@/resources'
import { useNewMhrRegistration } from '@/composables'
import { mockedMhrRegistration } from './test-data'
import MhrRegistration from '@/views/newMhrRegistration/MhrRegistration.vue'
import { Stepper } from '@/components/common'
import { nextTick } from 'vue'

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

  it('renders the Mhr Registry Corrections Submitting Party step', async () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('#registration-correction-header').text()).toBe('Registry Correction - Staff Error or Omission')
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findAll('.step').length).toBe(5)

    // no Corrected badges showing
    expect(wrapper.findAll('#updated-badge-component').length).toBe(0)
    expect(wrapper.vm.$route.name).toBe(RouteNames.SUBMITTING_PARTY)

  })

  it('renders the Mhr Registry Corrections Describe Your Home step', async () => {
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
})
