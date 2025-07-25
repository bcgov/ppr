<template>
  <v-card
    flat
    class="py-6 pl-6 pr-8 mb-5 rounded"
    :class="{ 'border-error-left': showTableError || showReviewedError}"
  >
    <v-row id="mhr-home-add-person">
      <v-col cols="3">
        <label
          class="generic-label"
          :class="{ 'error-text' : showTableError || showReviewedError}"
        >
          {{ getSidebarTitle }}
        </label>
      </v-col>
      <v-col cols="9">
        <!-- Qualified Supplier specific messaging when adding/editing owners -->
        <CautionBox
          v-if="isRoleQualifiedSupplier"
          class="mb-9"
          :set-msg="'Transfers to a trustee or a trust of any kind, cannot be completed online and must be ' +
            'registered by BC Registries staff.'"
        />

        <!-- Owner Roles Component-->
        <HomeOwnerRoles
          :party-type="owner.partyType"
          :disable-roles="isCurrentOwner(owner)"
          @update:party-type="owner.partyType = $event"
        />

        <v-form
          id="addHomeOwnerForm"
          ref="addHomeOwnerForm"
          v-model="isHomeOwnerFormValid"
        >
          <div v-if="isPerson">
            <label class="generic-label">
              Person's Name
            </label>
            <v-tooltip
              v-if="disableNameFields && isCurrentOwner(owner)"
              location="top"
              content-class="top-tooltip pa-5"
              transition="fade-transition"
              data-test-id="suffix-tooltip"
            >
              <template #activator="{ props }">
                <v-icon
                  class="mt-n1"
                  color="primary"
                  v-bind="props"
                >
                  mdi-information-outline
                </v-icon>
              </template>
              {{ disabledNameEditTooltip }}
            </v-tooltip>
            <v-row class="mt-2">
              <v-col cols="4">
                <v-text-field
                  id="first-name"
                  v-model="owner.individualName.first"
                  variant="filled"
                  color="primary"
                  label="First Name"
                  data-test-id="first-name"
                  :rules="firsNameRules"
                  :disabled="disableNameFields && isCurrentOwner(owner)"
                  :readonly="disableNameFields && isCurrentOwner(owner)"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="middle-name"
                  v-model="owner.individualName.middle"
                  variant="filled"
                  color="primary"
                  label="Middle Name (Optional)"
                  data-test-id="middle-name"
                  :rules="maxLength(50)"
                  :disabled="disableNameFields && isCurrentOwner(owner)"
                  :readonly="disableNameFields && isCurrentOwner(owner)"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="last-name"
                  v-model="owner.individualName.last"
                  variant="filled"
                  color="primary"
                  label="Last Name"
                  data-test-id="last-name"
                  :rules="lastNameRules"
                  :disabled="disableNameFields && isCurrentOwner(owner)"
                  :readonly="disableNameFields && isCurrentOwner(owner)"
                />
              </v-col>
            </v-row>
          </div>
          <div v-else>
            <label
              class="generic-label"
              for="org-name"
            >
              Business or Organization Name
            </label>
            <v-tooltip
              v-if="disableNameFields && isCurrentOwner(owner)"
              location="top"
              content-class="top-tooltip pa-5"
              transition="fade-transition"
            >
              <template #activator="{ props }">
                <v-icon
                  class="mt-n1"
                  color="primary"
                  v-bind="props"
                >
                  mdi-information-outline
                </v-icon>
              </template>
              {{ disabledNameEditTooltip }}
            </v-tooltip>
            <v-row
              v-if="!isCurrentOwner(owner)"
              class="mt-2"
            >
              <v-col>
                <p>
                  You can find the full legal name of an active B.C. business by entering the name
                  or incorporation number of the business, or you can type the full legal name of other types of
                  <v-tooltip
                    location="top"
                    content-class="top-tooltip pa-5"
                    transition="fade-transition"
                    data-test-id="organization-tooltip"
                  >
                    <template #activator="{ props }">
                      <span
                        class="underline"
                        v-bind="props"
                      > organizations.</span>
                    </template>
                    Organizations, other than active B.C. businesses, that can be listed as owners
                    include the following:<br><br>
                    <li>Indian Bands,</li>
                    <li>Public Bodies, or</li>
                    <li>Organizations not registered in B.C.</li><br>
                    Refer to "Help with Business and Organization Owners" for more details.
                  </v-tooltip>
                </p>

                <SimpleHelpToggle
                  class="pt-1"
                  toggle-button-title="Help with Business and Organization Owners"
                  :default-hide-text="false"
                >
                  <template #content>
                    <h3 class="text-center mb-2">
                      Business and Organization Owners
                    </h3>
                    <p>
                      Businesses and organizations that <b>can</b> own a manufactured home include the following:
                    </p>
                    <h3 class="mb-2 gray7">
                      B.C. Based Businesses
                    </h3>
                    <li>B.C. corporations</li>
                    <li>B.C. societies</li>
                    <li>B.C. cooperatives</li>
                    <li>
                      Extra-provincial companies registered in B.C. (corporations, societies and cooperatives)
                    </li><br>
                    <h3 class="mb-2 gray7">
                      Other Businesses and Organizations
                    </h3>
                    <li>Indian bands</li>
                    <li>Public bodies</li>
                    <li>Businesses and organizations not registered in B.C.</li><br>
                    <p>Businesses and organizations that <b>cannot</b> own a manufactured home:</p>
                    <h3 class="mb-2 gray7">
                      Sole Proprietorships / Partnerships
                    </h3>
                    <p>
                      Registered owners of a manufactured home <b>cannot</b> be a sole proprietorship, partnership,
                      or limited partnership. The owners of the proprietorship or partnership must be added as a
                      person or as an organization.
                    </p>
                    <hr class="mb-5 mt-6 solid">
                    <h3 class="text-center mb-2">
                      When B.C. Based Businesses Must be in Active Status
                    </h3>
                    <p><b>New owners:</b> Must be active at the time of registration.</p>
                    <p>
                      If you are adding a B.C. based business as a new owner, the business <b>must be active on the
                        B.C. Corporate Register at the time of the registration.</b>
                    </p><br>
                    <p><b>Existing owners:</b> Must be active at the time the bill of sale was signed.</p>
                    <p>
                      If you are including a business that is already an owner of the home, the business <b>must have
                        been active on the B.C. Corporate Register at the time the bill of sale was signed.</b>
                    </p>
                    <hr class="mb-5 mt-6 solid">
                    <h3 class="text-center mb-2">
                      My Business Isn't Listed
                    </h3>
                    <p>
                      The business look-up displays the list of all active businesses in B.C. If your business is
                      listed, select the business from the look-up list.
                    </p>
                    <p>
                      If you enter the name of a B.C. based business and the name does not appear in the business
                      look-up, the business is not active in the B.C. Corporate Register. In this case, please contact
                      the Manufactured Home Registry.
                    </p>
                    <p>
                      If you enter the name of another type of organization, the name will not appear in the look-up.
                      In this case, type the full legal name of the organization.
                    </p>
                  </template>
                </SimpleHelpToggle>
              </v-col>
            </v-row>
            <v-row class="my-2">
              <v-col>
                <v-text-field
                  id="org-name"
                  ref="orgNameSearchField"
                  v-model="searchValue"
                  :label="isCurrentOwner(owner)
                    ? 'Full Legal Name of Business or Organization'
                    : 'Find or enter the Full Legal Name of the Business or Organization'"
                  variant="filled"
                  color="primary"
                  persistent-hint
                  persistent-clear
                  :rules="orgNameRules"
                  :clearable="showClear"
                  :clear-icon="'mdi-close'"
                  :disabled="disableNameFields && isCurrentOwner(owner)"
                  :readonly="disableNameFields && isCurrentOwner(owner)"
                  @click:clear="showClear = false"
                >
                  <template #append-inner>
                    <v-progress-circular
                      v-if="loadingSearchResults"
                      indeterminate
                      color="primary"
                      class="mx-3"
                      :size="25"
                      :width="3"
                    />
                  </template>
                </v-text-field>

                <BusinessSearchAutocomplete
                  v-click-outside="setCloseAutoComplete"
                  :search-value="autoCompleteSearchValue"
                  :set-auto-complete-is-active="autoCompleteIsActive"
                  :show-dropdown="$refs.orgNameSearchField && $refs.orgNameSearchField.isFocused"
                  @search-value="setSearchValue"
                  @searching="loadingSearchResults = $event"
                />
              </v-col>
            </v-row>
          </div>

          <label class="generic-label">
            Additional Name Information
          </label>
          <v-tooltip
            v-if="disableNameFields && isCurrentOwner(owner)"
            location="top"
            content-class="top-tooltip pa-5"
            transition="fade-transition"
            data-test-id="suffix-tooltip"
          >
            <template #activator="{ props }">
              <v-icon
                class="mt-n1"
                color="primary"
                v-bind="props"
              >
                mdi-information-outline
              </v-icon>
            </template>
            {{ disabledNameEditTooltip }}
          </v-tooltip>
          <v-row class="my-2">
            <v-col class="col">
              <v-tooltip
                location="right"
                content-class="right-tooltip pa-5"
                transition="fade-transition"
                :disabled="!additionalNameTooltip"
              >
                <template #activator="{ props }">
                  <v-text-field
                    id="suffix"
                    v-model="owner[getSuffixOrDesc(owner)]"
                    variant="filled"
                    color="primary"
                    :label="nameConfig.label"
                    data-test-id="suffix"
                    :hint="(disableNameFields && isCurrentOwner(owner)) ? '' : nameConfig.hint"
                    persistent-hint
                    :rules="additionalNameRules"
                    :disabled="disableNameFields && isCurrentOwner(owner)"
                    :readonly="disableNameFields && isCurrentOwner(owner)"
                    v-bind="props"
                  />
                </template>
                <span v-html="additionalNameTooltip" />
              </v-tooltip>
            </v-col>
          </v-row>

          <label class="generic-label">
            Phone Number
          </label>
          <v-row class="my-2">
            <v-col cols="6">
              <v-text-field
                id="phone-number"
                ref="phoneNumberRef"
                v-model="displayPhone"
                v-maska:[phoneMask]
                variant="filled"
                color="primary"
                :rules="phoneNumberRules"
                label="Phone Number (Optional)"
                data-test-id="phone-number"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                id="phone-ext"
                v-model="owner.phoneExtension"
                variant="filled"
                color="primary"
                :rules="phoneExtensionRules"
                label="Extension (Optional)"
                data-test-id="phone-ext"
              />
            </v-col>
          </v-row>

          <label class="generic-label">
            Mailing Address
          </label>

          <BaseAddress
            :value="owner.address"
            :editing="true"
            :schema="{ ...addressSchema }"
            :trigger-errors="triggerAddressErrors"
            class="mt-6"
            hide-address-hint
            @valid="isAddressFormValid = $event"
            @update-address="owner.address = $event"
          />

          <!-- Group Add / Edit -->
          <template
            v-if="!isTransferDueToDeath && !(isMhrCorrection && editHomeOwner) &&
              !(disableNameFields && isCurrentOwner(owner))"
          >
            <hr class="mt-3 mb-10">
            <HomeOwnerGroups
              :group-id="isDefinedGroup ? ownersGroupId : null"
              :is-adding-home-owner="isAddingHomeOwner"
              :fractional-data="groupFractionalData"
              :is-mhr-transfer="isMhrTransfer"
              @set-owner-group-id="ownerGroupId = $event"
            />
          </template>
          <template v-else>
            <p class="fs-16 mt-3">
              <strong>Note:</strong> Group Details cannot be changed in this type of
              {{ isMhrCorrection ? 'registration' : 'transfer' }}.
            </p>
          </template>
        </v-form>
        <v-row
          no-gutters
          class="pt-5"
        >
          <v-col>
            <div class="form__row form__btns">
              <v-btn
                variant="outlined"
                color="error"
                class="remove-btn"
                :disabled="isAddingHomeOwner || disableOwnerRemoval"
                :ripple="false"
                @click="remove()"
              >
                <span>{{ isCurrentOwner(owner) ? 'Delete' : 'Remove' }} Owner</span>
              </v-btn>

              <span class="float-right">
                <v-btn
                  color="primary"
                  class="ml-auto mx-2"
                  :ripple="false"
                  size="large"
                  data-test-id="done-btn"
                  @click="done()"
                >
                  Done
                </v-btn>
                <v-btn
                  :ripple="false"
                  size="large"
                  color="primary"
                  variant="outlined"
                  data-test-id="cancel-btn"
                  @click="cancel()"
                >
                  Cancel
                </v-btn>
              </span>
            </div>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { useInputRules } from '@/composables/useInputRules'
