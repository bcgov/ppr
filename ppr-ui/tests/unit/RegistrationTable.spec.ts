// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'

// Components
import { RegistrationTable } from '@/components/registration'

// Other
import { mockedRegistration1, mockedRegistration2, mockedDraft1, mockedDraft2 } from './test-data'
import { DraftIF, RegistrationIF } from '@/interfaces'
import { axios as pprAxios } from '@/utils/axios-ppr'

const vuetify = new Vuetify({})
const store = getVuexStore()

const regTable: string = '#registration-table'


/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResult> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationTable, {
    localVue,
    store,
    vuetify
  })
}


describe('Test result table with results', () => {
  let wrapper: Wrapper<any>
  const pprResp: RegistrationIF[] = [mockedRegistration1, mockedRegistration2]
  const draftResp: DraftIF[] = []
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(pprAxios, 'get')
    get.returns(
      new Promise(resolve =>
        resolve({
          data: pprResp
        })
      )
    )
    get.returns(
      new Promise(resolve =>
        resolve({
          data: draftResp
        })
      )
    )
    wrapper = createComponent()
  })

  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders and displays correct elements with results', async () => {
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.tableData.length).toBe(2)
    
    const registrationTableDisplay = wrapper.findAll(regTable)
    expect(registrationTableDisplay.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header, include the filter row, so add 2
    expect(rows.length).toBe(pprResp.length + 2)
    /* for (let i = 0; i < pprResp.length; i++) {
      const searchQuery = mockedSearchHistory.searches[i].searchQuery
      const searchDate = mockedSearchHistory.searches[i].searchDateTime
      const totalResultsSize = mockedSearchHistory.searches[i].totalResultsSize
      const exactResultsSize = mockedSearchHistory.searches[i].exactResultsSize
      const selectedResultsSize = mockedSearchHistory.searches[i].selectedResultsSize
      const searchId = mockedSearchHistory.searches[i].searchId
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displaySearchValue(searchQuery))
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displayType(searchQuery.type))
      expect(rows.at(i + 1).text()).toContain(searchQuery.clientReferenceId)
      expect(rows.at(i + 1).text()).toContain(wrapper.vm.displayDate(searchDate))
      expect(rows.at(i + 1).text()).toContain(totalResultsSize)
      expect(rows.at(i + 1).text()).toContain(exactResultsSize)
      expect(rows.at(i + 1).text()).toContain(selectedResultsSize)
      expect(rows.at(i + 1).text()).toContain('PDF')
      wrapper.find(`#pdf-btn-${searchId}`).trigger('click')
      await Vue.nextTick()
      expect(downloadMock).toHaveBeenCalledWith(searchId)
    }
    */
  })
})
