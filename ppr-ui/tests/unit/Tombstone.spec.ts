// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { Tombstone, TombstoneDefault, TombstoneDischarge } from '@/components/tombstone'

// Other
import { AccountInformationIF, FinancingStatementIF, UserInfoIF } from '@/interfaces'
import { mockedFinancingStatementComplete, mockedSelectSecurityAgreement } from './test-data'
import mockRouter from './MockRouter'
import { AuthRoles, ProductCode, RouteNames } from '@/enums'
import { convertDate, pacificDate } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()
const router = mockRouter.mock()

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
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  router.push({ name: mockRoute })

  return mount((Tombstone as any), {
    localVue,
    store,
    router,
    vuetify
  })
}

describe('Tombstone component', () => {
  let wrapper: any
  const { assign } = window.location
  const accountInfo: AccountInformationIF = {
    accountType: '',
    id: 1,
    label: 'testPPR',
    type: ''
  }
  const userInfo: UserInfoIF = {
    contacts: [
      {
        created: '',
        createdBy: '',
        email: '',
        modified: '',
        phone: '',
        phoneExtension: ''
      }
    ],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: 'test',
    lastname: 'tester',
    username: '123d3crr3',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  }
  const registration: FinancingStatementIF = {
    ...mockedFinancingStatementComplete
  }
  const registrationType = mockedSelectSecurityAgreement()

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // setup data used by header
    await store.setAccountInformation(accountInfo)
    await store.setUserInfo(userInfo)
    await store.setRegistrationType(registrationType)
    await store.setRegistrationNumber(registration.baseRegistrationNumber)
    await store.setRegistrationCreationDate(registration.createDateTime)
    await store.setRegistrationExpiryDate(registration.expiryDate)
    await store.setAuthRoles([AuthRoles.PUBLIC, 'ppr'])
    await store.setUserProductSubscriptionsCodes([ProductCode.PPR])
    await nextTick()
  })

  afterEach(() => {
    router.replace('/')
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Tombstone component properly for Total Discharge', async () => {
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
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

  it('renders Tombstone component properly for Dashboard', async () => {
    wrapper = createComponent(RouteNames.DASHBOARD)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)

    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component peoperly for Search', async () => {
    wrapper = createComponent( RouteNames.SEARCH)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component peoperly for New Registration: length-trust', async () => {
    wrapper = createComponent(RouteNames.LENGTH_TRUST)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component peoperly for New Registration: parties/debtors', async () => {
    wrapper = createComponent(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component peoperly for New Registration: collateral', async () => {
    wrapper = createComponent(RouteNames.ADD_COLLATERAL)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })

  it('renders Tombstone component peoperly for New Registration: review/confirm', async () => {
    wrapper = createComponent(RouteNames.REVIEW_CONFIRM)
    await nextTick()

    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
    const extraInfo = wrapper.findAll(tombstoneInfo)
    expect(extraInfo.length).toBe(0)
  })
})
