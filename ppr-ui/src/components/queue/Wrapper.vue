<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import { storeToRefs } from 'pinia'
import { useAnalystQueueStore } from '@/store/analystQueue'
import { queueTableColumns } from '@/composables/analystQueue'

const { setMhrInformation } = useStore()
const { queueTableData } = storeToRefs(useAnalystQueueStore())
const { goToRoute } = useNavigation()
const { getQueueTabledata } = useAnalystQueueStore()
const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const sort = ref({ column: 'dateSubmitted', direction: 'desc' })
const loading = ref(false)
const tableClass = ref('')
const changeColumns = () => {}

// Add cell function to statusType, actions column
const columnsWithCellFunction = computed(() => {
  return queueTableColumns.map(column => {
    // status chip
    if (column.id === 'statusType') {
      return {
        ...column,
        cell: ({ row }) => {
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
      }
    }
    // Actions button
    else if (column.id === 'actions') {
      return {
        ...column,
        cell: ({ row }) => {
          return h(UButton, {
            size: 'md',
            variant: 'solid',
            color: 'primary',
            onClick: () => {
              tableRowActionHandler(row.original)
            }
          }, () => 'Action')
        }
      }
    }
    return column
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
        <span> MHR Queue ({{ queueTableData.length }}) </span>
        <div class="flex gap-4">
          <BaseMultiSelector
            :options="columnsWithCellFunction"
            class="w-[250px] font-light"
            value-attribute="id"
            option-attribute="header"
            label="Column to Show"
            @change="changeColumns"
          />
        </div>
      </div>
    </div>

    <div :class="tableClass">
      <BaseTable
        :columns="columnsWithCellFunction"
        :data="queueTableData"
        :sort="sort"
        :loading="loading"
        @update:sort="($event) => emit('update:sort', $event)"
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
@import '@/assets/styles/theme.scss';

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
