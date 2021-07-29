<template>
  <v-container fluid no-gutters class="pa-0">
    <v-data-table
      class="registration-table"
      :class="$style['reg-table']"
      :headers="headers"
      :items="tableData"
      disable-pagination
      hide-default-footer
      no-data-text="No registrations created yet."
    >
      <template v-slot:body.prepend>
        <tr class="filter-row">
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registrationNumber"
              type="text"
              label="Number"
              dense="true"
              @keypress="filterRow"
            ></v-text-field>
          </td>
          <td>
            <v-select
              :items="registrationTypes"
              single-line
              item-text="registrationTypeUI"
              item-value="registrationTypeAPI"
              filled
              dense="true"
              label="Registration Type"
              v-model="registrationType"
              id="txt-type"
              @change="filterRow"
            >
              <template slot="item" slot-scope="data">
                <span class="list-item">
                  {{ data.item.registrationTypeUI }}
                </span>
              </template>
            </v-select>
          </td>
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registrationDate"
              type="text"
              label="Date"
              dense="true"
            ></v-text-field>
          </td>
          <td></td>
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registeredBy"
              type="text"
              label="Registered By"
              dense="true"
            ></v-text-field>
          </td>
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="registeringParty"
              type="text"
              label="Registering Party"
              dense="true"
            ></v-text-field>
          </td>
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="securedParties"
              type="text"
              label="Secured Parties"
              dense="true"
            ></v-text-field>
          </td>
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="folioNumber"
              type="text"
              label=""
              dense="true"
            ></v-text-field>
          </td>
          <td>
            <v-text-field
              filled
              single-line
              hide-details="true"
              v-model="daysToExpiry"
              type="text"
              label="Days to Expiry"
              dense="true"
            ></v-text-field>
          </td>
          <td></td>
          <td></td>
        </tr>
      </template>
      <template v-slot:item="row" class="registration-data-table">
        <tr
          :key="row.item.id"
          class="registration-row"
          :class="draftClass(row.item.statusType)"
        >
          <td>
            {{ row.item.baseRegistrationNumber }}
          </td>
          <td>
            {{ getRegistrationType(row.item.registrationType) }}
          </td>
          <td>{{ getFormattedDate(row.item.createDateTime) }}</td>
          <td>{{ getStatusDescription(row.item.statusType) }}</td>
          <td></td>
          <td>{{ row.item.registeringParty || '' }}</td>
          <td>{{ row.item.securedParties || '' }}</td>
          <td>{{ row.item.clientReferenceId }}</td>
          <td>{{ row.item.expireDays || '' }}</td>
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
    const {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      registrationNumber,
      registrationDate,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      registrationType,
      registrationTypes,
      daysToExpiry,
      filterResults
    } = useRegistration()

    const localState = reactive({
      tableData: [],
      originalData: [],
      headers: registrationTableHeaders
    })

    const filterRow = () => {
      localState.tableData = filterResults(localState.originalData)
    }

    const draftClass = (val: string): string => {
      if (!val) {
        return 'font-italic'
      }
      return ''
    }

    /** Get the drafts and financing statements from the api. */
    onMounted(async () => {
      localState.tableData = await registrationHistory()
      const drafts = await draftHistory()
      // Array.prototype.push.apply(localState.tableData, drafts)
      localState.tableData = drafts
      localState.originalData = drafts
    })

    return {
      getFormattedDate,
      getRegistrationType,
      getStatusDescription,
      draftClass,
      registrationNumber,
      registrationType,
      registrationTypes,
      registrationDate,
      registeredBy,
      registeringParty,
      securedParties,
      folioNumber,
      daysToExpiry,
      filterRow,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.reg-table {
  max-height: 550px;
  tbody > tr > td:nth-child(1),
  thead > tr > th:nth-child(1) {
    position: sticky !important;
    position: -webkit-sticky !important;
    left: 0;
    z-index: 9998;
    background: white;
  }
  thead > tr > th:nth-child(1) {
    z-index: 9999;
  }
}
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
