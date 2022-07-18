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
        <tr v-if="isCurrentlyEditing(homeOwners.indexOf(row.item))">
          <td class="pa-0" :colspan="homeOwnersTableHeaders.length">
            <v-expand-transition>
              <AddHomeOwnerPerson
                :editHomeOwner="row.item"
                @done="edit($event)"
                @cancel="activeIndex = -1"
                @remove="remove(row.item)"
              />
            </v-expand-transition>
          </td>
        </tr>

        <tr v-else :key="row.item.id">
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
          <td class="text-right pr-2">
            <v-btn
              text
              color="primary"
              class="px-0"
              :ripple="false"
              :disabled="isAdding"
              @click="openForEditing(homeOwners.indexOf(row.item))"
            >
              <v-icon small>mdi-pencil</v-icon>
              <span>Edit</span>
              <v-divider class="ma-0 pl-3" vertical />
            </v-btn>
            <!-- Actions drop down menu -->
            <v-menu offset-y left nudge-bottom="4">
              <template v-slot:activator="{ on }">
                <v-btn
                  text
                  small
                  v-on="on"
                  color="primary"
                  :disabled="isAdding"
                >
                  <v-icon class="ml-n1">mdi-menu-down</v-icon>
                </v-btn>
              </template>

              <!-- More actions drop down list -->
              <v-list class="actions-dropdown actions__more-actions">
                <v-list-item class="my-n2">
                  <v-list-item-subtitle class="pa-0" @click="remove(row.item)">
                    <v-icon small>mdi-delete</v-icon>
                    <span class="ml-1 remove-btn-text">Remove</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { homeOwnersTableHeaders } from '@/resources/tableHeaders'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'

import { AddHomeOwnerPerson } from '@/components/mhrRegistration/HomeOwners'

export default defineComponent({
  name: 'HomeOwnersTable',
  props: {
    homeOwners: { default: [] },
    isAdding: { default: false }
  },
  components: {
    BaseAddress,
    AddHomeOwnerPerson
  },
  setup (props, context) {
    const addressSchema = PartyAddressSchema

    const localState = reactive({
      activeIndex: -1
    })

    const edit = (item): void => {
      context.emit('edit', { ...item, id: localState.activeIndex })
    }

    const remove = (item): void => {
      localState.activeIndex = -1
      context.emit('remove', item)
    }

    const openForEditing = (index: number) => {
      localState.activeIndex = index
    }

    const isCurrentlyEditing = (index: number): boolean => {
      return index === localState.activeIndex
    }

    return {
      addressSchema,
      homeOwnersTableHeaders,
      openForEditing,
      isCurrentlyEditing,
      edit,
      remove,
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
