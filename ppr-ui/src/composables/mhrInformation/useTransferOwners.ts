import { ActionTypes, ApiHomeTenancyTypes, ApiTransferTypes, HomeOwnerPartyTypes } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'
import { MhrRegistrationHomeOwnerIF } from '@/interfaces'

export const useTransferOwners = (enableAllActions: boolean = false) => {
  const {
    getMhrTransferType,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups
  } = useGetters<any>([
    'getMhrTransferType',
    'getMhrTransferHomeOwnerGroups',
    'getMhrTransferCurrentHomeOwnerGroups'
  ])

  /** Conditionally Enable HomeOwner Changes based on Transfer Type **/
  const enableHomeOwnerChanges = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
        return true // Always enable for Sale or Gift
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        // Check for joint tenancy (at least two owners who are not executors, trustees or admins)
        return getMhrTransferCurrentHomeOwnerGroups.value.some(group =>
          group.type === ApiHomeTenancyTypes.JOINT &&
            group.owners.filter(owner =>
              owner.partyType === HomeOwnerPartyTypes.OWNER_IND || owner.partyType === HomeOwnerPartyTypes.OWNER_BUS)
              .length >= 2
        )
      default:
        return false
    }
  }
  /** Conditionally Enable HomeOwner Additions based on Transfer Type **/
  const enableAddHomeOwners = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
        return true // Always enable for Sale or Gift
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        return false // Disable for Surviving Joint Tenants
      default:
        return false
    }
  }

  /** Conditionally Enable HomeOwner Group Actions based on Transfer Type **/
  const enableTransferOwnerGroupActions = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
        return true // Always enable for Sale or Gift
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        return false // Disable for Surviving Joint Tenants
      default:
        return false
    }
  }

  /** Conditionally Enable HomeOwner Action (ie delete, edit) based on Transfer Type **/
  const enableTransferOwnerActions = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
        return true // Always enable for Sale or Gift
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        // Check for joint tenancy (at least two owners who are not executors, trustees or admins)
        return owner.type === ApiHomeTenancyTypes.JOINT
      default:
        return false
    }
  }

  /** Conditionally Enable HomeOwner Dropdown Menu based on Transfer Type **/
  const enableTransferOwnerMenuActions = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
        return false // Disable for Sale or Gift
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        // Check for joint tenancy (at least two owners who are not executors, trustees or admins)
        return owner.type === ApiHomeTenancyTypes.JOINT
      default:
        return false
    }
  }

  /** Return true if there is a deceased owner outside the specific owners group **/
  const disableForDeceasedOwners = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT) {
      const hasDeceasedOwners = getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      const isDeceasedOwnerGroup = getMhrTransferHomeOwnerGroups.value.find(group =>
        group.groupId === owner.groupId).owners.some(owner => owner.action === ActionTypes.REMOVED)

      return hasDeceasedOwners && !isDeceasedOwnerGroup
    }
    return false
  }

  return {
    enableHomeOwnerChanges,
    enableTransferOwnerGroupActions,
    enableTransferOwnerActions,
    enableTransferOwnerMenuActions,
    enableAddHomeOwners,
    disableForDeceasedOwners
  }
}
