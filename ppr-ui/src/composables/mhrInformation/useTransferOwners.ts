import { ActionTypes, ApiHomeTenancyTypes, ApiTransferTypes, HomeOwnerPartyTypes } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'
import { MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { computed } from '@vue/composition-api'
import { isEqual } from 'lodash'
import { normalizeObject } from '@/utils'

/**
 * Composable to handle Ownership functionality and permissions specific to the varying Transfer of Ownership filings.
 * @param enableAllActions A flag to enable and bypass the permission functions. (ie for edge case like MHR)
 */
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

  /** Conditionally show DeathCertificate based on Transfer Type **/
  const showDeathCertificate = (): boolean =>
    getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT ||
    getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL

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

  /**
   * Return true if there is a deceased or modified owner outside the specified owners group
   * in Surviving Joint Tenants
   **/
  const isDisabledForSJTChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT) {
      const hasDeceasedOrChangedOwners = getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED || owner.action === ActionTypes.CHANGED))

      const isDeceasedOrChangedOwnerGroup = getMhrTransferHomeOwnerGroups.value.find(group =>
        group.groupId === owner.groupId).owners.some(owner =>
        owner.action === ActionTypes.REMOVED || owner.action === ActionTypes.CHANGED
      )

      return hasDeceasedOrChangedOwners && !isDeceasedOrChangedOwnerGroup
    }
    return false
  }

  /** Return true if the specified owner is part of the current/base ownership structure **/
  const isCurrentOwner = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    return getMhrTransferCurrentHomeOwnerGroups.value.some(group =>
      group.owners.some(baseOwner => baseOwner.ownerId === owner.ownerId)
    )
  }

  /**
   * Return the base owners snapshot by id.
   * @param ownerId The owner identifier
   */
  const getCurrentOwnerStateById = (ownerId: number): MhrRegistrationHomeOwnerIF => {
    let currentOwner
    getMhrTransferCurrentHomeOwnerGroups.value.forEach(group => group.owners.find(owner => {
      if (owner.ownerId === ownerId) currentOwner = owner
    }))
    return currentOwner
  }

  /** Return true if the specified owner has been modified from current state **/
  const hasCurrentOwnerChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    const currentOwner = getCurrentOwnerStateById(owner.ownerId)
    const isEqualAddress = isEqual(normalizeObject(currentOwner?.address), normalizeObject(owner.address))
    const isEqualPhone = normalizeObject(currentOwner)?.phoneNumber === normalizeObject(owner).phoneNumber &&
      normalizeObject(currentOwner)?.phoneExtension === normalizeObject(owner).phoneExtension

    return currentOwner && (!isEqualAddress || !isEqualPhone)
  }

  const isTransferDueToDeath = computed((): boolean => {
    return [
      ApiTransferTypes.SURVIVING_JOINT_TENANT,
      ApiTransferTypes.TO_ADMIN_PROBATE_NO_WILL,
      ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
      ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    ].includes(getMhrTransferType.value?.transferType)
  })

  return {
    enableHomeOwnerChanges,
    enableTransferOwnerGroupActions,
    enableTransferOwnerActions,
    enableTransferOwnerMenuActions,
    enableAddHomeOwners,
    showDeathCertificate,
    isDisabledForSJTChanges,
    isCurrentOwner,
    isTransferDueToDeath,
    getCurrentOwnerStateById,
    hasCurrentOwnerChanges
  }
}
