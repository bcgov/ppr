import { defaultFlagSet } from '@/utils'
import { mockMhrTransferCurrentHomeOwner } from './test-data'
import { createComponent, mapMhrTypeToProductCode, setupCurrentHomeOwners, setupMockUser } from './utils'
import { HomeOwners, MhrInformation } from '@/views'
import { MhrSubTypes, ProductCode, RouteNames } from '@/enums'
import { nextTick } from 'vue'
import { LienAlert } from '@/components/common'
import { TransferType } from '@/components/mhrTransfers'
import { HomeOwnersTable } from '@/components/mhrRegistration'
import { useStore } from '@/store/store'
import { beforeAll } from 'vitest'
import { useUserAccess } from '@/composables'
import flushPromises from 'flush-promises'


const store = useStore()

//TODO:  Work in progress to test the variations between QS Type in Transfers
const subProducts: MhrSubTypes[] = [MhrSubTypes.DEALERS, MhrSubTypes.LAWYERS_NOTARIES, MhrSubTypes.MANUFACTURER]
for (const subProduct of subProducts) {
  describe(`MhrInformation: ${subProduct}`, () => {
    let wrapper
    const { setQsInformationModel } = useUserAccess()

    beforeAll(async () => {
      // Setup User
      await setupMockUser()

      // Setup QS
      await store.setMhrSubProduct(subProduct)
      await setQsInformationModel(subProduct)
      await store.setUserProductSubscriptionsCodes([ProductCode.MHR, mapMhrTypeToProductCode(subProduct)])

      await flushPromises()
      await nextTick()
    })

    beforeEach(async () => {
      defaultFlagSet['mhr-transfer-enabled'] = true
      wrapper = await createComponent(
        MhrInformation,
        { appReady: true, isMhrTransfer: true },
        RouteNames.MHR_INFORMATION
      )

      await setupCurrentHomeOwners()
      wrapper.vm.dataLoaded = true
      await nextTick()
    })

    it('renders and displays the Mhr Information View for this QS type', async () => {
      // Verify Base Wrapper
      expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)
      expect(wrapper.find('#mhr-information-header').text()).toContain('Manufactured Home Information')

      // Verify Lien Messaging
      expect(wrapper.findComponent(LienAlert).exists()).toBe(false)

      // Verify Transfer Type Selector
      expect(wrapper.findComponent(TransferType).exists()).toBe(false)

      // Verify Home Owners
      const homeOwnersTable = await wrapper.findComponent(HomeOwnersTable)
      expect(wrapper.findComponent(HomeOwners).exists()).toBeTruthy()
      expect(wrapper.vm.getMhrTransferCurrentHomeOwnerGroups.length).toBe(1)
      expect(wrapper.vm.getMhrTransferHomeOwners.length).toBe(1)

      expect(homeOwnersTable.exists()).toBeTruthy()
      expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
      expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)
    })

    it('renders change owners button conditionally', async () => {
      expect(wrapper.find('#home-owners-header').exists()).toBe(true)
      expect(wrapper.vm.enableHomeOwnerChanges).toBe(true)
    })
  })
}
