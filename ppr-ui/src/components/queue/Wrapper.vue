<script setup lang="ts">
import { h, resolveComponent, ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAnalystQueueStore } from '@/store/analystQueue'
import { queueTableColumns } from '@/composables/analystQueue'
import { FilterTypes } from '@/enums'

const { setMhrInformation } = useStore()
const { goToRoute } = useNavigation()

const {
  assignees,
  filteredQueueReviews,
  columnsToShow,
  columnFilters,
  showClearFilterButton
} = storeToRefs(useAnalystQueueStore())
const { getQueueTabledata } = useAnalystQueueStore()

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const BaseTableHeader = resolveComponent('BaseTableHeader')
const sort = ref({ column: 'dateSubmitted', direction: 'desc' })
const loading = ref(false)
const columnVisibility = ref({})

const changeColumns = (selected: Array<string>) => {
  columnVisibility.value = queueTableColumns.reduce((result, col) => {
  if (!col.isFixed && !selected.includes(col.id)) {
    result[col.id] = false
  }
  return result
}, {})
}

const filterTable = (columnId, filterValue) => {
  columnFilters.value[columnId] = filterValue
}

const renderStatusChip = (col) => ({ row }) => {
    const color = {
      APPROVED: 'success' as const,
      DECLINED: 'error' as const,
      PAY_CANCELLED: 'neutral' as const,
      NEW: 'warning' as const
    }[row.getValue('statusType') as string]

    return h(UBadge, {
      as: 'div',
      class: 'size-full text-md text-center flex justify-center',
      variant: 'subtle',
      color
    }, () => row.getValue('statusType'))
  }

const renderSortableHeader = (columnData) => ({ column }: any) => {
  const isSorted = column.getIsSorted()

  return h(BaseTableHeader, {
    columnData: columnData,
    isSorted: isSorted,
    modelValue: columnFilters.value[columnData.id],
    showClearFilterButton: showClearFilterButton.value,
    onToggleSort: () => {
      column.toggleSorting(column.getIsSorted() === 'asc')
    },
    onFilterTable: (columnId, value) => {
      filterTable(columnId, value)
    },
    onResetFilter: () => {
      columnFilters.value = {}
    }
  })
}

// Add cell function to statusType, actions column
const columnsWithCellFunction = computed(() => {
  return columnsToShow.value.map(column => {
    if (column.id === 'statusType') {
      return {
        ...column,
        header: renderSortableHeader(column),
        cell: renderStatusChip(column)
      }
    }
    else if (column.id === 'assigneeName') {
      return {
        ...column,
        header: renderSortableHeader({
          ...column,
          get filter() {
            return {
              ...column.filter,
              options: assignees.value,
            }
          }
        })
      }
    }
    else if (column.id === 'actions') {
      return {
        ...column,
        header: renderSortableHeader(column),
        cell: ({ row }) =>
          h(UButton, {
              size: 'md',
              variant: 'solid',
              color: 'primary',
              onClick: () => {
                tableRowActionHandler(row.original)
              }
            }, () => 'Action'
          )
      }
    }
    return {
      ...column,
      header: renderSortableHeader(column),
    }
  })
})

onMounted(async () => {
  await getQueueTabledata()
})

const tableRowActionHandler = (rowEvent) => {
  setMhrInformation(rowEvent)
  goToRoute(RouteNames.MHR_QUEUE_TRANSFER)
}

</script>
<template>
  <div class="bg-white rounded-md shadow-sm overflow-hidden">
      <div
        class="font-bold text-gray-900 bg-bcGovColor-gray2 px-5 py-[18px] rounded-t"
      >
      <div class="flex justify-between items-center">
        <span> MHR Queue ({{ filteredQueueReviews?.length }}) </span>
        <div class="flex gap-4">
          <BaseMultiSelector
            :options="queueTableColumns"
            class="w-[200px] font-light"
            value-key="id"
            label-key="header"
            label="Column to Show"
            @change="changeColumns"
          />
        </div>
      </div>
    </div>

    <div>
      <BaseTable
        :columns="columnsWithCellFunction"
        :data="filteredQueueReviews"
        :sort="sort"
        :loading="loading"
        :column-visibility="columnVisibility"
        @update:sort="($event) => emit('update:sort', $event)"
        @row:click="($event) => emit('row-click', $event)"
      >
        <!-- forward all provided slots to BaseTable -->
        <template v-for="(_, slotName) in $slots" #[slotName]="slotProps">
          <slot :name="slotName" v-bind="slotProps" />
        </template>

        <template #empty-state>
          <slot name="empty-state">
            <div class="py-8 text-center text-gray-500">No results</div>
          </slot>
        </template>
      </BaseTable>
    </div>
  </div>

</template>


<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;

:deep(input) {
  /* default state */
  --tw-shadow: inset 0 -1px 0 0px;
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000),
              var(--tw-ring-shadow, 0 0 #0000),
              var(--tw-shadow);
  transition: box-shadow 200ms ease;

  &:focus {
    /* override on focus */
    --tw-shadow: inset 0 -2px 0 0px rgb(var(--v-theme-primary));
  }
}

:deep(.custom-select) {
  /* default state */
  --tw-shadow: inset 0 -1px 0 0px;
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000),
              var(--tw-ring-shadow, 0 0 #0000),
              var(--tw-shadow);
  transition: box-shadow 200ms ease;
}

:deep(.custom-select:focus),
:deep(.custom-select[data-state="open"]) {
  --tw-shadow: inset 0 -2px 0 0px rgb(var(--v-theme-primary));
}

</style>
