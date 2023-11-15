<template>
  <v-container class="pa-0 flat">
    <v-container class="pa-0">
      <v-row
        noGutters
        class="pb-8 pt-2 rounded-top"
      >
        <v-col>
          <v-table class="registering-table party-data-table">
            <template #default>
              <!-- Table Headers -->
              <thead>
                <tr>
                  <th
                    v-for="header in headers"
                    :key="header.value"
                    :class="header.class"
                  >
                    {{ header.text }}
                  </th>
                </tr>
              </thead>

              <!-- Table Body -->
              <tbody v-if="registeringParty.length > 0">
                <tr
                  v-for="item in registeringParty"
                  :key="item.partyId"
                  class="registering-row"
                >
                  <td
                    class="generic-label"
                  >
                    <v-row noGutters>
                      <v-col cols="auto">
                        <div class="icon-div mt-n1 pr-4">
                          <v-icon v-if="isBusiness(item)">
                            mdi-domain
                          </v-icon>
                          <v-icon v-else>
                            mdi-account
                          </v-icon>
                        </div>
                      </v-col>
                      <v-col cols="9">
                        <div>
                          {{ getName(item) }}
                        </div>
                      </v-col>
                    </v-row>
                  </td>
                  <td>
                    <BaseAddress
                      :value="item.address"
                      :editing="false"
                      :schema="addressSchema"
                    />
                  </td>
                  <td>{{ item.emailAddress }}</td>
                  <td>{{ item.code }}</td>
                  <td class="actions-cell actions-width px-0">
                    <div class="actions actions-up">
                      <v-btn
                        v-if="!item.action"
                        variant="text"
                        color="primary"
                        class="smaller-button edit-btn pr-2 float-right"
                        @click="changeRegisteringParty()"
                      >
                        <v-icon size="small">
                          mdi-pencil
                        </v-icon>
                        <span class="ml-1 mr-2">Change</span>
                      </v-btn>
                      <v-btn
                        v-else
                        variant="text"
                        color="primary"
                        class="smaller-button edit-btn pr-0"
                        :disabled="addEditInProgress"
                        @click="undo()"
                      >
                        <v-icon size="small">
                          mdi-undo
                        </v-icon>
                        <span class="ml-1 mr-2">Undo</span>
                      </v-btn>
                      <span
                        v-if="item.action && !item.code"
                        class="actions-border actions__more"
                      >
                        <v-menu
                          location="bottom"
                        >
                          <template #activator="{ props }">
                            <v-btn
                              variant="text"
                              size="small"
                              color="primary"
                              :disabled="addEditInProgress"
                              class="smaller-actions actions__more-actions__btn"
                              v-bind="props"
                            >
                              <v-icon>mdi-menu-down</v-icon>
                            </v-btn>
                          </template>
                          <v-list class="actions__more-actions">
                            <v-list-item @click="editRegisteringParty()">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-pencil</v-icon>
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
                        <edit-party
                          :isRegisteringParty="true"
                          @resetEvent="resetData"
                        />
                      </div>
                    </v-expand-transition>
                  </td>
                </tr>
              </tbody>

              <!-- No Data Message -->
              <tbody v-else>
                <tr>
                  <td
                    class="text-center"
                    :colspan="headers.length"
                  >
                    We were unable to retrieve Registering Party from your account. Please try
                    again later. If this issue persists, please contact us.
                    <br><br>
                    <v-btn
                      id="retry-registering-party"
                      variant="outlined"
                      color="primary"
                      @click="getRegisteringParty()"
                    >
                      Retry
                      <v-icon>mdi-refresh</v-icon>
                    </v-btn>
                    <error-contact class="search-contact-container pt-6" />
                  </td>
                </tr>
              </tbody>
            </template>
          </v-table>
        </v-col>
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
} from 'vue'
import { useStore } from '@/store/store'
import { EditParty } from '@/components/parties/party'
import { BaseAddress } from '@/composables/address'
import { useParty } from '@/composables/useParty'
import { useRegisteringParty } from '@/composables/useRegisteringParty'
import { RegistrationFlowType, ActionTypes } from '@/enums'
import { PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { editTableHeaders, registeringTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas' // eslint-disable-line no-unused-vars
import { ErrorContact } from '@/components/common'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    BaseAddress,
    EditParty,
    ErrorContact
  },
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors, getRegistrationFlowType } = storeToRefs(useStore())
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
    const { getRegisteringParty } = useRegisteringParty()
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
      headers: computed((): Array<any> => {
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
