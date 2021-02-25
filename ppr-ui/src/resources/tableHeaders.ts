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
        text: 'Make',
        value: 'vehicleCollateral.make',
        class: 'result-header'
      },
      {
        text: 'Model',
        value: 'vehicleCollateral.model',
        class: 'result-header'
      }
    ]
  }
