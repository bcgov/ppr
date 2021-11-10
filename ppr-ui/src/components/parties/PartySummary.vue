<template>
  <v-container flat class="pa-0" id="party-summary">
    <v-row no-gutters class="summary-header pa-2 rounded-top">
      <v-col cols="auto" class="pa-2">
        <v-icon color="darkBlue">mdi-account-multiple-plus</v-icon>
        <label class="pl-3" :class="$style['sectionText']"
          ><strong
            >Registering Party, Secured Parties, and Debtors</strong
          ></label
        >
      </v-col>
    </v-row>
    <v-container class="pa-0">
      <v-row class="pt-6 px-1">
        <v-col class="generic-label">Registering Party
          <span v-if="shouldShowHint">
            <v-tooltip
              class="pa-2"
              content-class="top-tooltip"
              top
              transition="fade-transition"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-icon class="ml-1" color="primary" v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
              </template>
              <div class="pt-2 pb-2">
                The Registering Party has been changed from the logged in account user.
              </div>
            </v-tooltip>
          </span></v-col>
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          <registering-party-summary
            class="registering-party-summary"
            :setEnableNoDataAction="true"
          />
        </v-col>
      </v-row>

      <v-row class="px-1">
        <v-col class="generic-label">Secured Parties</v-col>
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          <secured-party-summary
            class="secured-party-summary"
            :setEnableNoDataAction="true"
          />
        </v-col>
      </v-row>
      <v-row class="px-1">
        <v-col class="generic-label">Debtors</v-col>
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          <debtor-summary
            class="debtor-summary"
            :setEnableNoDataAction="true"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
import { AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useParty } from '@/composables/useParty'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'

import {
  partyTableHeaders,
  debtorTableHeaders,
  registeringTableHeaders
} from '@/resources'

export default defineComponent({
  components: {
    BaseAddress,
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary
  },
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const router = context.root.$router

    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    const addressSchema = PartyAddressSchema

    const { getName, getFormattedBirthdate, isBusiness } = useParty()
    const localState = reactive({
      debtors: parties.debtors,
      securedParties: parties.securedParties,
      registeringParty:
        parties.registeringParty !== null ? [parties.registeringParty] : [],
      debtorHeaders: computed(function () {
        const headersToShow = [...debtorTableHeaders]
        headersToShow.pop()
        return headersToShow
      }),
      partyHeaders: computed(function () {
        const headersToShow = [...partyTableHeaders]
        headersToShow.pop()
        return headersToShow
      }),
      registeringHeaders: registeringTableHeaders,
      showErrorSummary: computed((): boolean => {
        return !parties.valid
      }),
      shouldShowHint: computed((): boolean => {
        if ((parties.registeringParty) && (parties.registeringParty.action)) {
          return true
        }
        return false
      })
    })

    const goToParties = (): void => {
      parties.showInvalid = true
      setAddSecuredPartiesAndDebtors(parties)
      router.push({ path: '/add-securedparties-debtors' })
    }

    return {
      getName,
      isBusiness,
      addressSchema,
      getFormattedBirthdate,
      goToParties,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.sectionText {
  color: $gray9;
}
</style>
