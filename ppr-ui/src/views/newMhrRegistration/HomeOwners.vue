<template>
  <div id="mhr-home-owners-list">
    <section id="mhr-owners" class="mt-10">
      <h2>Owners</h2>
      <p class="mt-2 mb-6">
        Add a person or an organization as the owner of the home. You can add multiple owners to
        form joint tenancy or tenants in common ownership. Note: Tenants in common ownership
        requires more than one group of owners.
      </p>

      <p>Your registration must contain:</p>
      <p>At least one owner</p>
      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="showAddPersonSection || showAddPersonOrganizationSection"
        @click="() => showAddPersonSection = true"
      >
        <v-icon class="pr-1">mdi-account-plus</v-icon> Add a Person
      </v-btn>

      <span class="mx-2"></span>

      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="showAddPersonOrganizationSection || showAddPersonSection"
        @click="() => showAddPersonOrganizationSection = true"
      >
        <v-icon class="pr-1">mdi-domain-plus</v-icon> Add an Organization
      </v-btn>
    </section>

    <section v-if="showAddPersonSection">
      Add a Person placeholder
      <v-btn
        filled
        class="mt-1"
        color="primary"
        :ripple="false"
        @click="() => showAddPersonSection = false"
      >
      Done
      </v-btn>
    </section>

    <section v-if="showAddPersonOrganizationSection">
      Add a Organization placeholder
      <v-btn
        filled
        class="mt-1"
        color="primary"
        :ripple="false"
        @click="() => showAddPersonOrganizationSection = false"
      >
      Done
      </v-btn>
    </section>

  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({
  components: {
  }
})
export default class HomeOwners extends Vue {
  public showAddPersonSection = false
  public showAddPersonOrganizationSection = false
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
