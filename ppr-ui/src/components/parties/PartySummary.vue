<template>
  <v-container flat class="pa-0" id="party-summary">
    <v-row no-gutters class="summary-header pa-2 rounded-top">
      <v-col cols="auto" class="pa-2">
        <v-icon color="#38598A">mdi-account-multiple-plus</v-icon>
        <label class="pl-3"
          ><strong
            >Registering Party, Secured Parties, and Debtors</strong
          ></label
        >
      </v-col>
    </v-row>
    <v-container class="pa-0">
      <v-row
        class="pt-6 px-1"
      >
        <v-col class="generic-label">Registering Party</v-col>
      </v-row>
      <v-row
        no-gutters
        class="pb-6 pt-4"
       >
        <v-col>
          <v-data-table
            class="registering-table"
            :headers="registeringHeaders"
            :items="registeringParty"
            disable-pagination
            disable-sort
            hide-default-footer
            no-data-text="No Registering Party obtained yet from user Account Information."
          >
            <template v-slot:item="row" class="party-data-table">
              <tr :key="row.item.id" class="registering-row">
                <td class="list-item__title">
                  <div class="icon-div" v-if="isBusiness(row.item)"
                    ><v-icon class="mt-n2 pr-4">mdi-domain</v-icon></div
                  >
                  <div class="icon-div" v-else
                    ><v-icon class="mt-n2 pr-4">mdi-account</v-icon></div
                  >
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

      <v-row class="px-1">
        <v-col class="generic-label">Secured Parties</v-col>
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          <v-data-table
            class="party-summary-table"
            :headers="partyHeaders"
            :items="securedParties"
            disable-pagination
            disable-sort
            hide-default-footer
            no-data-text=""
          >
            <template v-slot:item="row" class="party-data-table">
              <tr :key="row.item.id" class="party-row">
                <td class="list-item__title">
                  <div class="icon-div" v-if="isBusiness(row.item)"
                    ><v-icon class="mt-n2 pr-4">mdi-domain</v-icon></div
                  >
                  <div class="icon-div" v-else
                    ><v-icon class="mt-n2 pr-4">mdi-account</v-icon></div
                  >
                  {{ getName(row.item) }}
                </td>
                <td>
                  <span v-html="getFormattedAddress(row.item)"> </span>
                </td>
                <td>{{ row.item.emailAddress }}</td>
                <td>{{ row.item.code }}</td>
              </tr>
            </template>
            <template slot="no-data">
                  <v-icon color="#D3272C">mdi-information-outline</v-icon>
                  <span class="invalid-message">
                    This step is unfinished.
                  </span>
                  <span
                    id="router-link-parties"
                    class="invalid-link"
                    @click="goToParties()"
                    >Return to this step to complete it.</span
                  >
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-row class="px-1">
        <v-col class="generic-label">Debtors</v-col>
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          <v-data-table
            class="debtor-summary-table"
            :headers="debtorHeaders"
            :items="debtors"
            disable-pagination
            disable-sort
            hide-default-footer
            no-data-text=""
          >
            <template v-slot:item="row" class="debtor-data-table">
              <tr :key="row.item.id" class="debtor-row">
                <td class="list-item__title">
                  <div class="icon-div" v-if="isBusiness(row.item)"
                    ><v-icon class="mt-n2 pr-4">mdi-domain</v-icon></div
                  >
                  <div class="icon-div" v-else
                    ><v-icon class="mt-n2 pr-4">mdi-account</v-icon></div
                  >
                  {{ getName(row.item) }}
                </td>
                <td>
                  <span v-html="getFormattedAddress(row.item)"> </span>
                </td>
                <td>{{ getFormattedBirthdate(row.item) }}</td>
              </tr>
            </template>
            <template slot="no-data">
                  <v-icon color="#D3272C">mdi-information-outline</v-icon>
                  <span class="invalid-message">
                    This step is unfinished.
                  </span>
                  <span
                    id="router-link-parties"
                    class="invalid-link"
                    @click="goToParties()"
                    >Return to this step to complete it.</span
                  >
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useParty } from '@/composables/useParty'

import {
  partyTableHeaders,
  debtorTableHeaders,
  registeringTableHeaders
} from '@/resources'

export default defineComponent({
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const router = context.root.$router

    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    const {
      getName,
      getFormattedAddress,
      getFormattedBirthdate,
      isBusiness
    } = useParty()
    const localState = reactive({
      debtors: parties.debtors,
      securedParties: parties.securedParties,
      registeringParty:
        parties.registeringParty !== null ? [parties.registeringParty] : [],
      debtorHeaders: computed(function () {
        const headersToShow = [...debtorTableHeaders]
        headersToShow.pop()
        return headersToShow
      }),
      partyHeaders: computed(function () {
        const headersToShow = [...partyTableHeaders]
        headersToShow.pop()
        return headersToShow
      }),
      registeringHeaders: registeringTableHeaders,
      showErrorSummary: computed((): boolean => {
        return !parties.valid
      })
    })

    const goToParties = (): void => {
      parties.showInvalid = true
      setAddSecuredPartiesAndDebtors(parties)
      router.push({ path: '/add-securedparties-debtors' })
    }

    return {
      getName,
      isBusiness,
      getFormattedAddress,
      getFormattedBirthdate,
      goToParties,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module></style>
