// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { createDraft, updateDraft, saveFinancingStatementDraft } from '@/utils'

// Components
import { RegistrationLengthTrust } from '@/components/registration'

// Other
import { DraftIF, ErrorIF, LengthTrustIF } from '@/interfaces'
import {
  mockedDraftFinancingStatementAll,
  mockedNewRegStep1,
  mockedNewRegStep2,
  mockedNewRegStep3,
  mockedSelectSecurityAgreement
} from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  defaultTrustIndenture: Boolean,
  defaultLifeInfinite: Boolean,
  defaultLifeYears: String,
  defaultRegistrationType: String
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationLengthTrust, {
    localVue,
    propsData: { defaultTrustIndenture, defaultLifeInfinite, defaultLifeYears, defaultRegistrationType },
    store,
    vuetify
  })
}

describe('API save, update draft Tests', () => {
  // Any jwt will do
  // eslint-disable-next-line max-len
  const jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJwU0JwdXphMjNEeGFpZE9IZ0RjVHBnRzFwSUNDZ3J5b3RxNnJfbTZTTlgwIn0.eyJleHAiOjE2MTI1NTQ3ODMsImlhdCI6MTYxMjU1Mjk4MywianRpIjoiZWI4NGY2MWItZTE2MS00Nzg0LTliZjktNGU5MTdiYWM5MmUzIiwiaXNzIjoiaHR0cHM6Ly90ZXN0Lm9pZGMuZ292LmJjLmNhL2F1dGgvcmVhbG1zL2ZjZjBrcHFyIiwiYXVkIjpbInNiYy1hdXRoLXdlYiIsInJlYWxtLW1hbmFnZW1lbnQiLCJhY2NvdW50Il0sInN1YiI6ImVlYmY3ZTg0LTM1NWQtNDcwZS05ODI0LTJjZGQwNzg1ZjM4MyIsInR5cCI6IkJlYXJlciIsImF6cCI6InNiYy1hdXRoLXdlYiIsInNlc3Npb25fc3RhdGUiOiJiMGIzMjI0Mi1iYWI3LTQwNTgtYTk4ZC0yZWIzYzMxMzcwNmYiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vdGVzdC5iY3JlZ2lzdHJ5LmNhIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJjb2xpbiIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwic3RhZmYiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIkNQIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsicmVhbG0tbWFuYWdlbWVudCI6eyJyb2xlcyI6WyJ2aWV3LWlkZW50aXR5LXByb3ZpZGVycyIsInZpZXctcmVhbG0iLCJtYW5hZ2UtaWRlbnRpdHktcHJvdmlkZXJzIiwiaW1wZXJzb25hdGlvbiIsInJlYWxtLWFkbWluIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNlcnMiLCJ2aWV3LWNsaWVudHMiLCJtYW5hZ2UtYXV0aG9yaXphdGlvbiIsIm1hbmFnZS1jbGllbnRzIiwicXVlcnktZ3JvdXBzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkRvdWciLCJyb2xlcyI6WyJjb2xpbiIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwic3RhZmYiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIkNQIl0sIm5hbWUiOiJEb3VnIERheGlvbSIsImlkcF91c2VyaWQiOiI4MDYxODVmNy01YjQ5LTQyOTctYjdiMC05Y2I5NWIzMzBlZDgiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJiY3Jvcy9kb3VnX2RheGlvbSIsImVtYWlsIjoiZG91Z0BkYXhpb20uY29tIiwibG9naW5Tb3VyY2UiOiJCQ1JPUyIsInVzZXJuYW1lIjoiYmNyb3MvZG91Z19kYXhpb20iLCJsYXN0bmFtZSI6IkRheGlvbSJ9.a7H0iROcngFrNoA7ZYXxQMwamqFa-Xccebg1vkof1FJJW3r5Zi6OuhkdKlJ-wkyK34LT2rlg7gv7VEcO7OeuPuuB8XqNaAhMi7RotKrTui2XsPPMVmmXo_1KpZgUXEJ6jUcRs25RRoLkATpQV2vjKKQM5kV129tk3FQtaYgG5S9KLMrrM2PxIGDvRgxdkLu-D6SuXfdoFNr2rVCm3aHKqM8qKon1UbK2UqDK1jaM6QR7U5lOSX1g2BHWJA8n__RS6LhGMKCEerdY0yRd0tST9kgvDAa8R12eDdKwgoXuIaCsYnXOsEwouYuGCgNoP9PcqqQ5KD0lWtWNv82SQuI5Yw'

  // Define Session
  sessionStorage.setItem('KEYCLOAK_TOKEN', jwt)
  sessionStorage.setItem('accountId', 'PS12345')
  sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/ppr/api/v1/')
  sessionStorage.setItem('PPR_API_KEY', process.env.PPR_API_KEY)

  it('API call to save new draft', async () => {
    const draft:DraftIF = JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll))
    const apiResponse:DraftIF = await createDraft(draft)
    // console.log(JSON.stringify(apiResponse))
    expect(apiResponse.financingStatement).toBeDefined()
    expect(apiResponse.financingStatement.documentId).toBeDefined()
    expect(apiResponse.createDateTime).toBeDefined()
  })
  it('API call to update existing draft', async () => {
    const draft:DraftIF = JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll))
    draft.financingStatement.documentId = 'D0034001'
    const apiResponse:DraftIF = await updateDraft(draft)
    // console.log(JSON.stringify(apiResponse))
    expect(apiResponse.financingStatement).toBeDefined()
    expect(apiResponse.financingStatement.documentId).toBeDefined()
    expect(apiResponse.createDateTime).toBeDefined()
    expect(apiResponse.lastUpdateDateTime).toBeDefined()
  })
  it('API call to update existing draft no documentId', async () => {
    const draft:DraftIF = JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll))
    const apiResponse:DraftIF = await updateDraft(draft)
    expect(apiResponse.error).toBeDefined()
  })
  it('API call to create draft unauthorized endpoint', async () => {
    sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-dev.apigee.net/ppr/api/v1/')
    const draft:DraftIF = JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll))
    const apiResponse:DraftIF = await createDraft(draft)
    sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/ppr/api/v1/')
    expect(apiResponse.error).toBeDefined()
  })
  it('API call to update existing draft unauthorized endpoint', async () => {
    sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-dev.apigee.net/ppr/api/v1/')
    const draft:DraftIF = JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll))
    draft.financingStatement.documentId = 'D0034001'
    const apiResponse:DraftIF = await updateDraft(draft)
    sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/ppr/api/v1/')
    expect(apiResponse.error).toBeDefined()
  })
})

