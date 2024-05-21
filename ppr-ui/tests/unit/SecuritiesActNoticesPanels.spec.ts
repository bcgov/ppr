import { createComponent } from './utils'
import { beforeEach, describe, expect, it } from 'vitest'
import SecuritiesActNoticesPanels from '@/components/registration/securities-act-notices/SecuritiesActNoticesPanels.vue'
import { AddEditSaNoticeIF } from '@/interfaces'
import { SaNoticeTypes } from '@/enums'
import { useStore } from '@/store/store'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import NoticePanel from '@/components/registration/securities-act-notices/NoticePanel.vue'

const store = useStore()

const mockNotice: AddEditSaNoticeIF = {
  securitiesActNoticeType: SaNoticeTypes.NOTICE_OF_LIEN,
  effectiveDate: '2024-01-01',
  securitiesActOrders: []
}

describe('NoticePanel.vue', () => {
  let wrapper
  beforeEach(async ()=> {
    await store.setSecuritiesActNotices([mockNotice])
    wrapper = await createComponent(SecuritiesActNoticesPanels, {
      isAddingNotice: false
    })
  })

  it('renders a notice panel correctly', () => {
    expect(wrapper.find('.notice-type-text').text()).toBe('Notice of Lien')
    expect(wrapper.find('.effective-date-text').text()).toContain('Effective Date: January 1, 2024')
    expect(wrapper.find('.security-notice-header-action').exists()).toBe(true)
    expect(wrapper.find('.security-notice-btn').exists()).toBe(true)
    expect(wrapper.find('#security-notice-menu-btn').exists()).toBe(true)

  })

  it('removes a notice correctly', async () => {
    expect(wrapper.find('.notice-type-text').text()).toBe('Notice of Lien')
    expect(wrapper.find('.effective-date-text').text()).toContain('Effective Date: January 1, 2024')

    await wrapper.findComponent(NoticePanel).vm.removeNotice(true)
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.notice-type-text').exists()).toBe(false)
    expect(wrapper.find('.effective-date-text').exists()).toBe(false)
  })
})
