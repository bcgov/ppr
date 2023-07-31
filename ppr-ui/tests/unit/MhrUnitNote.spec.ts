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
import { Attention, CertifyInformation, ContactInformation, DocumentId, Remarks } from '@/components/common'
import {
  EffectiveDateTime,
  ExpiryDate,
  UnitNoteAdd,
  UnitNoteReview,
  UnitNoteReviewDetailsTable
} from '@/components/unitNotes'
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

async function createUnitNoteComponent (unitNoteType: UnitNoteDocTypes) {
  await store.setMhrUnitNoteType(unitNoteType)
  return createComponent()
}

// Go to Unit Note Review & Confirm screen and return its component for further testing
async function getReviewConfirmComponent (wrapper: Wrapper<any>): Promise<Wrapper<any, Element>> {
  // trigger initial validation
  await wrapper.find('#btn-stacked-submit').trigger('click')
  await wrapper.findComponent(UnitNoteAdd).vm.$emit('isValid', true)
  await wrapper.find('#btn-stacked-submit').trigger('click')
  await nextTick()

  const reviewConfirmComponent = wrapper.findComponent(UnitNoteReview)
  expect(reviewConfirmComponent.exists()).toBeTruthy()

  return reviewConfirmComponent
}

describe('MHR Unit Note Filing', () => {
  let wrapper: Wrapper<any>
  setupMockStaffUser()

  const UNIT_NOTE_DOC_TYPE = UnitNoteDocTypes.NOTICE_OF_CAUTION

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders MhrUnitNote component and related sub-components', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_CAUTION)

    await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_CAUTION)

    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    const unitNoteAdd = wrapper.find(getTestId('unit-note-add'))
    expect(unitNoteAdd.find('h1').text()).toContain(UnitNotesInfo[UNIT_NOTE_DOC_TYPE].header)
    expect(wrapper.findComponent(UnitNoteAdd).exists()).toBeTruthy()
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()
  })

  it('renders MhrUnitNote base component for filing the Unit Note', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_CAUTION)

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
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_CAUTION)

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
        expiryDateTimeValid: true,
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
    // ExpiryDate component should not exists for this Unit Note type
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()

    // check that section numbers are updated because ExpiryDate is displayed
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h2').text()).toContain('1.')
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).find('h2').text()).toContain('2.')
    expect(UnitNoteReviewComponent.findComponent(Attention).find('h2').text()).toContain('3.')
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).find('h2').text()).toContain('4.')
    expect(UnitNoteReviewComponent.find('#staff-transfer-payment-section h2').text()).toContain('5.')

    expect(UnitNoteReviewComponent.findAll('.border-error-left').length).toBe(0)
    expect(UnitNoteReviewComponent.findAll('.error-text').length).toBe(0)

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findAll('.border-error-left').length).toBe(3)
  })

  it('Continued Notice of Caution (CAUC): renders and validates MhrUnitNote Review and Confirm', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION)

    const UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)

    // ExpiryDate component should exist for this Unit Note type
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeTruthy()

    // check that section numbers have default sequence
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h2').text()).toContain('1.')
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).find('h2').text()).toContain('2.')
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).find('h2').text()).toContain('3.')
    expect(UnitNoteReviewComponent.findComponent(Attention).find('h2').text()).toContain('4.')
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).find('h2').text()).toContain('5.')
    expect(UnitNoteReviewComponent.findComponent(StaffPayment).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.find('#staff-transfer-payment-section h2').text()).toContain('6.')

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findAll('.border-error-left').length).toBe(3)

    // select past date in EffectiveDateTime to trigger validation
    UnitNoteReviewComponent.findComponent(EffectiveDateTime).findAll('input[type=radio]').at(1).trigger('click')

    const expiryDateRadioButtons = UnitNoteReviewComponent.findComponent(ExpiryDate).findAll('input[type=radio]')
    // should be two radio buttons for this Unit Note type
    expect(expiryDateRadioButtons.length).toBe(2)
    // select future date in ExpiryDate to trigger validation
    expiryDateRadioButtons.at(1).trigger('click')

    await nextTick()
    expect(wrapper.findAll('.border-error-left').length).toBe(5)
  })

  it('Extension to Notice of Caution (CAUE): renders and validates MhrUnitNote Review and Confirm', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION)

    const UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)

    // ExpiryDate component should exist for this Unit Note type
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeTruthy()

    // check that section numbers are updated because ExpiryDate is displayed
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h2').text()).toContain('1.')
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).find('h2').text()).toContain('2.')
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).find('h2').text()).toContain('3.')
    expect(UnitNoteReviewComponent.findComponent(Attention).find('h2').text()).toContain('4.')
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).find('h2').text()).toContain('5.')
    expect(UnitNoteReviewComponent.findComponent(StaffPayment).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.find('#staff-transfer-payment-section h2').text()).toContain('6.')

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findAll('.border-error-left').length).toBe(4)

    // select past date in EffectiveDateTime to trigger validation
    UnitNoteReviewComponent.findComponent(EffectiveDateTime).findAll('input[type=radio]').at(1).trigger('click')

    const expiryDateRadioButtons = UnitNoteReviewComponent.findComponent(ExpiryDate).findAll('input[type=radio]')
    // should be no radio buttons for this Unit Note type
    expect(expiryDateRadioButtons.length).toBe(0)

    await nextTick()
    expect(wrapper.findAll('.border-error-left').length).toBe(5)
  })

  it('should not show field errors for optional Party Giving Notice', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.DECAL_REPLACEMENT)

    const UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(0)

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()

    // only one error for Document ID should be shown, as the other fields are optional
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(1)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(1)

    const PersonGivingNoticeComponent = UnitNoteAddComponent.findComponent(ContactInformation)
    expect(PersonGivingNoticeComponent.exists()).toBeTruthy()
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBe(0)

    await wrapper.findComponent(UnitNoteAdd).vm.$emit('isValid', true)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // should be on the Review & Confirm screen
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeTruthy()

    // 'Not Entered' should be shown 4 times for each column in the table
    expect(wrapper.find(getTestId('party-info-table')).findAll('.text-not-entered').length).toBe(4)
  })

  it('should not show EffectiveDateTime component for Decal Replacement and Public Note', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.DECAL_REPLACEMENT)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.DECAL_REPLACEMENT)

    let UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h2').text()).toContain('1.')
    expect(UnitNoteReviewComponent.findComponent(Attention).find('h2').text()).toContain('2.')
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).find('h2').text()).toContain('3.')
    expect(UnitNoteReviewComponent.find('#staff-transfer-payment-section h2').text()).toContain('4.')

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.PUBLIC_NOTE)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.PUBLIC_NOTE)

    UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h2').text()).toContain('1.')
    expect(UnitNoteReviewComponent.findComponent(Attention).find('h2').text()).toContain('2.')
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).find('h2').text()).toContain('3.')
    expect(UnitNoteReviewComponent.find('#staff-transfer-payment-section h2').text()).toContain('4.')
  })
})
