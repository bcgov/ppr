<template>
  <v-dialog
    v-model="dialog"
    width="50rem"
    persistent
    attach="#app"
    content-class="secured-party-dialog"
  >
    <v-card id="secured-party-dialog" class="pl-4 pr-1 pt-7 mt-7">
      <v-row no-gutters>
        <v-col cols="11">
          <v-row no-gutters>
            <v-col class="text-md-center">
              <v-icon color="red">mdi-information-outline</v-icon>
            </v-col>
          </v-row>
          <v-row no-gutters class="pt-5">
            <v-col class="text-md-center">
              <h2>2 Similar Secured Parties Found</h2>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters justify="end">
            <v-btn color="primary" icon :ripple="false" @click="exit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>

      <div>
        <p class="text-md-center px-6 pt-3">
          One or more similar Secured Parties were found. Do you want to use one
          ofthe existing Secured Parties listed below or use your information to
          create a new Secured Party?
        </p>
      </div>

      <div class="text-md-center generic-label">
        Use my information and create a new Secured Party:
      </div>

      <v-container class="currentParty">
        <v-row :class="$style['companyRow']">
          <v-col cols="1"><v-icon>mdi-domain</v-icon></v-col>
          <v-col cols="9">
            <div :class="$style['companyText']" class="businessName">{{ party.businessName }}</div>
            <div :class="$style['addressText']">
              {{ party.address.street }}, {{ party.address.city }}
              {{ party.address.region }} , {{ party.address.postalCode }},
              {{ party.address.country }}
            </div>
            <div>
              <v-chip x-small label color="primary" text-color="white"
                >New</v-chip
              >
            </div>
          </v-col>
          <v-col cols="2" class="pt-5"
            ><v-btn class="ml-auto" color="primary" @click="createParty()">
              Select
            </v-btn></v-col
          >
        </v-row>
      </v-container>

      <div class="text-md-center generic-label">
        Use one of the existing Secured Parties:
      </div>
      <v-container>
        <v-row
          class="searchResponse"
          :class="$style['companyRow']"
          v-for="(result, i) in results"
          :key="i"
        >
          <v-col cols="1"><v-icon>mdi-domain</v-icon></v-col>
          <v-col cols="9">
            <div :class="$style['companyText']" class="businessName">{{ result.businessName }}</div>
            <div :class="$style['addressText']">
              {{ result.address.street }}, {{ result.address.city }}
              {{ result.address.region }} , {{ result.address.postalCode }},
              {{ result.address.country }}
            </div>
            <div :class="$style['addressText']">
              Secured Party Code: {{ result.code }}
            </div>
          </v-col>
          <v-col cols="2" class="pt-5"
            ><v-btn class="ml-auto" color="primary" @click="selectParty(i)">
              Select
            </v-btn></v-col
          >
        </v-row>
      </v-container>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          id="dialog-cancel-button"
          color="primary"
          outlined
          @click="exit()"
          >Exit</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  ref, // eslint-disable-line no-unused-vars
  watch
} from '@vue/composition-api'
import { SearchPartyIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useSecuredParty } from '@/components/parties/composables/useSecuredParty'

export default defineComponent({
  props: {
    defaultDialog: Boolean,
    defaultParty: {
      type: Object as () => PartyIF
    },
    defaultResults: {
      type: Array as () => Array<SearchPartyIF>
    }
  },
  setup (props, context) {
    const localState = reactive({
      results: props.defaultResults,
      party: props.defaultParty,
      dialog: props.defaultDialog
    })

    const { addSecuredParty } = useSecuredParty(props, context)

    const selectParty = (idx: number) => {
      const selectedResult = localState.results[idx]
      const newParty: PartyIF = {
        businessName: selectedResult.businessName,
        address: selectedResult.address,
        emailAddress: selectedResult.emailAddress,
        code: selectedResult.code
      }
      addSecuredParty(newParty)
      context.emit('emitResetClose')
    }

    const createParty = () => {
      addSecuredParty(localState.party)
      context.emit('emitResetClose')
    }

    const exit = () => {
      context.emit('emitClose')
    }

    watch(
      () => props.defaultDialog,
      (val: boolean) => {
        localState.dialog = val
      }
    )

    watch(
      () => props.defaultParty,
      (party: PartyIF) => {
        localState.party = party
      }
    )

    watch(
      () => props.defaultResults,
      (parties: Array<SearchPartyIF>) => {
        localState.results = parties
      }
    )

    return {
      selectParty,
      createParty,
      exit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.addressText {
  font-size: 12px;
}
.companyText {
  font-weight: 700;
}

.companyRow {
  background-color: $gray2;
  border-radius: 4px 4px 4px 4px;
  margin-bottom: 10px;
}
</style>
