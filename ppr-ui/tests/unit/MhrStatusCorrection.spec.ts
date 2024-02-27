import { createComponent } from './utils'
import { MhrStatusCorrection } from '@/components/mhrRegistration'
import { RouteNames } from '@/enums'

describe('MhrStatusCorrection', () => {
  it('renders the component', async () => {
    const wrapper = await createComponent(MhrStatusCorrection)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays status options when displayStatusOptions is true', async () => {
    const wrapper = await createComponent(MhrStatusCorrection)

    // Ensure displayStatusOptions is initially true
    expect(wrapper.vm.displayStatusOptions).toBe(true)

    // Check if the status options are displayed
    const radioBtns = await wrapper.find('.v-radio-group')
    expect(radioBtns.exists()).toBe(true)
  })

  it('hide status options when on Mhr Review Route ', async () => {
    const wrapper = await createComponent(MhrStatusCorrection, null, RouteNames.MHR_REVIEW_CONFIRM)

    // Ensure displayStatusOptions is false on Mhr Review Confirm
    expect(wrapper.vm.displayStatusOptions).toBe(false)

    // Check if the status options are displayed
    const radioBtns = await wrapper.find('.v-radio-group')
    expect(radioBtns.exists()).toBe(false)
  })

  // it('does not display status options when displayStatusOptions is false', async () => {
  //   const wrapper = await createComponent(MhrStatusCorrection, {
  //     data() {
  //       return {
  //         displayStatusOptions: false
  //       }
  //     }
  //   })
  //
  //   // Check if the status options are not displayed
  //   expect(wrapper.find('#mhr-status-correction-options').exists()).toBe(false)
  // })

  // it('calls setMhrCorrectStatusType when mhrStatus changes', async () => {
  //   const wrapper = await createComponent(MhrStatusCorrection, {
  //     global: {
  //       provide: {
  //         setMhrCorrectStatusType
  //       }
  //     }
  //   })
  //
  //   // Simulate a change in mhrStatus
  //   await wrapper.setData({ mhrStatus: 'someStatus' })
  //
  //   // Check if setMhrCorrectStatusType was called
  //   expect(setMhrCorrectStatusType).toHaveBeenCalledWith('someStatus')
  // })
})
