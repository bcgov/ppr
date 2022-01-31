<template>
  <v-container fluid no-gutters id="debtors-component" class="pa-0">
    <v-row no-gutters>
      <v-col cols="auto"
        >Include Debtors as <b>either</b> an Individual or a Business. If the debtor is
        operating a business and you want to register both the name of the
        business and the individual associated with the business, enter them as
        separate debtors.<br /><br />
        Note: If a Debtor name is entered incorrectly, it could invalidate the
        entire registration.
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
      <v-col>
        <v-btn
          id="btn-add-individual"
          class="mr-4"
          outlined
          color="primary"
          :disabled="addEditInProgress"
          @click="initAdd(false)"
        >
          <v-icon>mdi-account-plus</v-icon>
          <span>Add an Individual Debtor</span>
        </v-btn>

        <v-btn
          id="btn-add-business"
          outlined
          color="primary"
          :disabled="addEditInProgress"
          @click="initAdd(true)"
        >
          <v-icon>mdi-domain-plus</v-icon>
          <span>Add a Business Debtor</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <div :class="{ 'invalid-section': invalidSection }">
          <v-expand-transition>
            <v-card flat class="add-debtor-container" v-if="showAddDebtor">
              <edit-debtor
                :activeIndex="activeIndex"
                :isBusiness="currentIsBusiness"
                :invalidSection="invalidSection"
                :setShowErrorBar="showErrorBar"
                @resetEvent="resetData"
              />
            </v-card>
          </v-expand-transition>
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pt-4">
      <v-col>
        <v-data-table
          class="debtor-table"
          :class="{ 'invalid-message': showErrorDebtors && !getDebtorValidity() }"
          :headers="headers"
          :items="debtors"
          disable-pagination
          disable-sort
          hide-default-footer
          no-data-text="No debtors added yet."
        >
          <template v-slot:item="row" class="debtor-data-table">
            <tr
              v-if="!showEditDebtor[row.index]"
              :key="row.item.id"
              class="debtor-row"
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
                <base-address :editing="false" :schema="addressSchema" :value="row.item.address" />
              </td>
              <td>{{ row.item.emailAddress }}</td>
              <td>{{ getFormattedBirthdate(row.item) }}</td>
              <!-- Action Btns -->
              <td class="actions-width actions-cell px-0">
                <div class="actions-up actions float-right">
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
                        <v-list-item @click="removeDebtor(row.index)">
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
                        <v-list-item @click="removeDebtor(row.index)">
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
            <tr v-if="showEditDebtor[row.index]">
              <td colspan="4" class="pa-0" :class="{ 'invalid-section': invalidSection }">
                <v-expand-transition>
                  <div class="edit-debtor-container col-12 pa-0">
                    <edit-debtor
                      :activeIndex="activeIndex"
                      :invalidSection="invalidSection"
                      :setShowErrorBar="showErrorBar"
                      @removeDebtor="removeDebtor"
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
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed,
  watch
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import EditDebtor from './EditDebtor.vue'
import { useParty } from '@/composables/useParty'
import { BaseAddress } from '@/composables/address'

import { debtorTableHeaders, editTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import { cloneDeep } from 'lodash'

export default defineComponent({
  components: {
    EditDebtor,
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
  setup (props, { emit }) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const {
      getAddSecuredPartiesAndDebtors,
      getRegistrationFlowType,
      getOriginalAddSecuredPartiesAndDebtors
    } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors',
      'getRegistrationFlowType',
      'getOriginalAddSecuredPartiesAndDebtors'
    ])

    const registrationFlowType = getRegistrationFlowType.value
    const addressSchema = PartyAddressSchema
    const {
      getName,
      getFormattedBirthdate,
      isPartiesValid,
      isBusiness
    } = useParty()

    const localState = reactive({
      summaryView: props.isSummary,
      showAddDebtor: false,
      currentIsBusiness: true,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditDebtor: [false],
      debtors: getAddSecuredPartiesAndDebtors.value.debtors,
      showErrorSummary: computed((): boolean => {
        return !getAddSecuredPartiesAndDebtors.value.valid
      }),
      showErrorDebtors: getAddSecuredPartiesAndDebtors.value.showInvalid,
      parties: computed((): AddPartiesIF => {
        return getAddSecuredPartiesAndDebtors.value
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      }),
      headers: [...debtorTableHeaders, ...editTableHeaders]
    })

    const removeDebtor = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      const currentDebtor = currentParties.debtors[index]
      if ((registrationFlowType === RegistrationFlowType.AMENDMENT) && (currentDebtor.action !== ActionTypes.ADDED)) {
        currentDebtor.action = ActionTypes.REMOVED
        localState.debtors.splice(index, 1, currentDebtor)
        setAddSecuredPartiesAndDebtors(currentParties)
      } else {
        localState.debtors.splice(index, 1)
        currentParties.debtors = localState.debtors
        currentParties.valid = isPartiesValid(currentParties)
        setAddSecuredPartiesAndDebtors(currentParties)
      }
      getDebtorValidity()
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditDebtor[index] = true
      emit('debtorOpen', true)
    }

    const initAdd = (currentIsBusiness: boolean) => {
      localState.currentIsBusiness = currentIsBusiness
      localState.addEditInProgress = true
      localState.showAddDebtor = true
      emit('debtorOpen', true)
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddDebtor = false
      localState.showEditDebtor = [false]
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      currentParties.valid = isPartiesValid(currentParties)
      setAddSecuredPartiesAndDebtors(currentParties)
      getDebtorValidity()
      emit('debtorOpen', false)
    }

    const undo = (index: number): void => {
      const originalParties = getOriginalAddSecuredPartiesAndDebtors.value
      localState.debtors.splice(index, 1, cloneDeep(originalParties.debtors[index]))
      getDebtorValidity()
    }

    const getDebtorValidity = (): boolean => {
      let validity = false
      if (registrationFlowType === RegistrationFlowType.AMENDMENT) {
        for (let i = 0; i < localState.debtors.length; i++) {
          // is valid if there is at least one debtor
          if (localState.debtors[i].action !== ActionTypes.REMOVED) {
            validity = true
          }
        }
      } else {
        if (localState.debtors.length > 0) {
          validity = true
        }
      }
      emit('setDebtorValid', validity)
      return validity
    }

    watch(() => props.setShowInvalid, (val) => {
      localState.showErrorDebtors = val
    })

    return {
      removeDebtor,
      getDebtorValidity,
      getName,
      getFormattedBirthdate,
      initEdit,
      initAdd,
      resetData,
      undo,
      isBusiness,
      addressSchema,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

td {
  word-wrap: break-word;
}

</style>
