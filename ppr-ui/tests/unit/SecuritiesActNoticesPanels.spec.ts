import { useStore } from '@/store/store'
import { nextTick } from 'vue'
import NoticePanel from '@/components/registration/securities-act-notices/NoticePanel.vue'
import SecuritiesActNoticesPanels from '@/components/registration/securities-act-notices/SecuritiesActNoticesPanels.vue'
import { beforeEach } from 'vitest'
import { createComponent } from './utils'
import { SaNoticeTypes } from '@/enums'

const store = useStore()

describe('SecuritiesActNoticesPanel.vue', () => {
  let wrapper
  beforeEach(async () => {
    wrapper = await createComponent(SecuritiesActNoticesPanels, {
      isAddingNotice: false
    })
  })

  it('renders no notices message when no notices are available', async () => {
    // Check if the no notices message is rendered
    expect(wrapper.find('.empty-notices-msg').exists()).toBe(true)
  })

  it('renders notice panels when notices are available', async () => {
    // Simulate having notices available
    store.setSecuritiesActNotices([
      {
        noticeType: SaNoticeTypes.NOTICE_OF_LIEN,
        effectiveDate: '2024-05-10'
      },
      {
        noticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
        effectiveDate: '2024-05-10'
      }
    ])

    await nextTick()

    // Check if notice panels are rendered
    expect(wrapper.findAllComponents(NoticePanel).length).toBe(2)
  })

  it('toggles panel when clicked', async () => {
    // Simulate having notices available
    store.setSecuritiesActNotices([
      {
        noticeType: SaNoticeTypes.NOTICE_OF_LIEN,
        effectiveDate: '2024-05-10'
      },
      {
        noticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
        effectiveDate: '2024-05-10'
      }
    ])

    const panels = await wrapper.findAllComponents(NoticePanel)

    // Click on the first panel
    await panels.at(0).find('.security-notice-header-action').trigger('click')

    // Check if the first panel is active
    expect(wrapper.vm.activePanels).toEqual([0])

    // Click on the second panel
    await panels.at(1).find('.security-notice-header-action').trigger('click')

    // Check if the second panel is active and the first active panel was closed
    expect(wrapper.vm.activePanels).toEqual([1])
  })
})
