<template>
  <v-container
    id="party-summary"
    class="pa-0 flat"
  >
    <v-row
      noGutters
      class="summary-header pa-2 rounded-top"
    >
      <v-col
        cols="auto"
        class="pa-2"
      >
        <v-icon color="darkBlue">
          mdi-account-multiple-plus
        </v-icon>
        <label class="pl-3 sectionText">
          <strong>Registering Party, Secured Parties, and Debtors</strong>
        </label>
      </v-col>
    </v-row>
    <v-container class="pa-0">
      <v-row class="pt-6 px-1">
        <v-col class="generic-label">
          Registering Party
          <span v-if="shouldShowHint">
            <v-tooltip
              class="pa-2"
              contentClass="top-tooltip"
              location="top"
              transition="fade-transition"
            >
              <template #activator="{ props }">
                <v-icon
                  class="ml-1"
                  color="primary"
                  v-bind="props"
                >mdi-information-outline</v-icon>
              </template>
              <div class="pt-2 pb-2">
                This Registering Party has been changed from the logged in account user.
              </div>
            </v-tooltip>
          </span>
        </v-col>
      </v-row>
      <v-row
        noGutters
        class="pb-6 pt-4"
      >
        <v-col>
          <registering-party-summary
            class="registering-party-summary"
            :set-enable-no-data-action="true"
          />
        </v-col>
      </v-row>

      <v-row class="px-1">
        <v-col class="generic-label">
          Secured Parties
        </v-col>
      </v-row>
      <v-row
        noGutters
        class="pb-6 pt-4"
      >
        <v-col>
          <secured-party-summary
            class="secured-party-summary"
            :set-enable-no-data-action="true"
          />
        </v-col>
      </v-row>
      <v-row class="px-1">
        <v-col class="generic-label">
          Debtors
        </v-col>
      </v-row>
      <v-row
        noGutters
        class="pb-6 pt-4"
      >
        <v-col>
          <debtor-summary
            class="debtor-summary"
            :set-enable-no-data-action="true"
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
} from 'vue'
import { useStore } from '@/store/store'
import { useRouter } from 'vue-router'

import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
import { AddPartiesIF } from '@/interfaces'
import { useParty } from '@/composables/useParty'
import { PartyAddressSchema } from '@/schemas'

import {
  partyTableHeaders,
  debtorTableHeaders,
  registeringTableHeaders
} from '@/resources'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    DebtorSummary,
    RegisteringPartySummary,
    SecuredPartySummary
  },
  setup () {
    const router = useRouter()
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const { getAddSecuredPartiesAndDebtors } = storeToRefs(useStore())
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
        return !!((parties.registeringParty) && (parties.registeringParty.action))
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

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.sectionText {
  color: $gray9;
}
</style>
