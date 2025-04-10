import {
  notCompleteDialog,
  registrationAddErrorDialog,
  registrationAlreadyAddedDialog,
  registrationFoundDialog,
  registrationNotFoundDialog,
  registrationRestrictedDialog,
  tableDeleteDialog,
  tableRemoveDialog,
  unsavedChangesDialog,
  manufacturerRegSuccessDialogOptions,
  manufacturedHomeDeliveredDialogOptions
} from '@/resources/dialogOptions'
import { createComponent, getLastEvent, getTestId } from './utils'
import { BaseDialog } from '@/components/dialogs'
import type { DialogOptionsIF } from '@/interfaces'
import flushPromises from 'flush-promises'
import { DialogButtons, DialogContent } from '@/components/dialogs/common'
import { nextTick } from 'vue'
import { UnitNoteDocTypes } from '@/enums'
import { UnitNotesInfo } from '@/resources'

// emitted events
const proceed = 'proceed'
// Input field selectors / buttons
const title = '.dialog-title'
const closeBtn = '.close-btn'

describe('Base Dialog tests', () => {
  let wrapper

  const optionsList = [
    { ...notCompleteDialog },
    { ...registrationAddErrorDialog },
    { ...registrationAlreadyAddedDialog },
    { ...registrationFoundDialog },
    { ...registrationNotFoundDialog },
    { ...registrationRestrictedDialog },
    { ...unsavedChangesDialog },
    { ...tableDeleteDialog },
    { ...tableRemoveDialog },
    { ...manufacturerRegSuccessDialogOptions }
  ]

  const props = {
    setAttach: '',
    setDisplay: true,
    setOptions: {
      acceptText: 'default accept',
      cancelText: 'default cancel',
      hasContactInfo: false,
      text: 'default text',
      textExtra: [],
      title: 'default title'
    } as DialogOptionsIF
  }

  beforeEach(async () => {
    wrapper = await createComponent(BaseDialog, props)
    await flushPromises()
  })

  it('renders the component with parts', async () => {
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(DialogContent).exists()).toBe(true)
    expect(wrapper.findComponent(DialogButtons).exists()).toBe(true)
    expect(wrapper.findComponent(DialogContent).isVisible()).toBe(true)
    expect(wrapper.findComponent(DialogButtons).isVisible()).toBe(true)
    expect(wrapper.findComponent(DialogContent).vm.$props.setBaseText).toBe('default text')
    expect(wrapper.findComponent(DialogContent).vm.$props.setExtraText).toEqual([])
    expect(wrapper.findComponent(DialogContent).vm.$props.setHasContactInfo).toBe(false)
    expect(wrapper.findComponent(DialogButtons).vm.$props.setAcceptText).toBe('default accept')
    expect(wrapper.findComponent(DialogButtons).vm.$props.setCancelText).toBe('default cancel')
    expect(wrapper.vm.$props.setDisplay).toBe(true)
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.find(title).text()).toBe('default title')
  })

  it('hides base dialog', async () => {
    wrapper = await createComponent(BaseDialog, { ...props, setDisplay: false })
    await nextTick()
    expect(wrapper.vm.$props.setDisplay).toBe(false)
    expect(wrapper.find('.dialog-title').exists()).toBe(false)
  })

  it('renders base dialog with given options', async () => {
    for (let i = 0; i < optionsList.length; i++) {
      const options = optionsList[i]
      wrapper = await createComponent(BaseDialog,
        {
          setAttach: '',
          setDisplay: true,
          setOptions: options as DialogOptionsIF
        }
      )
      await flushPromises()
      expect(wrapper.findComponent(BaseDialog).isVisible()).toBe(true)
      expect(wrapper.findComponent(DialogContent).isVisible()).toBe(true)
      expect(wrapper.findComponent(DialogButtons).isVisible()).toBe(true)
      expect(wrapper.findAll(title).length).toBe(1)
      expect(wrapper.find(title).text()).toBe(options.title)
      expect(wrapper.findComponent(DialogContent).vm.$props.setBaseText).toBe(options.text)
      expect(wrapper.findComponent(DialogContent).vm.$props.setExtraText).toEqual(options.textExtra || [])
      expect(wrapper.findComponent(DialogContent).vm.$props.setHasContactInfo).toBe(options.hasContactInfo || false)
      expect(wrapper.findComponent(DialogButtons).vm.$props.setAcceptText).toBe(options.acceptText)
      expect(wrapper.findComponent(DialogButtons).vm.$props.setCancelText).toBe(options.cancelText)
    }
  })

  it('renders base dialog with a dismiss checkbox', async () => {
    wrapper = await createComponent(BaseDialog,
      {
        setAttach: '',
        setDisplay: true,
        setOptions: manufacturerRegSuccessDialogOptions,
        showDismissDialogCheckbox: true
      }
    )

    expect(wrapper.findComponent(BaseDialog).isVisible()).toBe(true)
    expect(wrapper.find('#dismiss-dialog-checkbox').isVisible()).toBe(true)
  })

  it('renders manufactured home delivered base dialog with a confirm checkbox', async () => {
    const dialogOptions = manufacturedHomeDeliveredDialogOptions(
      UnitNotesInfo[UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION].header
    )

    wrapper = await createComponent(BaseDialog, {
      setAttach: '',
      setDisplay: true,
      setConfirmActionLabel: 'I confirm this selection',
      setOptions: dialogOptions,
      showDismissDialogCheckbox: true
    })

    expect(wrapper.findComponent(BaseDialog).isVisible()).toBe(true)
    expect(wrapper.find('h2').text()).toBe(dialogOptions.title)
    expect(wrapper.find('.dialog-text').text()).toBe(dialogOptions.text.replace(/<[^>]*>/g, '')) // replace html tags

    const confirmActionCheckbox = wrapper.find(getTestId('confirm-action-checkbox'))
    expect(confirmActionCheckbox.exists()).toBe(true)
    expect(confirmActionCheckbox.text()).toBe('I confirm this selection')

    expect(confirmActionCheckbox.classes('v-input--error')).toBeFalsy() // checkbox should not be in error state
    wrapper.findComponent(DialogButtons).vm.$emit(proceed, true) // click the primary button in dialog
    await nextTick()
    expect(confirmActionCheckbox.classes('v-input--error')).toBeTruthy() // checkbox should be in error state
  })

  it('Emits the button actions', async () => {
    wrapper.findComponent(DialogButtons).vm.$emit(proceed, true)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(true)
    wrapper.findComponent(DialogButtons).vm.$emit(proceed, false)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
    expect(wrapper.find(closeBtn).exists()).toBe(true)
    await wrapper.find(closeBtn).trigger('click')
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })
})
