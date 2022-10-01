<template>
  <v-card flat rounded :class="{ 'border-error-left': showTableError }">
    <v-data-table
      id="mh-home-owners-table"
      class="home-owners-table"
      :class="{ 'review-mode': isReadonlyTable }"
      :headers="homeOwnersTableHeaders"
      hide-default-footer
      :items="homeOwners"
      item-key="groupId"
      :group-by="showGroups ? 'groupId' : null"
      disable-sort
      disable-pagination
    >
      <template v-slot:group.header="{ group, items }" class="group-header-slot">
        <td :colspan="4" class="py-1">
          <TableGroupHeader
            :groupId="group"
            :owners="hasActualOwners(items) ? items : []"
            :showEditActions="showEditActions"
            :isMhrTransfer="isMhrTransfer"
          />
        </td>
      </template>

      <template v-slot:item="row" v-if="homeOwners.length">
        <tr v-if="isCurrentlyEditing(homeOwners.indexOf(row.item))">
          <td class="pa-0" :colspan="homeOwnersTableHeaders.length">
            <v-expand-transition>
              <AddEditHomeOwner
                :editHomeOwner="row.item"
                :isHomeOwnerPerson="!row.item.organizationName"
                :isMhrTransfer="isMhrTransfer"
                @cancel="currentlyEditingHomeOwnerId = -1"
                @remove="remove(row.item)"
              />
            </v-expand-transition>
          </td>
        </tr>

        <tr v-else-if="row.item.id" :key="row.item.id" class="owner-info">
          <td class="owner-name">
            <div v-if="row.item.individualName" class="owner-icon-name">
              <v-icon class="mr-2">mdi-account</v-icon>
              <div class="owner-name-bold">
                {{ row.item.individualName.first }}
                {{ row.item.individualName.middle }}
                {{ row.item.individualName.last }}
              </div>
            </div>
            <div v-else class="owner-icon-name">
              <v-icon class="mr-2">mdi-domain</v-icon>
              <div>
                {{ row.item.organizationName }}
              </div>
            </div>
            <div v-if="row.item.suffix" class="suffix">
              {{ row.item.suffix }}
            </div>
            <v-chip v-if="isMhrTransfer" class="badge-added ml-8 mt-2" color="primary" label text-color="white" x-small>
              <b>ADDED</b>
            </v-chip>
          </td>
          <td>
            <base-address :schema="addressSchema" :value="row.item.address" />
          </td>
          <td>
            {{ toDisplayPhone(row.item.phoneNumber) }}
            <span v-if="row.item.phoneExtension"> Ext {{ row.item.phoneExtension }} </span>
          </td>
          <td v-if="showEditActions" class="text-right">
            <v-btn
              text
              color="primary"
              class="pr-0"
              :ripple="false"
              :disabled="isAddingMode || isEditingMode || isGlobalEditingMode"
              @click="openForEditing(homeOwners.indexOf(row.item))"
              data-test-id="table-edit-btn"
            >
              <v-icon small>mdi-pencil</v-icon>
              <span>Edit</span>
              <v-divider class="ma-0 pl-3" vertical />
            </v-btn>
            <!-- Actions drop down menu -->
            <v-menu offset-y left nudge-bottom="0">
              <template v-slot:activator="{ on }">
                <v-btn text v-on="on"
                 color="primary" class="px-0"
                 :disabled="isAddingMode || isGlobalEditingMode"
                >
                  <v-icon>mdi-menu-down</v-icon>
                </v-btn>
              </template>

              <!-- More actions drop down list -->
              <v-list class="actions-dropdown actions__more-actions">
                <v-list-item class="my-n2">
                  <v-list-item-subtitle class="pa-0" @click="remove(row.item)">
                    <v-icon small style="margin-bottom: 3px;">mdi-delete</v-icon>
                    <span class="ml-1 remove-btn-text">Remove</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </td>
        </tr>
        <tr v-else>
          <td :colspan="4" class="py-1">
            <div class="my-6 text-center">
              No owners added yet.
            </div>
          </td>
        </tr>
      </template>
      <template v-slot:no-data>
        <div class="error-text pa-4 text-center">No owners added yet.</div>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { homeOwnersTableHeaders, homeOwnersTableHeadersReview } from '@/resources/tableHeaders'
