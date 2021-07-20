<template>
  <v-container fluid no-gutters class="pa-0">
    <v-data-table
      class="registration-table"
      :headers="headers"
      :items="tableData"
      disable-pagination
      hide-default-footer
      no-data-text="No registrations created yet."
    >
      <template v-slot:item="row" class="registration-data-table">
        <tr :key="row.item.id" class="registration-row">
          <td>
            {{ row.item.baseRegistrationNumber }}
          </td>
          <td>
            {{ getRegistrationType(row.item.registrationType) }}
          </td>
          <td>{{ row.item.statusType || 'Draft' }}</td>
          <td>{{ row.item.securedParties || '' }}</td>
          <td>{{ getFormattedDate(row.item.createDateTime) }}</td>
          <td>{{ row.item.registeringParty || '' }}</td>
          <td>{{ row.item.clientReferenceId }}</td>
          <td>{{ row.item.expireDays || '' }}</td>
          <td>{{ getFormattedDate(row.item.lastUpdateDateTime) }}</td>
          <td></td>

          <!-- Action Btns -->
          <td class="actions-cell px-0 py-2">
            <div class="actions float-right">
              <span class="edit-action">
                <v-btn
                  text
                  color="primary"
                  class="edit-btn"
                  :id="'class-' + row.index + '-change-added-btn'"
                >
                  <v-icon small>mdi-pencil</v-icon>
                  <span>Edit</span>
                </v-btn>
              </span>

              <span class="actions__more">
                <v-menu offset-y left nudge-bottom="4">
                  <template v-slot:activator="{ on }">
                    <v-btn
                      text
                      small
                      v-on="on"
                      color="primary"
                      class="actions__more-actions__btn"
                    >
                      <v-icon>mdi-menu-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list class="actions__more-actions">
                    <v-list-item>
                      <v-list-item-subtitle>
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1">Remove</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </div>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  onMounted
} from '@vue/composition-api'

import { registrationTableHeaders } from '@/resources'
import { registrationHistory, draftHistory } from '@/utils' // eslint-disable-line
import { useRegistration } from '@/composables/useRegistration'

export default defineComponent({
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { getFormattedDate, getRegistrationType } = useRegistration()

    const localState = reactive({
      tableData: [],
      headers: registrationTableHeaders
    })

    /** Get the drafts and financing statements from the api. */
    onMounted(async () => {
      localState.tableData = await registrationHistory()
      const drafts = await draftHistory()
      // Array.prototype.push.apply(localState.tableData, drafts)
      localState.tableData = drafts
    })

    return {
      getFormattedDate,
      getRegistrationType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.length-trust-label {
  font-size: 0.875rem;
}
.summary-text {
  font-size: 14px;
  color: $gray7;
}
.title-text {
  color: $gray9 !important;
}
.summary-cell {
  overflow: visible;
  text-overflow: inherit;
  white-space: inherit;
}
</style>
