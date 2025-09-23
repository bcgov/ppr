import { FilterTypes } from '@/enums'
import { ReviewStatusTypes, ReviewRegTypes } from '@/composables/analystQueue/enums'

export const queueTableColumns = [
    { id: 'registrationNumber',
      header: 'Registration Number',
      accessorKey: 'mhrNumber',
      sortable: true,
      filter: {
        type: FilterTypes.TEXT_FIELD,
        placeholder: 'Registration Number',
      }
    },
    { id: 'statusType',
      header: 'Status',
      accessorKey: 'statusType',
      sortable: true,
      filter: {
        type: FilterTypes.SELECT,
        placeholder: 'Status',
        options: Object.values(ReviewStatusTypes).map(status => ({
            label: status,
            value: status
        }))
      }
    },{ id: 'registrationType',
      header: 'Registration Type',
      accessorKey: 'registrationType',
      sortable: true,
      filter: {
        type: FilterTypes.SELECT,
        placeholder: 'Registration Type',
        options: Object.values(ReviewRegTypes).map(status => ({
            label: status,
            value: status
        }))
      }
    },{ id: 'dateSubmitted',
      header: 'Date Submitted',
      accessorKey: 'submittingName',
      sortable: true,
      filter: {
        type: FilterTypes.DATE_PICKER,
        placeholder: 'Date Submitted',
      }
    },{ id: 'submittingParty',
      header: 'Submitting Party',
      accessorKey: 'submittingName',
      sortable: true,
      filter: {
        type: FilterTypes.TEXT_FIELD,
        placeholder: 'Submitting Party',
      }
    },{ id: 'assignee',
      header: 'Assignee',
      accessorKey: 'assigneeName',
      sortable: true,
      filter: {
        type: FilterTypes.SELECT,
        placeholder: 'Assignee',
      }
    },{ id: 'actions',
      header: 'Actions',
      accessorKey: 'actions'
     }
  ]
