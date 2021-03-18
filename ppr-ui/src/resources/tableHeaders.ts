import { APISearchTypes } from '@/enums'
import { TableHeadersIF } from '@/interfaces'

export const tableHeaders: TableHeadersIF =
  {
    [APISearchTypes.SERIAL_NUMBER]: [
      {
        text: 'Serial Number',
        value: 'vehicleCollateral.serialNumber'
      },
      {
        text: 'Type',
        value: 'vehicleCollateral.type'
      },
      {
        text: 'Year',
        value: 'vehicleCollateral.year'
      },
      {
        text: 'Make/Model',
        value: 'makeModel'
      }
    ],
    [APISearchTypes.INDIVIDUAL_DEBTOR]: [
      {
        text: 'Debtor Name',
        value: 'debtor.personalName'
      },
      {
        text: 'Birthdate',
        value: ''
      }
    ],
    [APISearchTypes.BUSINESS_DEBTOR]: [
      {
        text: 'Debtor Name',
        value: 'debtor.businessName'
      }
    ],
    [APISearchTypes.MHR_NUMBER]: [
      {
        text: 'Manufactured Home Registration Number',
        value: 'vehicleCollateral.manufacturedHomeRegistrationNumber'
      },
      {
        text: 'Serial Number',
        value: 'vehicleCollateral.serialNumber'
      },
      {
        text: 'Year',
        value: 'vehicleCollateral.year'
      },
      {
        text: 'Make/Model',
        value: 'makeModel'
      }
    ],
    [APISearchTypes.AIRCRAFT]: [
      {
        text: 'Serial Number',
        value: 'vehicleCollateral.serialNumber'
      },
      {
        text: 'Year',
        value: 'vehicleCollateral.year'
      },
      {
        text: 'Make/Model',
        value: 'makeModel'
      }
    ],
    [APISearchTypes.REGISTRATION_NUMBER]: [
      {
        text: 'Registration Number',
        value: 'registrationNumber'
      }
    ]
  }
