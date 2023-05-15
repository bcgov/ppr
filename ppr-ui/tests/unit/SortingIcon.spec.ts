import { mount } from '@vue/test-utils'
import { SortingIcon } from '@/components/tables/common'
import { nextTick } from '@vue/composition-api'
import { getTestId } from './utils'

describe('SortingIcon', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(SortingIcon, {
      propsData: {
        sortAsc: false
      }
    })
  })

  it('should emit sortEvent with false when not sorted and clicked', async () => {
    await wrapper.find('v-icon').trigger('click')

    expect(wrapper.emitted('sortEvent')).toBeTruthy()
    expect(wrapper.emitted('sortEvent')[0][0]).toBe(false)
  })

  it('should emit sortEvent with true when sorted and clicked', async () => {
    wrapper.setProps({ sortAsc: true })
    await nextTick()

    await wrapper.find('v-icon').trigger('click')
    await nextTick()

    expect(wrapper.emitted('sortEvent')).toBeTruthy()
    expect(wrapper.emitted('sortEvent')[0][0]).toBe(true)
  })

  it('should render the up arrow icon when not desc', async () => {
    const upArrowIcon = wrapper.find(getTestId('up-arrow-icon'))
    const downArrowIcon = wrapper.find(getTestId('down-arrow-icon'))

    expect(upArrowIcon.exists()).toBe(true)
    expect(downArrowIcon.exists()).toBe(false)
  })

  it('should render the down arrow icon when desc', async () => {
    wrapper.setProps({ sortAsc: true })
    await nextTick()

    const upArrowIcon = wrapper.find(getTestId('up-arrow-icon'))
    const downArrowIcon = wrapper.find(getTestId('down-arrow-icon'))

    expect(upArrowIcon.exists()).toBe(false)
    expect(downArrowIcon.exists()).toBe(true)
  })
})
