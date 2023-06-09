import { RouteNames } from '@/enums'
import { ButtonConfigIF } from '@/interfaces'

export const MHRButtonFooterConfig: Array<ButtonConfigIF> = [
  {
    stepName: RouteNames.YOUR_HOME,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: false,
    showNext: true,
    backRouteName: '',
    nextText: 'Submitting Party',
    nextRouteName: RouteNames.SUBMITTING_PARTY
  },
  {
    stepName: RouteNames.SUBMITTING_PARTY,
    showCancel: true,
    showSave: true,
    showSaveResume: true,
    showBack: true,
    showNext: true,
    backRouteName: RouteNames.YOUR_HOME,
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
    backRouteName: RouteNames.SUBMITTING_PARTY,
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
