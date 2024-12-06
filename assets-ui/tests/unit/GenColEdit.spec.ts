import { nextTick } from 'vue'
import { GenColEdit } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { mockedOtherCarbon } from './test-data'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const store = useStore()

// Input field selectors / buttons
const generalCollateralEdit = '#general-collateral'
const errorMsg = '.v-messages__message'
const showError = '.border-error-left'

describe('GenColEdit tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setGeneralCollateral([])
    wrapper = await createComponent(GenColEdit, { showInvalid: false })
  })

  it('renders default with no existing collateral', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await nextTick()

    expect(wrapper.findComponent(GenColEdit).exists()).toBe(true)
    expect(wrapper.vm.newDesc).toBe('')
    expect(wrapper.vm.generalCollateral).toEqual([])
    expect(wrapper.vm.showErrorComponent).toBe(false)
    expect(wrapper.findAll(generalCollateralEdit).length).toBe(1)
    expect(wrapper.findAll(errorMsg).length).toBe(0)
    expect(wrapper.findAll(showError).length).toBe(0)
  })

  it('updates general collateral with new description text', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await nextTick()

    wrapper.vm.newDesc = 'new description'
    await nextTick()
    expect(wrapper.vm.generalCollateral).toEqual([{ description: 'new description' }])
  })

  it('updates new description text with existing general collateral txt in new registration', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setGeneralCollateral([{ description: 'existing general collateral' }])
    await nextTick()

    expect(wrapper.vm.generalCollateral).toEqual([{ description: 'existing general collateral' }])
    expect(wrapper.vm.newDesc).toBe('existing general collateral')
  })

  it('should pre-fill General Collateral with a default value', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setRegistrationType(mockedOtherCarbon())
    wrapper = await createComponent(GenColEdit, { showInvalid: false })
    await nextTick()

    // General COllateral should be pre-filled with custom default text value
    expect(store.getGeneralCollateral[0].description)
      .toContain('All the debtor’s present and after acquired personal property')
  })

  it('shows error bar when set', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = await createComponent(GenColEdit, { showInvalid: true })
    await nextTick()

    expect(wrapper.findAll(generalCollateralEdit).length).toBe(1)
    expect(wrapper.findAll(errorMsg).length).toBe(0)
    expect(wrapper.findAll(showError).length).toBe(1)
  })
})
