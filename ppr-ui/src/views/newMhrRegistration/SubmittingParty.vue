<template>
  <div id="mhr-submitting-party-shim">
    <section id="mhr-add-submitting-party" class="mt-10">
      <h2>Submitting Party</h2>
      <p class="mt-2">
        Provide the name and contact information for the person or business submitting this registration. You can add
        the submitting party information manually, or, if the submitting party has a Personal Property Registry party
        code, you can look up the party code or name.
      </p>

      <!-- Parties Look Up -->
      <PartySearch isMhrPartySearch />

      <!-- Mhr Submitting Party Form -->
      <MhrSubmittingParty />
    </section>

    <section id="mhr-submitting-partyy-reference" class="mt-10">
      <h2>Attention or Reference Number</h2>
      <p class="mt-2">
        THIS COPY NEEDS TO BE REWRITTEN Add optional attention or reference number information for this transaction
        for your own tracking purposes. This information is not used by the Manufactured Home Registry.
      </p>

      <!-- Insert Attention or Reference Number here -->
      <v-card flat rounded id="attention-or-reference-number-card" class="mt-8 pa-8 pr-6 pb-3">
        <v-row no-gutters class="pt-3">
          <v-col cols="12" sm="2" >
            <label class="generic-label" :class="{'error-text': false}">Attention or Reference Number</label>
          </v-col>
          <v-col cols="12" sm="10" class="px-1">
            <v-text-field
              filled
              id="attention-or-reference-number"
              class="pr-2"
              label="Attention or Reference Number (Optional)"
              v-model="attentionReferenceNum"
              :rules="attentionReferenceNumRule"
            />
          </v-col>
        </v-row>
      </v-card>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import { MhrSubmittingParty } from '@/components/mhrRegistration'
import { PartySearch } from '@/components/parties/party'
import { Action } from 'vuex-class'
// eslint-disable-next-line no-unused-vars
import { ActionBindingIF } from '@/interfaces'
import { useInputRules } from '@/composables'

@Component({
  components: {
    PartySearch,
    MhrSubmittingParty
  }
})
export default class SubmittingParty extends Vue {
  @Action setMhrAttentionReferenceNum : ActionBindingIF

  private attentionReferenceNum = ''

  private attentionReferenceNumRule = useInputRules().maxLength(40)

  @Watch('attentionReferenceNum')
  private updateAttentionReferenceNum (val) {
    this.setMhrAttentionReferenceNum(val)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#mhr-submitting-party-shim {
  /* Set "header-counter" to 0 */
  counter-reset: header-counter;
}

h2::before {
  /* Increment "header-counter" by 1 */
  counter-increment: header-counter;
  content: counter(header-counter) '. ';
}
</style>
