// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { getVuexStore } from '@/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedAmendmentCertified,
  mockedRegisteringParty1
} from './test-data'

// Components
import { CertifyInformation } from '@/components/common'
import { CertifyIF } from '@/interfaces'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()
const certifyInitial: CertifyIF = {
  valid: false,
  certified: false,
  legalName: '',
  registeringParty: mockedRegisteringParty1
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  showErrors: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(CertifyInformation, {
    localVue,
    propsData: { setShowErrors: showErrors },
    store,
    vuetify
  })
}

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Certify Information on the confirmation page', () => {
  let wrapper: any

  beforeEach(async () => {
    const currentAccount = {
      id: '123456'
    }
    sessionStorage.setItem(SessionStorageKeys.CurrentAccount, JSON.stringify(currentAccount))
    // eslint-disable-next-line max-len
    sessionStorage.setItem(SessionStorageKeys.AuthApiUrl, 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
    // eslint-disable-next-line max-len
    sessionStorage.setItem(SessionStorageKeys.KeyCloakIdToken, 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2MzU0Nzg5NDAsImlhdCI6MTYzNTQ2MDk0MCwiYXV0aF90aW1lIjoxNjM1NDM5ODE5LCJqdGkiOiIyMjQzZjBkMC1hMTFlLTRkMzYtYjI0NC04OWNmNGExNDZmNDUiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiJmZDM2MjYwMC1kMTM5LTQyMTUtYTQwNy1mZWQ4NTljNmQwOTMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwibm9uY2UiOiJlYjY2NDhkNS0wNDI2LTQwNmItOGFlMy00MDFjNDY2OWE1N2EiLCJzZXNzaW9uX3N0YXRlIjoiNzQzY2RhMTYtY2FmNi00Yzc5LTg2OWEtNzk0Y2Y5OTI4MTQzIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJwdWJsaWNfdXNlciIsInBwciIsImVkaXQiLCJhY2NvdW50X2hvbGRlciIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkJDUkVHMiBEZWxsYSIsInJvbGVzIjpbInB1YmxpY191c2VyIiwicHByIiwiZWRpdCIsImFjY291bnRfaG9sZGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ0ZXN0ZXIiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiQkNSRUcyIERlbGxhIEZPUlRZVEhSRUUiLCJpZHBfdXNlcmlkIjoiTFZZVzRDQlVNT1JSNjZLN0YyVVEySTNNWkNRUk00QVYiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJiY3NjL2x2eXc0Y2J1bW9ycjY2azdmMnVxMmkzbXpjcXJtNGF2IiwibG9naW5Tb3VyY2UiOiJCQ1NDIiwibGFzdG5hbWUiOiJGT1JUWVRIUkVFIiwidXNlcm5hbWUiOiJiY3NjL2x2eXc0Y2J1bW9ycjY2azdmMnVxMmkzbXpjcXJtNGF2In0.RHuBGt9k6ViMrA6iN8U3A_fyAGm7EwltUciWN6P1QywCnPIXKuAzGGNzCNapi2ZiPTIZ3mUlWGUlGw-qRNK3jwRQjQUFx-uZMN4myNcoWN7i1R45wUrT-NhCY8q0DLdSlhwMG3muf2XcYc3OHcjognepRGU5CH8yekVm2ZgJVHoiLGszl1HgQQKVR1_idJ8cK1FoTD5iWqfwZOvKmd3fNvTu_ARxeCd0obm_8xhtp6EKnDpSUHHo67s-OJ5UOEA6VPBrmWWitxDOXplxZBiuUjDm9hXO4CAPD9oKRaEledlIvCO75jKH8AAtCDHetsNklau2ICCO60yYpzWmO8hhiA')

    await store.dispatch('setCertifyInformation', certifyInitial)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the view with checkbox', () => {
    wrapper = createComponent(false)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.find('#checkbox-certified').exists()).toBe(true)
  })

  it('renders the certify information valid data from the store', async () => {
    await store.dispatch('setCertifyInformation', mockedAmendmentCertified)
    wrapper = createComponent(false)
    const certifyInfo:CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toEqual(mockedAmendmentCertified.legalName)
    expect(certifyInfo.certified).toBeTruthy()
    expect(certifyInfo.registeringParty).toBeDefined()
    expect(certifyInfo.registeringParty.businessName).toBeDefined()
    expect(certifyInfo.registeringParty.address).toBeDefined()
    expect(certifyInfo.valid).toBeTruthy()
    expect(wrapper.vm.legalName).toEqual(mockedAmendmentCertified.legalName)
    expect(wrapper.vm.valid).toBeTruthy()
    expect(wrapper.vm.showErrors).toBeFalsy()
    expect(wrapper.vm.showErrorComponent).toBeFalsy()
    expect(wrapper.vm.registeringParty[0]).toBeDefined()
    expect(wrapper.vm.registeringParty[0].businessName).toBeDefined()
    expect(wrapper.vm.registeringParty[0].address).toBeDefined()
    expect(wrapper.vm.infoText.length).toBeGreaterThan(10)
  })

  it('renders the certify information invalid state data from the store', async () => {
    wrapper = createComponent(true)
    const certifyInfo:CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toBeDefined()
    expect(certifyInfo.certified).toBeFalsy()
    expect(certifyInfo.valid).toBeFalsy()
    expect(wrapper.vm.legalName).toBeDefined()
    expect(wrapper.vm.certified).toBeFalsy()
    expect(wrapper.find('#checkbox-certified').element.value).toBeFalsy()
    expect(wrapper.vm.valid).toBeFalsy()
    expect(wrapper.vm.showErrors).toBeTruthy()
    expect(wrapper.vm.showErrorComponent).toBeTruthy()
    expect(wrapper.vm.registeringParty).toBeDefined()
  })

  it('renders the certify information transition from initial to valid state', async () => {
    wrapper = createComponent(true)
    wrapper.find('#checkbox-certified').trigger('click')
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.valid).toBeTruthy()
    expect(wrapper.emitted().certifyValid).toBeTruthy()
    expect(wrapper.vm.showErrorComponent).toBeFalsy()
  })
})


