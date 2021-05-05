// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { LengthTrust } from '@/views'
import { RegistrationFee, Stepper, Tombstone } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'

// Other
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const saveResumeBtn: string = '#reg-save-resume-btn'
const backBtn: string = '#reg-back-btn'
const nextBtn: string = '#reg-next-btn'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Length and Trust Indenture new registration component', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'length-trust' })
    wrapper = shallowMount(LengthTrust, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Length Trust View with child components', () => {
    expect(wrapper.findComponent(LengthTrust).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
  })
  it('Length Trust cancel button event', async () => {
    wrapper.find(cancelBtn).trigger('click')
    await Vue.nextTick()
    // expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Length Trust save button event', async () => {
    wrapper.find(saveBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Length Trust save and resume button event', async () => {
    wrapper.find(saveResumeBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Length Trust next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Length Trust submitCancel', async () => {
    wrapper.vm.submitCancel()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Length Trust submitBack', async () => {
    wrapper.vm.submitBack()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Length Trust submitNext', async () => {
    wrapper.vm.submitNext()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
  })
  it('Length Trust submitSave', async () => {
    wrapper.vm.submitSave()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Length Trust submitSaveResume', async () => {
    wrapper.vm.submitSaveResume()
    await Vue.nextTick()
  })
})
