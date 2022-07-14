<template>
  <v-card flat rounded class="mt-2">
    <v-data-table
      id="mh-home-owners-table"
      class="home-owners-table"
      disable-sort
      fixed
      fixed-header
      :headers="homeOwnersTableHeaders"
      hide-default-footer
      :items="homeOwners"
      item-key="id"
      no-data-text="No owners added yet"
    >
      <template v-slot:item="row">
        <tr :key="row.item.id">
          <td>
            {{ row.item.individualName.first }}
            {{ row.item.individualName.middle }}
            {{ row.item.individualName.last }}
          </td>
          <td></td>
          <td>{{ row.item.phoneNumber }} Ext {{ row.item.phoneExtension }}</td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'
import { homeOwnersTableHeaders } from '@/resources/tableHeaders'

export default defineComponent({
  name: 'HomeOwnersTable',
  props: {
    homeOwners: { default: [] }
  },
  setup () {
    return {
      homeOwnersTableHeaders
    }
  }
})
</script>

<style scoped></style>
