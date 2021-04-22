import { APIRegistrationTypes, UIRegistrationTypes } from '@/enums'
import { RegistrationTypeIF } from '@/interfaces'

export const RegistrationTypes: Array<RegistrationTypeIF> = [
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.SECURITY_AGREEMENT,
    registrationTypeAPI: APIRegistrationTypes.SECURITY_AGREEMENT,
    textLabel: 'Security Agreement'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.REPAIRERS_LIEN,
    registrationTypeAPI: APIRegistrationTypes.REPAIRERS_LIEN,
    textLabel: 'Repairers Lien'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.MARRIAGE_MH,
    registrationTypeAPI: APIRegistrationTypes.MARRIAGE_MH,
    textLabel: 'Marriage / Separation Agreement affecting Manufactured Home under Family Law Act'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.SALE_OF_GOODS,
    registrationTypeAPI: APIRegistrationTypes.SALE_OF_GOODS,
    textLabel: 'Possession under S.30 of the Sale of Goods Act'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.LAND_TAX_LIEN,
    registrationTypeAPI: APIRegistrationTypes.LAND_TAX_LIEN,
    textLabel: 'Land Tax Deferment Lien on a Manufactured Home'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.MANUFACTURED_HOME_LIEN,
    registrationTypeAPI: APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
    textLabel: 'Tax Lien Under S.27/28 of the Manufactured Home Act'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
    registrationTypeAPI: APIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
    textLabel: 'Forestry - Contractor Lien'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
    registrationTypeAPI: APIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
    textLabel: 'Forestry - Contractor Charge'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN,
    registrationTypeAPI: APIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN,
    textLabel: 'Forestry - Sub-contractor Charge'
  },
  {
    // divider in dropdown list
    divider: true,
    selectDisabled: true,
    registrationTypeUI: null,
    registrationTypeAPI: null,
    textLabel: null
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.MISCELLANEOUS_REGISTRATION,
    registrationTypeAPI: APIRegistrationTypes.MISCELLANEOUS_REGISTRATION,
    textLabel: 'Miscellaneous Registration Act - Crown Charge Registration'
  },
  {
    divider: false,
    selectDisabled: false,
    registrationTypeUI: UIRegistrationTypes.MISCELLANEOUS_OTHER,
    registrationTypeAPI: APIRegistrationTypes.MISCELLANEOUS_OTHER,
    textLabel: 'Miscellaneous Registration Act - Others'
  }
]
