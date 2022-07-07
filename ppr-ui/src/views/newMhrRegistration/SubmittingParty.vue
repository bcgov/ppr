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

    <section id="mhr-submitting-party-reference" class="mt-10">
      <h2>Attention or Reference Number</h2>
      <p class="mt-2">
        THIS COPY NEEDS TO BE REWRITTEN Add optional attention or reference number information for this transaction
        for your own tracking purposes. This information is not used by the Manufactured Home Registry.
      </p>

      <!-- Insert Attention or Reference Number here -->
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { MhrSubmittingParty } from '@/components/mhrRegistration'
import { PartySearch } from '@/components/parties/party'

@Component({
  components: {
    PartySearch,
    MhrSubmittingParty
  }
})
export default class SubmittingParty extends Vue {
  private addItem = (val): void => {
    console.log(val)
    console.log('Add Item')
  }

  private initAdd = (): void => {
    console.log('initAdd')
  }

  private addRegisteringParty = (): void => {
    console.log('addRegisteringParty')
  }

  private removeRegisteringParty = (): void => {
    console.log('removeRegisteringParty')
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#mhr-submitting-party {
  /* Set "header-counter" to 0 */
  counter-reset: header-counter;
}

h2::before {
  /* Increment "header-counter" by 1 */
  counter-increment: header-counter;
  content: counter(header-counter) '. ';
}
</style>
