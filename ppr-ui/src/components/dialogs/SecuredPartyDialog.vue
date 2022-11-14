<template>
  <v-dialog
    v-model="dialog"
    width="50rem"
    persistent
    attach="#app"
    content-class="secured-party-dialog"
  >
    <v-card id="secured-party-dialog" class="pr-1 pt-7 mt-7" :class="!isDuplicate && !isReview ? 'pl-4 ' : 'pl-1'">
      <v-row no-gutters>
        <v-col cols="11">
          <v-row no-gutters>
            <v-col class="text-md-center ml-8">
              <v-icon :class="$style['iconRed']">mdi-alert-circle-outline</v-icon>
            </v-col>
          </v-row>
          <v-row no-gutters v-if="!isDuplicate" class="pt-5">
            <v-col class="text-md-center ml-8">
              <h1 :class="$style['dialogTitle']">{{ totalParties }} Similar {{ partyWord }} Parties Found</h1>
            </v-col>
          </v-row>
          <v-row v-else no-gutters class="pt-5">
            <v-col class="text-md-center ml-8">
              <h1 :class="$style['dialogTitle']">Duplicate Secured Parties</h1>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters justify="end" style="margin-top: -10px; padding-right: 15px;">
            <v-btn color="primary" icon :ripple="false" @click="exit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>

      <div>
        <p v-if="!isDuplicate" class="text-md-center px-6 pt-3" :class="$style['intro']">
          One or more similar {{ partyWord }} Parties were found. Do you want to use an
          existing {{ partyWord }} Party listed below or use your information to create
          a new {{ partyWord }} Party?
        </p>
        <p v-else-if="!isReview" class="text-md-center px-6 pt-3" :class="$style['intro']">
          Registrations cannot list a Secured Party with the same name and address more than once. This registration
          already contains this Secured Party:
        </p>
        <p v-else class="text-md-center px-6 pt-3" :class="$style['intro']">
          Duplicate Secured Parties have been detected in this registration.<br>
          Registrations cannot list a Secured Party with the same name and address more than once.<br>
          <b>Note:</b> these duplicates may not be visible due to a system error.
        </p>
      </div>
      <div :class="$style['partyWindow']">
        <div v-if="!isDuplicate" class="text-md-center generic-label" id="create-new-party">
          Use my information and create a new {{ partyWord }} Party:
        </div>

        <v-container class="currentParty">
          <v-row :class="[$style[isDuplicate ? 'companyRowDuplicate' : 'companyRow'],
            { 'primaryRow': showSelected && !isDuplicate }]">
            <v-col cols="auto" :class="$style['iconColumn']">
              <v-icon :class="$style['companyIcon']">
                {{party.businessName ? 'mdi-domain' : 'mdi-account'}}
              </v-icon>
            </v-col>
            <v-col cols="9">
              <div :class="$style['companyText']" class="businessName">
                {{party.businessName ? party.businessName :
                party.personName.first+" "+party.personName.middle+" "+party.personName.last}}
              </div>
              <div :class="$style['addressText']">
                {{ party.address.street }}, {{ party.address.city }}
                {{ party.address.region }} , {{ party.address.postalCode }},
                {{ getCountryName(party.address.country) }}
              </div>
              <div>
                <v-chip  x-small v-if="!isDuplicate" label color="primary" text-color="white">
                  NEW
                </v-chip>
              </div>
            </v-col>
            <v-col cols="2" class="pt-5"
              ><v-btn
                v-if="!isDuplicate"
                class="ml-auto float-right"
                color="primary"
                :class="$style['partyButton']"
                @click="createParty()"
              >
                Select
              </v-btn></v-col>
          </v-row>
        </v-container>

        <div v-if="!isDuplicate" class="text-md-center generic-label">
          Use an existing {{ partyWord }} Party:
        </div>
        <v-container v-if="!isDuplicate">
          <v-row
            class="searchResponse"
            :class="$style['companyRow']"
            v-for="(result, i) in results"
            :key="i"
            @mouseover="onHover"
          >
            <v-col cols="auto" :class="$style['iconColumn']"
              ><v-icon :class="$style['companyIcon']">mdi-domain</v-icon>
            </v-col>
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
                {{ partyWord }} Party Code: {{ result.code }}
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
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
        <div v-else-if="isReview" >
          <p class="text-md-center px-6 pt-3" :class="$style['intro']">
            Cancelling and re-starting you registration may resolve this issue.<br>
            If you do not wish to proceed, contact BC registries staff:
          </p>
          <error-contact :class="$style['padLeft']"/>
        </div>
      </div>
      <v-card-actions class="pt-6 pb-8">
        <v-btn v-if="!isDuplicate && !isReview"
          :class="$style['dialogButton']"
          id="dialog-cancel-button"
          color="primary"
          outlined
          @click="exit()"
          >Exit</v-btn>
        <v-btn v-else
          :class="$style['dialogButton']"
          class="primary dialog-btn"
          color="primary"
          @click="exit()"
          >OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed
} from '@vue/composition-api'
import { SearchPartyIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useSecuredParty } from '@/components/parties/composables/useSecuredParty'
import {
  useCountriesProvinces
} from '@/composables/address/factories'
import { ActionTypes } from '@/enums'
import ErrorContact from '@/components/common/ErrorContact.vue'

