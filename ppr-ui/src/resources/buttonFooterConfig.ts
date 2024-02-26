import { RouteNames } from '@/enums'
import { ButtonConfigIF } from '@/interfaces'

export const MHRButtonFooterConfig: Array<ButtonConfigIF> = [
  {
    stepName: RouteNames.SUBMITTING_PARTY,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Describe Your Home',
    nextRouteName: RouteNames.YOUR_HOME
  },
  {
    stepName: RouteNames.YOUR_HOME,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.SUBMITTING_PARTY,
    nextText: 'List the Home Owners',
    nextRouteName: RouteNames.HOME_OWNERS
  },
  {
    stepName: RouteNames.HOME_OWNERS,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.YOUR_HOME,
    nextText: 'Location of Home',
    nextRouteName: RouteNames.HOME_LOCATION
  },
  {
    stepName: RouteNames.HOME_LOCATION,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.HOME_OWNERS,
    nextText: 'Review and Confirm',
    nextRouteName: RouteNames.MHR_REVIEW_CONFIRM
  },
  {
    stepName: RouteNames.MHR_REVIEW_CONFIRM,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.HOME_LOCATION,
    nextText: 'Register and Pay',
    nextRouteName: RouteNames.DASHBOARD
  }]

export const MHRManufacturerButtonFooterConfig: Array<ButtonConfigIF> = [
  {
    stepName: RouteNames.YOUR_HOME,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Review and Confirm',
    nextRouteName: RouteNames.MHR_REVIEW_CONFIRM
  },
  {
    stepName: RouteNames.MHR_REVIEW_CONFIRM,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.YOUR_HOME,
    nextText: 'Register and Pay',
    nextRouteName: RouteNames.DASHBOARD
  }
]

export const MhrUserAccessButtonFooterConfig: Array<ButtonConfigIF> = [
  {
    stepName: RouteNames.QS_ACCESS_TYPE,
    showCancel: true,
    showSave: false,
    showSaveResume: false,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Complete Qualified Supplier Application',
    nextRouteName: RouteNames.QS_ACCESS_INFORMATION
  },
  {
    stepName: RouteNames.QS_ACCESS_INFORMATION,
    showCancel: true,
    showSave: false,
    showSaveResume: false,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.QS_ACCESS_TYPE,
    nextText: 'Review and Confirm',
    nextRouteName: RouteNames.QS_ACCESS_REVIEW_CONFIRM
  },
  {
    stepName: RouteNames.QS_ACCESS_REVIEW_CONFIRM,
    showCancel: true,
    showSave: false,
    showSaveResume: false,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.QS_ACCESS_INFORMATION,
    nextText: 'Submit Application',
    nextRouteName: RouteNames.DASHBOARD
  }
]

export const MhrExemptionFooterConfig: Array<ButtonConfigIF> = [
  {
    stepName: RouteNames.EXEMPTION_DETAILS,
    showCancel: true,
    showSave: false,
    showSaveResume: false,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Review and Confirm',
    nextRouteName: RouteNames.EXEMPTION_REVIEW
  },
  {
    stepName: RouteNames.EXEMPTION_REVIEW,
    showCancel: true,
    showSave: false,
    showSaveResume: false,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.EXEMPTION_DETAILS,
    nextText: 'Register and Pay',
    nextRouteName: RouteNames.DASHBOARD
  }
]

export const RegistrationButtonFooterConfig: Array<ButtonConfigIF> = [
  {
    stepName: RouteNames.LENGTH_TRUST,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Add Secured Parties and Debtors',
    nextRouteName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS
  },
  {
    stepName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.LENGTH_TRUST,
    nextText: 'Add Collateral',
    nextRouteName: RouteNames.ADD_COLLATERAL
  },
  {
    stepName: RouteNames.ADD_COLLATERAL,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    nextText: 'Review and Confirm',
    nextRouteName: RouteNames.REVIEW_CONFIRM
  },
  {
    stepName: RouteNames.REVIEW_CONFIRM,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.ADD_COLLATERAL,
    nextText: 'Register and Pay',
    nextRouteName: RouteNames.DASHBOARD
  }]
