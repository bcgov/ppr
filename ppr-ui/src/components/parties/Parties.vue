<template>
  <v-container fluid no-gutters class="pa-0" v-if="summaryView">
    <party-summary />
  </v-container>
  <v-container fluid no-gutters v-else class="pa-0">
    <v-row no-gutters>
      <v-col cols="auto" class="generic-label"
        >Your registration must include the following:</v-col
      >
    </v-row>
    <v-row no-gutters class="pt-6">
      <v-col class="ps-4" cols="auto">
        <div v-if="registeringParty">
          <v-icon color="green darken-2" class="agreement-valid-icon"
            >mdi-check</v-icon
          >
          The Registering Party
        </div>
        <ul v-else>
          <li>The Registering Party</li>
        </ul>
        <div v-if="securedParties.length > 0">
          <v-icon color="green darken-2" class="agreement-valid-icon"
            >mdi-check</v-icon
          >
          {{ securedPartyText }}
        </div>
        <ul v-else>
          <li>{{ securedPartyText }}</li>
        </ul>
        <div v-if="debtors.length > 0">
          <v-icon color="green darken-2" class="agreement-valid-icon"
            >mdi-check</v-icon
          >
          At least one Debtor
        </div>
        <ul v-else>
          <li>At least one Debtor</li>
        </ul>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
      <v-col>
        <h3>
          Registering Party
          <v-tooltip
            top
            content-class="top-tooltip pa-5"
            transition="fade-transition"
          >
            <template v-slot:activator="{ on }">
              <v-icon class="pl-1 mt-n1" color="primary" v-on="on"
                >mdi-information-outline</v-icon
              >
            </template>
            The default Registering Party is based on your BC Registries user
            account information. This information can be updated within your
            account settings. You can change to a different Registering Party by
            using the Change button.
          </v-tooltip>
        </h3>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col v-if="!openChangeScreen">
        <registering-party
          @changeRegisteringParty="changeRegisteringParty"
          @setRegisteringParty="setRegisteringParty"
        />
      </v-col>
      <v-col v-else>
        <v-card flat class="add-party-container">
          <div class="px-6 pt-5">
            <h3 class="pb-2">Change Registering Party</h3>
            Change the Registering Party by entering the registering party code
            or their name (business or person), or if the Registering Party you
            want to include is new (i.e., they do not have a registering party
            code), you can add their information manually.
          </div>
          <party-search
            :isAutoCompleteDisabled="addEditInProgress"
            :setIsRegisteringParty="true"
            @showSecuredPartyAdd="initAdd"
            @hideSearch="openChangeScreen = false"
          />
          <div v-if="showAddRegisteringParty">
            <edit-party :setIsRegisteringParty="true" @resetEvent="resetData" />
          </div>
          <div v-if="!showAddRegisteringParty" class="pa-5" style="height:80px">
            <v-btn
              id="cancel-btn-chg-reg-party"
              large
              outlined
              color="primary"
              class="float-right"
              @click="openChangeScreen = false"
            >
              Cancel
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-row no-gutters class="py-4">
      <v-col>
        <h3>{{ securedPartyTitle }}</h3>
        <secured-parties />
      </v-col>
    </v-row>
    <v-row no-gutters class="py-4">
      <v-col>
        <h3>Debtors</h3>
        <debtors />
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
// import { useGetters, useActions } from 'vuex-composition-helpers'
import Debtors from './Debtors.vue'
import SecuredParties from './SecuredParties.vue'
import PartySummary from './PartySummary.vue'
import RegisteringParty from './RegisteringParty.vue'
import { useSecuredParty } from './composables/useSecuredParty'
import { useGetters } from 'vuex-composition-helpers'
import EditParty from './EditParty.vue'
import PartySearch from './PartySearch.vue'

export default defineComponent({
  components: {
    Debtors,
    SecuredParties,
    PartySummary,
    PartySearch,
    EditParty,
    RegisteringParty
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    const { getRegistrationType } = useGetters<any>(['getRegistrationType'])
    const registrationType = getRegistrationType.value.registrationTypeAPI
    const { isSecuredPartyRestrictedList } = useSecuredParty(props, context)
    const localState = reactive({
      registeringParty: getAddSecuredPartiesAndDebtors.value.registeringParty,
      securedParties: getAddSecuredPartiesAndDebtors.value.securedParties,
      debtors: getAddSecuredPartiesAndDebtors.value.debtors,
      openChangeScreen: false,
      showAddRegisteringParty: false,
      addEditInProgress: false,
      securedPartyText: computed((): string => {
        if (isSecuredPartyRestrictedList(registrationType)) {
          return 'The Secured Party'
        } else {
          return 'At least one Secured Party'
        }
      }),
      securedPartyTitle: computed((): string => {
        if (isSecuredPartyRestrictedList(registrationType)) {
          return 'Secured Party'
        } else {
          return 'Secured Parties'
        }
      })
    })
    const summaryView = toRefs(props).isSummary

    const setRegisteringParty = () => {
      localState.registeringParty =
        getAddSecuredPartiesAndDebtors.value.registeringParty
    }

    const changeRegisteringParty = () => {
      localState.openChangeScreen = true
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddRegisteringParty = true
    }

    const resetData = () => {
      localState.addEditInProgress = false
      localState.showAddRegisteringParty = false
      localState.openChangeScreen = false
    }

    return {
      summaryView,
      setRegisteringParty,
      changeRegisteringParty,
      initAdd,
      resetData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module></style>
