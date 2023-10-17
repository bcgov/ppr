import { nextTick } from 'vue'
import { ExemptionReview } from '@/views'
import { createComponent, setupMockLawyerOrNotary, setupMockStaffUser } from './utils'
import { axe } from 'jest-axe'
import {
  AccountInfo,
  Attention,
  CertifyInformation,
  FolioOrReferenceNumber,
  FormCard,
  ReviewCard
} from '@/components/common'
import { PartySearch } from '@/components/parties/party'
import { ConfirmCompletion } from '@/components/mhrTransfers'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'

describe('ExemptionReview', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ExemptionReview, { showErrors: false }, null, true)
    setupMockStaffUser()
    await nextTick()
  })

  it('mounts the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the header content', () => {
    expect(wrapper.find('h2').text()).toBe('Review and Confirm')
    const paragraphText = wrapper.find('p').text()
    expect(paragraphText).toContain('Review the information in your exemption')
    expect(paragraphText).toContain('If you need to change anything, return to the previous step')
  })

  it('renders the ReviewCard for Staff', async () => {
    expect(wrapper.findComponent(ReviewCard).exists()).toBe(true)
  })

  it('renders the AccountInfo for Qualified Supplier', async () => {
    setupMockLawyerOrNotary()
    await nextTick()

    expect(wrapper.findComponent(AccountInfo).exists()).toBe(true)
  })

  it('renders the PartySearch and FormCard for Staff', async () => {
    expect(wrapper.findComponent(PartySearch).exists()).toBe(true)
    expect(wrapper.findComponent(FormCard).exists()).toBe(true)
  })

  it('renders the Attention section', () => {
    expect(wrapper.findComponent(Attention).exists()).toBe(true)
  })

  it('renders the FolioOrReferenceNumber for Qualified Supplier', async () => {
    setupMockLawyerOrNotary()
    await nextTick()

    expect(wrapper.findComponent(FolioOrReferenceNumber).exists()).toBe(true)
  })

  it('renders the ConfirmCompletion section', () => {
    expect(wrapper.findComponent(ConfirmCompletion).exists()).toBe(true)
  })

  it('renders the CertifyInformation section', () => {
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
  })

  it('renders the StaffPayment for Staff', async () => {
    expect(wrapper.findComponent(StaffPayment).exists()).toBe(true)
  })

  it('should have no accessibility violations', async () => {
    const results = await axe(wrapper.html())
    expect(results).toHaveNoViolations()
  })
})
