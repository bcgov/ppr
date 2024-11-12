import { MhrSubTypes, MhrActions } from '@/enums/mhrSubProductActions'
import { SubProductConfigIF } from '@/interfaces'

export const MhrSubProductConfig: Array<SubProductConfigIF> = [
  {
    type: MhrSubTypes.LAWYERS_NOTARIES,
    label: `${MhrSubTypes.QUALIFIED_SUPPLIER} - ${MhrSubTypes.LAWYERS_NOTARIES}`,
    productBullets: [
      MhrActions.MHR_SEARCH, MhrActions.TRANSPORT_PERMITS, MhrActions.TRANSFER_TRANSACTIONS,
      MhrActions.TRANSFER_TRANSACTIONS_SJT, MhrActions.RESIDENTIAL_EXEMPTIONS
    ],
    hasImportantBullet: false,
    /* eslint-disable max-len */
    note: `General Service Providers who are not lawyers or notaries cannot request Qualified Supplier access online
     and <a href="https://www2.gov.bc.ca/gov/content/housing-tenancy/owning-a-home/manufactured-home-registry#qualified-supplier"
     target="_blank">must submit a paper application <span class="mdi mdi-open-in-new"></span></a> to BC Registries.`
    /* eslint-enable max-len */
  },
  {
    type: MhrSubTypes.MANUFACTURER,
    label: `${MhrSubTypes.QUALIFIED_SUPPLIER} - ${MhrSubTypes.MANUFACTURER}`,
    productBullets: [
      MhrActions.MHR_SEARCH, MhrActions.TRANSPORT_PERMITS, MhrActions.HOME_TRANSFER_TRANSACTIONS,
      MhrActions.REGISTRATIONS
    ],
    hasImportantBullet: false
  },
  {
    type: MhrSubTypes.DEALERS,
    label: `${MhrSubTypes.QUALIFIED_SUPPLIER} - ${MhrSubTypes.DEALERS}`,
    productBullets: [
      MhrActions.MHR_SEARCH, MhrActions.TRANSPORT_PERMITS, MhrActions.TRANSFER_TRANSACTIONS
    ],
    hasImportantBullet: false
  }
]
