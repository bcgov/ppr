// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import flushPromises from 'flush-promises'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import { axios } from '@/utils/axios-auth'
import sinon from 'sinon'

// Components
import App from '@/App.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'

// Other
import mockRouter from './MockRouter'
import { Dashboard } from '@/views'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('App component', () => {
  let wrapper: any
  const { assign } = window.location
  const authUrl = 'myhost/basePath/auth/'
  sessionStorage.setItem('AUTH_URL', authUrl)
  // dev token (need a real token to parse - expired is okay)
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2MTI5MjM1MTEsImlhdCI6MTYxMjkwNTUxMSwiYXV0aF90aW1lIjoxNjEyODk4NDEwLCJqdGkiOiI0YzkyZmE1NC1jNDdkLTQ0MGQtYTU2ZC05ZjY4YmRhNmM3NTgiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJjb21tb24tc2VydmljZXMiLCJuYW1lLXJlcXVlc3RzLXdlYiIsImVudGl0eS1zZXJ2aWNlcyIsInNiYy1hdXRoLXdlYiIsImFjY291bnQtc2VydmljZXMiLCJhY2NvdW50Il0sInN1YiI6IjA5M2Q4M2RkLTY5NTYtNDVjYS04ODlmLTE3ZTNiMWJiZTY2YyIsInR5cCI6IkJlYXJlciIsImF6cCI6ImFjY291bnQtd2ViIiwibm9uY2UiOiI1NjhmMjY3NC04MTVmLTQ2MGEtOWMyOS05OGRkYmE2N2M5YjUiLCJzZXNzaW9uX3N0YXRlIjoiZjQyMDg0ZmQtMzcxZi00ZTY3LTk2NGUtYTJmYWZhZGY2Zjg1IiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwOi8vbG9jYWxob3N0OjgwODAiLCJodHRwczovL2Rldi5iY3JlZ2lzdHJ5LmNhIiwiaHR0cDovL2xvY2FsaG9zdDo4MDgyIiwiaHR0cDovL2xvY2FsaG9zdDo4MDgxIiwiKiIsImh0dHA6Ly9sb2NhbGhvc3Q6NDIwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsicHVibGljX3VzZXIiLCJlZGl0IiwiYWNjb3VudF9ob2xkZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQiLCJhY2NvdW50SWQiOiIxMjM0IiwiZmlyc3RuYW1lIjoiQkNSRUdURVNUIERhbGlhIiwicm9sZXMiOlsicHVibGljX3VzZXIiLCJlZGl0IiwiYWNjb3VudF9ob2xkZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl0sIm5hbWUiOiJCQ1JFR1RFU1QgRGFsaWEgT05FIiwiaWRwX3VzZXJpZCI6IkJIR1Y1MjVDQUFPNlVKSlZRVkM3UlFIUzJFRUEyT0QzIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYmNzYy9iaGd2NTI1Y2FhbzZ1amp2cXZjN3JxaHMyZWVhMm9kMyIsImxvZ2luU291cmNlIjoiQkNTQyIsInVzZXJuYW1lIjoiYmNzYy9iaGd2NTI1Y2FhbzZ1amp2cXZjN3JxaHMyZWVhMm9kMyIsImxhc3RuYW1lIjoiT05FIn0.LD72JvfJGabcFqispDZwk6-TEWVLCc7yHhl_xOEfww_FM2j_N26lZEIK0ix08SgBSxDiNil-ZyHglK0SYluKJUB0wb4lJvJwg7Q1_RWY7gq_thb7s5QWUn0djSGt5d3-EupGz1xrNz663nlcbAZKr8vWyHUmUXcu55mDmw3CSPFeTbkN5ijfqMTfEH5AMqqo-x32nbFBEK0BSY4MgJeCqPpBZMgCSBV0iTAxDGeQdYN22No9XM36IvdClheWgFhU-b-bcTihgecfzndT0HzKqNSCUpiVi5srR_u_Y3F7F2h0E9Bi6SSFeDNYtYy_b7A8h-oG9OJo4BAhC1exkVzqBA') // eslint-disable-line max-len

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    const get = sinon.stub(axios, 'get')

    // GET current user
    get.withArgs('users/@me')
      .returns(new Promise((resolve) => resolve({
        data:
        {
          email: 'test@example.com'
        }
      })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    wrapper = shallowMount(App, { localVue, store, router, vuetify, stubs: { Affix: true } })

    // wait for all queries to complete
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sinon.restore()
    wrapper.destroy()
  })

  it('renders the sub-components properly', () => {
    expect(wrapper.findComponent(App).exists()).toBe(true)
    expect(wrapper.findComponent(SbcHeader).exists()).toBe(true)
    expect(wrapper.findComponent(SbcFooter).exists()).toBe(true)
  })

  it('gets auth and user info properly', () => {
    expect(store.state.stateModel.tombstone.userInfo).not.toBeNull()
    expect(store.state.stateModel.tombstone.userInfo.email).toBe('test@example.com')
    // verify no redirection
    expect(window.location.assign).not.toHaveBeenCalled()
  })
})
