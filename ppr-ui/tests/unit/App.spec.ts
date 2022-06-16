// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import flushPromises from 'flush-promises'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import sinon from 'sinon'
import { StatusCodes } from 'http-status-codes'

// Components
import App from '@/App.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import { Tombstone } from '@/components/tombstone'
import { Breadcrumb } from '@/components/common'

// Other
import { axios } from '@/utils/axios-auth'
import { axios as axiosPay } from '@/utils/axios-pay'
import { axios as axiosPPR } from '@/utils/axios-ppr'
import mockRouter from './MockRouter'
import { mockedDisableAllUserSettingsResponse, mockedProductSubscriptions } from './test-data'
import { FeeCodes } from '@/composables/fees/enums'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { AccountProductCodes, AccountProductMemberships } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('App component basic rendering normal account', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  const currentAccount = { id: 'test_id' }
  const authUrl = 'myhost/basePath/auth/'
  sessionStorage.setItem(SessionStorageKeys.AuthWebUrl, authUrl)
  // dev token (need a real token to parse - expired is okay)
  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2NDQ1MzYxMzEsImlhdCI6MTY0NDUxODEzMSwiYXV0aF90aW1lIjoxNjQ0NTE2NTM0LCJqdGkiOiIxZjc5OTkyOC05ODQwLTRlNzktYTEwZS1jMmI5ZTJjZTE3ZWQiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiI3NWMzMzE5Ni0zOTk3LTRkOTctODBlNi01ZGQyYWE1YmU5N2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwibm9uY2UiOiIwNDRjYzAyOC01NTZmLTRmNDgtYWM0NS1jNzU5OGEwMWQ0YTgiLCJzZXNzaW9uX3N0YXRlIjoiOGFiNjZmMDktZWQyYi00ZGQ4LWE1YmYtM2NjYWI2MThlMzVhIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJwdWJsaWNfdXNlciIsInBwciIsImVkaXQiLCJhY2NvdW50X2hvbGRlciIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkJDUkVHMiBTdmV0bGFuYSIsInJvbGVzIjpbInB1YmxpY191c2VyIiwicHByIiwiZWRpdCIsImFjY291bnRfaG9sZGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiQkNSRUcyIFN2ZXRsYW5hIEZPVVJURUVOIiwiaWRwX3VzZXJpZCI6IkhERjNEWVFFUUhQVU1VT01QUUMyQkFGSVJETFZPV0s2IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYmNzYy9oZGYzZHlxZXFocHVtdW9tcHFjMmJhZmlyZGx2b3drNiIsImxvZ2luU291cmNlIjoiQkNTQyIsImxhc3RuYW1lIjoiRk9VUlRFRU4iLCJ1c2VybmFtZSI6ImJjc2MvaGRmM2R5cWVxaHB1bXVvbXBxYzJiYWZpcmRsdm93azYifQ.UUamIDN1LWms2oK5YG9yEmfen6ISFoY9AGw7ZJrsmDiElt0XwI_lj6DPYdMieXgXQ4Ji7jRVSMNhX4LfxpC1JipepUbI3kBLf0lelTudhZyD9MOg-VYaLAAEwAY57Z8h7EOCQp0PLS8NAMwNs90t4sJ449uZ3HprEMfMvkaZ0X3Cv495U0m5Qr-GDT7PHeLqkh3297gvxx3PdIGZIWcIwz-lFo8jNYxpEtY1LivZXnCsfrLDEW-vVK5kmnB1boIJksiUq8ATjF6F26B7ytBhE89SvolmA5nMkLiB-yusbSMY0ccxRWpPmX4MJ2yKuM6Sr6L6Dxrw_FWBHU1ThnnxUw') // eslint-disable-line max-len
  sessionStorage.setItem(SessionStorageKeys.AuthApiUrl, 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
  sessionStorage.setItem(SessionStorageKeys.CurrentAccount, JSON.stringify(currentAccount))

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    sandbox = sinon.createSandbox()

    const get = sandbox.stub(axios, 'get')
    const getSettings = sandbox.stub(axiosPPR, 'get')
    const getFees = sandbox.stub(axiosPay, 'get')
    const getProducts = get.withArgs(`orgs/${currentAccount.id}/products`)
    const getAuthorizations = get.withArgs(`accounts/${currentAccount.id}/products/${AccountProductCodes.RPPR}/authorizations`)

    getProducts.returns(new Promise(resolve => resolve({ data: mockedProductSubscriptions.ALL })))
    getAuthorizations.returns(new Promise(resolve => resolve({ data: {
      membership: AccountProductMemberships.MEMBER,
      roles: ['search']
    } })))

    // GET current user
    get.withArgs('users/@me').returns(new Promise((resolve) => resolve(
      {
        data:
        {
          contacts: [],
          firstname: 'first',
          lastname: 'last',
          username: 'username'
        },
        status: StatusCodes.OK
      })))

    getSettings.withArgs('user-profile').returns(new Promise((resolve) => resolve({
      data: mockedDisableAllUserSettingsResponse, status: StatusCodes.OK
    })))

    getFees.withArgs(`fees/PPR/${FeeCodes.SEARCH}`).returns(new Promise((resolve) => resolve({
      data: { filingFees: 7, serviceFees: 1.5 }, status: StatusCodes.OK
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    router.push({ name: 'dashboard' })
    wrapper = shallowMount(App, { localVue, store, router, vuetify, stubs: { Affix: true } })

    // wait for all queries to complete
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders the sub-components properly', async () => {
    expect(wrapper.findComponent(App).exists()).toBe(true)
    expect(wrapper.findComponent(SbcHeader).exists()).toBe(true)
    expect(wrapper.findComponent(SbcFooter).exists()).toBe(true)
    expect(wrapper.findComponent(Tombstone).exists()).toBe(false)
    expect(wrapper.findComponent(Breadcrumb).exists()).toBe(false)
  })

  it('gets auth and user info/settings properly', async () => {
    expect(wrapper.vm.$store.state.stateModel.authorization.authRoles).toContain('ppr')
    await Vue.nextTick()
    expect(wrapper.vm.$store.state.stateModel.userInfo).not.toBeNull()
    expect(wrapper.vm.$store.state.stateModel.userInfo.firstname).toBe('first')
    expect(wrapper.vm.$store.state.stateModel.userInfo.lastname).toBe('last')
    expect(wrapper.vm.$store.state.stateModel.userInfo.username).toBe('username')
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings.selectConfirmationDialog).toBe(false)
    expect(wrapper.vm.$store.state.stateModel.userInfo.feeSettings).toBeNull()
    // verify no redirection
    expect(window.location.assign).not.toHaveBeenCalled()
  })
})

describe('App component basic rendering non billable account', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  const currentAccount = { id: 'test_id' }
  const authUrl = 'myhost/basePath/auth/'
  sessionStorage.setItem('AUTH_WEB_URL', authUrl)
  // dev token (need a real token to parse - expired is okay)
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2NDQ1MzYxMzEsImlhdCI6MTY0NDUxODEzMSwiYXV0aF90aW1lIjoxNjQ0NTE2NTM0LCJqdGkiOiIxZjc5OTkyOC05ODQwLTRlNzktYTEwZS1jMmI5ZTJjZTE3ZWQiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiI3NWMzMzE5Ni0zOTk3LTRkOTctODBlNi01ZGQyYWE1YmU5N2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwibm9uY2UiOiIwNDRjYzAyOC01NTZmLTRmNDgtYWM0NS1jNzU5OGEwMWQ0YTgiLCJzZXNzaW9uX3N0YXRlIjoiOGFiNjZmMDktZWQyYi00ZGQ4LWE1YmYtM2NjYWI2MThlMzVhIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJwdWJsaWNfdXNlciIsInBwciIsImVkaXQiLCJhY2NvdW50X2hvbGRlciIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkJDUkVHMiBTdmV0bGFuYSIsInJvbGVzIjpbInB1YmxpY191c2VyIiwicHByIiwiZWRpdCIsImFjY291bnRfaG9sZGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiQkNSRUcyIFN2ZXRsYW5hIEZPVVJURUVOIiwiaWRwX3VzZXJpZCI6IkhERjNEWVFFUUhQVU1VT01QUUMyQkFGSVJETFZPV0s2IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYmNzYy9oZGYzZHlxZXFocHVtdW9tcHFjMmJhZmlyZGx2b3drNiIsImxvZ2luU291cmNlIjoiQkNTQyIsImxhc3RuYW1lIjoiRk9VUlRFRU4iLCJ1c2VybmFtZSI6ImJjc2MvaGRmM2R5cWVxaHB1bXVvbXBxYzJiYWZpcmRsdm93azYifQ.UUamIDN1LWms2oK5YG9yEmfen6ISFoY9AGw7ZJrsmDiElt0XwI_lj6DPYdMieXgXQ4Ji7jRVSMNhX4LfxpC1JipepUbI3kBLf0lelTudhZyD9MOg-VYaLAAEwAY57Z8h7EOCQp0PLS8NAMwNs90t4sJ449uZ3HprEMfMvkaZ0X3Cv495U0m5Qr-GDT7PHeLqkh3297gvxx3PdIGZIWcIwz-lFo8jNYxpEtY1LivZXnCsfrLDEW-vVK5kmnB1boIJksiUq8ATjF6F26B7ytBhE89SvolmA5nMkLiB-yusbSMY0ccxRWpPmX4MJ2yKuM6Sr6L6Dxrw_FWBHU1ThnnxUw') // eslint-disable-line max-len
  sessionStorage.setItem(SessionStorageKeys.CurrentAccount, JSON.stringify(currentAccount))

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    sandbox = sinon.createSandbox()

    const get = sandbox.stub(axios, 'get')
    const getSettings = sandbox.stub(axiosPPR, 'get')
    const getFees = sandbox.stub(axiosPay, 'get')
    const getProducts = get.withArgs(`orgs/${currentAccount.id}/products`)
    const getAuthorizations = get.withArgs(`accounts/${currentAccount.id}/products/${AccountProductCodes.RPPR}/authorizations`)

    getProducts.returns(new Promise(resolve => resolve({ data: mockedProductSubscriptions.ALL })))
    getAuthorizations.returns(new Promise(resolve => resolve({ data: {
      membership: AccountProductMemberships.MEMBER,
      roles: ['search']
    } })))
    
    // GET current user
    get.withArgs('users/@me').returns(new Promise((resolve) => resolve(
      {
        data:
        {
          contacts: [],
          firstname: 'first',
          lastname: 'last',
          username: 'username'
        },
        status: StatusCodes.OK
      })))

    getSettings.withArgs('user-profile').returns(new Promise((resolve) => resolve({
      data: mockedDisableAllUserSettingsResponse, status: StatusCodes.OK
    })))

    getFees.withArgs(`fees/PPR/${FeeCodes.SEARCH}`).returns(new Promise((resolve) => resolve({
      data: { filingFees: 0, serviceFees: 1 }, status: StatusCodes.OK
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    router.push({ name: 'dashboard' })
    wrapper = shallowMount(App, { localVue, store, router, vuetify, stubs: { Affix: true } })

    // wait for all queries to complete
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('fee settings are set to expected values', async () => {
    expect(wrapper.vm.$store.state.stateModel.userInfo.feeSettings.isNonBillable).toBe(true)
    expect(wrapper.vm.$store.state.stateModel.userInfo.feeSettings.serviceFee).toBe(1)
  })
})
