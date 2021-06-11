<template>
  <v-container fluid no-gutters class="white pa-0" v-if="summaryView">
    <v-card flat id="collateral-summary">
      <v-row no-gutters class="summary-header pa-2">
        <v-col cols="auto" class="pa-2">
          <v-icon color="#38598A">mdi-car</v-icon>
          <label class="pl-3"><strong>Secured Parties</strong></label>
        </v-col>
      </v-row>
      <v-container
        v-if="showErrorSummary"
        :class="{ 'invalid-message': showErrorSummary }"
      >
        <v-row no-gutters class="pa-6">
          <v-col cols="auto">
            <v-icon color="#D3272C">mdi-information-outline</v-icon>
            <span class="invalid-message">This step is unfinished.</span>
            <router-link
              id="router-link-collateral"
              class="invalid-link"
              :to="{ path: '/add-collateral' }"
            >
              Return to this step to complete it.
            </router-link>
          </v-col>
        </v-row>
      </v-container>
      <v-container v-else>
        <v-row no-gutters class="ps-6 pb-3"> </v-row>
      </v-container>
    </v-card>
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
        <v-card flat>
          <div></div>
        </v-card>
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

export default defineComponent({
  components: {
    Debtors,
    SecuredParties
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
