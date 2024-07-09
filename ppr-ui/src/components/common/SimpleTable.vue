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
      <template
        v-for="(item, rowIndex) in tableData"
        :key="`${item.name}-${rowIndex}`"
      >
        <tr>
          <td
            v-for="(header, colIndex) in tableHeaders"
            :key="`cell-${rowIndex}-${colIndex}`"
            :class="{
              'font-weight-bold gray9' : colIndex === 1,
              'expanded-row-cell' : expandRow[rowIndex]
            }"
          >
            <!-- Expand/Collapse Btn -->
            <v-btn
              v-if="colIndex === 0"
              class="toggle-expand-row-btn"
              color="primary"
              variant="plain"
              :ripple="false"
              @click="toggleRowState(rowIndex)"
            >
              <v-icon
                class="hide-show-chevron"
                size="small"
              >
                {{ expandRow[rowIndex] ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
              </v-icon>
              <span class="generic-link pl-1">
                {{ expandRow[rowIndex] ? 'Hide' : 'View' }} {{ rowLabel }}
              </span>
            </v-btn>
            <!-- Cell Content -->
            <template v-else>
              <slot
                :name="`cell-slot-${colIndex}`"
                :content="item"
              >
                {{ getItemValue(item, header.value) }}
              </slot>
            </template>
          </td>
        </tr>
        <tr
          v-if="expandRow[rowIndex]"
          class="content-slot-row"
        >
          <td />
          <td :colspan="tableHeaders.length">
            <slot
              name="content-slot"
              :content="tableData[rowIndex]"
            />
          </td>
        </tr>
      </template>
    </tbody>
  </v-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { isObject } from 'lodash'
import { shortPacificDate } from '@/utils'
import { BaseHeaderIF } from '@/interfaces'

/** Props **/
const props = withDefaults(defineProps<{
  tableHeaders?: Array<BaseHeaderIF>,
  tableData?: Array<any>,
  rowLabel?: string,
  dateFallBackLabel?: string
}>(), {
  tableHeaders: null,
  tableData: null,
  rowLabel: 'History',
  dateFallBackLabel: 'Current'
})

const expandRow = ref([])

/** Toggle expanded state of rows **/
const toggleRowState = (index: number) => {
  expandRow.value[index] = !expandRow.value[index]
}

/**
 * Retrieves nested values from an object based on an array of dot-separated value paths.
 * Handles array indexing within the paths and formats date values if 'date' is included in the value path.
 * Allows combining multiple values into a single return value.
 *
 * @param {Object} item - The object to retrieve the values from.
 * @param {Array<string>|string} valuePaths - The array of dot-separated paths specifying the values to retrieve, or a
 * single path as a string.
 * @returns {string} - The combined values retrieved from the specified paths, or an empty string if none are found.
 */
const getItemValue = (item: object, valuePaths: Array<string> | string): string => {

  const retrieveValue = (path) => {
    if (!path) return ''

    // Function to retrieve a single value from the item based on a path
    const result = path.split('.').reduce((result, key) => {
      if (result && isObject(result)) {
        // Handle array indexing in the path (e.g., sections[0].serialNumber)
        if (key.includes('[')) {
          const [mainKey, index] = key.split(/\[|\]/).filter(Boolean)
          return result[mainKey]?.[parseInt(index)]
        }
        // Otherwise, retrieve the nested value
        return result[key]
      }
      // Return empty string if the path is invalid
      return ''
    }, item)

    // Format the value as a date if the path includes 'date'
    if (path.toLowerCase().includes('date')) {
      return !!result ? shortPacificDate(result) : props.dateFallBackLabel
    }

    return result
  }

  // If valuePaths is an array, retrieve and concatenate values for each path
  if (Array.isArray(valuePaths)) {
    return valuePaths.map(retrieveValue).filter(Boolean).join(' ')
  }

  // Otherwise, retrieve the single value
  return retrieveValue(valuePaths)
}

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
.gray9 {
  color: $gray9 !important;
}
.expanded-row-cell {
  border-bottom: 0!important;
}
.hide-show-chevron {
  background-color: $app-blue;
  border-radius: 50%;
  color: white;
}
</style>
