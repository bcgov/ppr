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
import { mockedFinancingStatementComplete, mockedSelectSecurityAgreement } from './test-data'
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import { convertDate, pacificDate } from '@/utils'

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
 * @returns a Wrapper<SearchedResult> object with the given parameters.
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

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // setup data
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setRegistrationNumber', registration.baseRegistrationNumber)
    await store.dispatch('setRegistrationCreationDate', registration.createDateTime)
    await store.dispatch('setRegistrationExpiryDate', registration.expiryDate)
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Tombstone component properly for Total Discharge', async () => {
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE)
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
    expect(extraInfo.at(0).text()).toContain(convertDate(new Date(registration.createDateTime), true, true)?.trim())
    expect(extraInfo.at(1).text()).toContain('Current Expiry Date and Time: ')
    expect(extraInfo.at(1).text()).toContain(convertDate(new Date(registration.expiryDate), true, true)?.trim())
  })
})
