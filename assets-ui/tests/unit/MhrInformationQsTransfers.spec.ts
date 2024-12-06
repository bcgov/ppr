import { defaultFlagSet } from '@/utils'
import { mockMhrTransferCurrentHomeOwner } from './test-data'
import { createComponent, mapMhrTypeToProductCode, setupCurrentHomeOwners, setupMockUser } from './utils'
import { HomeOwners, MhrInformation } from '@/views'
import {
  APIRegistrationTypes,
  MhApiFrozenDocumentTypes,
  MhApiStatusTypes,
  MhrSubTypes,
  ProductCode,
  RouteNames
} from '@/enums'
import { nextTick } from 'vue'
import { LienAlert } from '@/components/common'
import { TransferType } from '@/components/mhrTransfers'
import { HomeOwnersTable } from '@/components/mhrRegistration'
import { useStore } from '@/store/store'
import { afterEach, beforeAll } from 'vitest'
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

    afterEach(async () => {
      store.setLienType('')
      store.setMhrStatusType(null)
      store.setMhrFrozenDocumentType(null)
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
      expect(wrapper.find('#home-owners-change-btn').exists()).toBe(true)
    })

    it('renders Lien Alert', async () => {
      store.setLienType(APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT_TAX)
      await nextTick()

      expect(wrapper.find('#home-owners-header').exists()).toBe(true)
      expect(wrapper.find('#home-owners-change-btn').exists()).toBe(true)
      // Verify disabled Home Owners Change btn
      expect(wrapper.find('#home-owners-change-btn').attributes().disabled).toBeDefined()
    })

    it('does not render Lien Alert and disable Transfers for TRANSITION_SECURITY_AGREEMENT', async () => {
      store.setLienType(APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT)
      await nextTick()

      expect(wrapper.find('#home-owners-header').exists()).toBe(true)
      expect(wrapper.find('#home-owners-change-btn').exists()).toBe(true)
      // Verify Enabled Home Owners Change btn
      expect(wrapper.find('#home-owners-change-btn').attributes().disabled).toBeUndefined()
    })

    it('verify frozen state due to affe filing', async () => {
      store.setMhrStatusType(MhApiStatusTypes.FROZEN)
      store.setMhrFrozenDocumentType(MhApiFrozenDocumentTypes.TRANS_AFFIDAVIT)
      await nextTick()

      // Verify showTransfer type
      expect(wrapper.vm.showTransferType).toBe(false)

      // Verify in-progress-filing messaging due to affe
      expect(wrapper.vm.showInProgressMsg).toBe(true)

      // Verify disabled Home Owners Change btn
      expect(wrapper.find('#home-owners-change-btn').attributes().disabled).toBeDefined()
    })

    it('verify role based transfer messaging and button states', async () => {
      const isManufacturer = subProduct === MhrSubTypes.MANUFACTURER
      const isDealer = subProduct === MhrSubTypes.DEALERS
      // enable transfers based on role
      wrapper.vm.disableRoleBaseTransfer = isManufacturer || isDealer
      await nextTick()

      // Verify showTransfer type
      expect(wrapper.vm.showTransferType).toBe(false)

      // Verify Mismatch text
      expect(wrapper.find('.dealer-manufacturer-mismatch-text').exists()).toBe(isManufacturer || isDealer)

      // Role based tests
      switch (subProduct) {
        case MhrSubTypes.DEALERS:
          expect(wrapper.find('#home-owners-change-btn').attributes().disabled).toBeDefined()
          // Verify Mismatch text content
          expect(wrapper.find('.dealer-manufacturer-mismatch-text').text()).toContain('You cannot register an ownership ' +
            'transfer or change because the home does not have a sole owner whose name matches')
          break;
        case MhrSubTypes.MANUFACTURER:
          expect(wrapper.find('#home-owners-change-btn').attributes().disabled).toBeDefined()
          // Verify Mismatch text content
          expect(wrapper.find('.dealer-manufacturer-mismatch-text').text()).toContain('You cannot register an ownership ' +
            'transfer or change because the home does not have a sole owner whose name matches')
          break;
        case MhrSubTypes.LAWYERS_NOTARIES:
          expect(wrapper.find('#home-owners-change-btn').attributes().disabled).toBeUndefined()
          wrapper.find('#home-owners-change-btn').trigger('click')
          await nextTick()
          break;
      }

      // Verify showTransfer type
      expect(wrapper.vm.showTransferType).toBe(subProduct === MhrSubTypes.LAWYERS_NOTARIES)
    })
  })
}
