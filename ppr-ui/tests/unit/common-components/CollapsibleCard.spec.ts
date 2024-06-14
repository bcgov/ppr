import CollapsibleCard from '@/components/common/CollapsibleCard.vue'
import { getTestId } from '../utils'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

describe('CollapsibleCard', () => {
  let wrapper: any

  const HEADER_LABEL = 'Main Header Label'
  const TOGGLE_LABEL = 'Toggle Label'

  beforeEach(async () => {
    wrapper = mount(CollapsibleCard, {
      props: {
        headerLabel: HEADER_LABEL,
        toggleLabel: TOGGLE_LABEL
      },
      slots: {
        infoSlot: '<div>Info Content</div>',
        mainSlot: '<div>Main Content</div>'
      }
    })
  })

  it('renders component with props', async () => {
    const collapsibleCard = wrapper.findComponent(CollapsibleCard)
    expect(collapsibleCard.exists()).toBe(true)
    expect(collapsibleCard.find(getTestId('card-header-label')).text()).toBe(HEADER_LABEL)
    expect(collapsibleCard.find(getTestId('card-toggle-label')).text()).toBe('Hide ' + TOGGLE_LABEL)

    const cardSlots = collapsibleCard.find(getTestId('card-slots'))

    expect(cardSlots.exists()).toBe(true)
    expect(cardSlots.text()).toContain('Info Content')
    expect(cardSlots.text()).toContain('Main Content')

    // collapse the card and slots
    collapsibleCard.vm.toggleCardOpen()
    await nextTick()

    expect(collapsibleCard.find(getTestId('card-slots')).exists()).toBe(false)
    expect(collapsibleCard.find(getTestId('card-toggle-label')).text()).toBe('Show ' + TOGGLE_LABEL)
  })
})
