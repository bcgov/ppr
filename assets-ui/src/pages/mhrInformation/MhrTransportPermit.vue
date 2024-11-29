<template>
  <div id="mhr-transport-permit">
    <!-- Confirm New Transport Permit -->
    <BaseDialog
      :set-options="confirmNewTransportPermit"
      :set-display="state.showConfirmNewPermitDialog"
      @proceed="handleConfirmNewPermit"
    >
      <template #content>
        <p class="px-0 mr-n11">
          By applying for a new transport permit you are confirming that the active transport permit
          {{ getMhrInformation.permitRegistrationNumber }} issued on
          {{ pacificDate(getMhrInformation.permitDateTime, true) }} has been completed and will no longer be active.
        </p>
        <HomeLocationReview
          class="mx-n8 mt-n1"
          hide-default-header
          is-create-new-permit
        />
      </template>
    </BaseDialog>

    <!-- Header bar with actions -->
    <header
      id="home-location-change-header"
      class="review-header mt-10"
      :class="{ 'mb-n10': isExemptMhr && !hasActiveTransportPermit }"
    >
      <v-row
        no-gutters
        align="center"
      >
        <v-col
          cols="8"
          class="d-flex"
        >
          <img
            class="ml-1 review-header-icon"
            alt="home-location-review-icon"
            src="@/assets/svgs/homelocationicon_reviewscreen.svg"
          >
          <h3 class="fs-16 lh-24 ml-2">
            Location of Home
          </h3>
        </v-col>
        <v-col
          cols="4"
          class="text-right"
        >
          <!-- Active Transport Permit Actions: New Permit -->
          <v-btn
            v-if="isNewPermitActive"
            variant="plain"
            color="primary"
            :ripple="false"
            @click="handleConfirmNewPermit(false)"
          >
            <v-icon
              color="primary"
              size="small"
              class="mr-1"
            >
              mdi-close
            </v-icon>
            Cancel New Transport Permit
          </v-btn>

          <!-- New Transport Permit when QS didn't issue Permit -->
          <v-btn
            v-if="hasMhrReIssuePermitEnabled && !isRoleStaff && hasActiveTransportPermit &&
              !getTransportPermitChangeAllowed && !isNewPermitActive"
            variant="plain"
            color="primary"
            :ripple="false"
            :disabled="disabledDueToLocation"
            @click="handleConfirmNewPermit(true)"
          >
            <img
              alt="extend-icon"
              class="icon-small"
              src="@/assets/svgs/iconNewPermit.svg"
            >
            Create New Transport Permit
          </v-btn>

          <!-- Active Transport Permit Actions: Amend Permit -->
          <v-btn
            v-else-if="hasActiveTransportPermit && isAmendChangeLocationEnabled &&
              !isCancelChangeLocationActive && !isExtendChangeLocationActive && !isNewPermitActive"
            id="home-location-change-btn"
            variant="plain"
            color="primary"
            :ripple="false"
            :disabled="disable || !getTransportPermitChangeAllowed"
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

            <!-- Segmented Menu and Dropdown Cancel Option disabled until Development -->
            <template v-if="isCancelChangeLocationEnabled">
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
                  <!-- Extend Permit -->
                  <v-list-item
                    v-if="hasMhrReIssuePermitEnabled && !state.disableTransportPermitExtension"
                    data-test-id="extend-transport-permit-btn"
                    @click="toggleExtendTransportPermit(true)"
                  >
                    <v-list-item-subtitle
                      class="pa-0"
                    >
                      <span class="pt-3">
                        <img
                          alt="extend-icon"
                          class="icon-small"
                          src="@/assets/svgs/iconExtend.svg"
                        >
                      </span>
                      <span class="extend-btn-text ml-1">Extend Transport Permit</span>
                    </v-list-item-subtitle>
                  </v-list-item>

                  <!-- Create New Permit -->
                  <v-list-item
                    v-if="hasMhrReIssuePermitEnabled && !state.disableNewTransportPermit"
                    data-test-id="create-new-transport-permit-btn"
                    @click="state.showConfirmNewPermitDialog = true"
                  >
                    <v-list-item-subtitle
                      class="pa-0"
                    >
                      <span class="pt-3">
                        <img
                          alt="extend-icon"
                          class="icon-small"
                          src="@/assets/svgs/iconNewPermit.svg"
                        >
                      </span>
                      <span class="extend-btn-text ml-1">Create New Transport Permit</span>
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item
                    data-test-id="cancel-transport-permit-btn"
                    :disabled="!getTransportPermitChangeAllowed"
                    @click="toggleCancelTransportPermit(true)"
                  >
                    <v-list-item-subtitle
                      class="pa-0"
                    >
                      <v-icon
                        size="small"
                        class="mt-n1"
                      >
                        mdi-delete
                      </v-icon>
                      <span class="ml-1 remove-btn-text">Cancel Transport Permit</span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-btn>

          <v-btn
            v-else-if="isCancelChangeLocationActive"
            variant="plain"
            color="primary"
            data-test-id="undo-transport-permit-cancellation-btn"
            :ripple="false"
            @click="toggleCancelTransportPermit(false)"
          >
            <v-icon
              size="small"
              class="mr-2"
            >
              mdi-undo
            </v-icon> Undo Cancellation
          </v-btn>

          <v-btn
            v-else-if="isExtendChangeLocationActive"
            variant="plain"
            color="primary"
            data-test-id="undo-transport-permit-extend-btn"
            :ripple="false"
            @click="toggleExtendTransportPermit(false)"
          >
            <v-icon
              size="small"
              class="mr-2"
            >
              mdi-undo
            </v-icon> Cancel Transport Permit Extension
          </v-btn>

          <!-- Default Transport Permit Actions -->
          <v-btn
            v-else-if="!isExemptMhr && !hasActiveTransportPermit && !isCancelledMhr"
            id="home-location-change-btn"
            variant="plain"
            color="primary"
            :ripple="false"
            :disabled="disable || disabledDueToLocation"
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
      v-if="isNewPermitActive"
      class="mt-12 mb-4"
    >
      Transport permits are issued by changing the location on the manufactured home. Transport permits expire 30 days
      from the date of issue.
    </p>

    <p
      v-else-if="disabledDueToLocation && !hasActiveTransportPermit"
      role="alert"
      class="mt-12"
    >
      <b>Note</b>: You cannot register a transport permit / location change because
      the home’s registered location does not match your lot location information. Transport permits can be issued by
      BC Registries staff or by a qualified lawyer or notary.
    </p>

    <div
      v-else-if="!isExemptMhr || hasActiveTransportPermit"
      class="mt-8"
      data-test-id="active-trans-permit"
    >
      <template v-if="hasActiveTransportPermit">
        <p role="alert">
          A transport permit has already been issued for this home. The transport permit can only be modified by the
          issuing qualified supplier or BC Registries staff.
        </p>
        <p
          v-if="isCancelChangeLocationActive"
          data-test-id="cancel-permit-info"
          class="my-6"
        >
          Cancelling the transport permit will restore the previous registered location for this home.
        </p>
        <p
          v-else-if="isExtendChangeLocationActive"
          data-test-id="extend-permit-info"
          class="my-6"
        >
          <b>Note</b>: The expiry date will be extended by 30 days from the date this extension is submitted.
        </p>
      </template>
      <template v-else>
        <p>
          Transport permits are issued by changing the location on the manufactured home. Transport permits
          expire 30 days from the date of issue.
        </p>
      </template>
    </div>

    <!-- Change active template -->
    <template v-if="isChangeLocationActive && !isNewPermitActive">
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
        <b>Note:</b> If the home has already been moved without a permit, a change of
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
    </template>


    <!-- Help Content -->
    <SimpleHelpToggle
      v-if="isChangeLocationActive || isCancelChangeLocationActive || isExtendChangeLocationActive"
      class="mt-1"
      toggle-button-title="Help with Transport Permits"
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

    <!-- New Permit Review -->
    <template v-if="isNewPermitActive">
      <CautionBox
        class="my-9"
        :set-msg="`Creating a new transport can only be performed once the manufactured home has been transported to the
         current registered location. When the new transport permit is issued, the current Transport Permit
          ${getMhrInformation.permitRegistrationNumber} will no longer be active.`"
      />

      <HomeLocationReview
        is-transfer-review
        :hide-default-header="true"
        :is-pad-editable="false"
      />
      <v-card
        flat
        class="mt-2"
      >
        <TransportPermitDetails
          is-completed-location
        />
      </v-card>
    </template>

    <!-- Document ID -->
    <section
      v-if="isRoleStaffReg && (isChangeLocationActive || isCancelChangeLocationActive || isExtendChangeLocationActive)"
      id="document-id-section"
      class="mt-7"
    >
      <DocumentId
        :content="{ sideLabel: 'Document ID', hintText: 'Enter the 8-digit Document ID number' }"
        :document-id="state.transportPermitDocumentId"
        :validate="validate"
        @set-store-property="setMhrTransportPermit({ key: 'documentId', value: $event })"
        @is-valid="setValidation('isDocumentIdValid', $event)"
      />
    </section>

    <HomeLocationReview
      v-if="isExtendChangeLocationActive"
      is-transfer-review
      :hide-default-header="true"
      :is-pad-editable="false"
    />

    <div
      v-if="isCancelChangeLocationActive"
      data-test-id="verify-location-details"
      class="mt-10"
    >
      <h3 class="fs-18 mb-1 lh-28">
        Verify Home Location Details
      </h3>
      <p>Verify the location details. If the restored details are incorrect, please contact BC Registries staff.</p>
    </div>

    <!-- Location Change Type -->
    <section
      v-if="isChangeLocationActive || isExtendChangeLocationActive"
      id="location-change-type-section"
      class="mt-5"
    >
      <LocationChange
        ref="locationChangeRef"
        :validate="validate"
        @update-location-type="emit('updateLocationType')"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { CautionBox, DocumentId, SimpleHelpToggle } from '@/components/common'
import { LocationChange, TransportPermitDetails } from '@/components/mhrTransportPermit'
import { useMhrInformation, useMhrInfoValidation, useTransportPermits } from "@/composables/mhrInformation"
import { APIMhrTypes, LocationChangeTypes } from '@/enums'
import { useStore } from "@/store/store"
import { storeToRefs } from "pinia"
import { computed, reactive } from "vue"
import { HomeLocationReview } from '@/components/mhrRegistration'
import { BaseDialog } from '@/components/dialogs'
import { confirmNewTransportPermit } from '@/resources/dialogOptions'
import { pacificDate } from '@/utils'

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

const { setMhrTransportPermit, setMhrTransportPermitLocationChangeType } = useStore()

const {
  isRoleStaff,
  isRoleStaffReg,
  isRoleManufacturer,
  getMhrInformation,
  getMhrInfoValidation,
  getMhrTransportPermit,
  hasMhrReIssuePermitEnabled,
  getTransportPermitChangeAllowed
} = storeToRefs(useStore())
const {
  hasActiveTransportPermit, isChangeLocationActive, isNewPermitActive, isAmendLocationActive,
  isCancelChangeLocationActive, setLocationChange, setAmendLocationChange, prefillTransportPermit,
  setLocationChangeType, isActivePermitWithinSamePark, isAmendChangeLocationEnabled, isCancelChangeLocationEnabled,
  setCancelLocationChange, setExtendLocationChange, isExtendChangeLocationActive, setNewPermitChange
 } = useTransportPermits()
const { isExemptMhr, isCancelledMhr } = useMhrInformation()

const {
  setValidation,
} = useMhrInfoValidation(getMhrInfoValidation.value)

const state = reactive({
  showConfirmNewPermitDialog: false,
  transportPermitDocumentId: computed(() => getMhrTransportPermit.value.documentId),
  disableTransportPermitExtension: computed(() => {
    const hasPreviousExtend = getMhrInformation.value.changes.some(reg =>
      reg.registrationType === APIMhrTypes.TRANSPORT_PERMIT_EXTEND
    )
    return !isRoleStaffReg.value && hasPreviousExtend
  }),
  disableNewTransportPermit: computed(() => {
    return isRoleManufacturer.value
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

const toggleCancelTransportPermit = (val: boolean) => {
  setLocationChangeType(val ? LocationChangeTypes.TRANSPORT_PERMIT_CANCEL : null)
  if (val) {
    setCancelLocationChange(val)
  } else {
    emit('cancelTransportPermitChanges', false)
  }
}

const toggleExtendTransportPermit = (val: boolean) => {
  setExtendLocationChange(val)
  setMhrTransportPermitLocationChangeType(val ? LocationChangeTypes.EXTEND_PERMIT : null)
  if (!val) emit('cancelTransportPermitChanges', val)
}

const handleConfirmNewPermit = (val: boolean) => {
  setNewPermitChange(val)
  setLocationChange(val)
  setLocationChangeType(val ? LocationChangeTypes.TRANSPORT_PERMIT : null)
  state.showConfirmNewPermitDialog = false
  if (!val) emit('cancelTransportPermitChanges', val)
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';
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