import { BaseAddress } from '@/composables/address'
import { useHomeOwners } from '@/composables/mhrRegistration'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'
import { AddEditHomeOwner } from '@/components/mhrRegistration/HomeOwners'
import TableGroupHeader from '@/components/mhrRegistration/HomeOwners/TableGroupHeader.vue'
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnerIF } from '@/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeOwnersTable',
  props: {
    homeOwners: { default: [] as MhrRegistrationHomeOwnerIF[] },
    isAdding: { default: false },
    isReadonlyTable: { type: Boolean, default: false },
    isMhrTransfer: { type: Boolean, default: false }
  },
  components: {
    BaseAddress,
    AddEditHomeOwner,
    TableGroupHeader
  },
  setup (props) {
    const addressSchema = PartyAddressSchema

    const {
      showGroups,
      removeOwner,
      deleteGroup,
      isGlobalEditingMode,
      setGlobalEditingMode,
      hasEmptyGroup
    } = useHomeOwners()

    const localState = reactive({
      currentlyEditingHomeOwnerId: -1,
      isEditingMode: computed((): boolean => localState.currentlyEditingHomeOwnerId >= 0),
      isAddingMode: computed((): boolean => props.isAdding),
      showTableError: computed((): boolean => hasEmptyGroup.value && showGroups.value),
      showEditActions: computed((): boolean => !props.isReadonlyTable),
      homeOwnersTableHeaders: props.isReadonlyTable ? homeOwnersTableHeadersReview : homeOwnersTableHeaders
    })

    const remove = (item): void => {
      localState.currentlyEditingHomeOwnerId = -1
      removeOwner(item, props.isMhrTransfer)
    }

    const openForEditing = (index: number) => {
      localState.currentlyEditingHomeOwnerId = index
    }

    const isCurrentlyEditing = (index: number): boolean => {
      return index === localState.currentlyEditingHomeOwnerId
    }

    // To render Group table header the owners array must not be empty
    // check for at least one owner with an id
    // This util function will help to show Owners: 0 in the table header
    const hasActualOwners = (owners: MhrRegistrationHomeOwnerIF[]): boolean => {
      return owners.length > 0 && owners[0]?.id !== undefined
    }

    watch(
      () => localState.currentlyEditingHomeOwnerId,
      () => {
        setGlobalEditingMode(localState.isEditingMode)
      }
    )

    return {
      addressSchema,
      toDisplayPhone,
      openForEditing,
      isCurrentlyEditing,
      showGroups,
      hasEmptyGroup,
      hasActualOwners,
      remove,
      deleteGroup,
      isGlobalEditingMode,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.home-owners-table ::v-deep {
  tr.v-row-group__header,
  tbody tr.v-row-group__header:hover {
    background-color: #e2e8ee;
  }

  .owner-name,
  i {
    color: $gray9 !important;
    font-weight: bold;
  }

  .owner-name-bold {
    color: #212529;
    font-weight: bold;
  }

  table {
    tbody > tr > td {
      padding: 20px 12px;
    }
    th:first-child,
    td:first-child {
      padding-left: 30px;
    }
    td:last-child {
      padding-right: 30px;
      padding-top: 8px;
    }
    tbody > tr.v-row-group__header,
    tbody > tr.v-row-group__header:hover {
      background: #e2e8ee !important;
    }

    .no-owners-error {
      text-align: center;
      color: $error;
    }
  }

  .owner-icon-name {
    display: flex;
    align-items: flex-start;
    div {
      word-break: break-word;
    }
    i {
      margin-top: -3px;
    }
  }
  .owner-info {
    td {
      white-space: normal;
      vertical-align: top;
    }
  }

  .v-data-table-header th {
    padding: 0 12px;
  }

  .suffix {
    color: #495057;
    font-size: 14px;
    line-height: 22px;
    margin-left: 32px;
  }
  .theme--light.v-btn.v-btn--disabled {
    color:#1669bb !important;
    opacity: 0.4 !important;
  }
}

.v-menu__content {
  cursor: pointer;
}
.review-mode ::v-deep {
  table {
    th:first-child,
    td:first-child {
      padding-left: 0 !important;
    }
  }
  tbody > tr.v-row-group__header {
    margin-left: 20px !important;
    padding-left: 20px !important;
  }
}
</style>
