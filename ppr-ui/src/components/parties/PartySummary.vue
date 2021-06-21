<template>
  <v-card flat id="collateral-summary">
    <v-row no-gutters class="summary-header pa-2">
      <v-col cols="auto" class="pa-2">
        <v-icon color="#38598A">mdi-car</v-icon>
        <label class="pl-3"><strong>Registering Party, Secured Parties, and Debtors</strong></label>
      </v-col>
    </v-row>
    <v-container
      v-if="showErrorSummary"
      :class="{ 'invalid-message': showErrorSummary }"
    >
      <v-row no-gutters class="pa-6">
        <v-col cols="auto">
          <v-icon color="#D3272C">mdi-information-outline</v-icon>
          <span class="invalid-message">This step is unfinished.</span>
          <router-link
            id="router-link-parties"
            class="invalid-link"
            :to="{ path: '/add-securedparties-debtors' }"
          >
            Return to this step to complete it.
          </router-link>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="generic-label">Regsitering Party</v-col>
      </v-row>
      <v-row no-gutters class="pt-4">
        <v-col>
          <v-data-table
            class="party-table"
            :headers="partyHeaders"
            :items="registeringParty"
            disable-pagination
            disable-sort
            hide-default-footer
          >
            <template v-slot:item="row" class="party-data-table">
              <tr :key="row.item.id" class="party-row">
                <td class="list-item__title">
                  {{ getName(row.item) }}
                </td>
                <td>
                  <span v-html="getFormattedAddress(row.item)"> </span>
                </td>
                <td>{{ row.item.emailAddress }}</td>
                <td>{{ row.item.code }}</td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      
      <v-row>
        <v-col class="generic-label">Secured Parties</v-col>
      </v-row>
      <v-row no-gutters class="pt-4">
        <v-col>
          <v-data-table
            class="party-table"
            :headers="partyHeaders"
            :items="securedParties"
            disable-pagination
            disable-sort
            hide-default-footer
            no-data-text="No Parties addeed yet."
          >
            <template v-slot:item="row" class="party-data-table">
              <tr :key="row.item.id" class="party-row">
                <td class="list-item__title">
                  {{ getName(row.item) }}
                </td>
                <td>
                  <span v-html="getFormattedAddress(row.item)"> </span>
                </td>
                <td>{{ row.item.emailAddress }}</td>
                <td>{{ row.item.code }}</td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="generic-label">Debtors</v-col>
      </v-row>
      <v-row no-gutters class="pt-4">
        <v-col>
          <v-data-table
            class="debtor-table"
            :headers="debtorHeaders"
            :items="debtors"
            disable-pagination
            disable-sort
            hide-default-footer
            no-data-text="No debtors added yet."
          >
            <template v-slot:item="row" class="debtor-data-table">
              <tr :key="row.item.id" class="debtor-row">
                <td class="list-item__title">
                  {{ getName(row.item) }}
                </td>
                <td>
                  <span v-html="getFormattedAddress(row.item)"> </span>
                </td>
                <td>{{ getFormattedBirthdate(row.item) }}</td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>


    </v-container>
  </v-card>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs
  // watch,
  // computed
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useParty } from '@/composables/useParty'

import { partyTableHeaders } from '@/resources'
import { debtorTableHeaders } from '@/resources'


export default defineComponent({
  setup (props, { emit }) {
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])

    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    const { getName, getFormattedAddress, getFormattedBirthdate } = useParty()
    const localState = reactive({
      debtors: parties.debtors,
      securedParties: parties.securedParties,
      registeringParty: [parties.registeringParty],
      debtorHeaders: debtorTableHeaders,
      partyHeaders: partyTableHeaders
    })

    return {
      getName,
      getFormattedAddress,
      getFormattedBirthdate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module></style>
