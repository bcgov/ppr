// Libraries
import { nextTick } from 'vue'

// Components
import { HomeLandOwnership } from '@/components/mhrRegistration'
import { createComponent, getTestId } from './utils'
import { useStore } from '../../src/store/store'

const store = useStore()

describe('Home Land Ownership', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(HomeLandOwnership)
  })

  it('renders base component', async () => {
    expect(wrapper.findComponent(HomeLandOwnership).exists()).toBe(true)
  })

  it('ownership radio group performs as expected', async () => {
    expect(store.getMhrRegistrationOwnLand).toBe(null)
    expect(wrapper.find(getTestId('ownership-radios'))).toBeTruthy()

    //no instructional paragraph should be displayed initially
    expect(wrapper.find(getTestId('yes-paragraph')).exists()).toBe(false)
    expect(wrapper.find(getTestId('no-paragraph')).exists()).toBe(false)

    const yesRadioBtn = <HTMLInputElement>(
      wrapper.find(getTestId('yes-ownership-radio-btn'))).element
    const noRadioBtn = <HTMLInputElement>(
      wrapper.find(getTestId('no-ownership-radio-btn'))).element

    //no button should be selected initially
    expect(yesRadioBtn.checked).toBeFalsy()
    expect(noRadioBtn.checked).toBeFalsy()

    //click yes button
    wrapper.find(getTestId('yes-ownership-radio-btn')).trigger('click')
    // simulate click
    wrapper.vm.isOwnLand = true
    await nextTick()

    expect(store.getMhrRegistrationOwnLand).toBe(true)
    expect(wrapper.find(getTestId('yes-paragraph')).exists()).toBe(true)
    expect(wrapper.find(getTestId('no-paragraph')).exists()).toBe(false)

    //click no button
    wrapper.find(getTestId('no-ownership-radio-btn')).trigger('click')
    // simulate click
    wrapper.vm.isOwnLand = false
    await nextTick()
    expect(store.getMhrRegistrationOwnLand).toBe(false)
    expect(wrapper.find(getTestId('yes-paragraph')).exists()).toBe(false)
    expect(wrapper.find(getTestId('no-paragraph')).exists()).toBe(true)
  })
})
