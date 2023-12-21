<template>
  <div id="Mhr-Transport-Permit">
    <!-- Header bar with actions -->
    <header
      id="home-location-change-header"
      class="review-header mt-10"
    >
      <v-row
        noGutters
        align="center"
      >
        <v-col cols="8">
          <img
            class="ml-1 review-header-icon"
            alt="home-location-review-icon"
            src="@/assets/svgs/homelocationicon_reviewscreen.svg"
          >
          <label class="font-weight-bold pl-2">Location of Home</label>
        </v-col>
        <v-col
          cols="4"
          class="text-right"
        >
          <v-btn
            id="home-location-change-btn"
            variant="plain"
            class=""
            color="primary"
            :ripple="false"
            :disabled="disable"
            @click="setLocationChange(!isChangeLocationActive)"
          >
            <span v-if="!isChangeLocationActive">
              <v-icon
                color="primary"
                size="small"
              >mdi-pencil</v-icon> Change Location / Transport Permit
            </span>
            <span v-else>
              <v-icon
                color="primary"
                size="small"
              >mdi-close</v-icon> Cancel Location Change / Transport Permit
            </span>
          </v-btn>
        </v-col>
      </v-row>
    </header>

    <p class="mt-8">
      Transport permits are issued by changing the location on the manufactured home. Transport permits expire 30 days
      from the date of issue.
    </p>

    <!-- Change active template -->
    <template v-if="isChangeLocationActive">
      <p class="mt-4">
        To change the location of this home, first select the Location Change Type.
      </p>

      <p v-if="!isRoleStaffReg" class="mt-4">
        <span class="font-weight-bold">Note:</span> If the home has already been moved without a permit, a change of
        location cannot be completed online. You must notify BC Registries of the new location by submitting a
        <a
          :href="'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/' +
            'permits-licences-and-registration/registries-forms/form_13_mhr_-_registered_location_change.pdf'"
          class="generic-link"
          target="_blank"
        >
          Registered Location Change form
          <v-icon>mdi-open-in-new</v-icon>
        </a>
      </p>

      <!-- Help Content -->
      <SimpleHelpToggle
        class="mt-1"
        toggleButtonTitle="Help with Transport Permits"
      >
        <template #content>
          <h3 class="text-center mb-2">
            Help with Transport Permit
          </h3>
          <div class="pr-15">
            <div class="mt-5">
              <p>A manufactured home cannot be moved without a transport permit.</p>
              <p class="mt-6">
                Please note the following conditions and requirements under the Manufactured Home Act and the
                Manufactured Home Regulations:
              </p>
              <p class="mt-6">
                <ol class="ml-5">
                  <li>
                    Unless stated below as an exception, a tax certificate is required confirming that all local taxes
                    have been paid. A tax certificate can be obtained from the local municipality or rural tax authority
                    having taxing authority over the manufactured home. Exceptions to obtaining a tax certificate
                    include:
                  </li>
                  <ul class="ml-4 mt-3">
                    <li>moving the manufactured home to a different pad within the same park, or</li>
                    <li class="mt-1">
                      moving the manufactured home from locations on a manufacturer or dealer’s lot.
                    </li>
                  </ul>
                  <li class="mt-6">
                    Transport permits are only valid for 30 days from the date of issue, at which time they expire.
                  </li>
                  <li class="mt-2">
                    If the manufactured home is not moved before the transport permit expires, you must report the
                    physical location of the manufactured home to the Registrar within three (3) days after the
                    transport permit expires.
                  </li>
                  <li class="mt-2">
                    If the manufactured home is permanently moved to a different location than what is described on the
                    transport permit, the owner of the manufactured home must report the details of the new location to
                    the Registrar within three (3) days of the transportation.
                  </li>
                  <li class="mt-2">
                    This transport permit is valid for one (1) move only. A new transport permit must be obtained for
                    any subsequent move of the manufactured home.
                  </li>
                  <li class="mt-2">
                    Upon leaving British Columbia, a manufactured home is exempt from the Manufactured Home Act. The
                    home must be re-registered under the same number if it re-enters British Columbia.
                  </li>
                </ol>
              </p>
              <p class="help-note">
                <span>Note: </span> A manufactured home (generally 16 feet or wider) may be subject to routing
                restrictions in accordance with the requirements of the Ministry of Transportation and Infrastructure.
                You are responsible for confirming any such restrictions and you may visit
                <a
                  class="generic-link"
                  href="https://onroutebc.gov.bc.ca/#contactus"
                  target="_blank"
                >
                  onRouteBC - Home (gov.bc.ca)
                </a>
                or contact the Provincial Permit Centre for details.
              </p>
            </div>
          </div>
        </template>
      </SimpleHelpToggle>

      <!-- Document ID -->
      <section
        v-if="isRoleStaffReg"
        id="document-id-section"
        class="mt-7"
      >
        <DocumentId
          :content="{ sideLabel: 'Document ID', hintText: 'Enter the 8-digit Document ID number' }"
          :documentId="docID"
          :validate="false"
        />
      </section>

      <!-- Location Change Type -->
      <section
        id="location-change-type-section"
        class="mt-7"
      >
        <FormCard
          label="Location Change Type"
          :showErrors="false"
          :class="{'border-error-left': false}"
        >
          <template #formSlot>
            <v-select />
          </template>
        </FormCard>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Ref, ref } from 'vue'
import { FormCard, SimpleHelpToggle } from '@/components/common'
import DocumentId from '@/components/common/DocumentId.vue'
import { useStore } from '@/store/store'
import { useTransportPermits } from '@/composables'

// Props
defineProps<{
  disable?: boolean
}>()

// State
const { isRoleStaffReg } = useStore()

// Composables
const { isChangeLocationActive, setLocationChange } = useTransportPermits()

// LocalState
const docID: Ref<string> = ref('')
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.help-note {
  margin-top: 20px;
  font-size: 14px;
  line-height: 22px;
  color: $gray7;
  span {
    font-weight: bold;
  }
}
</style>
