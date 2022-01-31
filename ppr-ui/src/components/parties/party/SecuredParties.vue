<template>
  <v-container fluid no-gutters id="secured-parties-component" class="pa-0">
    <change-secured-party-dialog
      attach="#app"
      :display="showDialog"
      :securedPartyName="currentPartyName"
      @proceed="dialogSubmit($event)"
    />
    <v-row v-if="isSecuredPartyRestrictedList(registrationType)">
      <v-col cols="auto"
        >Include the Secured Party in your registration by adding their secured
        party code or their name (business or person). The account number of the
        Secured Party must match the account number of the Registering Party.<br />
        <div class="font-weight-bold pt-2">
          Only one Secured Party is allowed.
        </div>
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
                :setShowErrorBar="showErrorBar"
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
          :class="{ 'invalid-message': showErrorSecuredParties && !getSecuredPartyValidity() }"
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
              :class="{ 'disabled-text-not-action': row.item.action === ActionTypes.REMOVED}"
            >
              <td class="list-item__title title-text" style="padding-left:30px">
                <v-row no-gutters>
                  <v-col cols="3" :class="{ 'disabled-text': row.item.action === ActionTypes.REMOVED}">
                    <div class="icon-div mt-n1 pr-4">
                      <v-icon v-if="isBusiness(row.item)">mdi-domain</v-icon>
                      <v-icon v-else>mdi-account</v-icon>
                    </div>
                  </v-col>
                  <v-col cols="9">
                    <div :class="{ 'disabled-text': row.item.action === ActionTypes.REMOVED}">
                      {{ getName(row.item) }}
                    </div>
                    <div v-if="row.item.action && registrationFlowType === RegistrationFlowType.AMENDMENT">
                      <v-chip v-if="row.item.action === ActionTypes.REMOVED"
                          x-small label color="#grey lighten-2" text-color="grey darken-1">
                          {{ row.item.action }}
                      </v-chip>
                      <v-chip v-else x-small label color="#1669BB" text-color="white">
                        {{ row.item.action }}
                      </v-chip>
                    </div>
                  </v-col>
                </v-row>
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
              <td class="actions-cell actions-width px-0">
                <div
                  class="actions float-right actions-up"
                  v-if="
                    isRegisteringParty(row.item) ||
                      isSecuredPartyRestrictedList(registrationType) ||
                      row.item.code > ''
                  "
                >
                  <v-list
                    class="actions__more-actions"
                    :disabled="addEditInProgress"
                  >
                  <v-list-item
                    v-if="(registrationFlowType === RegistrationFlowType.AMENDMENT
                      && row.item.action === ActionTypes.REMOVED && !isSecuredPartyRestrictedList(registrationType))
                      || (isSecuredPartyRestrictedList(registrationType) && row.item.action === ActionTypes.ADDED
                      && registrationFlowType === RegistrationFlowType.AMENDMENT)"
                      class="v-remove"
                      @click="undo(row.index)"
                    >
                      <v-list-item-subtitle>
                        <v-icon small>mdi-undo</v-icon>
                        <span class="ml-1">Undo</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item
                      v-else-if="!isSecuredPartyRestrictedList(registrationType)
                        || registrationFlowType === RegistrationFlowType.NEW"
                      class="v-remove"
                      @click="removeParty(row.index)"
                    >
                      <v-list-item-subtitle>
                        <v-icon small>mdi-delete</v-icon>
                        <span
                          v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && row.item.action !== ActionTypes.ADDED"
                        >
                          Delete
                        </span>
                        <span v-else class="ml-1">Remove</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </div>
                <div v-else class="actions-up actions float-right">
                  <span
                    v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                    || (registrationFlowType === RegistrationFlowType.AMENDMENT &&
                    (row.item.action === ActionTypes.ADDED) || !row.item.action)"
                    class="edit-button"
                  >
                    <v-btn
                      text
                      color="primary"
                      class="smaller-button edit-btn"
                      :id="'class-' + row.index + '-change-added-btn'"
                      @click="initEdit(row.index)"
                      :disabled="addEditInProgress"
                    >
                      <v-icon small>mdi-pencil</v-icon>
                      <span
                        v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                        && row.item.action !== ActionTypes.ADDED"
                      >
                        Amend
                      </span>
                      <span v-else>Edit</span>
                    </v-btn>
                  </span>
                  <span class="actions-border actions__more"
                    v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                    || (registrationFlowType === RegistrationFlowType.AMENDMENT && (!row.item.action ||
                    row.item.action === ActionTypes.ADDED))"
                  >
                    <v-menu offset-y left nudge-bottom="4">
                      <template v-slot:activator="{ on }">
                        <v-btn
                          text
                          small
                          v-on="on"
                          color="primary"
                          class="smaller-actions actions__more-actions__btn"
                          :disabled="addEditInProgress"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list class="actions__more-actions">
                        <v-list-item @click="removeParty(row.index)">
                          <v-list-item-subtitle>
                            <v-icon small>mdi-delete</v-icon>
                            <span
                              v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                              && row.item.action !== ActionTypes.ADDED"
                            >
                              Delete
                            </span>
                            <span v-else class="ml-1">Remove</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </span>
                  <span
                    v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                    && ((row.item.action === ActionTypes.REMOVED) || (row.item.action === ActionTypes.EDITED))"
                    class="edit-button"
                  >
                    <v-btn
                      text
                      color="primary"
                      class="smaller-button edit-btn"
                      :id="'class-' + row.index + '-undo-btn'"
                      @click="undo(row.index)"
                      :disabled="addEditInProgress"
                    >
                      <v-icon small>mdi-undo</v-icon>
                      <span>Undo</span>
                    </v-btn>
                  </span>

                  <span class="actions-border actions__more"
                    v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                    && row.item.action === ActionTypes.EDITED"
                  >
                    <v-menu offset-y left nudge-bottom="4">
                      <template v-slot:activator="{ on }">
                        <v-btn
                          text
                          small
                          v-on="on"
                          color="primary"
                          class="smaller-actions actions__more-actions__btn"
                          :disabled="addEditInProgress"
                        >
                          <v-icon>mdi-menu-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list class="actions__more-actions">
                        <v-list-item @click="initEdit(row.index)">
                          <v-list-item-subtitle>
                            <v-icon small>mdi-pencil</v-icon>
                            <span class="ml-1">Amend</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item @click="removeParty(row.index)">
                          <v-list-item-subtitle>
                            <v-icon small>mdi-delete</v-icon>
                            <span
                              v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                              && row.item.action !== ActionTypes.ADDED"
                            >
                              Delete
                            </span>
                            <span v-else class="ml-1">Remove</span>
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
                      :setShowErrorBar="showErrorBar"
                      @removeSecuredParty="removeParty"
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
// external libraries
import {
  defineComponent,
  reactive,
  toRefs,
  computed,
  watch,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { cloneDeep, isEqual } from 'lodash'
// local components
import { ChangeSecuredPartyDialog } from '@/components/dialogs'
import { EditParty, PartyAutocomplete, PartySearch } from '@/components/parties/party'
import { BaseAddress } from '@/composables/address'
// local helpers / types / etc.
import { useCountriesProvinces } from '@/composables/address/factories'
import { useParty } from '@/composables/useParty'
import { useSecuredParty } from '@/components/parties/composables/useSecuredParty'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import { PartyIF, AddPartiesIF, SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { editTableHeaders, partyTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { partyCodeAccount } from '@/utils'

export default defineComponent({
  components: {
    EditParty,
    PartySearch,
    BaseAddress,
    PartyAutocomplete,
    ChangeSecuredPartyDialog
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowInvalid: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const {
      getAddSecuredPartiesAndDebtors,
      getRegistrationType,
      getOriginalAddSecuredPartiesAndDebtors,
      getRegistrationFlowType
    } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors',
      'getRegistrationType',
      'getOriginalAddSecuredPartiesAndDebtors',
      'getRegistrationFlowType'
    ])
    const registrationType = getRegistrationType.value.registrationTypeAPI
    const registrationFlowType = getRegistrationFlowType.value
    const countryProvincesHelpers = useCountriesProvinces()

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
      parties: computed((): AddPartiesIF => {
        return getAddSecuredPartiesAndDebtors.value
      }),
      securedParties: getAddSecuredPartiesAndDebtors.value.securedParties,
      registeringPartyAdded: false,
      currentPartyName: '',
      showDialog: false,
      savedParty: null,
      showErrorSummary: computed((): boolean => {
        return !getAddSecuredPartiesAndDebtors.value.valid
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      }),
      showErrorSecuredParties: computed((): boolean => {
        return getAddSecuredPartiesAndDebtors.value.showInvalid
      }),
      headers: [...partyTableHeaders, ...editTableHeaders]
    })

    const removeParty = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      if (isRegisteringParty(localState.securedParties[index])) {
        localState.registeringPartyAdded = false
      }
      const currentParty = localState.securedParties[index]

      if ((registrationFlowType === RegistrationFlowType.AMENDMENT) && (currentParty.action !== ActionTypes.ADDED)) {
        currentParty.action = ActionTypes.REMOVED
        localState.securedParties.splice(index, 1, currentParty)
        currentParties.securedParties = localState.securedParties
        setAddSecuredPartiesAndDebtors(currentParties)
      } else {
        localState.securedParties.splice(index, 1)
        currentParties.securedParties = localState.securedParties
        currentParties.valid = isPartiesValid(currentParties)
        setAddSecuredPartiesAndDebtors(currentParties)
      }
      localState.searchValue = { code: '', businessName: '' }
      getSecuredPartyValidity()
    }

    const removeRegisteringParty = (): void => {
      for (let i = 0; i < localState.securedParties.length; i++) {
        if (isEqual(localState.securedParties[i], localState.parties.registeringParty)) {
          removeParty(i)
          localState.registeringPartyAdded = false
        }
      }
    }

    const undo = (index: number): void => {
      const originalParties = getOriginalAddSecuredPartiesAndDebtors.value
      const currentParties = getAddSecuredPartiesAndDebtors.value
      if (isSecuredPartyRestrictedList(registrationType)) {
        localState.securedParties = cloneDeep(originalParties.securedParties)
        delete localState.securedParties[0].action
        localState.searchValue = { code: '', businessName: '' }
      } else {
        localState.securedParties.splice(index, 1, cloneDeep(originalParties.securedParties[index]))
      }
      currentParties.securedParties = localState.securedParties
      setAddSecuredPartiesAndDebtors(currentParties)
      getSecuredPartyValidity()
    }

    const addRegisteringParty = () => {
      let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      let newList: PartyIF[] = parties.securedParties // eslint-disable-line
      const registeringParty: PartyIF =
        parties.registeringParty !== null ? parties.registeringParty : null
      newList.push(registeringParty)

      parties.securedParties = newList
      parties.valid = isPartiesValid(parties)
      setAddSecuredPartiesAndDebtors(parties)
      localState.registeringPartyAdded = true
    }

    const isRegisteringParty = (partyRow: PartyIF): boolean => {
      if (isEqual(partyRow, localState.parties.registeringParty)) {
        return true
      }
      return false
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditParty[index] = true
      context.emit('securedPartyOpen', true)
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddSecuredParty = true
      context.emit('securedPartyOpen', true)
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddSecuredParty = false
      localState.showEditParty = [false]
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      currentParties.valid = isPartiesValid(currentParties)
      setAddSecuredPartiesAndDebtors(currentParties)
      getSecuredPartyValidity()
      context.emit('securedPartyOpen', false)
    }

    const fetchOtherSecuredParties = async () => {
      localState.loading = true
      // go to the service and see if there are similar secured parties
      const response: [SearchPartyIF] = await partyCodeAccount()
      // check if any results
      if (response?.length > 0) {
        localState.partyResults = response
        localState.loading = false
      } else {
        setTimeout(fetchOtherSecuredParties, 3000)
      }
    }

    onMounted(() => {
      for (let i = 0; i < localState.securedParties.length; i++) {
        if (isEqual(localState.securedParties[i], localState.parties.registeringParty)) {
          localState.registeringPartyAdded = true
        }
      }

      if (isSecuredPartyRestrictedList(registrationType)) {
        fetchOtherSecuredParties()
      }
    })

    const getSecuredPartyValidity = (): boolean => {
      let validity = false
      if (registrationFlowType === RegistrationFlowType.AMENDMENT) {
        for (let i = 0; i < localState.securedParties.length; i++) {
          // is valid if there is at least one debtor
          if (localState.securedParties[i].action !== ActionTypes.REMOVED) {
            validity = true
          }
        }
      } else {
        if (localState.securedParties.length > 0) {
          validity = true
        }
      }
      context.emit('setSecuredPartiesValid', validity)
      return validity
    }

    const filterList = (
      item: SearchPartyIF,
      queryText: string,
      itemText: string
    ) => {
      const textOne = item.businessName.toLowerCase()
      const searchText = queryText.toLowerCase()
      return (
        textOne.startsWith(searchText) || item.code.startsWith(searchText)
      )
    }

    const selectResult = (party: SearchPartyIF) => {
      let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      const newParty: PartyIF = {
        code: party.code,
        businessName: party.businessName,
        emailAddress: party.emailAddress || '',
        address: party.address,
        personName: { first: '', middle: '', last: '' },
        action: ActionTypes.ADDED
      }
      if ((localState.securedParties.length > 0) && (localState.securedParties[0].code === party.code)) {
        return
      }
      // if secured party already shown
      if (localState.securedParties.length > 0) {
        localState.currentPartyName = party.code + ' ' + party.businessName
        localState.savedParty = newParty
        localState.showDialog = true
      } else {
        parties.securedParties = [newParty]
        parties.valid = isPartiesValid(parties)
        setAddSecuredPartiesAndDebtors(parties)
        localState.securedParties = [newParty]
      }
    }

    const dialogSubmit = (proceed: boolean) => {
      if (proceed) {
        let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
        if (registrationFlowType === RegistrationFlowType.AMENDMENT) {
          const originalParties = getOriginalAddSecuredPartiesAndDebtors.value
          // original secured party must be shown as removed
          const originalParty = originalParties.securedParties[0]
          originalParty.action = ActionTypes.REMOVED
          localState.securedParties = [localState.savedParty, originalParty]
        } else {
          localState.securedParties = [localState.savedParty]
        }
        parties.securedParties = localState.securedParties
        parties.valid = isPartiesValid(parties)
        setAddSecuredPartiesAndDebtors(parties)
      } else {
        localState.searchValue = {
          code: localState.securedParties[0].code,
          businessName: localState.securedParties[0].businessName
        }
      }
      localState.showDialog = false
    }

    watch(() => props.setShowInvalid, (val) => {
      localState.showErrorSecuredParties = val
    })

    return {
      removeParty,
      getName,
      isBusiness,
      initEdit,
      initAdd,
      resetData,
      isRegisteringParty,
      addRegisteringParty,
      removeRegisteringParty,
      addressSchema,
      isSecuredPartyRestrictedList,
      registrationType,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      undo,
      selectResult,
      getSecuredPartyValidity,
      filterList,
      dialogSubmit,
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
  font-size: 0.875rem;
  width: 35rem;
}

td {
  word-wrap: break-word;
}

::v-deep .party-search .v-select__selections {
  color: $gray7 !important;
}

::v-deep .v-data-table:not(.party-table)
  > .v-data-table__wrapper
  > table
  > tbody
  > tr
  > td.list-item__title {
  height: auto;
}

::v-deep .v-list-item--active {
  color: $primary-blue !important;
  font-size: 0.875rem;
}

::v-deep .v-list-item__content {
  padding: 6px 0;
}

</style>
