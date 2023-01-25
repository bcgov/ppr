export interface AccountModelIF {
  currentAccount: {
    id: number
  }
  currentAccountMembership: any
  currentUser: Object
  pendingApprovalCount: number
  userSettings: Array<Object>
}
