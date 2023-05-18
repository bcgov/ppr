// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { TombstoneDischarge } from '@/components/tombstone'

// Other
import { FinancingStatementIF } from '@/interfaces'
import { mockedFinancingStatementComplete, mockedMhrInformation, mockedSelectSecurityAgreement } from './test-data'
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import { pacificDate } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const tombstoneHeader: string = '.tombstone-header'
const tombstoneSubHeader: string = '.tombstone-sub-header'
const tombstoneInfo: string = '.tombstone-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (mockRoute: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: mockRoute })

  return mount(TombstoneDischarge, {
    localVue,
    propsData: {},
    store,
    router,
    vuetify
  })
}

describe('Tombstone component', () => {
  let wrapper: any
  const { assign } = window.location

  const registration: FinancingStatementIF = {
    ...mockedFinancingStatementComplete
  }
  const registrationType = mockedSelectSecurityAgreement()

  beforeAll(async () => {
    // setup data
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationNumber', registration.baseRegistrationNumber)
    await store.dispatch('setRegistrationCreationDate', registration.createDateTime)
    await store.dispatch('setRegistrationExpiryDate', registration.expiryDate)
  })

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  afterAll(async () => {
    await store.dispatch('setRegistrationType', null)
    await store.dispatch('setRegistrationNumber', null)
    await store.dispatch('setRegistrationCreationDate', null)
    await store.dispatch('setRegistrationExpiryDate', null)
  })

  it('renders Tombstone component properly for Total Discharge', async () => {
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE)
    const tombstoneDischarge = wrapper.findComponent(TombstoneDischarge)
    expect(tombstoneDischarge.exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })

  it('renders Tombstone component properly for Renewal', async () => {
    wrapper = createComponent(RouteNames.RENEW_REGISTRATION)
    expect(wrapper.findComponent(TombstoneDischarge).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })

  it('renders Tombstone component properly for Amendment', async () => {
    wrapper = createComponent(RouteNames.AMEND_REGISTRATION)
    expect(wrapper.findComponent(TombstoneDischarge).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Base Registration Number ' + registration.baseRegistrationNumber)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(registrationType.registrationTypeUI)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(2)
    expect(extraInfo.at(0).text()).toContain('Base Registration Date and Time: ')
    expect(extraInfo.at(0).text()).toContain(pacificDate(new Date(registration.createDateTime))?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(pacificDate(new Date(registration.expiryDate))?.trim())
  })
})

describe('TombstoneDischarge component - MHR', () => {
  let wrapper: any
  const { assign } = window.location
  const mhrRegistrationInfo = mockedMhrInformation

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // setup data
    await store.dispatch('setMhrInformation', mockedMhrInformation)
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Tombstone component properly for Mhr', async () => {
    wrapper = createComponent(RouteNames.MHR_INFORMATION)
    const tombstoneDischarge = wrapper.findComponent(TombstoneDischarge)
    tombstoneDischarge.vm.$props.isMhrInformation = true
    await Vue.nextTick()
    expect(wrapper.findComponent(TombstoneDischarge).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Manufactured Home Registration Number ' +
                                          mhrRegistrationInfo.mhrNumber)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(1)
    expect(extraInfo.at(0).text()).toContain('Registration Status:')
    expect(extraInfo.at(0).text()).toContain('Active')
  })
})
