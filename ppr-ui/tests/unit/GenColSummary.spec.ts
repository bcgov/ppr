// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedGeneralCollateral2
} from './test-data'

// Components
import { GenColSummary } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { pacificDate } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

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

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((GenColSummary as any), {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('GenColSummary tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setGeneralCollateral([])
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders showing general collateral under header in new reg flow', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    const newDescription = 'new description'
    await store.setGeneralCollateral([{ description: newDescription }])
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
    await store.setRegistrationFlowType(RegistrationFlowType.DISCHARGE)
    await store.setGeneralCollateral(mockedGeneralCollateral2)
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
    expect(wrapper.findAll(description).at(0).text()).toContain('Base Registration General Collateral:')
    expect(
      wrapper.findAll(description).at(0).text()
    ).toContain(mockedGeneralCollateral2[wrapper.vm.baseGenCollateralIndex].description)
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
        expect(wrapper.find(generalCollateralSummary).text()).toContain(pacificDate(date))
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

describe('GenColSummary Amendment tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders showing general collateral and amend button', async () => {
    const newDescription = 'new description'
    await store.setGeneralCollateral([{ description: newDescription, addedDateTime: '2021-10-21' }])
    wrapper = createComponent()
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.vm.showingHistory).toBe(false)
    expect(wrapper.findAll(title).length).toBe(1)
    // it starts with history open
    expect(wrapper.findAll(history).length).toBe(1)
    expect(wrapper.findAll(historyBtn).length).toBe(1)
    // amend button
    expect(wrapper.findAll('#gen-col-amend-btn').length).toBe(1)
  })

  it('renders showing general collateral and undo button', async () => {
    await store.setGeneralCollateral([{ descriptionAdd: 'test', descriptionDelete: 'othertest' }])
    wrapper = createComponent()
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.vm.showingHistory).toBe(false)
    expect(wrapper.findAll(title).length).toBe(1)
    // it starts with history open
    expect(wrapper.findAll(history).length).toBe(1)
    expect(wrapper.findAll(historyBtn).length).toBe(1)
    // undo button
    expect(wrapper.findAll('#gen-col-undo-btn').length).toBe(1)
  })

  it('shows/hides items depending on the props', async () => {
    wrapper = createComponent()
    wrapper.vm.$props.setShowHistory = false
    wrapper.vm.$props.setShowAmendLink = false
    wrapper.vm.$props.setShowViewLink = false
    await nextTick()
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.vm.showingHistory).toBe(false)
    // title should not show
    expect(wrapper.findAll(title).length).toBe(0)
    // history button should not show
    expect(wrapper.findAll(historyBtn).length).toBe(0)
    // undo button should not show
    expect(wrapper.findAll('#gen-col-undo-btn').length).toBe(0)
  })
})
