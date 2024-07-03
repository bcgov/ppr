<template>
  <v-table id="simple-table">
    <thead>
      <tr>
        <th
          v-for="(header, index) in tableHeaders"
          :key="`${header.name}-${index}`"
          :class="header?.class"
        >
          {{ header.name }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(item, index) in tableData"
        :key="`${item.name}-${index}`"
      >
        <td>{{ item.name }}</td>
      </tr>
    </tbody>
  </v-table>
</template>

<script setup lang="ts">
/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  tableHeaders: Array<any>,
  tableData: Array<any>
}>(), {
  tableHeaders: null,
  tableData: null
})

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
