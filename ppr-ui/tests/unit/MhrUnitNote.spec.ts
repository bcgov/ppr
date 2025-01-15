import { nextTick } from 'vue'
import { useStore } from '../../src/store/store'
import type { Wrapper } from '@vue/test-utils'

import { MhrUnitNote } from '@/pages'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { createComponent, getTestId, setupMockStaffUser } from './utils'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { Attention, CertifyInformation, ContactInformation, DocumentId, Remarks, StaffPayment } from '@/components/common'
import {
  EffectiveDate,
  ExpiryDate,
  UnitNoteAdd,
  UnitNoteReview,
  UnitNoteReviewDetailsTable
} from '@/components/unitNotes'
import type { MhrUnitNoteValidationStateIF } from '@/interfaces'
import { isEqual } from 'lodash'
import {
  collectorInformationContent,
  remarksContent,
  hasNoPersonGivingNoticeText,
  submittingPartyRegistrationContent,
  submittingPartyChangeContent
} from '@/resources'
import { mockedCancelPublicNote, mockedUnitNotes5 } from './test-data'
import { useMhrUnitNote } from '@/composables'

const store = useStore()

async function createUnitNoteComponent (unitNoteType: UnitNoteDocTypes) {
  await store.setMhrUnitNoteType(unitNoteType)
  return await createComponent(MhrUnitNote, { appReady: true }, RouteNames.MHR_INFORMATION_NOTE )
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

describe('MHR Unit Note Filing', async () => {
  let wrapper: Wrapper<any>
  await setupMockStaffUser()

  const UNIT_NOTE_DOC_TYPE = UnitNoteDocTypes.NOTICE_OF_CAUTION

  it('renders MhrUnitNote component and related sub-components', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_CAUTION)

    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_INFORMATION_NOTE)
    expect(wrapper.exists()).toBeTruthy()

    const unitNoteAdd = wrapper.find(getTestId('unit-note-add'))
    expect(unitNoteAdd.find('h1').text()).toContain(UnitNotesInfo[UNIT_NOTE_DOC_TYPE].header)
    expect(wrapper.find(getTestId('cau-exp-note')).exists()).toBeTruthy()
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
    expect(UnitNoteReviewComponent.find(getTestId('cancel-note-info')).exists()).toBeFalsy()

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

    // select past date in EffectiveDate to trigger validation
    await UnitNoteReviewComponent.findComponent(EffectiveDate).findAll('input[type=radio]').at(1).setValue(true)

    const expiryDateRadioButtons = UnitNoteReviewComponent.findComponent(ExpiryDate).findAll('input[type=radio]')
    // should be two radio buttons for this Unit Note type
    expect(expiryDateRadioButtons.length).toBe(2)
    // select future date in ExpiryDate to trigger validation
    await expiryDateRadioButtons.at(1).setValue(true)

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

    // select past date in EffectiveDate to trigger validation
    await UnitNoteReviewComponent.findComponent(EffectiveDate).findAll('input[type=radio]').at(1).setValue(true)

    const expiryDateRadioButtons = UnitNoteReviewComponent.findComponent(ExpiryDate).findAll('input[type=radio]')
    // should be no radio buttons for this Unit Note type
    expect(expiryDateRadioButtons.length).toBe(0)

    await nextTick()
    expect(wrapper.findAll('.border-error-left').length).toBe(5)
  })

  it('should not show field errors when no person giving notice checkbox is checked', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.PUBLIC_NOTE)

    let UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(0)
    expect(wrapper.find(getTestId('cau-exp-note')).exists()).toBeFalsy()

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()

    // Asserts error shown before checking the checkbox(document ID, remarks, contactInfo)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(3)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(3)

    const PersonGivingNoticeComponent = UnitNoteAddComponent.findComponent(ContactInformation)

    // Asserts form is not disabled and showcases errors
    expect(PersonGivingNoticeComponent.find('#contact-info').classes('v-card--disabled')).toBe(false)
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBeGreaterThan(0)

    // check the checkbox
    await UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').setValue(true)
    await nextTick()
    expect(store.getMhrUnitNote.hasNoPersonGivingNotice).toBe(true)

    // Assert contact form is disabled
    expect(PersonGivingNoticeComponent.find('#contact-info').exists()).toBeFalsy()

    // Asserts error not shown after checking the checkbox (2 error remains from doucment ID and remarks)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(2)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(2)
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBe(0)

    // uncheck the checkbox
    await UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').setValue(false)
    await nextTick()
    expect(store.getMhrUnitNote.hasNoPersonGivingNotice).toBe(false)

    // Asserts error shown after the checkbox is unchecked and form is not disabled
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(3)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(3)
    expect(PersonGivingNoticeComponent.findAll('.error-text').length).toBeGreaterThan(0)
    expect(PersonGivingNoticeComponent.find('#contact-info').classes('v-card--disabled')).toBe(false)

    // recheck check box
    await UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').setValue(true)
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

  it('Person Giving Notice should be checked if doctype is decal replacement', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.DECAL_REPLACEMENT)

    const UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    
    expect((UnitNoteAddComponent.find('#no-person-giving-notice-checkbox').element as HTMLInputElement)
      .checked).toBe(true)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeFalsy()

    // Asserts error shown before checking the checkbox(document ID)
    expect(UnitNoteAddComponent.findAll('.border-error-left').length).toBe(1)
    expect(UnitNoteAddComponent.findAll('.error-text').length).toBe(1)


    await wrapper.findComponent(UnitNoteAdd).vm.$emit('isValid', true)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // should be on the Review & Confirm screen
    expect(wrapper.findComponent(UnitNoteReview).exists()).toBeTruthy()

    // 'There no Person Giving Notice...' should be shown next to Person Giving Notice
    expect(wrapper.find('.no-person-giving-notice').text())
      .toBe(hasNoPersonGivingNoticeText)
  })
   
  it('should not show EffectiveDate component for Decal Replacement, Public Note, and Confidential Note', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.DECAL_REPLACEMENT)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.DECAL_REPLACEMENT)

    let UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDate).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.PUBLIC_NOTE)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.PUBLIC_NOTE)

    UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDate).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.CONFIDENTIAL_NOTE)

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.CONFIDENTIAL_NOTE)
    UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    expect(UnitNoteReviewComponent.findComponent(EffectiveDate).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.findComponent(ExpiryDate).exists()).toBeFalsy()
    expect(UnitNoteReviewComponent.find(getTestId('cancel-note-info')).exists()).toBeFalsy()
  })

  it('Notice of Tax Sale (TAXN): should show additional Remarks & correct title for Giving Notice Party', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_TAX_SALE)

    const UnitNoteAddComponent = wrapper.findComponent(UnitNoteAdd)
    const additionalRemarksCheckbox = UnitNoteAddComponent.findComponent(Remarks).find(
      getTestId('additional-remarks-checkbox')
    )

    expect(additionalRemarksCheckbox.exists()).toBeTruthy()
    additionalRemarksCheckbox.find('input').setValue(true)

    const ContactInformationComponent = UnitNoteAddComponent.findComponent(ContactInformation)

    expect(ContactInformationComponent.find('h3').text()).toContain(collectorInformationContent.title)

    const UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    const UnitNoteReviewTable = UnitNoteReviewComponent.findComponent(UnitNoteReviewDetailsTable)

    expect(UnitNoteReviewTable.text()).toContain(remarksContent.checkboxLabel)
    expect(UnitNoteReviewTable.text()).toContain(collectorInformationContent.title)
  })

  it('Cancel Note (NCAN): renders Landing & Review pages for Public Note cancellation', async () => {
    await store.setMhrUnitNote(mockedCancelPublicNote)
    await nextTick()
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTE_CANCELLATION)

    const header = wrapper.find(getTestId('unit-note-add')).find('h1').text()
    expect(header).toContain(UnitNotesInfo[UnitNoteDocTypes.NOTE_CANCELLATION].header)
    expect(header).toContain(UnitNotesInfo[UnitNoteDocTypes.PUBLIC_NOTE].header)

    expect(wrapper.findComponent(DocumentId).vm.$props.documentId).toBe('')
    expect(wrapper.findComponent(Remarks).vm.$props.unitNoteRemarks).toBe(mockedCancelPublicNote.remarks)
    expect(wrapper.findComponent(Remarks).find('.generic-label').text()).toBe(remarksContent.sideLabelCancelNote)

    const UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    const UnitNoteReviewTable = UnitNoteReviewComponent.findComponent(UnitNoteReviewDetailsTable)

    const reviewHeader = UnitNoteReviewTable.findAll('.details').at(0).text()
    expect(reviewHeader).toContain(UnitNotesInfo[UnitNoteDocTypes.NOTE_CANCELLATION].header)
    expect(reviewHeader).toContain(UnitNotesInfo[UnitNoteDocTypes.PUBLIC_NOTE].header)

    // additional info text should exists for Cancel Note
    expect(UnitNoteReviewComponent.find(getTestId('cancel-note-info')).text())
      .toContain(UnitNotesInfo[UnitNoteDocTypes.PUBLIC_NOTE].header)

    // Effective Date should not existing for Cancel Note
    expect(UnitNoteReviewComponent.findComponent(EffectiveDate).exists()).toBeFalsy()

    expect(UnitNoteReviewComponent.findComponent(ContactInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h3').text()).toBe(
      submittingPartyChangeContent.title
    )
    expect(UnitNoteReviewComponent.findComponent(Attention).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(StaffPayment).exists()).toBeTruthy()
  })

  it('Notice of Redemption (NRED): renders Landing & Review pages', async () => {
    const noticeOfTaxSale = mockedUnitNotes5[0]
    // simulate clicking on File Notice of Redemption (for Notice of Tax Sale)
    const noticeOfRedemption = await useMhrUnitNote()
      .prefillUnitNote(noticeOfTaxSale, UnitNoteDocTypes.NOTICE_OF_REDEMPTION)

    await store.setMhrUnitNote(noticeOfRedemption)
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_REDEMPTION)
    await nextTick()

    expect(wrapper.find(getTestId('cau-exp-note')).exists()).toBeFalsy()
    const header = wrapper.find(getTestId('unit-note-add')).find('h1').text()
    expect(header).toContain(UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_REDEMPTION].header)

    expect(wrapper.findComponent(DocumentId).vm.$props.documentId).toBe('') // doc id should be cleared out
    expect(wrapper.findComponent(Remarks).vm.$props.unitNoteRemarks).toBe(noticeOfTaxSale.remarks)
    expect(wrapper.findComponent(Remarks).find('.side-label').text()).toBe(remarksContent.sideLabel)

    const UnitNoteReviewComponent = await getReviewConfirmComponent(wrapper)
    const UnitNoteReviewTable = UnitNoteReviewComponent.findComponent(UnitNoteReviewDetailsTable)

    const reviewHeader = UnitNoteReviewTable.findAll('.details').at(0).text()
    expect(reviewHeader).toContain(UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_REDEMPTION].header)

    // additional info text should exists for Cancel Note
    expect(UnitNoteReviewComponent.find(getTestId('redemption-note-info')).exists()).toBeTruthy()

    // Effective Date should not existing for Cancel Note
    expect(UnitNoteReviewComponent.findComponent(EffectiveDate).exists()).toBeFalsy()

    expect(UnitNoteReviewComponent.findComponent(ContactInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(ContactInformation).find('h3').text()).toBe(
      submittingPartyRegistrationContent.title
    )
    expect(UnitNoteReviewComponent.findComponent(Attention).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(CertifyInformation).exists()).toBeTruthy()
    expect(UnitNoteReviewComponent.findComponent(StaffPayment).exists()).toBeTruthy()
  })

  it('Additional Remarks checkbox should not be included for REST, NCON and NPUB Unit Notes', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.RESTRAINING_ORDER)

    expect(
      wrapper.findComponent(UnitNoteAdd).findComponent(Remarks).find(getTestId('additional-remarks-checkbox')).exists()
    ).toBeFalsy()

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.CONFIDENTIAL_NOTE)

    expect(
      wrapper.findComponent(UnitNoteAdd).findComponent(Remarks).find(getTestId('additional-remarks-checkbox')).exists()
    ).toBeFalsy()

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.PUBLIC_NOTE)

    expect(
      wrapper.findComponent(UnitNoteAdd).findComponent(Remarks).find(getTestId('additional-remarks-checkbox')).exists()
    ).toBeFalsy()
  })

  it('Remarks should be required for Public Note, optional for other notes', async () => {
    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.PUBLIC_NOTE)

    // should have Remarks error
    await wrapper.find('#btn-stacked-submit').trigger('click')
    expect(wrapper.findComponent(UnitNoteAdd).findAll('.border-error-left').length).toBe(3)
    expect(wrapper.findComponent(Remarks).findAll('.error-text')).toHaveLength(1)

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_TAX_SALE)

    // should not have Remarks error
    await wrapper.find('#btn-stacked-submit').trigger('click')
    expect(wrapper.findComponent(UnitNoteAdd).findAll('.border-error-left').length).toBe(2)
    expect(wrapper.findComponent(Remarks).findAll('.error-text')).toHaveLength(0)

    wrapper = await createUnitNoteComponent(UnitNoteDocTypes.NOTICE_OF_CAUTION)

    // should not have Remarks error
    await wrapper.find('#btn-stacked-submit').trigger('click')
    expect(wrapper.findComponent(UnitNoteAdd).findAll('.border-error-left').length).toBe(2)
    expect(wrapper.findComponent(Remarks).findAll('.error-text')).toHaveLength(0)
  })
})
