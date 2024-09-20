import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeOwnerPartyTypes,
  HomeTenancyTypes,
  MhApiFrozenDocumentTypes,
  MhApiStatusTypes,
  SupportingDocumentsOptions
} from '@/enums'
import { useStore } from '@/store/store'
import {
  MhrHomeOwnerGroupIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'
import { computed, reactive, toRefs } from 'vue'
import { find, isEqual, uniq } from 'lodash'
import { getFeatureFlag, normalizeObject } from '@/utils'
import {
  QSLockedStateUnitNoteTypes,
  transferOwnerPartyTypes,
  transferOwnerPrefillAdditionalName,
  transferSupportingDocumentTypes
} from '@/resources/'
import { storeToRefs } from 'pinia'
import { useHomeOwners } from '@/composables'

/**
 * Composable to handle Ownership functionality and permissions specific to the varying Transfer of Ownership filings.
 * @param enableAllActions A flag to enable and bypass the permission functions. (ie for edge case like MHR)
 */
export const useTransferOwners = (enableAllActions: boolean = false) => {
  const {
    // Actions
    setMhrTransferHomeOwnerGroups,
    setMhrTransferAffidavitCompleted
  } = useStore()
  const {
    // Getters
    hasUnsavedChanges,
    getMhrTransferType,
    getMhrInformation,
    getMhrTransferHomeOwners,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups,
    getMhrTransferAffidavitCompleted,
    isRoleQualifiedSupplierLawyersNotaries
  } = storeToRefs(useStore())
  const {
    getCurrentGroupById
  } = useHomeOwners(true)

  // Enables all Misc and Non Bill of Sale Transfers for Staff
  const isMiscTransfersEnabled: boolean = getFeatureFlag('mhr-misc-transfers-enabled')

  /** Local State for custom computed properties. **/
  const localState = reactive({
    isSOorJT: computed((): boolean => {
      return getMhrTransferCurrentHomeOwnerGroups.value.length === 1 &&
        (getMhrTransferCurrentHomeOwnerGroups.value[0].type === ApiHomeTenancyTypes.SOLE ||
        getMhrTransferCurrentHomeOwnerGroups.value[0].type === ApiHomeTenancyTypes.JOINT)
    })
  })

  const EATOwnerTypes: Array<HomeOwnerPartyTypes> = [
    HomeOwnerPartyTypes.EXECUTOR,
    HomeOwnerPartyTypes.ADMINISTRATOR,
    HomeOwnerPartyTypes.TRUSTEE
  ]

  const isRemovedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.REMOVED
  }

  const isAddedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.ADDED
  }

  const isChangedOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.CHANGED
  }

  /** Returns true when the selected transfer type is a 'due to death' scenario **/
  const isTransferDueToDeath = computed((): boolean => {
    return [
      // transfers types where Owner Groups cannot have the 'Deceased' owners
      // therefore Will Transfer type is not applicable
      ApiTransferTypes.SURVIVING_JOINT_TENANT,
      ApiTransferTypes.TO_ADMIN_NO_WILL,
      ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
      ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    ].includes(getMhrTransferType.value?.transferType)
  })

  /** Returns true when the selected transfer involves Executors or Administrators **/
  const isTransferToExecOrAdmin = computed((): boolean => {
    return [
      // transfers to Executors or Administrators
      ApiTransferTypes.TO_ADMIN_NO_WILL,
      ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
      ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    ].includes(getMhrTransferType.value?.transferType)
  })

  /** Returns true when the selected transfer is Bill Of Sale type **/
  const isTransferBillOfSale = computed((): boolean => {
    return [
      ApiTransferTypes.SALE_OR_GIFT,
      ApiTransferTypes.TRANS_FAMILY_ACT,
      ApiTransferTypes.TRANS_INFORMAL_SALE,
      ApiTransferTypes.TRANS_QUIT_CLAIM,
      ApiTransferTypes.TRANS_RECEIVERSHIP,
      ApiTransferTypes.TRANS_SEVER_GRANT,
      ApiTransferTypes.TRANS_WRIT_SEIZURE
    ].includes(getMhrTransferType.value?.transferType)
  })

  /** Returns true when the selected transfer is subset of Bill Of Sale (minus Gift/Sale transfer) **/
  const isTransferNonGiftBillOfSale = computed((): boolean => {
    return [
      ApiTransferTypes.TRANS_FAMILY_ACT,
      ApiTransferTypes.TRANS_INFORMAL_SALE,
      ApiTransferTypes.TRANS_QUIT_CLAIM,
      ApiTransferTypes.TRANS_RECEIVERSHIP,
      ApiTransferTypes.TRANS_SEVER_GRANT,
      ApiTransferTypes.TRANS_WRIT_SEIZURE
    ].includes(getMhrTransferType.value?.transferType)
  })

  /** Returns true when the selected transfer is not a type of Bill of Sale **/
  const isTransferWithoutBillOfSale = computed((): boolean => {
    return [
      // other types of transfers, that are not Bill of Sale
      ApiTransferTypes.ABAN,
      ApiTransferTypes.BANK,
      ApiTransferTypes.COU,
      ApiTransferTypes.FORE,
      ApiTransferTypes.GENT,
      ApiTransferTypes.TRANS_LAND_TITLE,
      ApiTransferTypes.REIV,
      ApiTransferTypes.REPV,
      ApiTransferTypes.SZL,
      ApiTransferTypes.TAXS,
      ApiTransferTypes.VEST
    ].includes(getMhrTransferType.value?.transferType)
  })

  /** Returns true when the selected transfer type is a 'SALE_OR_GIFT' scenario **/
  const isTransferDueToSaleOrGift = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.SALE_OR_GIFT
  })

  /** Returns true when the selected transfer type is a 'SURVIVING_JOINT_TENANT' scenario **/
  const isTransferToSurvivingJointTenant = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT
  })

  /** Returns true when the selected transfer type is a 'TO_EXECUTOR_PROBATE_WILL' scenario **/
  const isTransferToExecutorProbateWill = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
  })

  /** Returns true when the selected transfer type is a 'TO_EXECUTOR_PROBATE_WILL' scenario **/
  const isTransferToExecutorUnder25Will = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL
  })

  /** Returns true when the selected transfer type is a 'TO_ADMIN_NO_WILL' scenario **/
  const isTransferToAdminNoWill = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.TO_ADMIN_NO_WILL
  })

  /** Returns true when the passed transfer type is a 'TO_EXECUTOR_PROBATE_WILL' type **/
  const isTransAffi = (type: ApiTransferTypes): boolean => {
    return type === ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL
  }

  /** Returns true when Add/Edit Owner name fields should be disabled **/
  const disableNameFields = computed((): boolean => {
    return [
      ApiTransferTypes.SURVIVING_JOINT_TENANT
    ].includes(getMhrTransferType.value?.transferType)
  })

  /** Returns true when ownership structure is joint tenancy /w min 2  owners but not executors, trustees or admins. **/
  const isJointTenancyStructure = computed((): boolean => {
    return getMhrTransferCurrentHomeOwnerGroups.value.some(group => group.type === ApiHomeTenancyTypes.JOINT &&
      group.owners.filter(owner => owner.partyType === HomeOwnerPartyTypes.OWNER_IND ||
        owner.partyType === HomeOwnerPartyTypes.OWNER_BUS).length >= 2
    )
  })

  /** Returns true when ownership structure contains at least 1 group with owners that are not all businesses. **/
  const hasGroupsWithPersonOwners = computed((): boolean => {
    return getMhrTransferCurrentHomeOwnerGroups.value.some(group => group.owners
      .some(owner => owner.partyType !== HomeOwnerPartyTypes.OWNER_BUS)
    )
  })

  /** Conditionally show DeathCertificate based on Transfer Type **/
  const showDeathCertificate = (): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT
  }

  /** Conditionally show Grant of Probate with Will supporting options based on Transfer Type **/
  const showSupportingDocuments = (): boolean => {
    return [
      ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL,
      ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
      ApiTransferTypes.TO_ADMIN_NO_WILL
    ].includes(getMhrTransferType.value?.transferType)
  }

  /** Conditionally Enable HomeOwner Changes based on Transfer Type **/
  const enableHomeOwnerChanges = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TRANS_FAMILY_ACT:
      case ApiTransferTypes.TRANS_INFORMAL_SALE:
      case ApiTransferTypes.TRANS_QUIT_CLAIM:
      case ApiTransferTypes.TRANS_RECEIVERSHIP:
      case ApiTransferTypes.TRANS_SEVER_GRANT:
      case ApiTransferTypes.TRANS_WRIT_SEIZURE:
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:
      case ApiTransferTypes.ABAN:
      case ApiTransferTypes.BANK:
      case ApiTransferTypes.COU:
      case ApiTransferTypes.FORE:
      case ApiTransferTypes.GENT:
      case ApiTransferTypes.TRANS_LAND_TITLE:
      case ApiTransferTypes.REIV:
      case ApiTransferTypes.REPV:
      case ApiTransferTypes.SZL:
      case ApiTransferTypes.TAXS:
      case ApiTransferTypes.VEST:
        return true // Always enable for above transfer types
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        // Check for joint tenancy (at least two owners who are not executors, trustees or admins)
        return isJointTenancyStructure.value
      default:
        return false
    }
  }

  /** Conditionally Enable HomeOwner Additions based on Transfer Type **/
  const enableAddHomeOwners = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      // Bill Of Sale Transfers
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TRANS_FAMILY_ACT:
      case ApiTransferTypes.TRANS_INFORMAL_SALE:
      case ApiTransferTypes.TRANS_QUIT_CLAIM:
      case ApiTransferTypes.TRANS_RECEIVERSHIP:
      case ApiTransferTypes.TRANS_SEVER_GRANT:
      case ApiTransferTypes.TRANS_WRIT_SEIZURE:

      // Transfers Due to Death
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:

      case ApiTransferTypes.ABAN:
      case ApiTransferTypes.BANK:
      case ApiTransferTypes.COU:
      case ApiTransferTypes.FORE:
      case ApiTransferTypes.GENT:
      case ApiTransferTypes.TRANS_LAND_TITLE:
      case ApiTransferTypes.REIV:
      case ApiTransferTypes.REPV:
      case ApiTransferTypes.SZL:
      case ApiTransferTypes.TAXS:
      case ApiTransferTypes.VEST:
        return true
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
      case ApiTransferTypes.TRANS_FAMILY_ACT:
      case ApiTransferTypes.TRANS_INFORMAL_SALE:
      case ApiTransferTypes.TRANS_QUIT_CLAIM:
      case ApiTransferTypes.TRANS_RECEIVERSHIP:
      case ApiTransferTypes.TRANS_SEVER_GRANT:
      case ApiTransferTypes.TRANS_WRIT_SEIZURE:
      case ApiTransferTypes.ABAN:
      case ApiTransferTypes.BANK:
      case ApiTransferTypes.COU:
      case ApiTransferTypes.FORE:
      case ApiTransferTypes.GENT:
      case ApiTransferTypes.TRANS_LAND_TITLE:
      case ApiTransferTypes.REIV:
      case ApiTransferTypes.REPV:
      case ApiTransferTypes.SZL:
      case ApiTransferTypes.TAXS:
      case ApiTransferTypes.VEST:
        // Enable for all but FROZEN status due to Affe
        return !(getMhrInformation.value.statusType === MhApiStatusTypes.FROZEN &&
          getMhrInformation.value?.frozenDocumentType === MhApiFrozenDocumentTypes.TRANS_AFFIDAVIT)
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
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
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
        // Disable Owner actions for Executors and Admins in Trans Affi - Staff Only Transfer
        return ![HomeOwnerPartyTypes.EXECUTOR, HomeOwnerPartyTypes.ADMINISTRATOR].includes(owner.partyType) &&
          !groupHasAllBusinesses(getCurrentGroupById(owner.groupId))
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:
        return !groupHasAllBusinesses(getCurrentGroupById(owner.groupId))
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TRANS_FAMILY_ACT:
      case ApiTransferTypes.TRANS_INFORMAL_SALE:
      case ApiTransferTypes.TRANS_QUIT_CLAIM:
      case ApiTransferTypes.TRANS_RECEIVERSHIP:
      case ApiTransferTypes.TRANS_SEVER_GRANT:
      case ApiTransferTypes.TRANS_WRIT_SEIZURE:
      case ApiTransferTypes.ABAN:
      case ApiTransferTypes.BANK:
      case ApiTransferTypes.COU:
      case ApiTransferTypes.FORE:
      case ApiTransferTypes.GENT:
      case ApiTransferTypes.TRANS_LAND_TITLE:
      case ApiTransferTypes.REIV:
      case ApiTransferTypes.REPV:
      case ApiTransferTypes.SZL:
      case ApiTransferTypes.TAXS:
      case ApiTransferTypes.VEST:
        return true // Always enable for above transfer types
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        // Check for joint tenancy (at least two owners who are not executors, trustees or admins)
        // Disable If the owners group contains 1 or more businesses for Lawyers and Notaries
        const groupContainsBusinessOwners = getCurrentGroupById(owner.groupId)?.owners.some(
          owner => owner.partyType === HomeOwnerPartyTypes.OWNER_BUS
        )
        return owner.type === ApiHomeTenancyTypes.JOINT &&
          !(isRoleQualifiedSupplierLawyersNotaries.value && groupContainsBusinessOwners)
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
      case ApiTransferTypes.TRANS_FAMILY_ACT:
      case ApiTransferTypes.TRANS_INFORMAL_SALE:
      case ApiTransferTypes.TRANS_QUIT_CLAIM:
      case ApiTransferTypes.TRANS_RECEIVERSHIP:
      case ApiTransferTypes.TRANS_SEVER_GRANT:
      case ApiTransferTypes.TRANS_WRIT_SEIZURE:
      case ApiTransferTypes.ABAN:
      case ApiTransferTypes.BANK:
      case ApiTransferTypes.COU:
      case ApiTransferTypes.FORE:
      case ApiTransferTypes.GENT:
      case ApiTransferTypes.TRANS_LAND_TITLE:
      case ApiTransferTypes.REIV:
      case ApiTransferTypes.REPV:
      case ApiTransferTypes.SZL:
      case ApiTransferTypes.TAXS:
      case ApiTransferTypes.VEST:
        return false // Disable for Sale or Gift
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
        return owner.action === ActionTypes.ADDED
      case ApiTransferTypes.SURVIVING_JOINT_TENANT:
        // Check for joint tenancy (at least two owners who are not executors, trustees or admins)
        return owner.type === ApiHomeTenancyTypes.JOINT
      default:
        return false
    }
  }

  /** Conditionally Enable HomeOwner Delete All Owners/Groups based on Transfer Type **/
  const enableDeleteAllGroupsActions = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:
        return false // Disable for above transfer types
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TRANS_FAMILY_ACT:
      case ApiTransferTypes.TRANS_INFORMAL_SALE:
      case ApiTransferTypes.TRANS_QUIT_CLAIM:
      case ApiTransferTypes.TRANS_RECEIVERSHIP:
      case ApiTransferTypes.TRANS_SEVER_GRANT:
      case ApiTransferTypes.TRANS_WRIT_SEIZURE:
        return !(getMhrInformation.value.statusType === MhApiStatusTypes.FROZEN &&
          getMhrInformation.value?.frozenDocumentType === MhApiFrozenDocumentTypes.TRANS_AFFIDAVIT)
      default:
        return true
    }
  }

  /** Return true if the specified owners group does not contain the executor or administrator **/
  const isDisabledForSoGChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.SALE_OR_GIFT &&
      getMhrInformation.value.statusType === MhApiStatusTypes.FROZEN &&
      !QSLockedStateUnitNoteTypes.includes(getMhrInformation.value?.frozenDocumentType)) {
      const mostRecentExecutorOrAdmin = getMostRecentExecutorOrAdmin(getMhrTransferHomeOwnerGroups.value)
      return mostRecentExecutorOrAdmin.groupId !== owner.groupId
    }
    return false
  }

  /**
   * Retrieves the executor or administrator with the highest ownerId from a list of owner groups.
   *
   * @param {Array<MhrHomeOwnerGroupIF>} ownerGroups - The list of owner groups to search through.
   * @returns {MhrRegistrationHomeOwnerIF} - The executor or administrator with the highest ownerId.
   */
  const getMostRecentExecutorOrAdmin = (ownerGroups: Array<MhrHomeOwnerGroupIF>): MhrRegistrationHomeOwnerIF => {
    return ownerGroups
      .flatMap(group => group.owners) // Combine all owners into a single array
      .filter(owner => owner.partyType === HomeOwnerPartyTypes.EXECUTOR ||
        owner.partyType === HomeOwnerPartyTypes.ADMINISTRATOR) // Keep only executors or admins
      .reduce((highest: any, owner: any) => {
        return owner.ownerId > highest.ownerId ? owner : highest
      }, { ownerId: -Infinity }) // Find the executor with the highest ownerId
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

  // Disable Delete button for all Owners that are not in the Group of initially deleted owner (WILL transfer flow)
  const isDisabledForWillChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL ||
        getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL ||
        getMhrTransferType.value?.transferType === ApiTransferTypes.TO_ADMIN_NO_WILL) {
      const hasDeletedOwners = getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      const isDeletedOwnersInGroup = getMhrTransferHomeOwnerGroups.value.find(group =>
        group.groupId === owner.groupId).owners.some(owner => owner.action === ActionTypes.REMOVED)

      const partyType = isTransferToAdminNoWill.value ? HomeOwnerPartyTypes.ADMINISTRATOR : HomeOwnerPartyTypes.EXECUTOR

      return (hasDeletedOwners && !isDeletedOwnersInGroup) ||
        // in case of Undo, still disable Delete button
        ((hasUnsavedChanges.value && !hasDeletedOwners) && !hasAddedPartyTypeToGroup(owner.groupId, partyType))
    }
    return false
  }

  // Return true if all owners in all groups are removed
  const hasAllOwnersRemoved = (): boolean => {
    return getMhrTransferHomeOwners.value.every(owner =>
      owner.action === ActionTypes.REMOVED)
  }

  // Return true if there is only one group of owners
  const hasOnlyOneGroupOfOwners = (): boolean => {
    return getMhrTransferHomeOwnerGroups.value.length === 1
  }

  // Transfer Due to Sale or Gift flow and all the related conditions/logic
  const TransSaleOrGift: any = {
    isValidTransfer: computed((): boolean => {
      const allGroupsValid = getMhrTransferHomeOwnerGroups.value.every(group =>
        TransSaleOrGift.isGroupValid(group.groupId))

      return !TransSaleOrGift.hasMixedOwners.value && allGroupsValid
    }),
    isGroupValid: (groupId): boolean => {
      return !(
        TransSaleOrGift.hasMixedOwnersInGroup(groupId) ||
        TransSaleOrGift.hasPartlyRemovedEATOwners(groupId) ||
        (TransSaleOrGift.hasAllCurrentOwnersRemoved(groupId) && !TransSaleOrGift.hasAddedOwners(groupId)) ||
        !getMhrTransferHomeOwnerGroups.value?.some(group =>
          group.owners.filter(owner => owner.action !== ActionTypes.REMOVED)?.length)
      )
    },
    hasMixedOwners: computed((): boolean => {
      return !getMhrTransferHomeOwnerGroups.value
        .every((group: MhrRegistrationHomeOwnerGroupIF) =>
          !TransSaleOrGift.hasMixedOwnersInGroup(group.groupId))
    }),
    hasMixedOwnersInGroup: (groupId: number): boolean => {
      const ownerTypes: HomeOwnerPartyTypes[] = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .filter(owner => owner.action !== ActionTypes.REMOVED)
        .map(owner =>
          // workaround to treat IND and BUS owners the same (not unique roles)
          owner.partyType === HomeOwnerPartyTypes.OWNER_BUS ? HomeOwnerPartyTypes.OWNER_IND : owner.partyType)
      return ownerTypes.length === 1 ? false : uniq(ownerTypes).length > 1
    },
    hasPartlyRemovedEATOwners: (groupId: number): boolean => {
      // check if there are more than one Exec, Admin, Trustee owner that is not deleted
      const ownerTypes: MhrRegistrationHomeOwnerIF[] = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .filter(owner => EATOwnerTypes.includes(owner.partyType))

      const hasOneDeleted: boolean = !!find(ownerTypes, { action: ActionTypes.REMOVED })
      const hasSomeNotDeleted: boolean = ownerTypes.filter(owner => owner.action !== ActionTypes.REMOVED).length >= 1

      return hasOneDeleted && hasSomeNotDeleted
    },
    hasAllCurrentOwnersRemoved: (groupId): boolean => {
      const group: MhrHomeOwnerGroupIF = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId)

      // for newly Added or Deleted groups do not check for current owners
      if ([ActionTypes.ADDED, ActionTypes.REMOVED].includes(group.action)) return false

      if (group.owners?.length === 0) return true

      return group.owners
        .every(owner => isCurrentOwner(owner)
          ? owner.action === ActionTypes.REMOVED
          : owner.action === ActionTypes.ADDED)
    },
    hasAddedOwners: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId)
        .owners.some(owner => owner.action === ActionTypes.ADDED)
    }
  }

  // Transfer Will flow and all the related conditions/logic
  const TransToExec: any = {
    // based on the current/active transfer type, get the corresponding supporting document
    getSupportingDocForActiveTransfer: (): ApiTransferTypes => {
      return transferSupportingDocumentTypes[getMhrTransferType.value?.transferType]
    },
    isValidTransfer: computed((): boolean => {
      // check if there is a group that is valid for WILL transfer
      const groupWithDeletedOwners: MhrRegistrationHomeOwnerGroupIF = getMhrTransferHomeOwnerGroups.value?.find(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      if (!groupWithDeletedOwners) {
        const groupWithAddedOwner = getMhrTransferHomeOwnerGroups.value?.find(group =>
          group.owners.some(owner => owner.action === ActionTypes.ADDED))

        // if there are no groups with deleted owners, check if all owners are of the same type
        // if owners are same type, then group is valid
        const hasSameOwnerTypesInGroup = groupWithAddedOwner?.owners.every(owner =>
          owner.partyType === transferOwnerPartyTypes[getMhrTransferType.value?.transferType])

        return !!hasSameOwnerTypesInGroup
      }

      const isValidGroup = TransToExec.isValidGroup(groupWithDeletedOwners)
      const hasOwnersWithoutDeathCert = !TransToExec.isAllGroupOwnersWithDeathCerts(groupWithDeletedOwners.groupId)

      return isValidGroup && hasOwnersWithoutDeathCert
    }),
    isValidGroup: (group: MhrRegistrationHomeOwnerGroupIF): boolean => {
      const isValidAddedOwner = group.owners.every((owner: MhrRegistrationHomeOwnerIF) => {
        return isCurrentOwner(owner) ? TransToExec.hasValidSupportDocs(owner) : owner.action === ActionTypes.ADDED
      })
      // Group has at least one Executor
      const hasAddedExecutor = group.owners.some((owner: MhrRegistrationHomeOwnerIF) =>
        owner.action !== ActionTypes.REMOVED && owner.partyType === HomeOwnerPartyTypes.EXECUTOR)

      return isValidAddedOwner && hasAddedExecutor && TransToExec.hasAllCurrentOwnersRemoved(group.groupId)
    },
    hasOwnersWithValidSupportDocs: (groupId: number): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .every((owner: MhrRegistrationHomeOwnerIF) => {
          return TransToExec.hasValidSupportDocs(owner)
        })
    },
    // check if supportingDocument is either Death Certificate or Grant of Probate
    hasValidSupportDocs: (owner: MhrRegistrationHomeOwnerIF): boolean => {
      if (!owner.action || owner.action === ActionTypes.ADDED) return true

      // if deleted Exec, Admin or Trustee, then docs are not required and are valid
      if (owner.action === ActionTypes.REMOVED && EATOwnerTypes.includes(owner.partyType)) return true

      let hasValidSupportingDoc = false

      if (owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT ||
        owner.supportingDocument === SupportingDocumentsOptions.AFFIDAVIT) {
        hasValidSupportingDoc = owner.hasDeathCertificate &&
          !!owner.deathCertificateNumber && owner.deathCertificateNumber?.length <= 20 && !!owner.deathDateTime
      } else if (owner.partyType === HomeOwnerPartyTypes.OWNER_BUS) {
        hasValidSupportingDoc = !!owner.deathCorpNumber && !!owner.deathDateTime
      } else {
        hasValidSupportingDoc = owner.supportingDocument === TransToExec.getSupportingDocForActiveTransfer()
      }
      return hasValidSupportingDoc && owner.action === ActionTypes.REMOVED
    },
    hasOnlyOneOwnerInGroup: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .filter(owner => owner.action !== ActionTypes.ADDED)
        .length === 1
    },
    hasAddedExecutorsInGroup: (groupId): boolean => hasAddedPartyTypeToGroup(groupId, HomeOwnerPartyTypes.EXECUTOR),
    hasAllCurrentOwnersRemoved: (groupId): boolean => {
      const regOwners = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        // Filter as Execs, Admins and Trustees doest not have to be removed in order to have a valid group
        .filter(owner => [HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS]
          .includes(owner.partyType))

      if (regOwners?.length === 0) return true

      return regOwners
        .every(owner => isCurrentOwner(owner)
          ? owner.action === ActionTypes.REMOVED
          : owner.action === ActionTypes.ADDED)
    },
    hasSomeOwnersRemoved: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .some(owner => owner.action === ActionTypes.REMOVED)
    },
    hasAtLeastOneExecInGroup: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .some(owner => owner.action !== ActionTypes.REMOVED &&
          owner.partyType === HomeOwnerPartyTypes.EXECUTOR)
    },
    hasOwnerWithDeathCertificate: (): boolean => {
      return getMhrTransferHomeOwners.value.some(owner =>
        owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT)
    },
    // Check if all Owners within a group have Death Certificate as a supporting document
    isAllGroupOwnersWithDeathCerts: (groupId): boolean => {
      return getMhrTransferHomeOwners.value
        .filter(owner => owner.groupId === groupId && owner.action !== ActionTypes.ADDED)
        .every(owner => {
          return owner.action === ActionTypes.REMOVED &&
            // Ensure owner is an individual before checking death certificate
            (owner.partyType === HomeOwnerPartyTypes.OWNER_BUS ||
            // Affidavit type also has Death Certificate
            owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT)
        })
    },
    // Check if there's a deleted Owner with selected
    // Grant of Probate or Affidavit or Admin Grant as a supporting document.
    hasDeletedOwnersWithProbateGrantOrAffidavit: (): boolean => {
      return getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner =>
          (owner.action === ActionTypes.REMOVED &&
          [HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS].includes(owner.partyType) &&
          owner.supportingDocument === TransToExec.getSupportingDocForActiveTransfer()) ||
          (owner.action === ActionTypes.REMOVED && EATOwnerTypes.includes(owner.partyType)))
      )
    },
    prefillOwnerAsExecOrAdmin: (owner: MhrRegistrationHomeOwnerIF): void => {
      const transferType = getMhrTransferType.value?.transferType
      const allOwners = getMhrTransferHomeOwners.value
      const deletedOwnerGroup = find(getMhrTransferHomeOwnerGroups.value, { owners: [{ action: ActionTypes.REMOVED }] })

      // first try to find the deleted reg owner
      let deletedOwner: MhrRegistrationHomeOwnerIF = find(deletedOwnerGroup.owners, {
        action: ActionTypes.REMOVED,
        supportingDocument: TransToExec.getSupportingDocForActiveTransfer()
      })

      // if reg owner is not found, check for Exec, Admin, or Trustee
      if (!deletedOwner) {
        deletedOwner = find(deletedOwnerGroup.owners, { action: ActionTypes.REMOVED })
      }

      // prefill Description field Execs, Admin, Trustees have description as Additional Name
      let desc = ''
      if ([HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS].includes(deletedOwner.partyType)) {
        // if reg or business owner is deleted, prefill the additional name (suffix) with the name of the deleted owner
        const { first, middle, last } = deletedOwner.individualName || {}

        desc = deletedOwner.organizationName?.length > 0
          ? transferOwnerPrefillAdditionalName[transferType] + deletedOwner.organizationName
          : transferOwnerPrefillAdditionalName[transferType] +
            [first, middle, last].filter(Boolean).join(' ') +
            ', deceased'
      } else {
        // if executor, admin or trustee, copy the additional name (suffix) from the suffix of deleted owner
        desc = deletedOwner.description
      }

      Object.assign(owner, {
        ownerId: allOwners.length + 1,
        description: desc,
        partyType: transferOwnerPartyTypes[transferType],
        groupId: deletedOwnerGroup.groupId // new Owner will be added to the same group as deleted Owner
      } as MhrRegistrationHomeOwnerIF)
    },
    // find owners that 1. belong to groupId, 2. that are also removed, 3. have Grant of Probate as supporting document
    // switch their supporting document to Death Certificate if they have Grant of Probate selected
    resetGrantOfProbate: (groupId, excludedOwnerId) => {
      getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .forEach((owner: MhrRegistrationHomeOwnerIF) => {
          if (owner.action === ActionTypes.REMOVED && owner.ownerId !== excludedOwnerId &&
          owner.supportingDocument === TransToExec.getSupportingDocForActiveTransfer()) {
            owner.supportingDocument = SupportingDocumentsOptions.DEATH_CERT
          }
        })
    }
  }

  const TransJointTenants = {
    isValidTransfer: computed((): boolean => {
      const groupWithDeletedOwners: MhrRegistrationHomeOwnerGroupIF = getMhrTransferHomeOwnerGroups.value?.find(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      if (!groupWithDeletedOwners) return false

      const isValidGroup = groupWithDeletedOwners.owners
        .filter(owner => owner.action === ActionTypes.REMOVED)
        .every(
          owner =>
            // Deceased owner validations
            (owner.hasDeathCertificate &&
            !!owner.deathCertificateNumber &&
            owner.deathCertificateNumber?.length <= 20 &&
            !!owner.deathDateTime) ||
            // Historical owner validations
            (!!owner.deathCorpNumber && owner.deathCorpNumber?.length <= 20 && !!owner.deathDateTime)
        )
      const hasLivingOwners = !groupWithDeletedOwners.owners.every(owner => owner.action === ActionTypes.REMOVED)

      return isValidGroup && hasLivingOwners
    })
  }

  // Transfer Affidavit flow and all the related conditions/logic
  const TransAffidavit = {
    setCompleted: (completed: boolean): void => {
      setMhrTransferAffidavitCompleted(completed)
    },
    isCompleted: (): boolean => {
      return getMhrTransferAffidavitCompleted.value
    },
    getGroupIdWithExecutor: (): number => {
      return getMhrTransferHomeOwnerGroups.value.find(group =>
        group.owners.some(owner => owner.partyType === HomeOwnerPartyTypes.EXECUTOR)
      ).groupId
    }
  }

  const TransToAdmin = {
    isValidTransfer: computed((): boolean => {
      const groupWithDeletedOwners: MhrRegistrationHomeOwnerGroupIF = getMhrTransferHomeOwnerGroups.value?.find(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      if (!groupWithDeletedOwners) return false
      return TransToAdmin.hasAtLeastOneAdminInGroup(groupWithDeletedOwners.groupId) &&
        TransToAdmin.hasAllCurrentOwnersRemoved(groupWithDeletedOwners.groupId)
    }),
    hasAddedAdministratorsInGroup: (groupId): boolean =>
      hasAddedPartyTypeToGroup(groupId, HomeOwnerPartyTypes.ADMINISTRATOR),
    hasAtLeastOneAdminInGroup: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .some(owner => owner.action !== ActionTypes.REMOVED &&
          owner.partyType === HomeOwnerPartyTypes.ADMINISTRATOR)
    },
    hasAllCurrentOwnersRemoved: (groupId): boolean => {
      const regOwners = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        // Filter as Execs, Admins and Trustees doest not have to be removed in order to have a valid group
        .filter(owner => [HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS]
          .includes(owner.partyType))

      if (regOwners?.length === 0) return true

      return regOwners
        .every(owner => isCurrentOwner(owner)
          ? owner.action === ActionTypes.REMOVED
          : owner.action === ActionTypes.ADDED)
    }
  }

  const TransWithoutBillOfSale = {
    hasAllCurrentOwnersRemoved: (groupId): boolean => {
      const regOwners = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners

      if (regOwners?.length === 0) return true

      return regOwners
        .every(owner => isCurrentOwner(owner)
          ? owner.action === ActionTypes.REMOVED
          : owner.action === ActionTypes.ADDED)
    },
  }

  // For WIll and LETA Transfers, at least one Exec or Admin is required to proceed
  // Used for hiding group message (that all owners must be removed)
  const hasMinOneExecOrAdminInGroup = (groupId) => {
    if (isTransferToExecutorProbateWill.value || isTransferToExecutorUnder25Will.value) {
      return TransToExec.hasAtLeastOneExecInGroup(groupId)
    } else if (isTransferToAdminNoWill.value) {
      return TransToAdmin.hasAtLeastOneAdminInGroup(groupId)
    }
    return false
  }

  /** Return true if the specified owner is part of the current/base ownership structure **/
  const isCurrentOwner = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    return getMhrTransferCurrentHomeOwnerGroups.value.some(group =>
      group.owners.some(baseOwner => baseOwner.ownerId === owner.ownerId)
    )
  }

  /** Return true when all CURRENT owners of a group have been removed and some owners added in a SO/JT structure. **/
  const groupHasRemovedAllCurrentOwners = (group: MhrRegistrationHomeOwnerGroupIF) => {
    const owners = group.owners

    return localState.isSOorJT && owners.some(owner => owner.action === ActionTypes.ADDED) &&
        owners.every(owner => !!owner.action)
  }

  /** Remove current owners from existing ownership and move them to New Previous Owners group.  **/
  const moveCurrentOwnersToPreviousOwners = async (group: MhrRegistrationHomeOwnerGroupIF) => {
    // Retrieve and mark for removal all current owners
    const currentOwners = group?.owners.filter(owner => owner.action !== ActionTypes.ADDED)
      .map(owner => { return { ...owner, action: ActionTypes.REMOVED } })

    // Get current ownership structure and modify group ids and remove current owners
    const updatedGroups = getMhrTransferHomeOwnerGroups.value.map(group => {
      return {
        ...group,
        groupId: group.groupId + 1,
        owners: group.owners.filter(owner => owner.action !== ActionTypes.REMOVED)
      }
    })

    // Create a new ownership group defaulted to REMOVED
    const previousOwnersGroup: MhrRegistrationHomeOwnerGroupIF = {
      groupId: 1,
      interest: 'Undivided',
      interestDenominator: null,
      interestNumerator: null,
      owners: currentOwners,
      tenancySpecified: true,
      type: HomeTenancyTypes.NA,
      action: ActionTypes.REMOVED
    }
    updatedGroups.unshift(previousOwnersGroup)

    // When a user edits the current group before removing all current owners - update the action to ADDED
    const updatedGroup = updatedGroups.find(updatedGroup => updatedGroup.groupId === group.groupId + 1)
    if (groupHasAllAddedOwners(updatedGroup)) {
      updatedGroup.action = ActionTypes.ADDED
    }

    // Set new ownership structure to store
    await setMhrTransferHomeOwnerGroups(updatedGroups)
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

  /**
   * Return the base owners original groupId by owner id.
   * @param ownerId The owner identifier
   */
  const getCurrentOwnerGroupIdByOwnerId = (ownerId: number): MhrRegistrationHomeOwnerIF => {
    let currentOwnerGroupId
    getMhrTransferCurrentHomeOwnerGroups.value.forEach(group => group.owners.find(owner => {
      if (owner.ownerId === ownerId) currentOwnerGroupId = group.groupId
    }))

    return currentOwnerGroupId
  }

  /** Return true if the specified owner has been modified from current state **/
  const hasCurrentOwnerChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    const currentOwner = getCurrentOwnerStateById(owner.ownerId)
    const isEqualAddress = isEqual(normalizeObject(currentOwner?.address), normalizeObject(owner.address))
    const isEqualPhone = normalizeObject(currentOwner)?.phoneNumber === normalizeObject(owner).phoneNumber &&
      normalizeObject(currentOwner)?.phoneExtension === normalizeObject(owner).phoneExtension

    return currentOwner && (!isEqualAddress || !isEqualPhone)
  }

  /** Return true if the specified group has been modified from current state **/
  const hasCurrentGroupChanges =
    (group: MhrRegistrationHomeOwnerGroupIF, fractionalData: MhrRegistrationFractionalOwnershipIF): boolean => {
      const isEqualNumerator = isEqual(group?.interestNumerator, fractionalData.interestNumerator)
      const isEqualDenominator = isEqual(group?.interestDenominator, fractionalData.interestDenominator)

      return group && (!isEqualNumerator || !isEqualDenominator)
    }

  /** Return true if a member of a specified partyType has been added to the group **/
  const hasAddedPartyTypeToGroup = (groupId: number, partyType: HomeOwnerPartyTypes): boolean => {
    const isEAT = [
      HomeOwnerPartyTypes.EXECUTOR,
      HomeOwnerPartyTypes.ADMINISTRATOR,
      HomeOwnerPartyTypes.TRUSTEE
    ].includes(partyType)

    return getMhrTransferHomeOwnerGroups.value
      .find(group => group.groupId === groupId)
      .owners.some(owner =>
        owner.partyType === partyType && isEAT
          ? owner.action !== ActionTypes.REMOVED
          : owner.action === ActionTypes.ADDED
      )
  }

  /** Return true if all owners in the group have been added **/
  const groupHasAllAddedOwners = (group: MhrHomeOwnerGroupIF) => {
    return group?.owners?.every(owner => owner.action === ActionTypes.ADDED)
  }

  /** Return true if all owners in the group are Businesses **/
  const groupHasAllBusinesses = (group: MhrHomeOwnerGroupIF) => {
    return group?.owners?.every(owner => owner.partyType === HomeOwnerPartyTypes.OWNER_BUS)
  }

  return {
    isMiscTransfersEnabled,
    isAddedHomeOwnerGroup,
    isRemovedHomeOwnerGroup,
    isChangedOwnerGroup,
    enableHomeOwnerChanges,
    enableTransferOwnerGroupActions,
    enableTransferOwnerActions,
    enableTransferOwnerMenuActions,
    enableAddHomeOwners,
    enableDeleteAllGroupsActions,
    showDeathCertificate,
    showSupportingDocuments,
    isDisabledForSoGChanges,
    isDisabledForSJTChanges,
    isDisabledForWillChanges,
    hasAllOwnersRemoved,
    hasOnlyOneGroupOfOwners,
    TransSaleOrGift,
    TransToExec, // Transfer Due to Death - Grant of Probate (with Will)
    TransJointTenants,
    TransAffidavit, // Transfer to Executor under $25k - Affidavit
    TransToAdmin,
    TransWithoutBillOfSale,
    isTransAffi,
    isCurrentOwner,
    getMhrTransferType,
    isTransferDueToDeath,
    isTransferToExecOrAdmin,
    isTransferBillOfSale,
    isTransferNonGiftBillOfSale,
    isTransferWithoutBillOfSale,
    isTransferDueToSaleOrGift,
    isTransferToSurvivingJointTenant,
    isTransferToExecutorProbateWill,
    isTransferToExecutorUnder25Will,
    isTransferToAdminNoWill,
    disableNameFields,
    isJointTenancyStructure,
    getCurrentOwnerStateById,
    groupHasAllAddedOwners,
    groupHasAllBusinesses,
    hasGroupsWithPersonOwners,
    groupHasRemovedAllCurrentOwners,
    getCurrentOwnerGroupIdByOwnerId,
    hasCurrentOwnerChanges,
    hasCurrentGroupChanges,
    moveCurrentOwnersToPreviousOwners,
    hasMinOneExecOrAdminInGroup,
    getMostRecentExecutorOrAdmin,
    ...toRefs(localState)
  }
}
