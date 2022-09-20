export interface MhrRegistrationTotalOwnershipAllocationIF {
  totalAllocation: string // e.g. 4/4
  hasTotalAllocationError: Boolean // if totalAllocation is not equal to 1/1 or 100%
  hasMinimumGroupsError: Boolean // if Groups must have 2 groups
}
