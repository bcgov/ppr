<template>
  <v-container fluid no-gutters class="pa-0">
    <v-row no-gutters>
      <v-col cols="auto"
        >Include Debtors as either an Individual or a Business. If the debtor is
        operating a business and you want to register both the name of the
        business and the individual associated with the business, enter them as
        seperate debtors.<br />
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
          @click="initAdd(false)"
        >
          <v-icon>mdi-plus</v-icon>
          <span>Add an Individual Debtor</span>
        </v-btn>

        <v-btn
          id="btn-add-business"
          outlined
          color="primary"
          @click="initAdd(true)"
        >
          <v-icon>mdi-plus</v-icon>
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
                :isBusiness="isBusiness"
                :invalidSection="invalidSection"
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
          :class="{'invalid-message': showErrorDebtors}"
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
            >
              <td class="list-item__title">
                {{ getName(row.item) }}
              </td>
              <td>
                <span v-html="getFormattedAddress(row.item)"> </span>
              </td>
              <td>{{ getFormattedBirthdate(row.item) }}</td>
              <!-- Action Btns -->
              <td class="actions-cell pa-0">
                <div class="actions">
                  <span class="edit-action">
                    <v-btn
                      text
                      color="primary"
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
                        <v-list-item @click="removeDebtor(row.index)">
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
            <tr v-if="showEditDebtor[row.index]">
              <td colspan="4" :class="{ 'invalid-section': invalidSection }">
                <v-expand-transition>
                  <div class="edit-debtor-container col-12">
                    <edit-debtor
                      :activeIndex="activeIndex"
                      :invalidSection="invalidSection"
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
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import EditDebtor from './EditDebtor.vue'
import { useParty } from '@/composables/useParty'

import { debtorTableHeaders } from '@/resources'

export default defineComponent({
  components: {
    EditDebtor
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])

    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    const { getName, getFormattedAddress, getFormattedBirthdate, isPartiesValid } = useParty()

    const localState = reactive({
      summaryView: props.isSummary,
      showAddDebtor: false,
      isBusiness: true,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditDebtor: [false],
      debtors: parties.debtors,
      showErrorSummary: computed((): boolean => {
        return !parties.valid
      }),
      showErrorDebtors: computed((): boolean => {
        return parties.showInvalid && parties.debtors.length === 0
      }),
      headers: debtorTableHeaders
    })

    const removeDebtor = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      localState.debtors.splice(index, 1)
      currentParties.debtors = localState.debtors
      currentParties.valid = isPartiesValid(currentParties)
      setAddSecuredPartiesAndDebtors(currentParties)
      // setValid()
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditDebtor[index] = true
    }

    const initAdd = (isBusiness: boolean) => {
      localState.isBusiness = isBusiness
      localState.showAddDebtor = true
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddDebtor = false
      localState.showEditDebtor = [false]
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      currentParties.valid = isPartiesValid(currentParties)
      setAddSecuredPartiesAndDebtors(currentParties)
    }

    return {
      removeDebtor,
      getName,
      getFormattedAddress,
      getFormattedBirthdate,
      initEdit,
      initAdd,
      resetData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.length-trust-label {
  font-size: 0.875rem;
}
.summary-text {
  font-size: 14px;
  color: $gray7;
}
.summary-cell {
  overflow: visible;
  text-overflow: inherit;
  white-space: inherit;
}
</style>
