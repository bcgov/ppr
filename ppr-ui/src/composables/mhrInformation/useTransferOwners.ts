import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeOwnerPartyTypes,
  HomeTenancyTypes,
  SupportingDocumentsOptions
} from '@/enums'
import { useActions, useGetters } from 'vuex-composition-helpers'
import {
  MhrHomeOwnerGroupIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'
import { computed, reactive, toRefs } from '@vue/composition-api'
import { isEqual, find } from 'lodash'
import { normalizeObject } from '@/utils'
import { useHomeOwners } from '@/composables'

/**
 * Composable to handle Ownership functionality and permissions specific to the varying Transfer of Ownership filings.
 * @param enableAllActions A flag to enable and bypass the permission functions. (ie for edge case like MHR)
 */
export const useTransferOwners = (enableAllActions: boolean = false) => {
  const {
    hasUnsavedChanges,
    getMhrTransferType,
    getMhrTransferHomeOwners,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups
  } = useGetters<any>([
    'hasUnsavedChanges',
    'getMhrTransferType',
    'getMhrTransferHomeOwners',
    'getMhrTransferHomeOwnerGroups',
    'getMhrTransferCurrentHomeOwnerGroups'
  ])

  const {
    setMhrTransferHomeOwnerGroups
  } = useActions<any>([
    'setMhrTransferHomeOwnerGroups'
  ])

  const {
    getGroupById,
    getCurrentGroupById
  } = useHomeOwners(true)

  /** Local State for custom computed properties. **/
  const localState = reactive({
    isSOorJT: computed((): boolean => {
      return getMhrTransferCurrentHomeOwnerGroups.value.length === 1 &&
        (getMhrTransferCurrentHomeOwnerGroups.value[0].type === ApiHomeTenancyTypes.SOLE ||
        getMhrTransferCurrentHomeOwnerGroups.value[0].type === ApiHomeTenancyTypes.JOINT)
    })
  })

  /** Returns true when the selected transfer type is a 'due to death' scenario **/
  const isTransferDueToDeath = computed((): boolean => {
    return [
      // transfers types where Owner Groups cannot have the 'Deceased' owners
      // therefore Will Transfer type is not applicable
      ApiTransferTypes.SURVIVING_JOINT_TENANT,
      ApiTransferTypes.TO_ADMIN_PROBATE_NO_WILL,
      ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
      ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    ].includes(getMhrTransferType.value?.transferType)
  })

  const isRemovedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.REMOVED
  }

  const isAddedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.ADDED
  }

  const isChangedOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.CHANGED
  }

  /** Returns true when the selected transfer type is a 'TO_EXECUTOR_PROBATE_WILL' scenario **/
  const isTransferToExecutorProbateWill = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
  })

  /** Returns true when the selected transfer type is a 'SURVIVING_JOINT_TENANT' scenario **/
  const isTransferToSurvivingJointTenant = computed((): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT
  })

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

  /** Conditionally show DeathCertificate based on Transfer Type **/
  const showDeathCertificate = (): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT ||
           getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL
  }

  /** Conditionally show Grant of Probate with Will supporting options based on Transfer Type **/
  const showSupportingDocuments = (): boolean => {
    return getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
  }

  /** Conditionally Enable HomeOwner Changes based on Transfer Type **/
  const enableHomeOwnerChanges = (): boolean => {
    // Manual override to force enable all actions (ie MhRegistrations)
    if (enableAllActions) return true

    switch (getMhrTransferType.value?.transferType) {
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
        return true // Always enable for Sale or Gift
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
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
        return true // Always enable for Sale or Gift and Executor Will
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
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
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
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
        return true // Always enable for Sale or Gift and Executor Will
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
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
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
        return false // Disable for Grant of Probate with Will
      default:
        return true
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

  // Disable Delete button for all Owners that are not in the Group of initially deleted owner (WILL transfer flow)
  const isDisabledForWillChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL) {
      const hasDeletedOwners = getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      const isDeletedOwnersInGroup = getMhrTransferHomeOwnerGroups.value.find(group =>
        group.groupId === owner.groupId).owners.some(owner => owner.action === ActionTypes.REMOVED)

      const hasAddedExecutorInGroup = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === owner.groupId).owners
        .some(owner => owner.partyType === HomeOwnerPartyTypes.EXECUTOR)

      return (hasDeletedOwners && !isDeletedOwnersInGroup) ||
        // in case of Undo, still disable Delete button
        ((hasUnsavedChanges.value && !hasDeletedOwners) && !hasAddedExecutorInGroup)
    }
    return false
  }

  // Transfer Will flow and all the related conditions/logic
  const TransWill: any = {
    isValidTransfer: computed((): boolean => {
      // check if there is a group that is valid for WILL transfer
      return getMhrTransferHomeOwnerGroups.value.some(group => TransWill.isValidGroup(group))
    }),
    isValidGroup: (group: MhrRegistrationHomeOwnerGroupIF): boolean => {
      const isValidAddedOwner = group.owners.every((owner: MhrRegistrationHomeOwnerIF) => {
        return isCurrentOwner(owner) ? TransWill.hasValidSupportDocs(owner) : owner.action === ActionTypes.ADDED
      })
      // Group has at least one Executor
      const hasAddedExecutor = group.owners.some((owner: MhrRegistrationHomeOwnerIF) =>
        owner.action === ActionTypes.ADDED && owner.partyType === HomeOwnerPartyTypes.EXECUTOR)
      return isValidAddedOwner && hasAddedExecutor
    },
    // check if supportingDocument is either Death Certificate or Grant of Probate
    hasValidSupportDocs: (owner: MhrRegistrationHomeOwnerIF): boolean => {
      let hasValidDeathCertOrProbateGrant = false
      if (owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT) {
        hasValidDeathCertOrProbateGrant = owner.hasDeathCertificate &&
          !!owner.deathCertificateNumber && !!owner.deathDateTime
      } else {
        hasValidDeathCertOrProbateGrant = owner.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT
      }
      return hasValidDeathCertOrProbateGrant && owner.action === ActionTypes.REMOVED
    },
    hasOnlyOneOwnerInGroup: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .filter(owner => owner.action !== ActionTypes.ADDED)
        .length === 1
    },
    hasExecutorsInGroup: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .some(owner => owner.partyType === HomeOwnerPartyTypes.EXECUTOR)
    },
    hasAllCurrentOwnersRemoved: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .every(owner => isCurrentOwner(owner)
          ? TransWill.hasValidSupportDocs(owner)
          : owner.action === ActionTypes.ADDED)
    },
    hasSomeOwnersRemoved: (groupId): boolean => {
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .some(owner => owner.action === ActionTypes.REMOVED)
    },
    hasOwnerWithDeathCertificate: (): boolean => {
      return getMhrTransferHomeOwners.value.some(owner =>
        owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT)
    },
    // Check if there's a deleted Owner with selected Grant of Probate as a supporting document.
    hasDeletedOwnersWithProbateGrant: (): boolean => {
      return getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner => owner.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT)
      )
    },
    prefillOwnerAsExecutor: (owner: MhrRegistrationHomeOwnerIF): void => {
      const allOwners = getMhrTransferHomeOwners.value
      const deletedOwnerGroup = find(getMhrTransferHomeOwnerGroups.value, { owners: [{ action: ActionTypes.REMOVED }] })
      const deletedOwner = find(deletedOwnerGroup.owners, { action: ActionTypes.REMOVED, supportingDocument: SupportingDocumentsOptions.PROBATE_GRANT }) as MhrRegistrationHomeOwnerIF

      Object.assign(owner, {
        ownerId: allOwners.length + 1,
        suffix: deletedOwner.individualName
          ? 'Executor of the will of ' + Object.values(deletedOwner.individualName).join(' ')
          : 'Executor of the will of ' + owner.organizationName,
        partyType: HomeOwnerPartyTypes.EXECUTOR,
        groupId: deletedOwnerGroup.groupId // new Owner will be added to the same group as deleted Owner
      } as MhrRegistrationHomeOwnerIF)
    },
    updateExecutorSuffix: (): boolean => {
      const deceasedOwners = getMhrTransferHomeOwners.value
        .filter(owner => owner.action === ActionTypes.REMOVED && owner.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT)

      return TransWill.addRemoveExecutorSuffix(deceasedOwners[0] || null)
    },
    // find owners that 1. belong to groupId, 2. that are also removed, 3. have Grant of Probate as supporting document
    // switch their supporting document to Death Certificate if they have Grant of Probate selected
    resetGrantOfProbate: (groupId, excludedOwnerId) => {
      getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .forEach((owner: MhrRegistrationHomeOwnerIF) => {
          if (owner.action === ActionTypes.REMOVED && owner.ownerId !== excludedOwnerId &&
          owner.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT) {
            owner.supportingDocument = SupportingDocumentsOptions.DEATH_CERT
          }
        })
    },
    addRemoveExecutorSuffix: (owner: MhrRegistrationHomeOwnerIF): boolean => {
      let showSuffixError = false

      const allExecutors = getMhrTransferHomeOwners.value
        .filter(owner => owner.partyType === HomeOwnerPartyTypes.EXECUTOR && owner.action === ActionTypes.ADDED)

      if (allExecutors.length === 1 && owner !== null) {
        const suffix = owner.individualName
          ? 'Executor of the will of ' + Object.values(owner.individualName).join(' ')
          : 'Executor of the will of ' + owner.organizationName
        allExecutors[0].suffix = suffix
        showSuffixError = false
      } else {
        allExecutors.forEach((executor: MhrRegistrationHomeOwnerIF) => {
          executor.suffix = 'Executor of the will of N/A'
          showSuffixError = true
        })
      }
      return showSuffixError
    }

  }

  /** Return true if the specified owner is part of the current/base ownership structure **/
  const isCurrentOwner = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    return getMhrTransferCurrentHomeOwnerGroups.value.some(group =>
      group.owners.some(baseOwner => baseOwner.ownerId === owner.ownerId)
    )
  }

  /** Return true when all CURRENT owners of a group have been removed and some owners added in a SO/JT structure. **/
  const groupHasRemovedAllCurrentOwners = (groupId: number) => {
    const owners = getGroupById(groupId).owners

    return localState.isSOorJT && owners.some(owner => owner.action === ActionTypes.ADDED) &&
      owners.every(owner => !!owner.action)
  }

  /** Remove current owners from existing ownership and move them to New Previous Owners group.  **/
  const moveCurrentOwnersToPreviousOwners = async (groupId: number) => {
    // Retrieve and mark for removal all current owners
    const currentOwners = getGroupById(groupId)?.owners.filter(owner => owner.action !== ActionTypes.ADDED)
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
  const hasCurrentGroupChanges = (groupId: number, fractionalData: MhrRegistrationFractionalOwnershipIF): boolean => {
    const currentGroup = getCurrentGroupById(groupId)
    const isEqualNumerator = isEqual(currentGroup?.interestNumerator, fractionalData.interestNumerator)
    const isEqualDenominator = isEqual(currentGroup?.interestDenominator, fractionalData.interestDenominator)

    return currentGroup && (!isEqualNumerator || !isEqualDenominator)
  }

  return {
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
    isDisabledForSJTChanges,
    isDisabledForWillChanges,
    TransWill, // Transfer Due to Death - Grant of Probate (with Will)
    isCurrentOwner,
    getMhrTransferType,
    isTransferDueToDeath,
    isTransferToSurvivingJointTenant,
    isTransferToExecutorProbateWill,
    disableNameFields,
    isJointTenancyStructure,
    getCurrentOwnerStateById,
    groupHasRemovedAllCurrentOwners,
    getCurrentOwnerGroupIdByOwnerId,
    hasCurrentOwnerChanges,
    hasCurrentGroupChanges,
    moveCurrentOwnersToPreviousOwners,
    ...toRefs(localState)
  }
}
