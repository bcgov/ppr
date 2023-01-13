export interface MhrRegistrationTotalOwnershipAllocationIF {
  totalAllocation: string // e.g. 4/4
  hasTotalAllocationError: Boolean // if totalAllocation is not equal to 1/1 or 100%
  allocationErrorMsg: string // e.g. Ownership is under allocated
  hasMinimumGroupsError: Boolean // if Groups must have 2 groups
}
