import { nextTick } from 'vue'
import { GenColAmend } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'
import { useStore } from '@/store/store'

const store = useStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-gen-col'

describe('GenColAmend tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    await store.setGeneralCollateral([])

    wrapper = await createComponent(GenColAmend, { showInvalid: false })
  })

  it('renders default', async () => {
    expect(wrapper.findComponent(GenColAmend).exists()).toBe(true)
    expect(wrapper.vm.addDesc).toBe('')
    expect(wrapper.vm.delDesc).toBe('')
    expect(wrapper.vm.generalCollateral).toEqual([])
  })

  it('shows saved general collateral', async () => {
    await store.setGeneralCollateral([{ descriptionAdd: 'addexample', descriptionDelete: 'othertest' }])
    await nextTick()

    expect(wrapper.vm.addDesc).toBe('addexample')
    expect(wrapper.vm.delDesc).toBe('othertest')
  })

  it('does not show existing general collateral from previous amendment', async () => {
    await store.setGeneralCollateral(
      [{ descriptionAdd: 'addexample', descriptionDelete: 'othertest', addedDateTime: '2021-10-13' }])
    await nextTick()

    expect(wrapper.vm.addDesc).toBe('')
    expect(wrapper.vm.delDesc).toBe('')
  })

  it('updates general collateral', async () => {
    await store.setGeneralCollateral([])
    await nextTick()

    wrapper.vm.delDesc = 'JOE'
    wrapper.vm.addDesc = 'SCHMOE'
    wrapper.find(doneButtonSelector).trigger('click')
    expect(getLastEvent(wrapper, 'closeGenColAmend')).toBeTruthy()
    await flushPromises()
    // store should have 1 item now
    expect(store.getAddCollateral.generalCollateral.length).toBe(1)
  })

  it('saves amended general collateral over the previous one', async () => {
    await store.setGeneralCollateral(
      [{ descriptionAdd: 'addexample', descriptionDelete: 'othertest' }])
    await nextTick()

    wrapper.vm.delDesc = 'JOE'
    wrapper.vm.addDesc = 'SCHMOE'
    wrapper.find(doneButtonSelector).trigger('click')
    expect(getLastEvent(wrapper, 'closeGenColAmend')).toBeTruthy()
    await flushPromises()
    // store should still have 1 item now (replaced the last one)
    expect(store.getAddCollateral.generalCollateral.length).toBe(1)
    expect(store.getAddCollateral.generalCollateral[0].descriptionAdd).toBe('SCHMOE')
  })
})
