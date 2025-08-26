import { nextTick } from 'vue'
import { createComponent } from "./utils"
import { ConfirmMHRSearch } from '@/pages'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'
import { SearchedResultsMhr } from '@/components/tables/mhr'
import { RouteNames } from '@/enums'
import { FolioNumberSummary, StickyContainer } from '@/components/common'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { BaseDialog } from '@/components/dialogs'
import { defaultFlagSet } from '@/utils/feature-flags'
import { mockedMHRSearchResults } from './test-data'

const store = useStore()

describe('Confirm MHRSearch view', () => {
  let wrapper

  beforeEach(async () => {
    await store.setManufacturedHomeSearchResults(mockedMHRSearchResults)
    await nextTick()

    wrapper = await createComponent(ConfirmMHRSearch, { appReady: true }, RouteNames.MHRSEARCH_CONFIRM)
    await flushPromises()
  })

  it('renders Confirm Registration View with child components', () => {
    expect(wrapper.findComponent(ConfirmMHRSearch).exists()).toBe(true)
    expect(wrapper.findComponent(SearchedResultsMhr).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHRSEARCH_CONFIRM)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Pay and Download Result')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // folio
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
  })

  it('processes back button action', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHRSEARCH)
  })

  it('processes cancel button action', async () => {
    // setup
    await store.setUnsavedChanges(true)
    // dialog doesn't start visible
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    // pressing cancel triggers dialog
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(true)
    // if dialog emits proceed false it closes + stays on page
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHRSEARCH_CONFIRM)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('shows errors when folio is invalid', async () => {
    await wrapper.findComponent(FolioNumberSummary).vm.$emit('folioValid', false)
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      // turn show errors on when invalid
      expect(wrapper.vm.showErrors).toBe(true)
    }, 2000)
  })

  it('shows errors when staff payment is invalid', async () => {
    store.setIsStaffClientPayment(true)
    wrapper.vm.staffPaymentValid = false
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      // turn show errors on when invalid
      expect(wrapper.vm.showErrors).toBe(true)
    }, 2000)
  })

  it('processes submit button action', async () => {
    // TODO
  })
})
