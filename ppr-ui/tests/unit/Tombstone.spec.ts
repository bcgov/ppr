// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { Tombstone } from '@/components/common'

// Other
import { AccountInformationIF, BreadcrumbIF, UserInfoIF } from '@/interfaces'
import { tombstoneBreadcrumbSearch, tombstoneBreadcrumbRegistration } from '@/resources'
import { mockedSelectSecurityAgreement } from './test-data'
import mockRouter from './MockRouter'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const backBtn: string = '#tombstone-back-btn'
const tombstoneHeader: string = '#tombstone-header'
const tombstoneUserInfo: string = '#tombstone-user-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResult> object with the given parameters.
 */
function createComponent(backURL: string, mockRoute: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: mockRoute })

  return mount(Tombstone, {
    localVue,
    propsData: { backURL },
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
    firstname: 'test',
    lastname: 'tester',
    username: '123d3crr3',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  }

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    await store.dispatch('setAccountInformation', accountInfo)
    await store.dispatch('setUserInfo', userInfo)
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Tombstone component with breadcrumb', async () => {
    wrapper = createComponent('http://test/dashboard', 'dashboard')
    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll('.v-breadcrumbs__item')
    for (let i = 0; i < tombstoneBreadcrumbSearch.length - 1; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbSearch[i].text)
    }
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My PPR Dashboard')
    const userInfoDisplay = wrapper.findAll(tombstoneUserInfo)
    expect(userInfoDisplay.length).toBe(1)
    expect(userInfoDisplay.at(0).text()).toContain(userInfo.firstname)
    expect(userInfoDisplay.at(0).text()).toContain(userInfo.lastname)
    expect(userInfoDisplay.at(0).text()).toContain(accountInfo.label)
    expect(wrapper.find(backBtn).exists()).toBe(true)
  })

  it('renders registration Tombstone component with breadcrumb', async () => {
    wrapper = createComponent('http://test/dashboard', 'length-trust')
    expect(wrapper.findComponent(Tombstone).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll('.v-breadcrumbs__item')
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRegistration[i].text)
    }
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
  })
})
