<template>
  <v-container fluid no-gutters class="pa-0">
    <v-row v-if="isSecuredPartyRestrictedList(registrationType)">
      <v-col cols="auto"
        >Include Secured Party in your registration by adding their secured
        party code or their name (business or person). The account number of the
        Secured Party must match the account number of the Registering Party.<br/>
        <div class="font-weight-bold pt-2">Only one Secured Party is allowed.</div>
      </v-col>
    </v-row>
    <v-row
      no-gutters
      class="pb-4 pt-6"
      v-if="isSecuredPartyRestrictedList(registrationType)"
    >
      <v-col cols="12" class="party-search">
        <v-autocomplete
          id="secured-party-autocomplete"
          allow-overflow
          filled
          full-width
          hide-details
          :filter="filterList"
          :loading="loading"
          :items="partyResults"
          item-text="businessName"
          item-value="code"
          label="Secured Party Code or Name"
          no-data-text="No matches found."
          :menu-props="{ maxHeight: '325px' }"
          offset="1000"
          return-object
          v-model="searchValue"
          class="mx-7 my-8"
        >
           <template v-slot:selection="{ item }">
            <span v-text="item.code"></span>
            <span class="ml-4" v-text="item.businessName"></span>
          </template>
          <template v-slot:item="{ item }">
            <template>
              <v-list-item-content @click="selectResult(item)">
                <v-row class="auto-complete-row">
                  <v-col cols="1">{{ item.code }}</v-col>
                  <v-col cols="9"
                    >{{ item.businessName }}<br />
                    <div class="pt-2">
                    {{ item.address.street }},
                    {{ item.address.city }}
                    {{ item.address.region }}
                    {{ getCountryName(item.address.country) }},
                    {{ item.address.postalCode }}
                    </div>
                  </v-col>
                </v-row>
              </v-list-item-content>
            </template>
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>

    <v-row no-gutters v-if="!isSecuredPartyRestrictedList(registrationType)">
      <v-col cols="auto"
        >Include Secured Parties in your registration by adding their secured
        party code or their name (business or person), or if the Secured Party
        you want to include is new (i.e., they do not have a secured party code)
        you can add their information manually.
      </v-col>
    </v-row>
    <v-row
      no-gutters
      class="pb-4 pt-6"
      v-if="!isSecuredPartyRestrictedList(registrationType)"
    >
      <party-search
        :isAutoCompleteDisabled="addEditInProgress"
        :registeringPartyAdded="registeringPartyAdded"
        @showSecuredPartyAdd="initAdd"
        @addRegisteringParty="addRegisteringParty"
        @removeRegisteringParty="removeRegisteringParty"
      />
    </v-row>
    <v-row no-gutters>
      <v-col>
        <div :class="{ 'invalid-section': invalidSection }">
          <v-expand-transition>
            <v-card flat class="add-party-container" v-if="showAddSecuredParty">
              <edit-party
                :activeIndex="activeIndex"
                :invalidSection="invalidSection"
                @resetEvent="resetData"
              />
            </v-card>
          </v-expand-transition>
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pt-2">
      <v-col>
        <v-data-table
          class="party-table"
          :class="{ 'invalid-message': showErrorSecuredParties }"
          :headers="headers"
          :items="securedParties"
          disable-pagination
          disable-sort
          hide-default-footer
          no-data-text="No Parties added yet."
        >
          <template v-slot:item="row" class="party-data-table">
            <tr
              v-if="!showEditParty[row.index]"
              :key="row.item.id"
              class="party-row"
            >
              <td class="list-item__title title-text">
                <div class="icon-div" v-if="isBusiness(row.item)">
                  <v-icon class="mt-n2 pr-4">mdi-domain</v-icon>
                </div>
                <div class="icon-div" v-else>
                  <v-icon class="mt-n2 pr-4">mdi-account</v-icon>
                </div>
                {{ getName(row.item) }}
              </td>
              <td>
                <base-address
                  :editing="false"
                  :schema="addressSchema"
                  :value="row.item.address"
                />
              </td>
              <td>{{ row.item.emailAddress }}</td>
              <td>{{ row.item.code }}</td>
              <!-- Action Btns -->
              <td class="actions-cell  px-0 py-2">
                <div
                  class="actions float-right"
                  v-if="isRegisteringParty(row.item) || isSecuredPartyRestrictedList(registrationType)"
                >
                  <v-list
                    class="actions__more-actions"
                    :disabled="addEditInProgress"
                  >
                    <v-list-item
                      class="v-remove"
                      @click="removeParty(row.index)"
                    >
                      <v-list-item-subtitle>
                        <v-icon small>mdi-delete</v-icon>
                        <span class="ml-1">Remove</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </div>
                <div class="actions float-right" v-else>
                  <span class="edit-action">
                    <v-btn
                      text
                      color="primary"
                      class="edit-btn"
                      :id="'class-' + row.index + '-change-added-btn'"
                      @click="initEdit(row.index)"
                      :disabled="addEditInProgress"
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
                          :disabled="addEditInProgress"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list class="actions__more-actions">
                        <v-list-item @click="removeParty(row.index)">
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

            <!-- Edit Form -->
            <tr v-if="showEditParty[row.index]">
              <td
                colspan="5"
                class="pa-0"
                :class="{ 'invalid-section': invalidSection }"
              >
                <v-expand-transition>
                  <div class="edit-Party-container pa-0 col-12">
                    <edit-party
                      :activeIndex="activeIndex"
                      :invalidSection="invalidSection"
                      @removeParty="removeParty"
                      @resetEvent="resetData"
                    />
                  </div>
                </v-expand-transition>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row>
      <v-col> </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed,
  onMounted,
  watch
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { isEqual } from 'lodash'
import { PartyIF, AddPartiesIF, SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import EditParty from './EditParty.vue'
import PartySearch from './PartySearch.vue'
import PartyAutocomplete from './PartyAutocomplete.vue'
import { useParty } from '@/composables/useParty'
import { useSecuredParty } from './composables/useSecuredParty'
import { BaseAddress } from '@/composables/address'

import { partyTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { partyCodeSearch } from '@/utils'
import { APIRegistrationTypes } from '@/enums'
import { useCountriesProvinces } from '@/composables/address/factories'

export default defineComponent({
  components: {
    EditParty,
    PartySearch,
    BaseAddress,
    PartyAutocomplete
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    const { getRegistrationType } = useGetters<any>(['getRegistrationType'])
    const registrationType = getRegistrationType.value.registrationTypeAPI
    const countryProvincesHelpers = useCountriesProvinces()

    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    const addressSchema = PartyAddressSchema
    const { getName, isPartiesValid, isBusiness } = useParty()
    const { isSecuredPartyRestrictedList } = useSecuredParty(props, context)

    const localState = reactive({
      summaryView: props.isSummary,
      showAddSecuredParty: false,
      currentIsBusiness: true,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditParty: [false],
      partyResults: [],
      savedPartyResults: [],
      searchValue: { code: '', businessName: '' },
      loading: false,
      securedParties: parties.securedParties,
      registeringPartyAdded: false,
      showErrorSummary: computed((): boolean => {
        return !parties.valid
      }),
      showErrorSecuredParties: computed((): boolean => {
        return parties.showInvalid && parties.securedParties.length === 0
      }),
      headers: partyTableHeaders
    })

    const removeParty = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      if (isRegisteringParty(localState.securedParties[index])) {
        localState.registeringPartyAdded = false
      }
      localState.securedParties.splice(index, 1)
      currentParties.securedParties = localState.securedParties
      currentParties.valid = isPartiesValid(currentParties)
      setAddSecuredPartiesAndDebtors(currentParties)
      localState.searchValue = { code: '', businessName: '' }
    }

    const removeRegisteringParty = (): void => {
      for (let i = 0; i < localState.securedParties.length; i++) {
        if (isEqual(localState.securedParties[i], parties.registeringParty)) {
          removeParty(i)
          localState.registeringPartyAdded = false
        }
      }
    }

    const addRegisteringParty = () => {
      let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      let newList: PartyIF[] = parties.securedParties // eslint-disable-line
      const registeringParty: PartyIF =
        parties.registeringParty !== null ? parties.registeringParty : null
      newList.push(registeringParty)

      parties.securedParties = newList

      setAddSecuredPartiesAndDebtors(parties)
      localState.registeringPartyAdded = true
    }

    const isRegisteringParty = (partyRow: PartyIF): boolean => {
      if (isEqual(partyRow, parties.registeringParty)) {
        return true
      }
      return false
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditParty[index] = true
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddSecuredParty = true
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddSecuredParty = false
      localState.showEditParty = [false]
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      currentParties.valid = isPartiesValid(currentParties)
      setAddSecuredPartiesAndDebtors(currentParties)
    }

    const fetchOtherSecuredParties = async () => {
      localState.loading = true
      if (parties.registeringParty) {
        // go to the service and see if there are similar secured parties
        const response: [SearchPartyIF] = await partyCodeSearch(
          parties.registeringParty.businessName,
          true
        )
        // check if any results
        if (response?.length > 0) {
          localState.partyResults = response
          localState.loading = false
        }
      } else {
        setTimeout(fetchOtherSecuredParties, 3000)
      }
    }

    onMounted(() => {
      for (let i = 0; i < localState.securedParties.length; i++) {
        if (isEqual(localState.securedParties[i], parties.registeringParty)) {
          localState.registeringPartyAdded = true
        }
      }

      if (isSecuredPartyRestrictedList(registrationType)) {
        fetchOtherSecuredParties()
      }
    })

    const filterList = (
      item: SearchPartyIF,
      queryText: string,
      itemText: string
    ) => {
      const textOne = item.businessName.toLowerCase()
      const searchText = queryText.toLowerCase()
      return (
        textOne.indexOf(searchText) > -1 || item.code.indexOf(searchText) > -1
      )
    }

    const selectResult = (party: SearchPartyIF) => {
      let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      const newParty: PartyIF = {
        code: party.code,
        businessName: party.businessName,
        emailAddress: party.emailAddress || '',
        address: party.address,
        personName: { first: '', middle: '', last: '' }
      }
      parties.securedParties = [newParty]
      setAddSecuredPartiesAndDebtors(parties)
      localState.securedParties = [newParty]
    }

    return {
      removeParty,
      getName,
      isBusiness,
      initEdit,
      initAdd,
      resetData,
      parties,
      isRegisteringParty,
      addRegisteringParty,
      removeRegisteringParty,
      addressSchema,
      isSecuredPartyRestrictedList,
      registrationType,
      selectResult,
      filterList,
      ...countryProvincesHelpers,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.v-remove {
  padding-right: 40px;
}
.v-remove:hover {
  background-color: white important;
}

.party-search {
  background-color: white;
}
.auto-complete-row {
  font-size: 14px;
  width: 35rem;
}

::v-deep .party-search .v-select__selections {
  color: $gray7 !important;
}

::v-deep .v-list-item--active {
  padding-left: 30px;
  color: $primary-blue !important;
  font-size: 14px;
}

::v-deep .v-list-item__content {
  padding: 6px 0;
}
</style>
