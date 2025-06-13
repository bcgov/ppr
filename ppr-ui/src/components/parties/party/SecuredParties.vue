<template>
  <v-container
    id="secured-parties-component"
    fluid
    class="pa-0 noGutters"
    role="region"
  >
    <ChangeSecuredPartyDialog
      attach="#app"
      :display="showDialog"
      :secured-party-name="currentPartyName"
      @proceed="dialogSubmit($event)"
    />
    <v-row v-if="isSecuredPartiesRestricted">
      <v-col cols="auto">
        Include the Secured Party in your registration by adding their secured
        party code or their name (business or person). The account number of the
        Secured Party must match the account number of the Registering Party.<br>
        <div
          class="font-weight-bold pt-2"
          data-test-id="restricted-prompt"
          :class="{ 'error-text': securedParties.length >= 2 && !getSecuredPartyValidity() }"
        >
          Only one Secured Party is allowed.
        </div>
      </v-col>
    </v-row>
    <v-row
      v-if="isSecuredPartiesRestricted && !isStaffReg"
      no-gutters
      class="pb-4 pt-6"
    >
      <v-col
        cols="12"
        class="party-search bg-white"
      >
        <v-autocomplete
          id="secured-party-autocomplete"
          v-model="searchValue"
          variant="filled"
          color="primary"
          hide-details
          :loading="loading"
          :items="partyResults"
          item-title="businessName"
          item-value="code"
          label="Secured Party Code or Name"
          no-data-text="No matches found."
          :menu-props="{ maxHeight: '325px' }"
          offset="1000"
          return-object
          class="mx-7 my-8"
        >
          <template #selection="{ item }">
            <span v-text="item.value" />
            <span
              class="ml-4"
              v-text="item.title"
            />
          </template>
          <template #item="{ props, item }">
            <v-list-item
              v-bind="props"
              :title="null"
              @click="selectResult(item.raw)"
            >
              <v-row class="auto-complete-row fs-14 py-2">
                <v-col cols="1">
                  {{ item.value }}
                </v-col>
                <v-col cols="9">
                  {{ item.title }}<br>
                  <div class="pt-2">
                    {{ item.raw.address.street }},
                    {{ item.raw.address.city }}
                    {{ item.raw.address.region }}
                    {{ getCountryName(item.raw.address.country) }},
                    {{ item.raw.address.postalCode }}
                  </div>
                </v-col>
              </v-row>
            </v-list-item>
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>

    <v-row
      v-if="!isSecuredPartiesRestricted"
      no-gutters
    >
      <v-col cols="auto">
        Include Secured Parties in your registration by adding their secured
        party code or their name (business or person), or if the Secured Party
        you want to include is new (i.e., they do not have a secured party code)
        you can add their information manually.
      </v-col>
    </v-row>
    <v-row
      v-if="(!isSecuredPartiesRestricted || isStaffReg) && !isSecurityActNotice"
      no-gutters
      class="pb-4 pt-6"
    >
      <PartySearch
        :is-auto-complete-disabled="addEditInProgress"
        :registering-party-added="registeringPartyAdded"
        @select-item="addItem()"
        @show-secured-party-add="initAdd"
        @add-registering-party="addRegisteringParty"
        @remove-registering-party="removeRegisteringParty"
      />
    </v-row>
    <v-row no-gutters>
      <v-col>
        <div :class="{ 'invalid-section': invalidSection }">
          <v-expand-transition>
            <v-card
              v-if="showAddSecuredParty"
              flat
              class="add-party-container"
            >
              <EditParty
                :active-index="activeIndex"
                :invalid-section="invalidSection"
                :set-show-error-bar="setShowErrorBar"
                @reset-event="resetData"
              />
            </v-card>
          </v-expand-transition>
        </div>
      </v-col>
    </v-row>
    <v-row
      no-gutters
      class="pt-2"
    >
      <v-col>
        <v-table
          class="party-table party-data-table"
          :class="{
            'border-error-left': (showErrorSecuredParties && !getSecuredPartyValidity()) ||
              (setShowErrorBar && (isSecuredPartiesRestricted && !getSecuredPartyValidity()))
          }"
        >
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
            <tbody v-if="securedParties.length > 0">
              <tr
                v-for="(item, index) in securedParties"
                :key="item.partyId"
                class="party-row"
                :class="{ 'disabled-text-not-action': item.action === ActionTypes.REMOVED}"
              >
                <!-- Edit Form -->
                <template v-if="showEditParty[index]">
                  <td
                    colspan="5"
                    class="pa-0"
                    :class="{ 'invalid-section': invalidSection }"
                  >
                    <v-card
                      flat
                      class="edit-Party-container"
                    >
                      <EditParty
                        :active-index="activeIndex"
                        :invalid-section="invalidSection"
                        :set-show-error-bar="setShowErrorBar"
                        :is-edit-mode="true"
                        @remove-secured-party="removeParty"
                        @reset-event="resetData"
                      />
                    </v-card>
                  </td>
                </template>
                <!-- Table Cells -->
                <template v-else>
                  <td class="list-item__title chip-cell">
                    <v-row
                      no-gutters
                      :aria-label="`${isBusiness(item) ? 'Business' : 'Person'} ${getName(item)}`"
                    >
                      <v-col
                        cols="auto"
                        :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}"
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
                        <div :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}">
                          <span class="font-weight-bold">{{ getName(item) }}</span>
                        </div>
                        <div v-if="item.action && isAmendment">
                          <v-chip
                            v-if="item.action === ActionTypes.REMOVED"
                            x-small
                            variant="elevated"
                            color="greyLighten"
                          >
                            {{ item.action }}
                          </v-chip>
                          <v-chip
                            v-else
                            x-small
                            variant="elevated"
                            color="primary"
                          >
                            {{ item.action }}
                          </v-chip>
                        </div>
                      </v-col>
                    </v-row>
                  </td>
                  <td>
                    <BaseAddress
                      :editing="false"
                      :schema="addressSchema"
                      :value="item.address"
                    />
                  </td>
                  <td>{{ item.emailAddress }}</td>
                  <td class="code-cell">
                    {{ item.code }}
                  </td>
                  <!-- Action Btns -->
                  <td
                    v-if="!isSecurityActNotice"
                    class="actions-cell actions-width"
                  >
                    <div v-if="isRegisteringParty(item) || isSecuredPartiesRestricted || item.code > ''">
                      <v-list
                        class="actions__more-actions"
                        :disabled="addEditInProgress"
                      >
                        <v-list-item
                          v-if="isAmendment &&
                            (
                              (isSecuredPartiesRestricted && item.action === ActionTypes.ADDED) ||
                              (!isSecuredPartiesRestricted &&
                                (item.action === ActionTypes.REMOVED || item.action === ActionTypes.EDITED))
                            )"
                          class="v-remove"
                          @click="undo(index)"
                        >
                          <v-list-item-subtitle>
                            <v-icon size="small">
                              mdi-undo
                            </v-icon>
                            <span class="ml-1 mr-2">Undo</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item
                          v-else-if="!isSecuredPartiesRestricted
                            || registrationFlowType === RegistrationFlowType.NEW"
                          class="v-remove"
                          @click="removeParty(index)"
                        >
                          <v-list-item-subtitle>
                            <v-icon size="small">
                              mdi-delete
                            </v-icon>
                            <span
                              v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                && item.action !== ActionTypes.ADDED"
                              class="mr-2"
                            >
                              Delete
                            </span>
                            <span
                              v-else
                              class="ml-1 mr-2"
                            >Remove</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </div>
                    <div
                      v-else
                      class="actions-up"
                    >
                      <span
                        v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                          || (registrationFlowType === RegistrationFlowType.AMENDMENT &&
                            (item.action === ActionTypes.ADDED) || !item.action)"
                        class="edit-button"
                      >
                        <v-btn
                          :id="'class-' + index + '-change-added-btn'"
                          variant="plain"
                          color="primary"
                          class="smaller-button edit-btn"
                          :disabled="addEditInProgress"
                          @click="initEdit(index)"
                        >
                          <v-icon size="small">mdi-pencil</v-icon>
                          <span
                            v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                              && item.action !== ActionTypes.ADDED"
                          >
                            Amend
                          </span>
                          <span v-else>Edit</span>
                        </v-btn>
                      </span>
                      <span
                        v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                          || (registrationFlowType === RegistrationFlowType.AMENDMENT && (!item.action ||
                            item.action === ActionTypes.ADDED))"
                        class="actions-border actions__more pr-1"
                      >
                        <v-menu
                          location="bottom right"
                        >
                          <template #activator="{ props }">
                            <v-btn
                              variant="plain"
                              size="small"
                              color="primary"
                              class="smaller-actions actions__more-actions__btn"
                              :disabled="addEditInProgress"
                              v-bind="props"
                            >
                              <v-icon>mdi-menu-down</v-icon>
                            </v-btn>
                          </template>
                          <v-list class="actions__more-actions">
                            <v-list-item @click="removeParty(index)">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-delete</v-icon>
                                <span
                                  v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                    && item.action !== ActionTypes.ADDED"
                                >
                                  Delete
                                </span>
                                <span
                                  v-else
                                  class="ml-1"
                                >Remove</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </span>
                      <span
                        v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && ((item.action === ActionTypes.REMOVED) || (item.action === ActionTypes.EDITED))"
                        class="edit-button"
                        :class="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && item.action === ActionTypes.EDITED ? '' : 'mr-10'"
                      >
                        <v-btn
                          :id="'class-' + index + '-undo-btn'"
                          variant="plain"
                          color="primary"
                          class="smaller-button edit-btn"
                          :disabled="addEditInProgress"
                          @click="undo(index)"
                        >
                          <v-icon size="small">mdi-undo</v-icon>
                          <span>Undo</span>
                        </v-btn>
                      </span>

                      <span
                        v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && item.action === ActionTypes.EDITED"
                        class="actions-border actions__more"
                      >
                        <v-menu
                          location="bottom right"
                        >
                          <template #activator="{ props }">
                            <v-btn
                              variant="plain"
                              size="small"
                              color="primary"
                              class="smaller-actions actions__more-actions__btn"
                              :disabled="addEditInProgress"
                              v-bind="props"
                            >
                              <v-icon>mdi-menu-down</v-icon>
                            </v-btn>
                          </template>
                          <v-list class="actions__more-actions">
                            <v-list-item @click="initEdit(index)">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-pencil</v-icon>
                                <span class="ml-1">Amend</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                            <v-list-item @click="removeParty(index)">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-delete</v-icon>
                                <span
                                  v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                    && item.action !== ActionTypes.ADDED"
                                >
                                  Delete
                                </span>
                                <span
                                  v-else
                                  class="ml-1"
                                >Remove</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </span>
                    </div>
                  </td>
                </template>
              </tr>
            </tbody>
            <!-- No Data Message -->
            <tbody v-else>
              <tr>
                <td
                  class="text-center"
                  :colspan="headers.length"
                >
                  No Parties added yet.
                </td>
              </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>
    <v-row>
      <v-col />
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed,
  watch,
  onMounted
} from 'vue'
import { useStore } from '@/store/store'
import { cloneDeep, isEqual } from 'lodash'
import { BaseAddress } from '@/composables/address'
import { useCountriesProvinces } from '@/composables/address/factories'
import { useParty } from '@/composables/useParty'
import { useSecuredParty } from '@/composables/parties'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import type { PartyIF, AddPartiesIF, SearchPartyIF } from '@/interfaces'
import { editTableHeaders, partyTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { partyCodeAccount } from '@/utils/ppr-api-helper'
import { storeToRefs } from 'pinia'
import { usePprRegistration } from '@/composables'

export default defineComponent({
  components: {
    BaseAddress
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
  emits: ['securedPartyOpen', 'setSecuredPartiesValid'],
  setup (props, context) {
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const {
      // Getters
      getAddSecuredPartiesAndDebtors,
      getRegistrationType,
      getOriginalAddSecuredPartiesAndDebtors,
      getRegistrationFlowType,
      isRoleStaffReg
    } = storeToRefs(useStore())
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const registrationFlowType = getRegistrationFlowType.value
    const countryProvincesHelpers = useCountriesProvinces()

    const addressSchema = PartyAddressSchema
    const { getName, isPartiesValid, isBusiness } = useParty()
    const { isSecuredPartiesRestricted } = useSecuredParty()
    const { isSecurityActNotice } = usePprRegistration()

    const localState = reactive({
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
      parties: computed((): AddPartiesIF => getAddSecuredPartiesAndDebtors.value),
      isStaffReg: computed((): boolean => isRoleStaffReg.value),
      isAmendment: computed(() => registrationFlowType === RegistrationFlowType.AMENDMENT),
      securedParties: getAddSecuredPartiesAndDebtors.value.securedParties,
      registeringPartyAdded: false,
      currentPartyName: '',
      showDialog: false,
      savedParty: null,
      showErrorSummary: computed((): boolean => !getAddSecuredPartiesAndDebtors.value.valid),
      showErrorSecuredParties: false,
      headers: [...partyTableHeaders, ...editTableHeaders]
    })

    const removeParty = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      if (isRegisteringParty(localState.securedParties[index])) {
        localState.registeringPartyAdded = false
      }
      const currentParty = cloneDeep(localState.securedParties[index])

      if ((localState.isAmendment) && (currentParty.action !== ActionTypes.ADDED)) {
        currentParty.action = ActionTypes.REMOVED
        localState.securedParties.splice(index, 1, currentParty)
        currentParties.securedParties = localState.securedParties
        setAddSecuredPartiesAndDebtors(currentParties)
      } else {
        localState.securedParties.splice(index, 1)
        currentParties.securedParties = localState.securedParties
        currentParties.valid = isPartiesValid(currentParties, registrationType)
        setAddSecuredPartiesAndDebtors(currentParties)
      }
      localState.searchValue = { code: '', businessName: '' }
      const isValid = getSecuredPartyValidity()
      emitSecuredPartyValidity(isValid)
    }

    const removeRegisteringParty = (): void => {
      for (let i = 0; i < localState.securedParties.length; i++) {
        if (isEqual(localState.securedParties[i], localState.parties.registeringParty)) {
          removeParty(i)
          localState.registeringPartyAdded = false
        }
      }
    }

    const addItem = (): void => {
      const isValid = getSecuredPartyValidity()
      emitSecuredPartyValidity(isValid)
    }

    const undo = (index: number): void => {
      const originalParties = getOriginalAddSecuredPartiesAndDebtors.value
      const currentParties = getAddSecuredPartiesAndDebtors.value
      if (isSecuredPartiesRestricted.value) {
        localState.securedParties = cloneDeep(originalParties.securedParties)
        delete localState.securedParties[0].action
        localState.searchValue = { code: '', businessName: '' }
      } else {
        localState.securedParties.splice(index, 1, cloneDeep(originalParties.securedParties[index]))
      }
      currentParties.securedParties = localState.securedParties
      const isValid = getSecuredPartyValidity()
      currentParties.valid = isValid
      setAddSecuredPartiesAndDebtors(currentParties)
      emitSecuredPartyValidity(isValid)
    }

    const addRegisteringParty = () => {
      const parties = getAddSecuredPartiesAndDebtors.value
      const newList: PartyIF[] = parties.securedParties
      const registeringParty: PartyIF =
        parties.registeringParty !== null ? parties.registeringParty : null
      newList.push(registeringParty)

      parties.securedParties = newList
      parties.valid = isPartiesValid(parties, registrationType)
      setAddSecuredPartiesAndDebtors(parties)
      localState.registeringPartyAdded = true
    }

    const isRegisteringParty = (partyRow: PartyIF): boolean =>
      isEqual(partyRow, localState.parties.registeringParty)

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
      const currentParties = getAddSecuredPartiesAndDebtors.value
      currentParties.valid = isPartiesValid(currentParties, registrationType)
      setAddSecuredPartiesAndDebtors(currentParties)
      const isValid = getSecuredPartyValidity()
      emitSecuredPartyValidity(isValid)
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
      localState.showErrorSecuredParties = getAddSecuredPartiesAndDebtors.value.showInvalid
      for (let i = 0; i < localState.securedParties.length; i++) {
        if (isEqual(localState.securedParties[i], localState.parties.registeringParty)) {
          localState.registeringPartyAdded = true
        }
      }

      if (isSecuredPartiesRestricted.value && !localState.isStaffReg) {
        fetchOtherSecuredParties()
      }
    })

    const getSecuredPartyValidity = (): boolean => {
      let partyCount = 0
      if (localState.isAmendment) {
        partyCount = localState.securedParties.filter((party: PartyIF) =>
          party.action !== ActionTypes.REMOVED).length
      } else {
        partyCount = localState.securedParties.length
      }
      return isSecuredPartiesRestricted.value ? partyCount === 1 : partyCount >= 1
    }

    const emitSecuredPartyValidity = (validity: boolean): void => {
      context.emit('setSecuredPartiesValid', validity)
    }

    const filterList = (
      item: SearchPartyIF,
      queryText: string
    ) => {
      const textOne = item.businessName?.toLowerCase()
      const searchText = queryText?.toLowerCase()
      return (
        textOne.startsWith(searchText) || item.code.startsWith(searchText)
      )
    }

    const selectResult = (party: SearchPartyIF) => {
      const parties = getAddSecuredPartiesAndDebtors.value
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
        parties.valid = isPartiesValid(parties, registrationType)
        setAddSecuredPartiesAndDebtors(parties)
        localState.securedParties = [newParty]
      }
      emitSecuredPartyValidity(true)
    }

    const dialogSubmit = (proceed: boolean) => {
      if (proceed) {
        const parties = getAddSecuredPartiesAndDebtors.value
        if (registrationFlowType === RegistrationFlowType.AMENDMENT) {
          const originalParties = getOriginalAddSecuredPartiesAndDebtors.value
          // original secured party must be shown as removed
          const originalParty = cloneDeep(originalParties.securedParties[0])
          originalParty.action = ActionTypes.REMOVED
          localState.securedParties = [localState.savedParty, originalParty]
        } else {
          localState.securedParties = [localState.savedParty]
        }
        parties.securedParties = localState.securedParties
        parties.valid = isPartiesValid(parties, registrationType)
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
      isSecuredPartiesRestricted,
      registrationType,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      undo,
      selectResult,
      getSecuredPartyValidity,
      filterList,
      dialogSubmit,
      addItem,
      isSecurityActNotice,
      ...countryProvincesHelpers,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.code-cell, .th:last-child {
  min-width: 175px;
}
</style>
