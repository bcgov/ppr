<template>
  <v-container fluid no-gutters class="pa-0" v-if="summaryView">
    <party-summary />
  </v-container>
  <v-container fluid no-gutters v-else class="pa-0">
    <v-row no-gutters>
      <v-col cols="auto"
        ><b>Your registration must include one of the following:</b></v-col
      >
    </v-row>
    <v-row no-gutters class="pt-6">
      <v-col class="ps-4" cols="auto">
        <ul>
          <li>The Registering Party</li>
          <li>At least one Secured Party</li>
          <li>At least one Debtor</li>
        </ul>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
      <v-col>
        <h3>Registering Party</h3>
        <registering-party />
       </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
      <v-col>
        <h3>Secured Parties</h3>
        <secured-parties />
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-4 pt-10">
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
  toRefs
  // watch,
  // computed
} from '@vue/composition-api'
// import { useGetters, useActions } from 'vuex-composition-helpers'
import Debtors from './Debtors.vue'
import SecuredParties from './SecuredParties.vue'
import PartySummary from './PartySummary.vue'
import RegisteringParty from './RegisteringParty.vue'

export default defineComponent({
  components: {
    Debtors,
    SecuredParties,
    PartySummary,
    RegisteringParty
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const localState = reactive({})
    const summaryView = toRefs(props).isSummary

    return {
      summaryView,

      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module></style>
