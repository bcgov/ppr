// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { createLocalVue, shallowMount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
// Components
import { ConfirmMHRSearch } from '@/views'
import {
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
// ppr enums/utils/etc.
import { RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
// test mocks/data
import mockRouter from './MockRouter'
import { SearchedResultMhr } from '@/components/tables'
import { defaultFlagSet } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Confirm MHRSearch view', () => {
  let wrapper: any
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    defaultFlagSet['mhr-ui-enabled'] = true
    delete window.location
    window.location = { assign: jest.fn() } as any
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.MHRSEARCH_CONFIRM
    })
    wrapper = shallowMount(ConfirmMHRSearch as any, {
      localVue,
      store,
      router,
      stubs: { Affix: true },
      vuetify
    })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Confirm Registration View with child components', () => {
    expect(wrapper.findComponent(ConfirmMHRSearch).exists()).toBe(true)
    expect(wrapper.findComponent(SearchedResultMhr).exists()).toBe(true)
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
