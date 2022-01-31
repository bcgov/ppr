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
          >
            <template v-slot:item="row" class="party-data-table">
              <tr :key="row.item.id" class="registering-row">
                <td class="list-item__title title-text" style="padding-left:30px">
                  <v-row no-gutters>
                    <v-col cols="auto">
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
                <td class="actions-cell actions-width px-0">
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
            <template  v-slot:no-data>
              We were unable to retrieve Registering Party from your account. Please try
              again later. If this issue persists, please contact us.
              <br /><br />
              <v-btn
                id="retry-registering-party"
                outlined
                color="primary"
                @click="getRegisteringParty()"
              >
                Retry <v-icon>mdi-refresh</v-icon>
              </v-btn>
              <error-contact class="search-contact-container pt-6" />
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
// external libraries
import {
  defineComponent,
  onMounted,
  reactive,
  computed,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local components
import { EditParty } from '@/components/parties/party'
import { BaseAddress } from '@/composables/address'
// local helpers / types / etc.
import { useParty } from '@/composables/useParty'
import { RegistrationFlowType, ActionTypes } from '@/enums'
import { AddPartiesIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { editTableHeaders, registeringTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { getRegisteringPartyFromAuth } from '@/utils'
import { ErrorContact } from '@/components/common'

export default defineComponent({
  components: {
    BaseAddress,
    EditParty,
    ErrorContact
  },
  setup (props, context) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const {
      getAddSecuredPartiesAndDebtors,
      getRegistrationFlowType,
      isRoleStaffSbc,
      isRoleStaffReg
    } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors',
      'getRegistrationFlowType',
      'isRoleStaffSbc',
      'isRoleStaffReg'
    ])
    const addressSchema = PartyAddressSchema
    const registrationFlowType = getRegistrationFlowType.value

    /** First time get read only registering party from the auth api. After that get from the store. */
    onMounted(async () => {
      const regParty = getAddSecuredPartiesAndDebtors.value?.registeringParty
      if (regParty === null) {
        try {
          await getRegisteringParty()
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
        const regParty: PartyIF = getAddSecuredPartiesAndDebtors.value?.registeringParty
        if (regParty !== null) {
          return [regParty]
        }
        return []
      }),
      partyHeaders: computed((): Array<any> => {
        return [...registeringTableHeaders, ...editTableHeaders]
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
        const regParty = await getRegisteringPartyFromAuth(isRoleStaffReg.value)
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
      getRegisteringParty,
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

<style lang="scss" scoped>
.search-contact-container {
  width: 350px;
  font-size: 0.875rem;
}
</style>
