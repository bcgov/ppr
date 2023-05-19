<template>
  <v-container fluid class="pa-0 no-gutters" v-if="summaryView">
    <party-summary />
  </v-container>
  <v-container fluid v-else class="pa-0 no-gutters">
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
        <div v-if="isSecuredPartyChecked">
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
            class="registering-tooltip"
            content-class="top-tooltip pa-5"
            transition="fade-transition"
            v-if="!isSbc"
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
    <registering-party-change />
    <v-row no-gutters v-if="registeringParty && registeringParty.action">
      <v-col>
        <caution-box class="mt-4 mb-8" :setMsg="cautionTxt" :setImportantWord="'Note'" />
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
// external libraries
import {
  defineComponent,
  reactive,
  toRefs,
  computed
} from 'vue'
import { useStore } from '@/store/store'
// local components
import PartySummary from './PartySummary.vue' // need to import like this for jest tests - cyclic issue?
import { Debtors } from '@/components/parties/debtor'
import {
  RegisteringPartyChange,
  SecuredParties
} from '@/components/parties/party'
import { CautionBox } from '@/components/common'
// local helpers / types / etc.
import { PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { isSecuredPartyRestrictedList } from '@/utils'

export default defineComponent({
  components: {
    Debtors,
    SecuredParties,
    PartySummary,
    RegisteringPartyChange,
    CautionBox
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { getAddSecuredPartiesAndDebtors, getRegistrationType, isRoleStaffSbc } = useStore()
    const registrationType = getRegistrationType.registrationTypeAPI
    const localState = reactive({
      securedParties: getAddSecuredPartiesAndDebtors.securedParties,
      debtors: getAddSecuredPartiesAndDebtors.debtors,
      isSbc: isRoleStaffSbc,
      cautionTxt: 'The Registry will not provide the verification statement for this registration ' +
        'to the Registering Party named above.',
      registeringParty: computed((): PartyIF => {
        return getAddSecuredPartiesAndDebtors.registeringParty
      }),
      securedPartyText: computed((): string => {
        if (isSecuredPartyRestrictedList(registrationType)) {
          return 'The Secured Party'
        } else {
          return 'At least one Secured Party'
        }
      }),
      isSecuredPartyChecked: computed((): boolean => {
        if (isSecuredPartyRestrictedList(registrationType)) {
          return localState.securedParties.length === 1
        }
        return localState.securedParties.length > 0
      }),
      securedPartyTitle: computed((): string => {
        if (isSecuredPartyRestrictedList(registrationType)) {
          return 'Secured Party'
        } else {
          return 'Secured Parties'
        }
      }),
      summaryView: computed((): boolean => {
        return props.isSummary
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
  .body-text {
    color: $gray7;
  }
</style>
