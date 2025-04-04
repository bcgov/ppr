// Libraries
import { nextTick } from 'vue'
import { mockedGeneralCollateral2 } from './test-data'
import { GenColSummary } from '@/components/collateral/general'
import { RegistrationFlowType } from '@/enums'
import { pacificDate } from '@/utils'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const store = useStore()

// Input field selectors / buttons
const title = 'h3'
const history = '#general-collateral-history'
const historyBtn = '#gc-show-history-btn'
const generalCollateralSummary = '.general-collateral-summary'

const description = '.gc-description'
const descriptionAdd = '.gc-description-add'
const descriptionDelete = '.gc-description-delete'


describe('GenColSummary tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setGeneralCollateral([])
    wrapper = await createComponent(GenColSummary, { showInvalid: false })
  })

  it('renders showing general collateral under header in new reg flow', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    const newDescription = 'new description'
    await store.setGeneralCollateral([{ description: newDescription }])
    await nextTick()

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
    await nextTick()

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
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(GenColSummary, { showInvalid: false })
  })

  it('renders showing general collateral and amend button', async () => {
    const newDescription = 'new description'
    await store.setGeneralCollateral([{ description: newDescription, addedDateTime: '2021-10-21' }])
    await nextTick()

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
    await nextTick()

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
    wrapper = await createComponent(GenColSummary, {
      setShowHistory: false,
      setShowAmendLink: false,
      setShowViewLink: false
    })
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