describe('Financing Statement registration helper save, update draft Tests', () => {
  let wrapper: Wrapper<any>
  // Any jwt will do
  // eslint-disable-next-line max-len
  const jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJwU0JwdXphMjNEeGFpZE9IZ0RjVHBnRzFwSUNDZ3J5b3RxNnJfbTZTTlgwIn0.eyJleHAiOjE2MTI1NTQ3ODMsImlhdCI6MTYxMjU1Mjk4MywianRpIjoiZWI4NGY2MWItZTE2MS00Nzg0LTliZjktNGU5MTdiYWM5MmUzIiwiaXNzIjoiaHR0cHM6Ly90ZXN0Lm9pZGMuZ292LmJjLmNhL2F1dGgvcmVhbG1zL2ZjZjBrcHFyIiwiYXVkIjpbInNiYy1hdXRoLXdlYiIsInJlYWxtLW1hbmFnZW1lbnQiLCJhY2NvdW50Il0sInN1YiI6ImVlYmY3ZTg0LTM1NWQtNDcwZS05ODI0LTJjZGQwNzg1ZjM4MyIsInR5cCI6IkJlYXJlciIsImF6cCI6InNiYy1hdXRoLXdlYiIsInNlc3Npb25fc3RhdGUiOiJiMGIzMjI0Mi1iYWI3LTQwNTgtYTk4ZC0yZWIzYzMxMzcwNmYiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vdGVzdC5iY3JlZ2lzdHJ5LmNhIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJjb2xpbiIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwic3RhZmYiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIkNQIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsicmVhbG0tbWFuYWdlbWVudCI6eyJyb2xlcyI6WyJ2aWV3LWlkZW50aXR5LXByb3ZpZGVycyIsInZpZXctcmVhbG0iLCJtYW5hZ2UtaWRlbnRpdHktcHJvdmlkZXJzIiwiaW1wZXJzb25hdGlvbiIsInJlYWxtLWFkbWluIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNlcnMiLCJ2aWV3LWNsaWVudHMiLCJtYW5hZ2UtYXV0aG9yaXphdGlvbiIsIm1hbmFnZS1jbGllbnRzIiwicXVlcnktZ3JvdXBzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkRvdWciLCJyb2xlcyI6WyJjb2xpbiIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwic3RhZmYiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIkNQIl0sIm5hbWUiOiJEb3VnIERheGlvbSIsImlkcF91c2VyaWQiOiI4MDYxODVmNy01YjQ5LTQyOTctYjdiMC05Y2I5NWIzMzBlZDgiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJiY3Jvcy9kb3VnX2RheGlvbSIsImVtYWlsIjoiZG91Z0BkYXhpb20uY29tIiwibG9naW5Tb3VyY2UiOiJCQ1JPUyIsInVzZXJuYW1lIjoiYmNyb3MvZG91Z19kYXhpb20iLCJsYXN0bmFtZSI6IkRheGlvbSJ9.a7H0iROcngFrNoA7ZYXxQMwamqFa-Xccebg1vkof1FJJW3r5Zi6OuhkdKlJ-wkyK34LT2rlg7gv7VEcO7OeuPuuB8XqNaAhMi7RotKrTui2XsPPMVmmXo_1KpZgUXEJ6jUcRs25RRoLkATpQV2vjKKQM5kV129tk3FQtaYgG5S9KLMrrM2PxIGDvRgxdkLu-D6SuXfdoFNr2rVCm3aHKqM8qKon1UbK2UqDK1jaM6QR7U5lOSX1g2BHWJA8n__RS6LhGMKCEerdY0yRd0tST9kgvDAa8R12eDdKwgoXuIaCsYnXOsEwouYuGCgNoP9PcqqQ5KD0lWtWNv82SQuI5Yw'
  const defaultTrustIndenture: Boolean = Boolean(false)
  const defaultLifeInfinite: Boolean = Boolean(false)
  const defaultLifeYears: String = String('')
  const defaultRegistrationType: String = String('SA')

  // Define Session
  sessionStorage.setItem('KEYCLOAK_TOKEN', jwt)
  sessionStorage.setItem('accountId', 'PS12345')
  sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/ppr/api/v1/')
  sessionStorage.setItem('PPR_API_KEY', process.env.PPR_API_KEY)

  beforeEach(async () => {
    // reset the store data
    await store.dispatch('resetNewRegistration')
    const resetDraft:DraftIF = {
      type: '',
      financingStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    }
    await store.dispatch('setDraft', resetDraft)
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
    wrapper = createComponent(defaultTrustIndenture, defaultLifeInfinite, defaultLifeYears, defaultRegistrationType)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('Save new draft step 1', async () => {
    await wrapper.vm.$store.dispatch('setLengthTrust', mockedNewRegStep1)
    // const step1Model:LengthTrustIF = wrapper.vm.$store.state.stateModel.lengthTrustStep
    // console.log('step1 model:' + JSON.stringify(step1Model))
    const savedDraft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    expect(savedDraft).toBeDefined()
    expect(savedDraft.error).toBeUndefined()
    expect(savedDraft.financingStatement.documentId).toBeDefined()
    expect(savedDraft.createDateTime).toBeDefined()
  })
  it('Save new draft step 2', async () => {
    await wrapper.vm.$store.dispatch('setAddSecuredPartiesAndDebtors', mockedNewRegStep2)
    const savedDraft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    expect(savedDraft).toBeDefined()
    expect(savedDraft.error).toBeUndefined()
    expect(savedDraft.financingStatement.documentId).toBeDefined()
    expect(savedDraft.createDateTime).toBeDefined()
  })
  it('Save new draft step 3', async () => {
    await wrapper.vm.$store.dispatch('setAddCollateral', mockedNewRegStep3)
    const savedDraft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    expect(savedDraft).toBeDefined()
    expect(savedDraft.error).toBeUndefined()
    expect(savedDraft.financingStatement.documentId).toBeDefined()
    expect(savedDraft.createDateTime).toBeDefined()
  })
  it('Save new draft step 4', async () => {
    await wrapper.vm.$store.dispatch('setLengthTrust', mockedNewRegStep1)
    await wrapper.vm.$store.dispatch('setAddSecuredPartiesAndDebtors', mockedNewRegStep2)
    await wrapper.vm.$store.dispatch('setAddCollateral', mockedNewRegStep3)
    const savedDraft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    expect(savedDraft).toBeDefined()
    expect(savedDraft.error).toBeUndefined()
    expect(savedDraft.financingStatement.documentId).toBeDefined()
    expect(savedDraft.createDateTime).toBeDefined()
  })
  it('Save updated draft', async () => {
    await wrapper.vm.$store.dispatch('setLengthTrust', mockedNewRegStep1)
    await wrapper.vm.$store.dispatch('setAddSecuredPartiesAndDebtors', mockedNewRegStep2)
    var savedDraft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    expect(savedDraft).toBeDefined()
    expect(savedDraft.error).toBeUndefined()
    await wrapper.vm.$store.dispatch('setAddCollateral', mockedNewRegStep3)
    savedDraft.financingStatement.documentId = 'D0034001' // works with mock api service
    await wrapper.vm.$store.dispatch('setDraft', savedDraft)
    savedDraft = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    expect(savedDraft.financingStatement.documentId).toBeDefined()
    expect(savedDraft.lastUpdateDateTime).toBeDefined()
  })
})
