<template>
  <v-container
    class="pa-0 flat"
    role="region"
  >
    <v-container class="pa-0">
      <v-row
        no-gutters
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
              <tbody v-if="registeringParty.length > 0 && Object.keys(registeringParty[0]).length">
                <tr v-if="showEditParty">
                  <td
                    colspan="5"
                    class="pa-0"
                  >
                    <v-expand-transition>
                      <div class="edit-Party-container pa-0 col-12">
                        <edit-party
                          :is-registering-party="true"
                          :is-edit-mode="true"
                          @reset-event="resetData"
                        />
                      </div>
                    </v-expand-transition>
                  </td>
                </tr>
                <tr
                  v-for="item in registeringParty"
                  v-else
                  :key="item.partyId"
                  class="registering-row"
                >
                  <td
                    class="generic-label"
                  >
                    <v-row
                      no-gutters
                      :aria-label="`${isBusiness(item) ? 'Business' : 'Person'} ${getName(item)}`"
                    >
                      <v-col
                        cols="auto"
                        aria-hidden="true"
                      >
                        <div class="icon-div mt-n1 pr-2">
                          <v-icon v-if="isBusiness(item)">
                            mdi-domain
                          </v-icon>
                          <v-icon v-else>
                            mdi-account
                          </v-icon>
                        </div>
                      </v-col>
                      <v-col
                        cols="9"
                        aria-hidden="true"
                      >
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
                  <td>
                    <span
                      v-if="requiresEmail(item)"
                      class="error-text"
                    >*Required
                    </span>
                    <span v-else>
                      {{item.emailAddress}}
                    </span>
                  </td>
                  <td>
                    {{ item.code }}
                  </td>
                  <td
                    v-if="!isSecurityActNotice"
                    class="ml-8 pr-0"
                  >
                    <div class="actions inline-flex mt-0 pt-0">
                      <v-btn
                        v-if="!item.action"
                        variant="plain"
                        color="primary"
                        class="smaller-button edit-btn pr-2"
                        @click="editRegisteringParty()"
                      >
                        <v-icon size="small">
                          mdi-pencil
                        </v-icon>
                        <span class="ml-1 mr-2">Edit</span>
                      </v-btn>
                      <v-btn
                        v-else
                        variant="plain"
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
                        v-if="item.action"
                        class="actions-border actions__more m-auto"
                      >
                        <v-menu
                          location="bottom right"
                        >
                          <template #activator="{ props }">
                            <v-btn
                              variant="plain"
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
import type { PartyIF } from '@/interfaces'
import { editTableHeaders, registeringTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { ErrorContact } from '@/components/common'
import { storeToRefs } from 'pinia'
import { usePprRegistration } from '@/composables'
import { partyCodeAccount } from '@/utils/ppr-api-helper'
import { useSecuredParty } from '@/composables/parties'

export default defineComponent({
  components: {
    BaseAddress,
    EditParty,
    ErrorContact
  },
  emits: ['changeRegisteringParty', 'editingRegisteringParty', 'emailRequiredValidation'],
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors, getRegistrationFlowType } = storeToRefs(useStore())
    const addressSchema = PartyAddressSchema
    const registrationFlowType = getRegistrationFlowType.value
    const { isSecurityActNotice } = usePprRegistration()
    const { setRegisteringAndSecuredParty } = useSecuredParty()

    /** First time get read only registering party from the auth api. After that get from the store. */
    onMounted(async () => {
      if(isSecurityActNotice.value) {
        const party = await partyCodeAccount(true)
        await setRegisteringAndSecuredParty(party[0] as PartyIF)
        return
      }

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
      context.emit('editingRegisteringParty', true)
    }

    const undo = async () => {
      getRegisteringParty()
    }

    const resetData = () => {
      localState.addEditInProgress = false
      localState.showEditParty = false
      context.emit('editingRegisteringParty', false)
    }

    // Check if the item requires an email address
    const requiresEmail = (item) => {
      const required = !!(item.action && !item.emailAddress)
      context.emit('emailRequiredValidation', required)
      return required
    }

    return {
      getName,
      isBusiness,
      requiresEmail,
      registrationFlowType,
      changeRegisteringParty,
      editRegisteringParty,
      getRegisteringParty,
      resetData,
      RegistrationFlowType,
      ActionTypes,
      addressSchema,
      undo,
      isSecurityActNotice,
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
