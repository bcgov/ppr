import { ExemptionDetails } from '@/views'
import { CautionBox, DocumentId, Remarks, SimpleHelpToggle } from '@/components/common'
import { HomeLocationReview, HomeOwnersReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'

import { createComponent, setupMockStaffUser } from './utils'
import { nextTick } from 'vue'
import { axe } from 'jest-axe'

describe('ExemptionDetails', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent((ExemptionDetails as any), { showErrors: false })
    await nextTick()
  })

  it('mounts the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the basic applicable components', () => {
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(Remarks).exists()).toBe(false)
  })

  it('renders the applicable components for Staff', async () => {
    setupMockStaffUser()
    await nextTick()

    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(true)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(Remarks).exists()).toBe(true)
  })

  it('should have no accessibility violations', async () => {
    // Run the axe-core accessibility check on the component's HTML
    const results = await axe(wrapper.html())
    // Use the custom jest-axe matcher to check for violations
    expect(results).toHaveNoViolations()
  })
})
