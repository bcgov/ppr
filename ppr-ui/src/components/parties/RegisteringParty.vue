<template>
  <v-container flat class="pa-0">
    <v-container class="pa-0">
      <v-row v-if="registeringParty" no-gutters class="pb-6 pt-4">
        <v-col>
          <v-data-table
            class="registering-table"
            :headers="partyHeaders"
            :items="registeringParty"
            disable-pagination
            disable-sort
            hide-default-footer
            no-data-text="No Registering Party obtained from user Account Information."
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
      <v-row v-else no-gutters class="pb-6 pt-4">
        <v-col>No Registering Party obtained from user Account Information.</v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  onMounted,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { AddPartiesIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useParty } from '@/composables/useParty'

import { registeringTableHeaders } from '@/resources'
import { getRegisteringPartyFromAuth } from '@/utils'

export default defineComponent({
  setup (props, context) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    var parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    /** First time get read only registering party from the auth api. After that get from the store. */
    onMounted(async () => {
      if (parties.registeringParty === null) {
        try {
          const regParty = await getRegisteringPartyFromAuth()
          parties.registeringParty = regParty
          setAddSecuredPartiesAndDebtors(parties)
          localState.registeringParty = [regParty]
          context.emit('setRegisteringParty')
        } catch (e) {
          localState.registeringParty = null
          console.error('RegisteringParty.vue onMounted error: ' + e.message)
        }
      } else {
        localState.registeringParty = [parties.registeringParty]
      }
    })
    const { getName, getFormattedAddress, isBusiness } = useParty()
    const localState = reactive({
      registeringParty: null,
      partyHeaders: registeringTableHeaders
    })

    return {
      getName,
      getFormattedAddress,
      isBusiness,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>

</style>
