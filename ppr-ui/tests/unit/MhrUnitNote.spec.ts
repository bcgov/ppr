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
import { collectorInformationContent, remarksContent, hasNoPersonGivingNoticeText } from '@/resources'

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
    expect(
      UnitNoteAddComponent.findComponent(Remarks).find(getTestId('additional-remarks-checkbox')).exists()
    ).toBeFalsy()

    // Person giving notice for notice of caution is mandatory
    expect(UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').exists()).toBeFalsy()

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

    expect(UnitNoteReviewComponent.findComponent(Attention).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(StaffPayment).exists()).toBeTruthy()

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

  it('should not show field errors when no person giving notice checkbox is checked', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.DECAL_REPLACEMENT)

    let UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(0)

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()

    // Asserts error shown before checking the checkbox
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(2)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(2)

    const PersonGivingNoticeComponent = UnitNoteAddComponent.findComponent(ContactInformation)

    // Asserts form is not disabled and showcases errors
    expect(PersonGivingNoticeComponent.find('#contact-info').classes('v-card--disabled')).toBe(false)
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBeGreaterThan(0)

    // check the checkbox
    await UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').trigger('click')
    await nextTick()
    expect(store.getMhrUnitNote.hasNoPersonGivingNotice).toBe(true)

    // Assert contact form is disabled
    expect(PersonGivingNoticeComponent.find('#contact-info').exists()).toBeFalsy()

    // Asserts error not shown after checking the checkbox (1 error remains from doucment ID)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(1)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(1)
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBe(0)

    // uncheck the checkbox
    await UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').trigger('click')
    await nextTick()
    expect(store.getMhrUnitNote.hasNoPersonGivingNotice).toBe(false)

    // Asserts error shown after the checkbox is unchecked and form is not disabled
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(2)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(2)
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBeGreaterThan(0)
    expect(PersonGivingNoticeComponent.find('#contact-info').classes('v-card--disabled')).toBe(false)

    // recheck check box
    await UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').trigger('click')
    await nextTick()
    expect(store.getMhrUnitNote.hasNoPersonGivingNotice).toBe(true)

    await wrapper.findComponent(UnitNoteAdd).vm.$emit('isValid', true)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // should be on the Review & Confirm screen
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeTruthy()

    // 'There no Person Giving Notice...' should be shown next to Person Giving Notice
    expect(wrapper.find('.no-person-giving-notice').text())
      .toBe(hasNoPersonGivingNoticeText)

    // Return to the Unit Note Add screen and check the checkbox is still checked and errors are not shown
    await wrapper.find('#btn-stacked-back').trigger('click')
    await nextTick()

    UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    expect(UnitNoteAddComponent.exists()).toBeTruthy()
    expect((UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').element as HTMLInputElement)
      .checked).toBe(true)
  })

  // eslint-disable-next-line max-len
  it('should not show EffectiveDateTime component for Decal Replacement, Public Note, and Confidential Note', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.DECAL_REPLACEMENT)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.DECAL_REPLACEMENT)

    let UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.PUBLIC_NOTE)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.PUBLIC_NOTE)

    UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.CONFIDENTIAL_NOTE)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.CONFIDENTIAL_NOTE)
    UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDateTime).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()
  })

  it('Notice of Tax Sale (TAXN): should show additional Remarks & correct title for Giving Notice Party', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_TAX_SALE)

    const UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    const additionalRemarksCheckbox = UnitNoteAddComponent.findComponent(Remarks).find(
      getTestId('additional-remarks-checkbox')
    )

    expect(additionalRemarksCheckbox.exists()).toBeTruthy()
    additionalRemarksCheckbox.trigger('click')

    const ContactInformationComponent = UnitNoteAddComponent.findComponent(ContactInformation)

    expect(ContactInformationComponent.find('h2').text()).toContain(collectorInformationContent.title)

    const UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    const UnitNoteReviewTable = UnitNoteReviewComponent.findComponent(UnitNoteReviewDetailsTable)

    expect(UnitNoteReviewTable.text()).toContain(remarksContent.checkboxLabel)
    expect(UnitNoteReviewTable.text()).toContain(collectorInformationContent.title)
  })
})
