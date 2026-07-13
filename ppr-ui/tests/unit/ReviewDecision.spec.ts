import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
import { useAnalystQueueStore } from '@/store/analystQueue'
import ReviewDecision from '../../src/components/queue/ReviewDecision.vue'
import { ReviewStatusTypes } from '@/composables'
import { createComponent, setupMockStaffUser } from './utils'

describe('ReviewDecision', () => {
  let pinia
  let store
  let analystQueueStore
  let wrapper

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)

    store = useStore()
    analystQueueStore = useAnalystQueueStore()

    await store.setUserInfo({
      firstname: 'Test',
      lastname: 'User',
      username: 'user'
    } as any)
    setupMockStaffUser(store)

    analystQueueStore.queueTransfer = {
      status: ReviewStatusTypes.IN_REVIEW,
      assigneeName: 'someone-else'
    } as any

    wrapper = await createComponent(ReviewDecision, {}, null, {}, [pinia])
    await nextTick()
  })

  it('shows an error when a non-assignee clicks a decision button', async () => {
    const approveButton = wrapper.findAll('button').find(button => button.text().includes('Approve'))

    expect(approveButton).toBeTruthy()

    analystQueueStore.queueTransfer.assigneeName = 'someone-else'
    await approveButton!.trigger('click')
    await nextTick()

    expect(analystQueueStore.validationErrors.general).toBe(
      'Please assign this filing to yourself to approve or decline.'
    )
    expect(wrapper.text()).toContain('Please assign this filing to yourself to approve or decline.')
  })

  it('resets the review decision when the assignee changes to the current user', async () => {
    analystQueueStore.reviewDecision = {
      statusType: ReviewStatusTypes.DECLINED,
      declinedReasonType: 'NON_COMPLIANCE'
    } as any
    analystQueueStore.validationErrors.general = 'Please assign this filing to yourself to approve or decline.'
    analystQueueStore.validationErrors.declineReasonType = 'Please select a reason for declining'

    analystQueueStore.queueTransfer.assigneeName = 'user'
    await nextTick()

    expect(analystQueueStore.validationErrors.general).toBe('')
    expect(analystQueueStore.validationErrors.declineReasonType).toBe('')
    expect(analystQueueStore.reviewDecision.statusType).toBeUndefined()
    expect(analystQueueStore.reviewDecision.declinedReasonType).toBeUndefined()
    expect(wrapper.exists()).toBe(true)
  })
})