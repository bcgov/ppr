<template>
  <div id="mhr-transport-permit">
    <!-- Header bar with actions -->
    <header
      id="home-location-change-header"
      class="review-header mt-10"
      :class="{ 'mb-n10': isExemptMhr && !hasActiveTransportPermit }"
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
          <!-- Active Transport Permit Actions -->
          <v-btn
            v-if="hasActiveTransportPermit && isAmendChangeLocationEnabled"
            id="home-location-change-btn"
            variant="plain"
            class=""
            color="primary"
            :ripple="false"
            :disabled="false"
            data-test-id="amend-transport-permit-btn"
            @click="toggleAmendLocationChange()"
          >
            <v-icon
              color="primary"
              size="small"
              class="mr-1"
            >
              {{ isChangeLocationActive ? 'mdi-close' : 'mdi-pencil' }}
            </v-icon> {{ isChangeLocationActive ? 'Cancel Transport Permit Amendment' : 'Amend Transport Permit' }}
            <v-divider
              v-if="!isChangeLocationActive"
              class="my-2 px-3"
              vertical
            />
            <v-menu
              v-if="!isChangeLocationActive"
              location="bottom right"
            >
              <template #activator="{ props }">
                <v-btn
                  variant="plain"
                  color="primary"
                  class="mr-n8"
                  v-bind="props"
                >
                  <v-icon>mdi-menu-down</v-icon>
                </v-btn>
              </template>

              <!-- Permit actions drop down list -->
              <v-list>
                <v-list-item>
                  <v-list-item-subtitle class="pa-0">
                    <v-icon size="small">
                      mdi-delete
                    </v-icon>
                    <span class="ml-1 remove-btn-text">Cancel Transport Permit</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-btn>

          <!-- Default Transport Permit Actions -->
          <v-btn
            v-else-if="!isExemptMhr && !hasActiveTransportPermit"
            id="home-location-change-btn"
            variant="plain"
            class=""
            color="primary"
            :ripple="false"
            :disabled="disable || disabledDueToLocation || state.disableDueToLien"
            data-test-id="transport-permit-btn"
            @click="toggleLocationChange()"
          >
            <span v-if="!isChangeLocationActive">
              <v-icon
                color="primary"
                size="small"
              >mdi-pencil</v-icon> Transport Permit / Location Change
            </span>
            <span v-else>
              <v-icon
                color="primary"
                size="small"
              >mdi-close</v-icon> Cancel Transport Permit / Location Change
            </span>
          </v-btn>
        </v-col>
      </v-row>
    </header>

    <p
      v-if="disabledDueToLocation"
      class="mt-8"
    >
      <span class="font-weight-bold">Note</span>: You cannot register a transport permit / location change because
      the home’s registered location does not match your lot location information. Transport permits can be issued by
      BC Registries staff or by a qualified lawyer or notary.
    </p>

    <p
      v-else-if="!isExemptMhr || hasActiveTransportPermit"
      class="mt-8"
      data-test-id="active-trans-permit"
    >
      <template v-if="hasActiveTransportPermit">
        <span class="font-weight-bold">Note</span>: A transport permit has already been issued for this home. The
        transport permit location can be only amended by the qualified supplier who issued the permit or by BC
        Registries staff.
      </template>
      <template v-else>
        Transport permits are issued by changing the location on the manufactured home. Transport permits expire 30 days
        from the date of issue.
      </template>
    </p>

    <!-- Change active template -->
    <template v-if="isChangeLocationActive">
      <p
        v-if="!isAmendLocationActive"
        class="mt-4"
      >
        To change the location of this home, first select the Location Change Type.
      </p>

      <p
        v-if="!isRoleStaffReg && !isAmendLocationActive"
        class="mt-4"
      >
        <span class="font-weight-bold">Note:</span> If the home has already been moved without a permit, a change of
        location cannot be completed online. You must notify BC Registries of the new location by submitting a
        <a
          :href="'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/' +
            'permits-licences-and-registration/registries-forms/form_13_mhr_-_registered_location_change.pdf'"
          class="generic-link"
          target="_blank"
        >
          Registered Location Change form
          <v-icon size="18">mdi-open-in-new</v-icon>
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
                    This permit expires 30 days after the date of issue. If the manufactured home is not moved before
                    the transport permit expires, you must report the physical location of the manufactured home within
                    3 days of expiry of the permit.
                  </li>
                  <li class="mt-2">
                    If the home is permanently moved to a different location than what is specified on the transport
                    permit, you must report the physical location of the manufactured home within 3 days of the move.
                  </li>
                  <li class="mt-2">
                    This transport permit is valid for one (1) move only. A new transport permit must be obtained for
                    any subsequent move of the manufactured home.
                  </li>
                  <li class="mt-2">
                    Upon leaving British Columbia, a manufactured home is exempt from the Manufactured Home Act. The
                    home must be re-registered under the same number if it re-enters British Columbia. A manufactured
                    home may not be moved out of British Columbia unless an exemption is issued by the Registrar.
                  </li>
                </ol>
              </p>
              <p class="help-note">
                <span>Note: </span> A manufactured home may be subject to routing restrictions in accordance with the
                requirements of the Ministry of Transportation and Infrastructure. You are responsible for confirming
                any such restrictions and you may visit
                <a
                  class="generic-link"
                  href="https://onroutebc.gov.bc.ca/#contactus"
                  target="_blank"
                >
                  onRouteBC - Home (gov.bc.ca)
                  <v-icon
                    color="primary"
                    size="12"
                  >mdi-open-in-new</v-icon>
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
          :documentId="state.transportPermitDocumentId"
          :validate="validate"
          @setStoreProperty="handleDocumentIdUpdate($event)"
          @isValid="setValidation('isDocumentIdValid', $event)"
        />
      </section>

      <!-- Location Change Type -->
      <section
        id="location-change-type-section"
        class="mt-5"
      >
        <LocationChange
          ref="locationChangeRef"
          :validate="validate"
          @updateLocationType="emit('updateLocationType')"
        />
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { DocumentId, SimpleHelpToggle } from "@/components/common"
import { LocationChange } from "@/components/mhrTransportPermit"
import { useMhrInformation, useMhrInfoValidation, useTransportPermits } from "@/composables/mhrInformation"
import { APIRegistrationTypes, LocationChangeTypes } from "@/enums"
import { useStore } from "@/store/store"
import { storeToRefs } from "pinia"
import { computed, reactive } from "vue"