import { useHomeOwners, useMhrCorrections, useMhrValidations } from '@/composables/mhrRegistration'
import { BusinessSearchAutocomplete } from '@/components/search'
import { formatAddress } from '@/composables/address/factories'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { focusOnFirstError, fromDisplayPhone } from '@/utils'
import type {
  AdditionalNameConfigIF,
  FormIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'
import { CautionBox, SimpleHelpToggle } from '@/components/common'
import HomeOwnerGroups from './HomeOwnerGroups.vue'
import HomeOwnerRoles from './HomeOwnerRoles.vue'
import { useStore } from '@/store/store'
import { find } from 'lodash'
import { useMhrInformation, useTransferOwners } from '@/composables'
import { ActionTypes, HomeOwnerPartyTypes } from '@/enums'
import { AdditionalNameConfig, phoneMask, transfersContent } from '@/resources'
import { storeToRefs } from 'pinia'

interface FractionalOwnershipWithGroupIdIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: number
}

let DEFAULT_OWNER_ID = 1

export default defineComponent({
  name: 'AddEditHomeOwner',
  components: {
    CautionBox,
    BaseAddress,
    SimpleHelpToggle,
    HomeOwnerRoles,
    HomeOwnerGroups,
    BusinessSearchAutocomplete
  },
  props: {
    editHomeOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      default: null
    },
    isHomeOwnerPerson: {
      type: Boolean,
      default: false
    },
    isMhrTransfer: {
      type: Boolean,
      default: false
    },
    showTableError: {
      type: Boolean,
      default: false
    },
    disableOwnerRemoval: {
      type: Boolean,
      default: false
    }
  },
  emits: ['remove', 'cancel'],
  setup (props, context) {
    const { setUnsavedChanges } = useStore()
    const {
      // Getters
      isRoleStaffReg,
      isRoleQualifiedSupplier,
      getMhrRegistrationHomeOwnerGroups,
      getMhrTransferHomeOwnerGroups,
      getMhrRegistrationValidationModel,
      getMhrTransferType
    } = storeToRefs(useStore())
    const {
      MhrSectVal,
      getStepValidation,
      setValidation,
      MhrCompVal
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { isMhrCorrection, isPublicAmendment } = useMhrCorrections()

    const {
      required,
      customRules,
      maxLength,
      minLength,
      isPhone,
      isNumber,
      invalidSpaces
    } = useInputRules()

    const {
      getGroupForOwner,
      addOwnerToTheGroup,
      editHomeOwner,
      showGroups,
      setShowGroups,
      setGroupFractionalInterest,
      getMhrBaselineOwnerById,
      isCorrectedOwner,
      getTransferOrRegistrationHomeOwners
    } = useHomeOwners(props.isMhrTransfer, isMhrCorrection.value)

    const {
      isCurrentOwner,
      isTransferDueToDeath,
      isTransferToAdminNoWill,
      hasCurrentOwnerChanges,
      disableNameFields,
      isTransferToExecOrAdmin,
      TransToExec
    } = useTransferOwners()

    const {
      isFrozenMhr,
      isFrozenMhrDueToAffidavit
    } = useMhrInformation()

    const addressSchema = PartyAddressSchema
    const addHomeOwnerForm = ref(null) as FormIF

    const getTransferOrRegistrationHomeOwnerGroups = () =>
      props.isMhrTransfer ? getMhrTransferHomeOwnerGroups.value : getMhrRegistrationHomeOwnerGroups.value

    const defaultHomeOwner: MhrRegistrationHomeOwnerIF = {
      ...props.editHomeOwner,
      ownerId: props.editHomeOwner?.ownerId ||
        ((props.isMhrTransfer || isMhrCorrection.value)
          ? getTransferOrRegistrationHomeOwners().length + 1
          : DEFAULT_OWNER_ID++),
      phoneNumber: props.editHomeOwner?.phoneNumber || '',
      phoneExtension: props.editHomeOwner?.phoneExtension || '',
      suffix: props.editHomeOwner?.suffix || '',
      description: props.editHomeOwner?.description || '',
      address: {
        street: props.editHomeOwner?.address.street || '',
        streetAdditional: props.editHomeOwner?.address.streetAdditional || '',
        city: props.editHomeOwner?.address.city || '',
        region: props.editHomeOwner?.address.region || '',
        country: props.editHomeOwner?.address.country || '',
        postalCode: props.editHomeOwner?.address.postalCode || '',
        deliveryInstructions: props.editHomeOwner?.address.deliveryInstructions || ''
      },
      action: props.editHomeOwner?.action || null,
      partyType: props.editHomeOwner?.partyType || HomeOwnerPartyTypes.OWNER_IND
    }

    if (props.isHomeOwnerPerson) {
      defaultHomeOwner.individualName = {
        first: props.editHomeOwner?.individualName.first || '',
        middle: props.editHomeOwner?.individualName.middle || '',
        last: props.editHomeOwner?.individualName.last || ''
      }
    } else if (![HomeOwnerPartyTypes.EXECUTOR, HomeOwnerPartyTypes.ADMINISTRATOR, HomeOwnerPartyTypes.TRUSTEE]
      .includes(props.editHomeOwner?.partyType)) {
      defaultHomeOwner.organizationName = props.editHomeOwner?.organizationName || ''
      defaultHomeOwner.partyType = HomeOwnerPartyTypes.OWNER_BUS
    }

    // Transfers flow: Pre-fill suffix and type for new owners (not when editing existing owner)
    if (props.isMhrTransfer && isTransferToExecOrAdmin.value && !props.editHomeOwner &&
      TransToExec.hasDeletedOwnersWithProbateGrantOrAffidavit()) {
      TransToExec.prefillOwnerAsExecOrAdmin(defaultHomeOwner)
    }

    const allFractionalData = (getTransferOrRegistrationHomeOwnerGroups() || [{}]).map(group => {
      return {
        groupId: group.groupId || 1,
        type: group?.type || '',
        interest: group?.interest || 'Undivided',
        interestNumerator: group?.interestNumerator || null,
        interestDenominator: group?.interestDenominator || null
      }
    }) as FractionalOwnershipWithGroupIdIF[]

    const hasMultipleOwnersInGroup =
      find(getTransferOrRegistrationHomeOwnerGroups(), { groupId: props.editHomeOwner?.groupId })?.owners.length > 1

    if (allFractionalData.length === 0 || props.editHomeOwner == null || hasMultipleOwnersInGroup) {
      // Default LCM to be used if all denominators are the identical. UX feature for MHR's only
      const defaultLcm = allFractionalData
        .every(group => group.interestDenominator === allFractionalData[0]?.interestDenominator)
        ? allFractionalData[0]?.interestDenominator
        : null

      allFractionalData.push({
        groupId: (allFractionalData.length + 1),
        type: 'N/A',
        interest: 'Undivided',
        interestNumerator: defaultLcm ? allFractionalData[0]?.interestNumerator : null,
        interestDenominator: defaultLcm
      } as FractionalOwnershipWithGroupIdIF)
    }

    const localState = reactive({
      getSidebarTitle: computed((): string => {
        const addOrEdit = props.editHomeOwner === null ? 'Add a' : 'Edit'
        const entity = props.isHomeOwnerPerson ? 'Person' : 'Business or Organization'

        return isCurrentOwner(localState.owner) ? `Change ${entity} Details` : `${addOrEdit} ${entity}`
      }),
      group: getGroupForOwner(props.editHomeOwner?.ownerId) as MhrRegistrationHomeOwnerGroupIF,
      ownersGroupId: computed(() => (showGroups.value ? localState.group?.groupId : null)),
      owner: { ...defaultHomeOwner },
      showReviewedError: computed(() =>
        (!getStepValidation(MhrSectVal.HOME_OWNERS_VALID) && !getStepValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID))),
      ownerGroupId: props.editHomeOwner?.groupId,
      showGroups: showGroups.value,
      isPerson: props.isHomeOwnerPerson,
      isAddingHomeOwner: props.editHomeOwner == null,
      groupFractionalData: computed((): FractionalOwnershipWithGroupIdIF =>
        find(allFractionalData, { groupId: localState.ownerGroupId || 1 })),
      isHomeOwnerFormValid: false,
      isAddressFormValid: false,
      triggerAddressErrors: false,
      isHelpPanelOpen: false,
      displayPhone: props.editHomeOwner !== null ? props.editHomeOwner.phoneNumber : '',
      firsNameRules: customRules(required('Enter a first name'), maxLength(50)),
      lastNameRules: customRules(required('Enter a last name'), maxLength(50)),
      orgNameRules: customRules(
        required('Enter a business or organization name'),
        maxLength(70)
      ),
      phoneNumberRules: customRules(
        isPhone(14)
      ),
      phoneExtensionRules: customRules(
        isNumber(null, null, null, 'Enter numbers only'),
        invalidSpaces(),
        maxLength(5, true)
      ),
      loadingSearchResults: false,
      showClear: false,
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      searchValue: props.editHomeOwner?.organizationName,
      isDefinedGroup: computed((): boolean => {
        return !!localState.groupFractionalData?.interestNumerator &&
          !!localState.groupFractionalData?.interestDenominator
      }),
      nameConfig: computed((): AdditionalNameConfigIF => {
        return AdditionalNameConfig[localState.owner.partyType]
      }),
      additionalNameRules: computed((): Array<()=>string|boolean> => {
        return localState.nameConfig.isRequired
          ? customRules(required('This fields is required'), maxLength(70))
          : maxLength(70)
      }),
      additionalNameTooltip: computed((): string => {
        // Display owner tooltip for Staff only
        if (isRoleStaffReg.value && localState.owner.partyType === HomeOwnerPartyTypes.OWNER_IND) {
          return localState.nameConfig?.tooltipContent.default
        }

        return localState.nameConfig?.tooltipContent[getMhrTransferType.value?.transferType]
      }),
      disabledNameEditTooltip: `Owner name’s cannot be changed here. Name change requests should be submitted
        separately, with the appropriate supporting documents, prior to completing this transfer. See Help with
        Ownership Transfer or Change for more information.`
    })

    const done = async (): Promise<void> => {
      localState.owner.address = formatAddress(localState.owner.address)
      addHomeOwnerForm.value.validate()
      await nextTick()

      // validate additional name field as part of add/edit own submission
      const isValidAdditionalName =
        [HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS].includes(localState.owner.partyType)
          ?  true
          : !!localState.owner[getSuffixOrDesc(localState.owner)]

      if (localState.isHomeOwnerFormValid && localState.isAddressFormValid && isValidAdditionalName) {
        setValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID, MhrCompVal.OWNERS_VALID, true)
        if (props.editHomeOwner) {
          let updatedOwner = isCurrentOwner(localState.owner)
            ? {
                ...localState.owner, action: hasCurrentOwnerChanges(localState.owner) ? ActionTypes.CHANGED : null
              }
            : localState.owner

          const mhrBaselineOwner = getMhrBaselineOwnerById(localState.owner?.ownerId)
          if (isMhrCorrection && mhrBaselineOwner) {
            updatedOwner = {
              ...localState.owner,
              action: isCorrectedOwner(localState.owner)
                ? isPublicAmendment.value ? ActionTypes.EDITED : ActionTypes.CORRECTED
                : null
            }
          }

          editHomeOwner(
            updatedOwner as MhrRegistrationHomeOwnerIF,
            localState.ownerGroupId || 1
          )
        } else {
          // In TransToExec flow, if the owner is the executor, add to same group as deleted owner with Probate Grant
          if (props.isMhrTransfer &&
            TransToExec.hasDeletedOwnersWithProbateGrantOrAffidavit() &&
            localState.owner.partyType === HomeOwnerPartyTypes.EXECUTOR) {
            localState.ownerGroupId = localState.owner.groupId
          }

          if (props.isMhrTransfer &&
              isTransferToAdminNoWill.value &&
              localState.owner.partyType === HomeOwnerPartyTypes.ADMINISTRATOR) {

            // find group with deleted owner
            localState.ownerGroupId =
              find(getMhrTransferHomeOwnerGroups.value, { owners: [{ action: ActionTypes.REMOVED }] }).groupId
          }

          addOwnerToTheGroup(
            localState.owner as MhrRegistrationHomeOwnerIF,
            localState.ownerGroupId
          )
        }

        // this should occur when trying to add the group and fractional info
        // check if group has some fractional data
        if (localState.groupFractionalData?.interestNumerator && localState.ownerGroupId) {
          setShowGroups(true)

          // Get fractional data based on owner's group id
          const fractionalData = find(allFractionalData, {
            groupId: localState.ownerGroupId
          }) as FractionalOwnershipWithGroupIdIF

          setGroupFractionalInterest(localState.ownerGroupId || 1, fractionalData)
        }

        if (props.isMhrTransfer) setUnsavedChanges(props.editHomeOwner !== localState.owner)

        cancel()
      } else {
        localState.triggerAddressErrors = !localState.triggerAddressErrors
        focusOnFirstError('addHomeOwnerForm')
      }
    }
    const remove = (): void => {
      context.emit('remove')
      scrollTopHomeOwners()
    }
    const cancel = (): void => {
      localState.ownerGroupId = props.editHomeOwner?.groupId
      setValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID, MhrCompVal.OWNERS_VALID, true)
      context.emit('cancel')
      scrollTopHomeOwners()
    }

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      localState.owner.organizationName = searchValueTyped
      localState.showClear = true
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    const scrollTopHomeOwners = () => {
      setTimeout(() => {
        document.getElementById('mhr-home-owners-list')?.scrollIntoView({ behavior: 'smooth' })
      }, 350) // wait for collapse animation to finish before the scroll
    }

    // For Individual and Business Owners, bind suffix to additional name field model
    // For all other owners, bind description field
    const getSuffixOrDesc = (owner: MhrRegistrationHomeOwnerIF): string => {
      return [HomeOwnerPartyTypes.OWNER_IND, HomeOwnerPartyTypes.OWNER_BUS].includes(owner.partyType)
        ? 'suffix'
        : 'description'
    }

    /** Handle Phone changes and write to store. **/
    watch(
      () => localState.displayPhone,
      () => {
        localState.owner.phoneNumber = fromDisplayPhone(localState.displayPhone)
      }
    )

    watch(() => localState.searchValue, (val: string) => {
      if (val?.length >= 3) {
        localState.autoCompleteSearchValue = val
        // show autocomplete results when there is a searchValue
        localState.autoCompleteIsActive = val !== ''
      } else {
        localState.autoCompleteSearchValue = val
        localState.autoCompleteIsActive = false
      }
      localState.owner.organizationName = val
    })

    return {
      phoneMask,
      done,
      remove,
      cancel,
      addHomeOwnerForm,
      maxLength,
      minLength,
      addressSchema,
      setSearchValue,
      setCloseAutoComplete,
      getSuffixOrDesc,
      getStepValidation,
      MhrSectVal,
      isCurrentOwner,
      isMhrCorrection,
      isTransferDueToDeath,
      disableNameFields,
      HomeOwnerPartyTypes,
      transfersContent,
      isFrozenMhr,
      customRules,
      required,
      showGroups,
      setShowGroups,
      AdditionalNameConfig,
      isRoleQualifiedSupplier,
      isFrozenMhrDueToAffidavit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(.theme--light.v-icon.mdi-close) {
  color: $primary-blue !important;
}

.solid {
  border: 0;
  border-top: 0.25px solid $gray4 !important;
}

.underline {
    border-bottom: 1px dotted $gray7;
    text-decoration: none;
}

#addHomeOwnerForm {
  p {
    color: $gray7;
    line-height: 24px;
  }
  li {
    color: $gray7;
    line-height: 24px;
  }
  li::marker {
    font-size: 0.75rem;
    color: $gray7 !important;
  }
}

#org-name :deep(.hide-results) {
  .v-autocomplete__content.v-menu__content {
    display: none !important;
  }
}

.selected-radio {
  background-color: white;
  :deep(.theme--light.v-label:not(.v-label--is-disabled), .theme--light.v-messages) {
    color: $gray7 !important;
  }
}

:deep() {
  .v-text-field.v-input--is-disabled .v-input__control > .v-text-field__details > .v-messages {
    color: $gray7!important;
  }
  .v-input--selection-controls .v-input__slot, .v-input--selection-controls .v-radio {
    cursor: unset!important;
  }
  .theme--light.v-radio--is-disabled {
    pointer-events: none!important;
    user-select: none!important;

    label {
      color: $gray7;
      opacity: .4;
    }

    i {
      opacity: .4;
    }
  }
}
</style>
