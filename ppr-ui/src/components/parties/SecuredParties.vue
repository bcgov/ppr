<template>
  <v-container fluid no-gutters class="pa-0">
    <v-row no-gutters>
      <v-col cols="auto"
        >Include Secured Parties in your registration by adding their secured
        party code or their name (business or person), or if the Secured Party
        you want to include is new (i.e., they do not have a secured party code)
        you can add their information manually.
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
      <!-- Party Search here -->
    </v-row>
    <v-row no-gutters>
      <v-col>
        <div :class="{ 'invalid-section': invalidSection }">
          <v-expand-transition>
            <v-card flat class="add-party-container" v-if="showAddParty">
              <edit-party
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
          class="party-table"
          :headers="headers"
          :items="parties"
          disable-pagination
          disable-sort
          hide-default-footer
          no-data-text="No Parties addeed yet."
        >
          <template v-slot:item="row" class="party-data-table">
            <tr
              v-if="!showEditParty[row.index]"
              :key="row.item.id"
              class="party-row"
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
              <td colspan="6" :class="{ 'invalid-section': invalidSection }">
                <v-expand-transition>
                  <div class="edit-Party-container col-12">
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
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import EditParty from './EditParty.vue'
import { useParty } from '@/composables/useParty'

import { partyTableHeaders } from '@/resources'

export default defineComponent({
  components: {
    EditParty
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
    const { getName, getFormattedAddress } = useParty()

    const localState = reactive({
      summaryView: props.isSummary,
      showAddParty: false,
      isBusiness: true,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditParty: [false],
      securedParties: parties.securedParties,
      showErrorSummary: computed((): boolean => {
        return !parties.valid
      }),
      headers: partyTableHeaders
    })

    const removeParty = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      localState.securedParties.splice(index, 1)
      currentParties.securedParties = localState.securedParties
      setAddSecuredPartiesAndDebtors(currentParties)
      // setValid()
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditParty[index] = true
    }

    const initAdd = (isBusiness: boolean) => {
      localState.isBusiness = isBusiness
      localState.showAddParty = true
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddParty = false
      localState.showEditParty = [false]
    }

    return {
      removeParty,
      getName,
      getFormattedAddress,
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
