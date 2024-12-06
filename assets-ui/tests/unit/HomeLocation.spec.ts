import { createComponent } from './utils'
import { HomeLocation } from '@/views'
import { MhApiStatusTypes, RouteNames } from '@/enums'
import { MhrCorrectionStaff } from '@/resources'
import { useStore } from '@/store/store'
import { CautionBox } from '@/components/common'
import HomeLocationReview from '@/components/mhrRegistration/ReviewConfirm/HomeLocationReview.vue'
import { nextTick } from 'vue'

const store = useStore()

describe('HomeLocation', () => {
  it('renders correctly in default state', async () => {
    const wrapper = await createComponent(HomeLocation)

    // Assert that the component renders correctly
    expect(wrapper.exists()).toBe(true)

    // Assert that the standard MHR Home Location Components are rendered
    expect(wrapper.find('#mhr-home-location-type-wrapper').exists()).toBe(true)
    expect(wrapper.find('#mhr-home-civic-address-wrapper').exists()).toBe(true)
    expect(wrapper.find('#mhr-home-land-ownership-wrapper').exists()).toBe(true)

    // Assert that the correction template is not rendered
    expect(wrapper.find('#mhr-correction-has-active-permit').exists()).toBe(false)
  })

  it('renders correctly when isMhrCorrection is true and hasActiveTransportPermit is true',async () => {
    const wrapper = await createComponent(HomeLocation, null, RouteNames.HOME_LOCATION)
    await store.setRegistrationType(MhrCorrectionStaff)
    await store.setMhrInformation({
      permitDateTime: '2024-02-05T08:40:53-08:00',
      permitExpiryDateTime: '2024-03-06T09:00:00-07:53',
      permitRegistrationNumber: '00502383',
      permitStatus: MhApiStatusTypes.ACTIVE
    })
    await nextTick()

    // Assert that the component renders correctly
    expect(wrapper.exists()).toBe(true)

    // Assert that the standard MHR Home Location Components are not rendered
    expect(wrapper.find('#mhr-home-location-type-wrapper').exists()).toBe(false)
    expect(wrapper.find('#mhr-home-civic-address-wrapper').exists()).toBe(false)
    expect(wrapper.find('#mhr-home-land-ownership-wrapper').exists()).toBe(false)

    // Assert that the correction template is rendered HomeLocationReview
    expect(wrapper.find('#mhr-correction-has-active-permit').exists()).toBe(true)
  })
})
