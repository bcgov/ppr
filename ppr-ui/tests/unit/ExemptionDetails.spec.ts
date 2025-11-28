import { ExemptionDetails } from '@/pages'
import { CautionBox, DocumentId, LienAlert, Remarks, SimpleHelpToggle } from '@/components/common'
import { HomeLocationReview, HomeOwnersReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'

import { createComponent, getTestId, setupActiveTransportPermit, setupMockStaffUser } from './utils'
import { nextTick } from 'vue'
import { axe } from 'vitest-axe'
import { TransportPermitDetails } from '@/components/mhrTransportPermits'
import { useStore } from '@/store/store'
import { mockedAddress } from './test-data'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { createPinia, setActivePinia } from 'pinia'

const store = useStore()

describe('ExemptionDetails', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    wrapper = await createComponent(
      ExemptionDetails as any,
      { showErrors: false },
      RouteNames.EXEMPTION_DETAILS,
      null,
      [pinia])
    await nextTick()
  })

  it('mounts the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the basic applicable components', () => {
    expect(wrapper.findComponent(LienAlert).exists()).toBe(false)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(Remarks).exists()).toBe(false)
  })

  it('renders the applicable components for Staff', async () => {
    setupMockStaffUser(store)
    await nextTick()

    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(true)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(Remarks).exists()).toBe(true)
  })

  it.skip('should have no accessibility violations', async () => {
    // Run the axe-core accessibility check on the component's HTML
    const results = await axe(wrapper.html())
    expect(results).toBeDefined()
    expect(results.violations).toBeDefined()
    expect(results.violations).toHaveLength(0)
  })

  it('renders the Exemption Details with active Transport Permit', async () => {
    setupMockStaffUser(store)

    // setup active Transport Permit and Non-Res Exemption
    setupActiveTransportPermit(store)
    store.setMhrLocation({ key: 'address', value: mockedAddress })
    store.setMhrExemptionNote({ key: 'documentType', value: UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION })
    await nextTick()

    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(true)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).findComponent(HomeLocationReview).exists()).toBe(true)

    const transportPermitDetails = wrapper.findComponent(HomeLocationReview).findComponent(TransportPermitDetails)
    expect(transportPermitDetails.exists()).toBe(true)
    expect(transportPermitDetails.find(getTestId('void-transport-permit-badge')).exists()).toBeTruthy()
    expect(transportPermitDetails.find(getTestId('permit-details-info-text')).exists()).toBeTruthy()

    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(Remarks).exists()).toBe(true)
  })
})
