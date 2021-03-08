import { APISearchTypes } from '@/enums'
import { TableHeadersIF } from '@/interfaces'

export const tableHeaders: TableHeadersIF =
  {
    [APISearchTypes.SERIAL_NUMBER]: [
      {
        text: 'Serial Number',
        value: 'vehicleCollateral.serialNumber',
        class: 'result-header'
      },
      {
        text: 'Type',
        value: 'vehicleCollateral.type',
        class: 'result-header'
      },
      {
        text: 'Year',
        value: 'vehicleCollateral.year',
        class: 'result-header'
      },
      {
        text: 'Make/Model',
        value: 'makeModel',
        class: 'result-header'
      }
    ],
    [APISearchTypes.INDIVIDUAL_DEBTOR]: [
      {
        text: 'Debtor Name',
        value: 'debtor.personalName',
        class: 'result-header'
      },
      {
        text: 'Birthdate',
        value: '',
        class: 'result-header'
      }
    ],
    [APISearchTypes.BUSINESS_DEBTOR]: [
      {
        text: 'Debtor Name',
        value: 'debtor.businessName',
        class: 'result-header'
      }
    ],
    [APISearchTypes.MHR_NUMBER]: [
      {
        text: 'Manufactured Home Registration Number',
        value: 'vehicleCollateral.manufacturedHomeRegistrationNumber',
        class: 'result-header'
      },
      {
        text: 'Serial Number',
        value: 'vehicleCollateral.serialNumber',
        class: 'result-header'
      },
      {
        text: 'Year',
        value: 'vehicleCollateral.year',
        class: 'result-header'
      },
      {
        text: 'Make/Model',
        value: 'makeModel',
        class: 'result-header'
      }
    ],
    [APISearchTypes.AIRCRAFT]: [
      {
        text: 'Serial Number',
        value: 'vehicleCollateral.serialNumber',
        class: 'result-header'
      },
      {
        text: 'Year',
        value: 'vehicleCollateral.year',
        class: 'result-header'
      },
      {
        text: 'Make/Model',
        value: 'makeModel',
        class: 'result-header'
      }
    ],
    [APISearchTypes.REGISTRATION_NUMBER]: [
      {
        text: 'Registration Number',
        value: 'registrationNumber',
        class: 'result-header'
      }
    ]
  }
