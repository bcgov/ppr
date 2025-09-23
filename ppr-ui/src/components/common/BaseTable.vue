<script setup lang="ts">

type TableSort = {
  column: string
  direction: 'asc' | 'desc'
}

const props = defineProps<{
  columns: Array<any>
  data: Array<any>
  sort?: TableSort
  loading?: boolean
  ui?: Record<string, any>
}>()

const emit = defineEmits<{
  (e: 'update:sort', sort: TableSort): void
  (e: 'row-click', row: any): void
}>()
</script>

<template>
  <UTable
    :columns="columns"
    :data="data"
    :sort="sort"
    :loading="loading"
    :ui="ui"
    sticky
    @update:sort="($event) => emit('update:sort', $event)"
    @row:click="($event) => emit('row-click', $event)"
  >
    <template
      v-for="col in columns"
      :key="col.id"
      #[`${col.id}-header`]="slotProps"
    >
      <slot :name="`${col.id}-header`" v-bind="slotProps">
        <BaseTableHeader
          v-if="col.filter"
          v-model="col.filter.model"
          :type="col.filter.type"
          :options="col.filter.options"
          :placeholder="col.filter.placeholder || col.header"
          :props="col.filter.props"
          :sortable="col.sortable"
          :sort-direction="col.sortDirection"
        />
        <div
          v-else-if="col.id==='actions'"
          class="flex flex-col gap-2 items-center"
        >
          <div> {{ col.header }} </div>
          <UButton
            size="md"
            variant="outline"
            class="px-2"
            icon="i-mdi-cancel-circle"
          >
            Clear Filter
          </UButton>
          
        </div>
      </slot>
    </template>

    <template
      v-for="col in columns"
      :key="col.id"
      #[`${col.accessorKey}-data`]="{ row }"
    >
      <slot :name="`${col.accessorKey}-data`" :row="row">
        <component :is="col.cell({ row })" v-if="col.cell" />
        <template v-else>{{ row[col.accessorKey] }}</template>
      </slot>
    </template>

    <template #empty-state>
      <slot name="empty-state">
        <div class="py-8 text-center text-gray-500">No results</div>
      </slot>
    </template>
  </UTable>
</template>
<style scoped>
:deep(table) th:last-child,
:deep(table) td:last-child {
  display: table-cell;
  position: sticky;
  right: 0;
  width: 160px;
  max-width: 160px;
  min-width: 160px;
  text-align: center;
  background-color: #fff;

  border-left: 1px solid #dee2e6;
  box-shadow: inset 1px 0 0 0 #adb5bd;
}

</style>