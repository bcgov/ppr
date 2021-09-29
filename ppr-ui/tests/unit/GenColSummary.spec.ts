// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedGeneralCollateral2
} from './test-data'

// Components
import { GenColSummary } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { convertDate } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const title = 'h3'
const history = '#general-collateral-history'
const historyBtn = '#gc-show-history-btn'
const generalCollateralSummary = '.general-collateral-summary'

const description = '.gc-description'
const descriptionAdd = '.gc-description-add'
const descriptionDelete = '.gc-description-delete'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(GenColSummary, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('GenColSummary tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setGeneralCollateral', [])
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders showing general collateral under header in new reg flow', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    const newDescription = 'new description'
    await store.dispatch('setGeneralCollateral', [{ description: newDescription }])
    wrapper = createComponent()
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.vm.showingHistory).toBe(false)
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.findAll(history).length).toBe(0)
    expect(wrapper.findAll(historyBtn).length).toBe(0)
    expect(wrapper.findAll(generalCollateralSummary).length).toBe(1)
    expect(wrapper.findAll(generalCollateralSummary).at(0).text()).toBe(newDescription)
  })

  it('renders showing general collateral under header in discharge flow', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.DISCHARGE)
    await store.dispatch('setGeneralCollateral', mockedGeneralCollateral2)
    wrapper = createComponent()
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.vm.showingHistory).toBe(false)
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.findAll(history).length).toBe(1)
    expect(wrapper.findAll(historyBtn).length).toBe(1)
    expect(wrapper.findAll(generalCollateralSummary).length).toBe(0)
    await wrapper.find(historyBtn).trigger('click')
    expect(wrapper.vm.showingHistory).toBe(true)
    expect(wrapper.findAll(generalCollateralSummary).length).toBe(1)
    expect(wrapper.findAll(description).length).toBe(1)
    // base reg general collateral
    expect(wrapper.findAll(description).at(0).text()).toContain('Base Registration Collateral:')
    expect(
      wrapper.findAll(description).at(0).text()
    ).toContain(mockedGeneralCollateral2[wrapper.vm.$data.baseGenCollateralIndex].description)
    // ammended general collateral
    const descriptionAddAll = wrapper.findAll(descriptionAdd)
    const descriptionDeleteAll = wrapper.findAll(descriptionDelete)
    let addCount = 0
    let deleteCount = 0
    for (let i = 0; i < mockedGeneralCollateral2.length; i++) {
      expect(addCount < descriptionAddAll.length)
      expect(deleteCount < descriptionDeleteAll.length)
      if (mockedGeneralCollateral2[i].addedDateTime) {
        const date = new Date(mockedGeneralCollateral2[i].addedDateTime)
        expect(wrapper.find(generalCollateralSummary).text()).toContain(convertDate(date, true, true))
      }
      if (mockedGeneralCollateral2[i].descriptionAdd) {
        expect(descriptionAddAll.at(addCount).text()).toContain('ADDED')
        expect(descriptionAddAll.at(addCount).text()).toContain(mockedGeneralCollateral2[i].descriptionAdd)
        addCount += 1
      }
      if (mockedGeneralCollateral2[i].descriptionDelete) {
        expect(descriptionDeleteAll.at(deleteCount).text()).toContain('DELETED')
        expect(descriptionDeleteAll.at(deleteCount).text()).toContain(mockedGeneralCollateral2[i].descriptionDelete)
        deleteCount += 1
      }
    }
  })
})
