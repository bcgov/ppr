import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeOwnerPartyTypes,
  HomeTenancyTypes, MhApiStatusTypes,
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
import { isEqual, find, uniq } from 'lodash'
import { normalizeObject } from '@/utils'
import { useHomeOwners } from '@/composables'
import {
  transferOwnerPrefillAdditionalName,
  transferOwnerPartyTypes,
  transferSupportingDocumentTypes
} from '@/resources/'

/**
 * Composable to handle Ownership functionality and permissions specific to the varying Transfer of Ownership filings.
 * @param enableAllActions A flag to enable and bypass the permission functions. (ie for edge case like MHR)
 */
export const useTransferOwners = (enableAllActions: boolean = false) => {
  const {
    hasUnsavedChanges,
    getMhrTransferType,
    getMhrInformation,
    getMhrTransferHomeOwners,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups,
    getMhrTransferAffidavitCompleted
  } = useGetters<any>([
    'hasUnsavedChanges',
    'getMhrTransferType',
    'getMhrInformation',
    'getMhrTransferHomeOwners',
    'getMhrTransferHomeOwnerGroups',
    'getMhrTransferCurrentHomeOwnerGroups',
    'getMhrTransferAffidavitCompleted'
  ])

  const {
    setMhrTransferHomeOwnerGroups,
    setMhrTransferAffidavitCompleted
  } = useActions<any>([
    'setMhrTransferHomeOwnerGroups',
    'setMhrTransferAffidavitCompleted'
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

  const isRemovedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.REMOVED
  }

  const isAddedHomeOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.ADDED
  }

  const isChangedOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return group.action === ActionTypes.CHANGED
  }

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
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:
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
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:
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
        return getMhrInformation.value.statusType !== MhApiStatusTypes.FROZEN // Enable for all but FROZEN status
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
      case ApiTransferTypes.SALE_OR_GIFT:
      case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
      case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
      case ApiTransferTypes.TO_ADMIN_NO_WILL:
        return true // Always enable for above transfer types
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
        return getMhrInformation.value.statusType !== MhApiStatusTypes.FROZEN
      default:
        return true
    }
  }

  /** Return true if the specified owners group does not contain the executor or administrator **/
  const isDisabledForSoGChanges = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.SALE_OR_GIFT &&
      getMhrInformation.value.statusType === MhApiStatusTypes.FROZEN) {
      const isExecutorOrAdministratorOwnerGroup = getMhrTransferHomeOwnerGroups.value.find(group =>
        group.groupId === owner.groupId).owners.some(owner => {
        return owner.partyType === HomeOwnerPartyTypes.EXECUTOR || owner.partyType === HomeOwnerPartyTypes.ADMINISTRATOR
      })

      return !isExecutorOrAdministratorOwnerGroup
    }
    return false
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

  // Transfer Due to Sale or Gift flow and all the related conditions/logic
  const TransSaleOrGift: any = {
    hasMixedOwners: computed((): boolean => {
      return !getMhrTransferHomeOwnerGroups.value
        .every((group: MhrRegistrationHomeOwnerGroupIF) =>
          !TransSaleOrGift.hasMixedOwnersInGroup(group.groupId))
    }),
    hasMixedOwnersInGroup: (groupId: number): boolean => {
      const ownerTypes: HomeOwnerPartyTypes[] = getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .filter(owner => owner.action !== ActionTypes.REMOVED)
        .map(owner => owner.partyType)
      return ownerTypes.length === 1 ? false : uniq(ownerTypes).length > 1
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

      if (!groupWithDeletedOwners) return false

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
        owner.action === ActionTypes.ADDED && owner.partyType === HomeOwnerPartyTypes.EXECUTOR)
      return isValidAddedOwner && hasAddedExecutor
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
      if (owner.action === ActionTypes.ADDED) return true

      // if deleted Exec, Admin or Trustee, then docs are not required and are valid
      if (owner.action === ActionTypes.REMOVED &&
        [HomeOwnerPartyTypes.EXECUTOR, HomeOwnerPartyTypes.ADMINISTRATOR, HomeOwnerPartyTypes.TRUSTEE]
          .includes(owner.partyType)) return true

      let hasValidSupportingDoc = false

      if (owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT ||
        owner.supportingDocument === SupportingDocumentsOptions.AFFIDAVIT) {
        hasValidSupportingDoc = owner.hasDeathCertificate &&
          !!owner.deathCertificateNumber && !!owner.deathDateTime
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
      return getMhrTransferHomeOwnerGroups.value
        .find(group => group.groupId === groupId).owners
        .every(owner => isCurrentOwner(owner)
          ? owner.action === ActionTypes.REMOVED
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
    // Check if all Owners within a group have Death Certificate as a supporting document
    isAllGroupOwnersWithDeathCerts: (groupId): boolean => {
      return getMhrTransferHomeOwners.value
        .filter(owner => owner.groupId === groupId && owner.action !== ActionTypes.ADDED)
        .every(owner => {
          return owner.action === ActionTypes.REMOVED &&
            // Affidavit type also has Death Certificate
            (owner.supportingDocument === SupportingDocumentsOptions.DEATH_CERT)
        })
    },
    // Check if there's a deleted Owner with selected
    // Grant of Probate or Affidavit or Admin Grant as a supporting document.
    hasDeletedOwnersWithProbateGrantOrAffidavit: (): boolean => {
      return getMhrTransferHomeOwnerGroups.value.some(group =>
        group.owners.some(owner =>
          (owner.action === ActionTypes.REMOVED &&
          owner.partyType === HomeOwnerPartyTypes.OWNER_IND &&
          owner.supportingDocument === TransToExec.getSupportingDocForActiveTransfer()) ||
          (owner.action === ActionTypes.REMOVED &&
            [HomeOwnerPartyTypes.EXECUTOR, HomeOwnerPartyTypes.ADMINISTRATOR, HomeOwnerPartyTypes.TRUSTEE]
              .includes(owner.partyType)))
      )
    },
    prefillOwnerAsExecOrAdmin: (owner: MhrRegistrationHomeOwnerIF): void => {
      const transferType = getMhrTransferType.value?.transferType
      const allOwners = getMhrTransferHomeOwners.value
      const deletedOwnerGroup = find(getMhrTransferHomeOwnerGroups.value, { owners: [{ action: ActionTypes.REMOVED }] })

      // first try to find the deleted reg owner
      const deletedOwner = find(deletedOwnerGroup.owners, {
        action: ActionTypes.REMOVED
      }) as MhrRegistrationHomeOwnerIF

      let suffix = ''
      if ([HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS].includes(deletedOwner.partyType)) {
        // if reg or business owner is deleted, prefill the additional name (suffix) with the name of the deleted owner
        const { first, middle, last } = deletedOwner.individualName || {}

        suffix = deletedOwner.organizationName?.length > 0
          ? transferOwnerPrefillAdditionalName[transferType] + deletedOwner.organizationName
          : transferOwnerPrefillAdditionalName[transferType] + [first, middle, last].filter(Boolean).join(' ')
      } else {
        // if executor, admin or trustee, copy the additional name (suffix) from the suffix of deleted owner
        suffix = deletedOwner.description
      }

      Object.assign(owner, {
        ownerId: allOwners.length + 1,
        suffix: suffix,
        partyType: transferOwnerPartyTypes[transferType],
        groupId: deletedOwnerGroup.groupId // new Owner will be added to the same group as deleted Owner
      } as MhrRegistrationHomeOwnerIF)
    },
    updateExecutorSuffix: (): boolean => {
      const deceasedOwners = getMhrTransferHomeOwners.value
        .filter(owner => owner.action === ActionTypes.REMOVED)

      return TransToExec.addRemoveExecutorSuffix(deceasedOwners[0] || null)
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
    },
    addRemoveExecutorSuffix: (owner: MhrRegistrationHomeOwnerIF): boolean => {
      const transferType = getMhrTransferType.value?.transferType
      let showSuffixError = false

      const allExecutors = getMhrTransferHomeOwners.value
        .filter(owner => owner.partyType === transferOwnerPartyTypes[transferType] &&
          owner.action === ActionTypes.ADDED)

      if (allExecutors.length === 1 && owner !== null) {
        let suffix = ''

        if ([HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS].includes(owner.partyType)) {
          const { first, middle, last } = owner.individualName || {}
          suffix = owner.organizationName?.length > 0
            ? transferOwnerPrefillAdditionalName[transferType] + owner.organizationName
            : transferOwnerPrefillAdditionalName[transferType] + [first, middle, last].filter(Boolean).join(' ')
        } else {
          suffix = owner.description
        }

        allExecutors[0].suffix = suffix
        showSuffixError = false
      } else {
        allExecutors.forEach((executor: MhrRegistrationHomeOwnerIF) => {
          // reset suffix or description
          const additionalName = transferOwnerPrefillAdditionalName[transferType] + 'N/A'
          executor.suffix = executor.suffix ? additionalName : executor.description = additionalName
          showSuffixError = true
        })
      }
      return showSuffixError
    }
  }

  const TransJointTenants = {
    isValidTransfer: computed((): boolean => {
      const groupWithDeletedOwners: MhrRegistrationHomeOwnerGroupIF = getMhrTransferHomeOwnerGroups.value?.find(group =>
        group.owners.some(owner => owner.action === ActionTypes.REMOVED))

      if (!groupWithDeletedOwners) return false

      const isValidGroup = groupWithDeletedOwners.owners
        .filter(owner => owner.action === ActionTypes.REMOVED)
        .every(owner =>
          owner.hasDeathCertificate && !!owner.deathCertificateNumber && !!owner.deathDateTime)
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
    hasAddedAdministratorsInGroup: (groupId): boolean =>
      hasAddedPartyTypeToGroup(groupId, HomeOwnerPartyTypes.ADMINISTRATOR)
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

  /** Return true if a member of a specified partyType has been added to the group **/
  const hasAddedPartyTypeToGroup = (groupId: number, partyType: HomeOwnerPartyTypes): boolean => {
    return getMhrTransferHomeOwnerGroups.value
      .find(group => group.groupId === groupId).owners
      .some(owner => owner.partyType === partyType &&
        owner.action === ActionTypes.ADDED)
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
    isDisabledForSoGChanges,
    isDisabledForSJTChanges,
    isDisabledForWillChanges,
    TransSaleOrGift,
    TransToExec, // Transfer Due to Death - Grant of Probate (with Will)
    TransJointTenants,
    TransAffidavit, // Transfer to Executor under $25k - Affidavit
    TransToAdmin,
    isTransAffi,
    isCurrentOwner,
    getMhrTransferType,
    isTransferDueToDeath,
    isTransferToExecOrAdmin,
    isTransferDueToSaleOrGift,
    isTransferToSurvivingJointTenant,
    isTransferToExecutorProbateWill,
    isTransferToExecutorUnder25Will,
    isTransferToAdminNoWill,
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
