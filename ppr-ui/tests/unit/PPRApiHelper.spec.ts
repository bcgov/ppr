/* eslint-disable max-len */
// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'
// import { PPRApiHelper } from '@/store/actions'
import { PPRApiHelper } from '@/store/actions'
import { SearchCriteriaIF, SearchResponseIF, SearchResultIF } from '@/interfaces'

// Components
import { Dashboard } from '@/views'

// Other
import mockRouter from './MockRouter'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('PPR API Helper Tests', () => {
  // Verify JWT disabled in gateway mock environment.
  const jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJwU0JwdXphMjNEeGFpZE9IZ0RjVHBnRzFwSUNDZ3J5b3RxNnJfbTZTTlgwIn0.eyJleHAiOjE2MTI1NTQ3ODMsImlhdCI6MTYxMjU1Mjk4MywianRpIjoiZWI4NGY2MWItZTE2MS00Nzg0LTliZjktNGU5MTdiYWM5MmUzIiwiaXNzIjoiaHR0cHM6Ly90ZXN0Lm9pZGMuZ292LmJjLmNhL2F1dGgvcmVhbG1zL2ZjZjBrcHFyIiwiYXVkIjpbInNiYy1hdXRoLXdlYiIsInJlYWxtLW1hbmFnZW1lbnQiLCJhY2NvdW50Il0sInN1YiI6ImVlYmY3ZTg0LTM1NWQtNDcwZS05ODI0LTJjZGQwNzg1ZjM4MyIsInR5cCI6IkJlYXJlciIsImF6cCI6InNiYy1hdXRoLXdlYiIsInNlc3Npb25fc3RhdGUiOiJiMGIzMjI0Mi1iYWI3LTQwNTgtYTk4ZC0yZWIzYzMxMzcwNmYiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vdGVzdC5iY3JlZ2lzdHJ5LmNhIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJjb2xpbiIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwic3RhZmYiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIkNQIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsicmVhbG0tbWFuYWdlbWVudCI6eyJyb2xlcyI6WyJ2aWV3LWlkZW50aXR5LXByb3ZpZGVycyIsInZpZXctcmVhbG0iLCJtYW5hZ2UtaWRlbnRpdHktcHJvdmlkZXJzIiwiaW1wZXJzb25hdGlvbiIsInJlYWxtLWFkbWluIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNlcnMiLCJ2aWV3LWNsaWVudHMiLCJtYW5hZ2UtYXV0aG9yaXphdGlvbiIsIm1hbmFnZS1jbGllbnRzIiwicXVlcnktZ3JvdXBzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkRvdWciLCJyb2xlcyI6WyJjb2xpbiIsIm9mZmxpbmVfYWNjZXNzIiwidGVzdGVyIiwic3RhZmYiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIkNQIl0sIm5hbWUiOiJEb3VnIERheGlvbSIsImlkcF91c2VyaWQiOiI4MDYxODVmNy01YjQ5LTQyOTctYjdiMC05Y2I5NWIzMzBlZDgiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJiY3Jvcy9kb3VnX2RheGlvbSIsImVtYWlsIjoiZG91Z0BkYXhpb20uY29tIiwibG9naW5Tb3VyY2UiOiJCQ1JPUyIsInVzZXJuYW1lIjoiYmNyb3MvZG91Z19kYXhpb20iLCJsYXN0bmFtZSI6IkRheGlvbSJ9.a7H0iROcngFrNoA7ZYXxQMwamqFa-Xccebg1vkof1FJJW3r5Zi6OuhkdKlJ-wkyK34LT2rlg7gv7VEcO7OeuPuuB8XqNaAhMi7RotKrTui2XsPPMVmmXo_1KpZgUXEJ6jUcRs25RRoLkATpQV2vjKKQM5kV129tk3FQtaYgG5S9KLMrrM2PxIGDvRgxdkLu-D6SuXfdoFNr2rVCm3aHKqM8qKon1UbK2UqDK1jaM6QR7U5lOSX1g2BHWJA8n__RS6LhGMKCEerdY0yRd0tST9kgvDAa8R12eDdKwgoXuIaCsYnXOsEwouYuGCgNoP9PcqqQ5KD0lWtWNv82SQuI5Yw'

  // Define Session
  sessionStorage.setItem('KEYCLOAK_TOKEN', jwt)
  sessionStorage.setItem('accountId', 'PS12345')
  // Use mock service for api client configuration testing: expired JWT will work.
  sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/ppr/api/v1/')
  sessionStorage.setItem('PPR_API_KEY', process.env.PPR_API_KEY)

  it('Valid serial number search', async () => {
    const criteria:SearchCriteriaIF = {
      type: 'SERIAL_NUMBER',
      criteria: {
        value: 'JU622994'
      }
    }
    const pprApiHelper = new PPRApiHelper()
    const searchResponse:SearchResponseIF = await pprApiHelper.search(criteria)
    // console.log(JSON.stringify(searchResponse))
    expect(searchResponse.searchId).toBeDefined()
    expect(searchResponse.searchDateTime).toBeDefined()
    expect(searchResponse.searchQuery).toBeDefined()
    expect(searchResponse.results).toBeDefined()
    expect(searchResponse.maxResultsSize).toBe(1000)
    expect(searchResponse.totalResultsSize).toBeGreaterThanOrEqual(1)
    expect(searchResponse.returnedResultsSize).toBeGreaterThanOrEqual(1)
    const result:SearchResultIF = searchResponse.results[0]
    expect(result.baseRegistrationNumber).toBeDefined()
    expect(result.matchType).toBeDefined()
    expect(result.registrationType).toBeDefined()
    expect(result.createDateTime).toBeDefined()
  })
})
