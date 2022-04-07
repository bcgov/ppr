<template>
  <v-container flat class="pa-0" id="party-summary">
    <v-row no-gutters class="summary-header pa-2 rounded-top">
      <v-col cols="auto" class="pa-2">
        <v-icon color="darkBlue">mdi-account-multiple-plus</v-icon>
        <label class="pl-3" :class="$style['sectionText']"
          ><strong
            >Manufactured Home Details</strong
          ></label
        >
      </v-col>
    </v-row>
    <v-container class="pa-0 white rounded-bottom">
      <v-row class="pt-6 px-1">
        <v-col>Registration Number</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>Owner</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>Registration Status</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>Year Make Model</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>Serial Number</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>Location</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>Include lien information in search result</v-col>
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

import { AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useParty } from '@/composables/useParty'
import { PartyAddressSchema } from '@/schemas'


export default defineComponent({
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
