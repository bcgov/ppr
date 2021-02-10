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
  // Need to generate manually from dev keycloak
  const jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2MTI5OTE4MjMsImlhdCI6MTYxMjk3MzgyMywianRpIjoiMWJmYWE2MjUtMmVlMS00ZjU4LTlkZmEtZTc5ZWIwMzZlNDEzIiwiaXNzIjoiaHR0cHM6Ly9kZXYub2lkYy5nb3YuYmMuY2EvYXV0aC9yZWFsbXMvZmNmMGtwcXIiLCJhdWQiOlsic2JjLWF1dGgtd2ViIiwiYWNjb3VudC1zZXJ2aWNlcyIsImVudGl0eS1zZXJ2aWNlcyIsInJlYWxtLW1hbmFnZW1lbnQiLCJhY2NvdW50Il0sInN1YiI6IjAwZWZlMTYzLTQ5NjAtNGNlZC1hNWMyLTE3NzNlZDRhMzI0OSIsInR5cCI6IkJlYXJlciIsImF6cCI6InNiYy1hdXRoLXdlYiIsInNlc3Npb25fc3RhdGUiOiI0MGEwODhhZS1mNjcyLTRmNTUtYTMwYi1kZTZlNGUzNjQwMDkiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly8xOTIuMTY4LjAuMTM6ODA4MC8iLCJodHRwOi8vbG9jYWxob3N0OjgwODAvKiIsImh0dHBzOi8vZmF6YW4uaGx0aC5nb3YuYmMuY2E6NzUyMC8qIiwiMTkyLjE2OC4wLjEzIiwiaHR0cDovL2xvY2FsaG9zdDo0MjAwLyoiLCJodHRwczovL2J1c2luZXNzLWNyZWF0ZS10ZXN0LnBhdGhmaW5kZXIuZ292LmJjLmNhLyoiLCIqIiwiaHR0cDovLzE5Mi4xNjguMC4xMzo4MDgwIiwiaHR0cHM6Ly9kZXYudnMuZ292LmJjLmNhLyoiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImNvbGluIiwib2ZmbGluZV9hY2Nlc3MiLCJ0ZXN0ZXIiLCJzdGFmZiIsInVtYV9hdXRob3JpemF0aW9uIiwiQ1AiXX0sInJlc291cmNlX2FjY2VzcyI6eyJyZWFsbS1tYW5hZ2VtZW50Ijp7InJvbGVzIjpbInZpZXctaWRlbnRpdHktcHJvdmlkZXJzIiwidmlldy1yZWFsbSIsImNyZWF0ZS1jbGllbnQiLCJtYW5hZ2UtdXNlcnMiLCJxdWVyeS1yZWFsbXMiLCJ2aWV3LWF1dGhvcml6YXRpb24iLCJxdWVyeS1jbGllbnRzIiwicXVlcnktdXNlcnMiLCJ2aWV3LXVzZXJzIiwidmlldy1jbGllbnRzIiwibWFuYWdlLWF1dGhvcml6YXRpb24iLCJtYW5hZ2UtY2xpZW50cyIsInF1ZXJ5LWdyb3VwcyJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQiLCJmaXJzdG5hbWUiOiJEb3VnIiwicm9sZXMiOlsiY29saW4iLCJvZmZsaW5lX2FjY2VzcyIsInRlc3RlciIsInN0YWZmIiwidW1hX2F1dGhvcml6YXRpb24iLCJDUCJdLCJuYW1lIjoiRG91ZyBMb3ZldHQiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJkb3VnLWxvdmV0dCIsInByb2R1Y3RfY29kZSI6IkJVU0lORVNTIiwidXNlcm5hbWUiOiJkb3VnLWxvdmV0dCIsImxhc3RuYW1lIjoiTG92ZXR0In0.ZogjrfibVxbXW0x4xbXKBKtIpxwIhFpzn0rGy0QmkEwNZRq20T2tTPb5KbVUmM5nTEVwU6H1P2jGFVhGQhSDu5pBjz28gdX3vAi1f48Ow5RSqcsE_dhgs8iFyWp7-Fu1_X3Zz2mCiLiTVwx_F2RQOpbBn8vKwiAlXXgagZAqN4Ybcyb2sA5CnX2uux89CaVK7xnQShNalWUl11wFZ2eX4b-8kK1fxdPdaAEYgPxhTo9u_b5ShuThzpxvoK-lM8UT2rAWuKQe-RhdKCFViNv25d8WpDqUPtFkeViaJFJN2PXl5MH8kbFuRFTwzbi3UG61kDGOzvZAr7Bi2VATKGCL9w'

  // Define Session
  sessionStorage.setItem('KEYCLOAK_TOKEN', jwt)
  sessionStorage.setItem('accountId', 'PS12345')
  sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-dev.apigee.net/ppr/api/v1/')
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
