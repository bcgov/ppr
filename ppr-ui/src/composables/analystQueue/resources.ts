import { FilterTypes } from '@/enums'
import { ReviewStatusTypes, ReviewRegTypes } from '@/composables/analystQueue/enums'

const transformEnumToLabel = (enumValue: string): string => {
  return enumValue
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

export const queueTableColumns = [
    { id: 'mhrNumber',
      header: 'Registration Number',
      accessorKey: 'mhrNumber',
      sortable: true,
      filter: {
        type: FilterTypes.TEXT_FIELD,
        placeholder: 'Registration Number',
      },
      meta: {
        class: {
          th: 'w-[200px]'
        }
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
            label: transformEnumToLabel(status),
            value: status
        })),
      },
      meta: {
        class: {
          th: 'w-[200px]'
        }
      }
    },
    { id: 'registrationType',
      header: 'Registration Type',
      accessorKey: 'registrationType',
      sortable: true,
      filter: {
        type: FilterTypes.SELECT,
        placeholder: 'Registration Type',
        options: Object.values(ReviewRegTypes).map(status => ({
            label: transformEnumToLabel(status),
            value: status
        })),
      },
      meta: {
        class: {
          th: 'w-[200px]'
        }
      }
    },
    { id: 'createDateTime',
      header: 'Date Submitted',
      accessorKey: 'createDateTime',
      sortable: true,
      filter: {
        type: FilterTypes.DATE_PICKER,
        placeholder: 'Date Submitted',
      },
      meta: {
        class: {
          th: 'w-[200px]'
        }
      }
    },
    { id: 'submittingName',
      header: 'Submitting Party',
      accessorKey: 'submittingName',
      sortable: true,
      filter: {
        type: FilterTypes.TEXT_FIELD,
        placeholder: 'Submitting Party',
      },
      meta: {
        class: {
          th: 'w-[200px]'
        }
      }
    },
    { id: 'assigneeName',
      header: 'Assignee',
      accessorKey: 'assigneeName',
      sortable: true,
      filter: {
        type: FilterTypes.SELECT,
        placeholder: 'Assignee'
      },
      meta: {
        class: {
          th: 'w-[200px]'
        }
      }
    },
    { id: 'actions',
      header: 'Actions',
      accessorKey: 'actions',
      isFixed: true,
      filter: {
        type: FilterTypes.ACTIONS
      }
     }
  ]
