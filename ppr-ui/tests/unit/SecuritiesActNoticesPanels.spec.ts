import { useStore } from '@/store/store'
import { nextTick } from 'vue'
import NoticePanel from '@/components/registration/securities-act-notices/NoticePanel.vue'
import SecuritiesActNoticesPanels from '@/components/registration/securities-act-notices/SecuritiesActNoticesPanels.vue'
import { beforeEach } from 'vitest'
import { createComponent } from './utils'
import { SaNoticeTypes } from '@/enums'
import flushPromises from 'flush-promises'
import { AddEditSaNoticeIF } from '@/interfaces'

const store = useStore()

const mockNotice: AddEditSaNoticeIF = {
  securitiesActNoticeType: SaNoticeTypes.NOTICE_OF_LIEN,
  effectiveDateTime: '2024-01-01',
  securitiesActOrders: []
}

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
        effectiveDateTime: '2024-05-10'
      },
      {
        noticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
        effectiveDateTime: '2024-05-10'
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
        effectiveDateTime: '2024-05-10'
      },
      {
        noticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
        effectiveDateTime: '2024-05-10'
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

  it('renders a notice panel content correctly', async () => {
    await store.setSecuritiesActNotices([mockNotice])
    await nextTick()

    expect(wrapper.find('.notice-type-text').text()).toBe('Notice of Lien')
    expect(wrapper.find('.security-notice-header-action').exists()).toBe(true)
    expect(wrapper.find('.security-notice-btn').exists()).toBe(true)
    expect(wrapper.find('#security-notice-menu-btn').exists()).toBe(true)
  })

  it('removes a notice correctly', async () => {
    await store.setSecuritiesActNotices([mockNotice])
    await nextTick()
    expect(wrapper.find('.notice-type-text').text()).toBe('Notice of Lien')

    await wrapper.findComponent(NoticePanel).vm.removeNotice(true)
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.notice-type-text').exists()).toBe(false)
    expect(wrapper.find('.effective-date-text').exists()).toBe(false)
  })
})
