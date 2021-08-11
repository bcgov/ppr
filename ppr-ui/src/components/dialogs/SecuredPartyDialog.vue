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
            <v-col class="text-md-center ml-8">
              <v-icon :class="$style['iconRed']">mdi-information-outline</v-icon>
            </v-col>
          </v-row>
          <v-row no-gutters class="pt-5">
            <v-col class="text-md-center ml-8">
              <h1 :class="$style['dialogTitle']">2 Similar Secured Parties Found</h1>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters justify="end" style="margin-top: -10px">
            <v-btn color="primary" icon :ripple="false" @click="exit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>

      <div>
        <p class="text-md-center px-6 pt-3" :class="$style['intro']">
          One or more similar Secured Parties were found. Do you want to use an
          existing Secured Party listed below or use your information to create
          a new Secured Party?
        </p>
      </div>
      <div :class="$style['partyWindow']">
        <div class="text-md-center generic-label">
          Use my information and create a new Secured Party:
        </div>

        <v-container class="currentParty">
          <v-row :class="[$style['companyRow'], { 'primaryRow': showSelected }]">
            <v-col cols="auto" :class="$style['iconColumn']"
              ><v-icon :class="$style['companyIcon']">mdi-domain</v-icon></v-col
            >
            <v-col cols="9">
              <div :class="$style['companyText']" class="businessName">
                {{ party.businessName }}
              </div>
              <div :class="$style['addressText']">
                {{ party.address.street }}, {{ party.address.city }}
                {{ party.address.region }} , {{ party.address.postalCode }},
                {{ getCountryName(party.address.country) }}
              </div>
              <div>
                <v-chip x-small label color="primary" text-color="white"
                  >NEW</v-chip
                >
              </div>
            </v-col>
            <v-col cols="2" class="pt-5"
              ><v-btn
                class="ml-auto float-right"
                color="primary"
                :class="$style['partyButton']"
                @click="createParty()"
              >
                Select
              </v-btn></v-col
            >
          </v-row>
        </v-container>

        <div class="text-md-center generic-label">
          Use an existing Secured Party:
        </div>
        <v-container>
          <v-row
            class="searchResponse"
            :class="$style['companyRow']"
            v-for="(result, i) in results"
            :key="i"
            @mouseover="onHover"
          >
            <v-col cols="auto" :class="$style['iconColumn']"
              ><v-icon :class="$style['companyIcon']">mdi-domain</v-icon></v-col
            >
            <v-col cols="9">
              <div :class="$style['companyText']" class="businessName">
                {{ result.businessName }}
              </div>
              <div :class="$style['addressText']">
                {{ result.address.street }}, {{ result.address.city }}
                {{ result.address.region }} , {{ result.address.postalCode }},
                {{ getCountryName(result.address.country) }}
              </div>
              <div :class="$style['addressText']">
                Secured Party Code: {{ result.code }}
              </div>
            </v-col>
            <v-col cols="2" class="pt-5"
              ><v-btn
                class="ml-auto float-right"
                color="primary"
                :class="$style['partyButton']"
                @click="selectParty(i)"
              >
                Select
              </v-btn></v-col
            >
          </v-row>
        </v-container>
      </div>
      <v-card-actions class="pt-6 pb-8" style="display:block">
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
  watch
} from '@vue/composition-api'
import { SearchPartyIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useSecuredParty } from '@/components/parties/composables/useSecuredParty'
import {
  useCountriesProvinces
} from '@/composables/address/factories'

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
      dialog: props.defaultDialog,
      showSelected: true
    })

    const countryProvincesHelpers = useCountriesProvinces()

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

    const onHover = () => {
      localState.showSelected = false
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
      onHover,
      ...countryProvincesHelpers,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.addressText {
  font-size: 14px;
  color: $gray7;
}
.companyText {
  font-weight: 700;
}

.companyRow {
  background-color: #f1f1f1;
  border-radius: 4px 4px 4px 4px;
  margin-bottom: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  margin-right: 10px;
  margin-left: 10px;
}

.companyRow:hover {
  border: 1px solid $primary-blue;
}

.companyRow:focus {
  border: 1px solid $primary-blue;
}

.companyIcon {
  color: $gray9 !important;
}

.intro {
  color: $gray7;
}

@media (min-height: 800px) {
  .partyWindow {
    max-height: 420px;
    overflow-y: auto;
  }
}
@media (max-height: 800px) {
  .partyWindow {
    max-height: 250px;
    overflow-y: auto;
  }
}

.partyButton {
  span {
    font-weight: normal;
  }
}

.partyDialog {
  height: 90%;
}

.iconColumn {
  padding-right: 5px;
  padding-left: 20px;
}

.iconRed {
  color: #D3272C !important;
  font-size: 32px !important;
}

.dialogTitle {
  font-size: 24px;
}
</style>
