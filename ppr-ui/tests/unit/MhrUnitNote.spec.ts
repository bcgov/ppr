import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import mockRouter from './MockRouter'

import { MhrUnitNote } from '@/views'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { getTestId, setupMockStaffUser } from './utils'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { CertifyInformation, ContactInformation, DocumentId, Remarks } from '@/components/common'
import { EffectiveDateTime, UnitNoteAdd, UnitNoteReview, UnitNoteReviewDetailsTable } from '@/components/unitNotes'
import { Attention } from '@/components/mhrRegistration/ReviewConfirm'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { MhrUnitNoteValidationStateIF } from '@/interfaces'
import { isEqual } from 'lodash'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.MHR_INFORMATION_NOTE
  })

  document.body.setAttribute('data-app', 'true')
  return mount(MhrUnitNote as any, {
    localVue,
    router,
    vuetify
  })
}

describe('MHR Unit Note Filing', () => {
  let wrapper: Wrapper<any>
  setupMockStaffUser()

  const UNIT_NOTE_DOC_TYPE = UnitNoteDocTypes.NOTICE_OF_CAUTION

  beforeEach(async () => {
    await store.setMhrUnitNoteType(UNIT_NOTE_DOC_TYPE)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders MhrUnitNote component and related sub-components', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    const unitNoteAdd = wrapper.find(getTestId('unit-note-add'))
    expect(unitNoteAdd.find('h1').text()).toContain(UnitNotesInfo[UNIT_NOTE_DOC_TYPE].header)
    expect(wrapper.findComponent(UnitNoteAdd).exists()).toBeTruthy()
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()
  })

  it('renders MhrUnitNote base component for filing the Unit Note', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    const UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    expect(UnitNoteAddComponent.exists()).toBeTruthy()

    expect(UnitNoteAddComponent.findComponent(DocumentId).exists()).toBeTruthy()
    expect(UnitNoteAddComponent.findComponent(Remarks).exists()).toBeTruthy()
    expect(UnitNoteAddComponent.findComponent(ContactInformation).exists()).toBeTruthy()

    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(0)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(0)
  })

  it('renders and validates MhrUnitNote Review and Confirm page with its components', async () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // make sure Review page is not showing up as there are errors
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()
    expect(wrapper.findAll('.border-error-left').length).toBe(2)

    const unitNoteValidationState = store.getMhrUnitNoteValidation

    const expectedUnitNoteValidationState: MhrUnitNoteValidationStateIF = {
      unitNoteAddValid: {
        documentIdValid: false,
        remarksValid: true,
        personGivingNoticeValid: false,
        submittingPartyValid: false,
        effectiveDateTimeValid: true,
        attentionValid: true,
        authorizationValid: false,
        staffPaymentValid: false
      }
    }

    // compare app validation state of components against expected validation state
    expect(isEqual(unitNoteValidationState, expectedUnitNoteValidationState)).toBeTruthy()

    // simulate valid fields for Unit Note App screen
    await wrapper.findComponent(UnitNoteAdd).vm.$emit('isValid', true)

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    const UnitNoteReviewComponent = wrapper.findComponent(UnitNoteReview)
    expect(UnitNoteReviewComponent.exists()).toBeTruthy()

    expect(UnitNoteReviewComponent.findComponent(UnitNoteReviewDetailsTable).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(Attention).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(StaffPayment).exists()).toBeTruthy()

    expect(UnitNoteReviewComponent.findAll('.border-error-left').length).toBe(0)
    expect(UnitNoteReviewComponent.findAll('.error-text').length).toBe(0)

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findAll('.border-error-left').length).toBe(3)
  })
})
