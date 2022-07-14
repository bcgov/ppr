<template>
  <div id="mhr-home-owners-list">
    <section id="mhr-owners" class="mt-10">
      <h2>Owners</h2>
      <p class="mt-2 mb-6">
        Add a person or an organization as the owner of the home. You can add
        multiple owners to form joint tenancy or tenants in common ownership.
        Note: Tenants in common ownership requires more than one group of
        owners.
      </p>

      <p>Your registration must contain:</p>
      <p>
        <v-icon
          v-if="getMhrRegistrationHomeOwners.length > 0"
          color="green darken-2"
        >
          mdi-check
        </v-icon>
        <v-icon v-else color="black">mdi-circle-small</v-icon>
        At least one owner
      </p>
      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="showAddPersonSection || showAddPersonOrganizationSection"
        @click="showAddPersonSection = true"
      >
        <v-icon class="pr-1">mdi-account-plus</v-icon> Add a Person
      </v-btn>

      <span class="mx-2"></span>

      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="showAddPersonOrganizationSection || showAddPersonSection"
        @click="showAddPersonOrganizationSection = true"
      >
        <v-icon class="pr-1">mdi-domain-plus</v-icon> Add an Organization
      </v-btn>
    </section>

    <v-expand-transition>
      <AddHomeOwnerPerson
        v-if="showAddPersonSection"
        @done="addPerson($event)"
        @remove="() => {}"
        @cancel="showAddPersonSection = false"
      />
    </v-expand-transition>

    <v-expand-transition>
      <AddHomeOwnerOrganization
        v-if="showAddPersonOrganizationSection"
        @done="addPerson($event)"
        @remove="() => {}"
        @cancel="showAddPersonOrganizationSection = false"
      />
    </v-expand-transition>

    <div>
      <HomeOwnersTable :homeOwners="getMhrRegistrationHomeOwners" />
    </div>
  </div>
</template>

<script lang="ts">
import {
  AddHomeOwnerPerson,
  AddHomeOwnerOrganization,
  HomeOwnersTable
} from '@/components/mhrRegistration/HomeOwners'
import { Component, Vue } from 'vue-property-decorator'
import { Action, Getter } from 'vuex-class'
/* eslint-disable no-unused-vars */
import { ActionBindingIF } from '@/interfaces/store-interfaces/action-interface'
import { MhrRegistrationHomeOwnersIF } from '@/interfaces/mhr-registration-interfaces'
/* eslint-enable no-unused-vars */

@Component({
  components: {
    AddHomeOwnerPerson,
    AddHomeOwnerOrganization,
    HomeOwnersTable
  }
})
export default class HomeOwners extends Vue {
  @Getter getMhrRegistrationHomeOwners: MhrRegistrationHomeOwnersIF[]
  @Action setMhrRegistrationHomeOwners: ActionBindingIF

  public showAddPersonSection = false
  public showAddPersonOrganizationSection = false

  private async addPerson (personData): Promise<void> {
    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    homeOwners.push(personData)
    this.setMhrRegistrationHomeOwners(homeOwners)
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