withDefaults(defineProps<{
  disable: boolean,
  validate: boolean,
  disabledDueToLocation: boolean
}>(), {
  disable: false,
  validate: false,
  disabledDueToLocation: false
})

const emit = defineEmits(['updateLocationType', 'cancelTransportPermitChanges'])

const { setMhrTransportPermit } = useStore()

const {
  isRoleStaffReg,
  getMhrInfoValidation,
  getMhrTransportPermit,
  hasLien,
  isRoleQualifiedSupplier,
  getLienRegistrationType
} = storeToRefs(useStore())
const { hasActiveTransportPermit, isChangeLocationActive, isAmendLocationActive,
  setLocationChange, setAmendLocationChange, prefillTransportPermit, setLocationChangeType,
  isActivePermitWithinSamePark, isAmendChangeLocationEnabled
 } = useTransportPermits()
const { isExemptMhr } = useMhrInformation()

const {
  setValidation,
} = useMhrInfoValidation(getMhrInfoValidation.value)

const state = reactive({
  transportPermitDocumentId: computed(() => getMhrTransportPermit.value.documentId),
  disableDueToLien: computed((): boolean => {
    return isRoleQualifiedSupplier.value && hasLien.value &&
      getLienRegistrationType.value !== APIRegistrationTypes.SECURITY_AGREEMENT
  })
})

const toggleLocationChange = () => {
  if (isChangeLocationActive.value) {
    // trigger cancel dialog
    emit('cancelTransportPermitChanges')
  } else {
    // open transport permit
    setLocationChange(true)
  }
}

const toggleAmendLocationChange = async () => {
  if (isChangeLocationActive.value && isAmendLocationActive.value) {
    // trigger cancel dialog
    emit('cancelTransportPermitChanges')
  } else {
    // open transport permit
    setLocationChange(true)
    setAmendLocationChange(true)
    prefillTransportPermit()
    setLocationChangeType(isActivePermitWithinSamePark.value
      ? LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
      : LocationChangeTypes.TRANSPORT_PERMIT
    )
    // note: reset of unsaved changes will occur in LocationChange component
  }
}

const handleDocumentIdUpdate = (documentId: string) => {
  if (documentId) {
    setMhrTransportPermit({ key: 'documentId', value: documentId })
  }
}

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
ol li::marker {
  font-weight: normal;
}
</style>
