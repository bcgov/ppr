<template>
  <v-container
    v-if="isSummary"
    fluid
    class="pa-0 no-gutters"
  >
    <PartySummary />
  </v-container>
  <v-container
    v-else
    class="pa-0 no-gutters"
  >
    <v-row noGutters>
      <v-col
        cols="auto"
        class="generic-label"
      >
        Your registration must include the following:
      </v-col>
    </v-row>
    <v-row
      noGutters
      class="pt-6"
    >
      <v-col
        class="ps-4"
        cols="auto"
      >
        <div v-if="!!parties.registeringParty">
          <v-icon
            color="green-darken-2"
            class="agreement-valid-icon"
          >
            mdi-check
          </v-icon>
          The Registering Party
        </div>
        <ul v-else>
          <li>The Registering Party</li>
        </ul>
        <div v-if="isSecuredPartyChecked">
          <v-icon
            color="green-darken-2"
            class="agreement-valid-icon"
          >
            mdi-check
          </v-icon>
          {{ securedPartyText }}
        </div>
        <ul v-else>
          <li>{{ securedPartyText }}</li>
        </ul>
        <div v-if="parties.debtors.length > 0">
          <v-icon
            color="green-darken-2"
            class="agreement-valid-icon"
          >
            mdi-check
          </v-icon>
          At least one Debtor
        </div>
        <ul v-else>
          <li>At least one Debtor</li>
        </ul>
      </v-col>
    </v-row>
    <v-row
      noGutters
      class="pb-4 pt-10"
    >
      <v-col>
        <h3>
          Registering Party
          <v-tooltip
            v-if="!isRoleStaffSbc"
            class="registering-tooltip"
            contentClass="top-tooltip pa-5"
            transition="fade-transition"
            location="top"
          >
            <template #activator="{ props }">
              <v-icon
                class="pl-1 mt-n1"
                color="primary"
                v-bind="props"
              >
                mdi-information-outline
              </v-icon>
            </template>
            The default Registering Party is based on your BC Registries user
            account information. This information can be updated within your
            account settings. You can change to a different Registering Party by
            using the Change button.
          </v-tooltip>
        </h3>
      </v-col>
    </v-row>
    <RegisteringPartyChange />
    <v-row
      v-if="!!parties.registeringParty && !!parties.registeringParty.action"
      noGutters
    >
      <v-col>
        <CautionBox
          class="mt-4 mb-8"
          :setMsg="cautionTxt"
          :setImportantWord="'Note'"
        />
      </v-col>
    </v-row>
    <v-row
      noGutters
      class="py-4"
    >
      <v-col>
        <h3>{{ securedPartyTitle }}</h3>
        <SecuredParties />
      </v-col>
    </v-row>
    <v-row
      noGutters
      class="py-4"
    >
      <v-col>
        <h3>Debtors</h3>
        <Debtors />
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
import { AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { storeToRefs } from 'pinia'
import { useSecuredParty } from '@/composables/parties'

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
  setup () {
    const { getAddSecuredPartiesAndDebtors, isRoleStaffSbc } = storeToRefs(useStore())
    const { isSecuredPartiesRestricted } = useSecuredParty()

    const localState = reactive({
      parties: computed((): AddPartiesIF => getAddSecuredPartiesAndDebtors.value),
      cautionTxt: 'The Registry will not provide the verification statement for this registration ' +
        'to the Registering Party named above.',
      securedPartyText: isSecuredPartiesRestricted.value ? 'The Secured Party' : 'At least one Secured Party',
      securedPartyTitle: isSecuredPartiesRestricted.value ? 'Secured Party' : 'Secured Parties',
      isSecuredPartyChecked: computed(() : boolean => {
        const len = localState.parties.securedParties.length
        return isSecuredPartiesRestricted.value ? len === 1 : len > 0
      })
    })

    return {
      isRoleStaffSbc,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
