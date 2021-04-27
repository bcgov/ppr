// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { AddSecuredPartiesAndDebtors } from '@/views'
import { RegistrationFee, Stepper, Tombstone } from '@/components/common'

// Other
import mockRouter from './MockRouter'
import { mockedError } from './test-data'
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

describe('AddParties new registration component', () => {
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
    await router.push({ name: 'add-securedparties-debtors' })
    wrapper = shallowMount(AddSecuredPartiesAndDebtors, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Add Parties View with child components', () => {
    expect(wrapper.findComponent(AddSecuredPartiesAndDebtors).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
  })
  it('Add Parties cancel button event', async () => {
    wrapper.find(cancelBtn).trigger('click')
    await Vue.nextTick()
    // expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Add Parties save button event', async () => {
    wrapper.find(saveBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Add Parties save and resume button event', async () => {
    wrapper.find(saveResumeBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Add Parties back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Add Parties next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Add Parties emitError', async () => {
    wrapper.vm.emitError(mockedError)
  })
  it('Add Parties submitCancel', async () => {
    wrapper.vm.submitCancel()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Add Parties submitBack', async () => {
    wrapper.vm.submitBack()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
  })
  it('Add Parties submitNext', async () => {
    wrapper.vm.submitNext()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_COLLATERAL)
  })
  it('Add Parties submitSave', async () => {
    wrapper.vm.submitSave()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
  it('Add Parties submitSaveResume', async () => {
    wrapper.vm.submitSaveResume()
    await Vue.nextTick()
  })
})
