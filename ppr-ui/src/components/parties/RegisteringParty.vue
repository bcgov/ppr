<template>
  <v-container flat class="pa-0">
    <v-container class="pa-0">
      <v-row v-if="registeringParty" no-gutters class="pb-8 pt-2">
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
                <td class="list-item__title title-text" style="padding-left:30px">
                  <v-row no-gutters>
                    <v-col cols="3">
                      <div class="icon-div mt-n1 pr-4">
                        <v-icon v-if="isBusiness(row.item)">mdi-domain</v-icon>
                        <v-icon v-else>mdi-account</v-icon>
                      </div>
                    </v-col>
                    <v-col cols="9">
                      <div>
                        {{ getName(row.item) }}
                      </div>
                    </v-col>
                  </v-row>
                </td>
                <td>
                  <base-address :editing="false" :schema="addressSchema" :value="row.item.address" />
                </td>
                <td>{{ row.item.emailAddress }}</td>
                <td>{{ row.item.code }}</td>
                <td class="actions-cell actions-width px-0" v-if="registrationFlowType === RegistrationFlowType.NEW">
                <div class="actions float-right actions-up">

                  <v-btn
                      text
                      color="primary"
                      class="smaller-button edit-btn pr-5"
                      v-if="!row.item.action"
                      @click="changeRegisteringParty()"
                  >
                        <v-icon small>mdi-pencil</v-icon>
                        <span class="ml-1">Change</span>
                  </v-btn>
                  <v-btn
                      text
                      color="primary"
                      class="smaller-button edit-btn pr-5"
                      :disabled="addEditInProgress"
                      v-else
                      @click="undo()"
                  >
                        <v-icon small>mdi-undo</v-icon>
                        <span class="ml-1">Undo</span>
                  </v-btn>
                  <span class="actions-border actions__more"
                    v-if="row.item.action && !row.item.code"
                  >
                    <v-menu offset-y left nudge-bottom="4">
                      <template v-slot:activator="{ on }">
                        <v-btn
                          text
                          small
                          v-on="on"
                          color="primary"
                          :disabled="addEditInProgress"
                          class="smaller-actions actions__more-actions__btn"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list class="actions__more-actions">
                        <v-list-item @click="editRegisteringParty()">
                          <v-list-item-subtitle>
                            <v-icon small>mdi-pencil</v-icon>
                            <span class="ml-1">Edit</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </span>
                </div>
                </td>
              </tr>
              <tr v-if="showEditParty">
              <td
                colspan="5"
                class="pa-0"
              >
                <v-expand-transition>
                  <div class="edit-Party-container pa-0 col-12">
                    <edit-party :setIsRegisteringParty="true" @resetEvent="resetData" />
                  </div>
                </v-expand-transition>
              </td>
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
  computed,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { AddPartiesIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useParty } from '@/composables/useParty'
import { BaseAddress } from '@/composables/address'
import EditParty from './EditParty.vue'

import { editTableHeaders, registeringTableHeaders } from '@/resources'
import { getRegisteringPartyFromAuth } from '@/utils'
import { PartyAddressSchema } from '@/schemas'
import { RegistrationFlowType, ActionTypes } from '@/enums'

export default defineComponent({
  components: {
    BaseAddress,
    EditParty
  },
  setup (props, context) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const { getAddSecuredPartiesAndDebtors, getRegistrationFlowType, isRoleStaffSbc } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors', 'getRegistrationFlowType', 'isRoleStaffSbc'
    ])
    var parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    const addressSchema = PartyAddressSchema
    const registrationFlowType = getRegistrationFlowType.value

    /** First time get read only registering party from the auth api. After that get from the store. */
    onMounted(async () => {
      if (parties.registeringParty === null) {
        try {
          getRegisteringParty()
        } catch (e) {
          console.error('RegisteringParty.vue onMounted error: ' + ((e as Error).message))
        }
      }
    })
    const { getName, isBusiness } = useParty()
    const localState = reactive({
      addEditInProgress: false,
      showEditParty: false,
      registeringParty: computed((): Array<PartyIF> => {
        if (parties.registeringParty !== null) {
          return [parties.registeringParty]
        }
        return []
      }),
      partyHeaders: computed((): Array<any> => {
        if (registrationFlowType === RegistrationFlowType.NEW) {
          return [...registeringTableHeaders, ...editTableHeaders]
        } else {
          return registeringTableHeaders
        }
      })
    })

    const changeRegisteringParty = () => {
      context.emit('changeRegisteringParty')
    }

    const editRegisteringParty = () => {
      localState.showEditParty = true
    }

    const undo = async () => {
      getRegisteringParty()
    }

    const resetData = () => {
      localState.addEditInProgress = false
      localState.showEditParty = false
    }

    const getRegisteringParty = async () => {
      var parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
      if (!isRoleStaffSbc.value) {
        const regParty = await getRegisteringPartyFromAuth()
        parties.registeringParty = regParty
        setAddSecuredPartiesAndDebtors(parties)
      } else {
        parties.registeringParty = null
      }
    }

    return {
      getName,
      isBusiness,
      registrationFlowType,
      changeRegisteringParty,
      editRegisteringParty,
      resetData,
      RegistrationFlowType,
      ActionTypes,
      addressSchema,
      undo,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>

</style>
