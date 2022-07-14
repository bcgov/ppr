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
          <td class="py-6">
            <v-icon color="darker">mdi-account</v-icon>
            {{ row.item.individualName.first }}
            {{ row.item.individualName.middle }}
            {{ row.item.individualName.last }}
          </td>
          <td class="py-6">
            <base-address :schema="addressSchema" :value="row.item.address" />
          </td>
          <td class="py-6">
            {{ row.item.phoneNumber }}
            <span v-if="row.item.phoneExtension">
              Ext {{ row.item.phoneExtension }}
            </span>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'
import { homeOwnersTableHeaders } from '@/resources/tableHeaders'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'

export default defineComponent({
  name: 'HomeOwnersTable',
  props: {
    homeOwners: { default: [] }
  },
  components: {
    BaseAddress
  },
  setup () {
    const addressSchema = PartyAddressSchema

    return {
      addressSchema,
      homeOwnersTableHeaders
    }
  }
})
</script>

<style scoped></style>
