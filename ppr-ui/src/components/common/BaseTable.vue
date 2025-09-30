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
  columnVisibility?: object
}>()

const columnVisibility = computed(() => {
  return props.columnVisibility
})


const emit = defineEmits<{
  (e: 'row-click', row: any): void
}>()
</script>

<template>
  <UTable
    v-model:column-visibility="columnVisibility"
    :columns="columns"
    :data="data"
    :sort="sort"
    :loading="loading"
    :ui="ui"
    sticky
    class="min-h-[400px]"
    @row:click="($event) => emit('row-click', $event)"
  >

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