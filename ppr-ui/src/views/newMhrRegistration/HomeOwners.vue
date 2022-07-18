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
      <div class="my-7">
        <v-icon
          v-if="getMhrRegistrationHomeOwners.length > 0"
          color="green darken-2"
        >
          mdi-check
        </v-icon>
        <v-icon v-else color="black">mdi-circle-small</v-icon>
        At least one owner
      </div>
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
        <v-icon class="pr-1">mdi-domain-plus</v-icon>
        Add a Business or Organization
      </v-btn>

      <div class="my-6">Tenancy Type: {{ tenancyType }}</div>
    </section>

    <v-expand-transition>
      <AddHomeOwnerPerson
        v-if="showAddPersonSection"
        @done="addPerson($event)"
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
      <HomeOwnersTable
        :homeOwners="getMhrRegistrationHomeOwners"
        @edit="editHomeOwner($event)"
        @remove="removeHomeOwner($event)"
      />
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

  public get tenancyType (): string {
    if (this.getMhrRegistrationHomeOwners?.length === 0) return 'N/A'
    return this.getMhrRegistrationHomeOwners?.length === 1
      ? 'Sole Ownership'
      : 'Joint Tenancy'
  }

  private async addPerson (personData): Promise<void> {
    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    homeOwners.push(personData)
    this.setMhrRegistrationHomeOwners(homeOwners)
  }

  public async editHomeOwner (owner): Promise<void> {
    console.log('Editing Home Owner')

    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    // Create edited homeSection without id
    const { id, ...editedOwner } = owner
    // Apply edited section to temp array
    homeOwners[owner.id] = editedOwner

    this.setMhrRegistrationHomeOwners(homeOwners)
  }

  public async removeHomeOwner (owner): Promise<void> {
    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    homeOwners.splice(homeOwners.indexOf(owner), 1)
    this.setMhrRegistrationHomeOwners(homeOwners)
  }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
