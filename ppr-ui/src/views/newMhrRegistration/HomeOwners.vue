<template>
  <div id="mhr-home-owners-list">
    <section id="mhr-owners" class="mt-10">
      <h2>Owners</h2>
      <p class="mt-2 mb-0">
        Add a person or an organization as the owner of the home. You can add
        multiple owners to form joint tenancy or tenants in common ownership.
        Note: Tenants in common ownership requires more than one group of
        owners.
      </p>

      <div class="help-with-owners">
        <v-expansion-panels>
          <v-expansion-panel @change="() => (isPanelOpen = !isPanelOpen)">
            <v-expansion-panel-header
              class="px-0 py-2 primary--text"
              :hide-actions="true"
            >
              <div>
                <v-icon color="primary">mdi-information-outline </v-icon>
                {{ header }}
              </div>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="help-toggle-content">
              <hr class="my-8" />
              <h3 class="text-center">Help with Owners</h3>
              <h4>Sole Ownership</h4>
              <p>
                This applies when the home is owned by a single individual or
                organization.
              </p>
              <h4>Joint Tenancy</h4>
              <p>
                This applies when the home is jointly owned by a number of
                individuals or organizations or some combination of the two.
              </p>
              <h4>Tenants in Common</h4>
              <p>
                This applies when the home is owned by a number of groups or
                individuals or organizations or some combination of the two
                (where a group could consist of a single owner) and each group
                of owners has the right to dispose of their share independent of
                the other owner groups and will be disposed of as part of the
                estate in the case of a death.
              </p>
              <hr class="my-8" />
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>

      <label class="generic-label">
        Your registration must include the following:
      </label>
      <div class="mt-5 mb-11">
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
        :disabled="
          showAddPersonSection ||
            showAddPersonOrganizationSection ||
            isEditingMode
        "
        @click="showAddPersonSection = true"
      >
        <v-icon class="pr-1">mdi-account-plus</v-icon> Add a Person
      </v-btn>

      <span class="mx-2"></span>

      <v-btn
        outlined
        color="primary"
        :ripple="false"
        :disabled="
          showAddPersonOrganizationSection ||
            showAddPersonSection ||
            isEditingMode
        "
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
        @done="addHomeOwner($event)"
        @cancel="showAddPersonSection = false"
      />
    </v-expand-transition>

    <v-expand-transition>
      <AddHomeOwnerOrganization
        v-if="showAddPersonOrganizationSection"
        @done="addHomeOwner($event)"
        @cancel="showAddPersonOrganizationSection = false"
      />
    </v-expand-transition>

    <div>
      <HomeOwnersTable
        :homeOwners="getMhrRegistrationHomeOwners"
        @isEditing="isEditingMode = $event"
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

  private showAddPersonSection = false
  private showAddPersonOrganizationSection = false
  private isPanelOpen = false
  private isEditingMode = false

  private get tenancyType (): string {
    if (this.getMhrRegistrationHomeOwners?.length === 0) return 'N/A'
    return this.getMhrRegistrationHomeOwners?.length === 1
      ? 'Sole Ownership'
      : 'Joint Tenancy'
  }

  private get header (): string {
    return this.isPanelOpen ? 'Hide Help with Owners' : 'Help with Owners'
  }

  private async addHomeOwner (owner): Promise<void> {
    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    homeOwners.push(owner)
    this.setMhrRegistrationHomeOwners(homeOwners)
  }

  private async editHomeOwner (owner): Promise<void> {
    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    const { id, ...editedOwner } = owner
    homeOwners[owner.id] = editedOwner
    this.setMhrRegistrationHomeOwners(homeOwners)
  }

  private async removeHomeOwner (owner): Promise<void> {
    const homeOwners = [...this.getMhrRegistrationHomeOwners]
    homeOwners.splice(homeOwners.indexOf(owner), 1)
    this.setMhrRegistrationHomeOwners(homeOwners)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.help-with-owners ::v-deep {
  .v-expansion-panel-header {
    background-color: $gray1;
    height: 64px;
  }

  .v-expansion-panel-content__wrap {
    padding: 0;
    background-color: $gray1;
  }

  h4 {
    color: #495057;
  }
}
</style>
