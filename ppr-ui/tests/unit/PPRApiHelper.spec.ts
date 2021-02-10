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
  const jwt = ''

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