export default defineComponent({
  components: {
    ErrorContact
  },
  props: {
    defaultDialog: Boolean,
    defaultParty: {
      type: Object as () => PartyIF
    },
    defaultResults: {
      type: Array as () => Array<SearchPartyIF>
    },
    isDuplicate: {
      type: Boolean,
      default: false
    },
    isReview: {
      type: Boolean,
      default: false
    },
    defaultIsRegisteringParty: Boolean
  },
  setup (props, context) {
    const localState = reactive({
      showSelected: true,
      party: computed((): PartyIF => {
        return props.defaultParty
      }),
      dialog: computed((): boolean => {
        return props.defaultDialog
      }),
      isRegisteringParty: computed((): boolean => {
        return props.defaultIsRegisteringParty
      }),
      results: computed((): Array<SearchPartyIF> => {
        return props.defaultResults
      }),
      totalParties: computed((): number => {
        return props.defaultResults.length
      }),
      partyWord: computed((): string => {
        if (props.defaultIsRegisteringParty) {
          return 'Registering'
        }
        return 'Secured'
      })
    })

    const countryProvincesHelpers = useCountriesProvinces()

    const { addSecuredParty, setRegisteringParty } = useSecuredParty(props, context)

    const selectParty = (idx: number) => {
      const selectedResult = localState.results[idx]
      const newParty: PartyIF = {
        businessName: selectedResult.businessName,
        address: selectedResult.address,
        emailAddress: selectedResult.emailAddress,
        code: selectedResult.code
      }
      if (localState.isRegisteringParty) {
        newParty.action = ActionTypes.EDITED
        setRegisteringParty(newParty)
      } else {
        addSecuredParty(newParty)
      }
      context.emit('emitResetClose')
    }

    const createParty = () => {
      if (localState.isRegisteringParty) {
        localState.party.action = ActionTypes.EDITED
        setRegisteringParty(localState.party)
      } else {
        addSecuredParty(localState.party)
      }
      context.emit('emitResetClose')
    }

    const exit = () => {
      context.emit('emitClose')
    }

    const onHover = () => {
      localState.showSelected = false
    }

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
  font-size: 0.875rem;
  color: $gray7;
}
.companyText {
  font-weight: 700;
}
.companyRowDuplicate {
  background-color: #f1f1f1;
  border-radius: 4px 4px 4px 4px;
  margin-bottom: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  margin-right: 10px;
  margin-left: 10px;
  border: 1px solid white;
}

.companyRow {
  background-color: #f1f1f1;
  border-radius: 4px 4px 4px 4px;
  margin-bottom: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  margin-right: 10px;
  margin-left: 10px;
  border: 1px solid white;
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
  color: $error !important;
  font-size: 32px !important;
}

.dialogTitle {
  font-size: 1.5rem;
}

.dialogButton {
  margin-left: 330px;
  width: 75px;
}
.pad-left {
  margin-left: 225px;
  width: 400px;
}
</style>