describe('Certify Information for staff', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.dispatch('setAuthRoles', ['staff', 'gov_account_user'])
    // eslint-disable-next-line max-len
    sessionStorage.setItem(SessionStorageKeys.KeyCloakIdToken, 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2MzU0Nzg5NDAsImlhdCI6MTYzNTQ2MDk0MCwiYXV0aF90aW1lIjoxNjM1NDM5ODE5LCJqdGkiOiIyMjQzZjBkMC1hMTFlLTRkMzYtYjI0NC04OWNmNGExNDZmNDUiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiJmZDM2MjYwMC1kMTM5LTQyMTUtYTQwNy1mZWQ4NTljNmQwOTMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwibm9uY2UiOiJlYjY2NDhkNS0wNDI2LTQwNmItOGFlMy00MDFjNDY2OWE1N2EiLCJzZXNzaW9uX3N0YXRlIjoiNzQzY2RhMTYtY2FmNi00Yzc5LTg2OWEtNzk0Y2Y5OTI4MTQzIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJwdWJsaWNfdXNlciIsInBwciIsImVkaXQiLCJhY2NvdW50X2hvbGRlciIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkJDUkVHMiBEZWxsYSIsInJvbGVzIjpbInB1YmxpY191c2VyIiwicHByIiwiZWRpdCIsImFjY291bnRfaG9sZGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ0ZXN0ZXIiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiQkNSRUcyIERlbGxhIEZPUlRZVEhSRUUiLCJpZHBfdXNlcmlkIjoiTFZZVzRDQlVNT1JSNjZLN0YyVVEySTNNWkNRUk00QVYiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJiY3NjL2x2eXc0Y2J1bW9ycjY2azdmMnVxMmkzbXpjcXJtNGF2IiwibG9naW5Tb3VyY2UiOiJCQ1NDIiwibGFzdG5hbWUiOiJGT1JUWVRIUkVFIiwidXNlcm5hbWUiOiJiY3NjL2x2eXc0Y2J1bW9ycjY2azdmMnVxMmkzbXpjcXJtNGF2In0.RHuBGt9k6ViMrA6iN8U3A_fyAGm7EwltUciWN6P1QywCnPIXKuAzGGNzCNapi2ZiPTIZ3mUlWGUlGw-qRNK3jwRQjQUFx-uZMN4myNcoWN7i1R45wUrT-NhCY8q0DLdSlhwMG3muf2XcYc3OHcjognepRGU5CH8yekVm2ZgJVHoiLGszl1HgQQKVR1_idJ8cK1FoTD5iWqfwZOvKmd3fNvTu_ARxeCd0obm_8xhtp6EKnDpSUHHo67s-OJ5UOEA6VPBrmWWitxDOXplxZBiuUjDm9hXO4CAPD9oKRaEledlIvCO75jKH8AAtCDHetsNklau2ICCO60yYpzWmO8hhiA')


    await store.dispatch('setCertifyInformation', certifyInitial)
  })

  afterEach(() => {
    wrapper.destroy()
  })


  it('renders the certify information for staff', async () => {
    await store.dispatch('setCertifyInformation', mockedAmendmentCertified)
    wrapper = createComponent(false)
    const certifyInfo:CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toEqual(mockedAmendmentCertified.legalName)
    expect(certifyInfo.certified).toBeTruthy()
    expect(certifyInfo.registeringParty).toBeDefined()
    expect(certifyInfo.registeringParty.businessName).toBe('SBC Staff')
    expect(certifyInfo.registeringParty.address).toBeFalsy()
    expect(wrapper.vm.legalName).toEqual(mockedAmendmentCertified.legalName)

  })


})
