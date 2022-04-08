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
    <v-container class="pa-0 pl-6 white rounded-bottom">
      <v-row class="pt-6 px-1">
        <v-col><span class="generic-label">Registration Number</span><br>
        {{ mhResult.registrationNumber}}</v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>
          <span class="generic-label">Owner</span><br>
          {{ mhResult.ownerName.last }}, {{ mhResult.ownerName.first }}
        </v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>
          <span class="generic-label">Registration Status</span><br>
          {{ mhResult.status }}
        </v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>
          <span class="generic-label">Year Make Model</span><br>
          {{ mhResult.year }} {{ mhResult.make }} {{ mhResult.model }}
        </v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>
          <span class="generic-label">Serial Number</span><br>
          {{ mhResult.serialNumber }}
        </v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col>
          <span class="generic-label">Location</span><br>
          {{ mhResult.homeLocation }}
        </v-col>
      </v-row>
      <v-row class="pt-6 px-1">
        <v-col><v-checkbox label="Include lien information in search result"></v-checkbox></v-col>
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
import { useGetters } from 'vuex-composition-helpers'

import { ManufacturedHomeSearchResultIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  setup (props, context) {
    const { getSelectedManufacturedHome } = useGetters<any>([
      'getSelectedManufacturedHome'
    ])

    const localState = reactive({
      mhResult: computed((): ManufacturedHomeSearchResultIF => {
        if (getSelectedManufacturedHome.value) {
          return getSelectedManufacturedHome.value
        } else {
          return {
            id: 0,
            ownerName: {
              first: '',
              last: ''
            },
            status: '',
            registrationNumber: '',
            serialNumber: '',
            year: '',
            make: '',
            model: '',
            homeLocation: ''
          }
        }
      })
    })

    return {
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
