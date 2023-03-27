<template>
  <v-card flat class="py-6 px-8 mb-5 rounded" :class="{ 'border-error-left': showTableError || showReviewedError}">
    <v-row id="mhr-home-add-person">
      <v-col cols="3">
        <label class="generic-label"
        :class="{ 'error-text' : showTableError || showReviewedError}"
        >
          {{ getSidebarTitle }}
        </label>
      </v-col>
      <v-col cols="9">
        <!-- Owner Roles -->
        <v-row no-gutters v-if="isTransferDueToDeath">
          <v-col cols="12">
            <label class="generic-label">
              Role
            </label>
          </v-col>
          <v-col class="pt-2 pb-9">
            <v-radio-group
              id="owner-role-options"
              class="mt-0 pr-2" row
              hide-details="true"
              v-model="owner.partyType"
            >
              <v-radio
                id="owner-option"
                class="owner-radio pr-4"
                label="Owner"
                active-class="selected-radio"
                v-model="HomeOwnerPartyTypes.OWNER_IND"
              />
              <v-tooltip
                v-if="isTransferDueToDeath"
                top
                content-class="top-tooltip pa-5"
                transition="fade-transition"
                data-test-id="suffix-tooltip"
              >
                <template v-slot:activator="{ on }">
                  <v-radio
                    v-on="on"
                    id="executor-option"
                    class="executor-radio px-4"
                    active-class="selected-radio"
                    v-model="HomeOwnerPartyTypes.EXECUTOR"
                   >
                    <template v-slot:label><div><u>Executor</u></div></template>
                  </v-radio>
                </template>
                  An Executor is the personal representative named in the will or appointed by court to carry out the
                  requirements of a will. They are also referred to as trustee or liquidator (in Quebec).
              </v-tooltip>
              <v-radio
                id="trustee-option"
                class="trustee-radio px-4"
                label="Trustee"
                active-class="selected-radio"
                :disabled="isTransferDueToDeath"
                v-model="HomeOwnerPartyTypes.TRUSTEE"
              />
              <v-radio
                id="administrator-option"
                class="administrator-radio pl-4"
                label="Administrator"
                active-class="selected-radio"
                :disabled="isTransferDueToDeath"
                v-model="HomeOwnerPartyTypes.ADMINISTRATOR"
              />
            </v-radio-group>
          </v-col>
        </v-row>

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
              v-if="disableNameFields"
              top
              content-class="top-tooltip pa-5"
              transition="fade-transition"
              data-test-id="suffix-tooltip"
            >
              <template v-slot:activator="{ on }">
                <v-icon class="mt-n1" color="primary" v-on="on">
                  mdi-information-outline
                </v-icon>
              </template>
              {{ disabledNameEditTooltip }}
            </v-tooltip>
            <v-row>
              <v-col cols="4">
                <v-text-field
                  id="first-name"
                  v-model="owner.individualName.first"
                  filled
                  label="First Name"
                  data-test-id="first-name"
                  :rules="firsNameRules"
                  :disabled="disableNameFields"
                  :readonly="disableNameFields"
                  @mousedown.prevent
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="middle-name"
                  v-model="owner.individualName.middle"
                  filled
                  label="Middle Name (Optional)"
                  data-test-id="middle-name"
                  :rules="maxLength(15)"
                  :disabled="disableNameFields"
                  :readonly="disableNameFields"
                  @mousedown.prevent
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="last-name"
                  v-model="owner.individualName.last"
                  filled
                  label="Last Name"
                  data-test-id="last-name"
                  :rules="lastNameRules"
                  :disabled="disableNameFields"
                  :readonly="disableNameFields"
                  @mousedown.prevent
                />
              </v-col>
            </v-row>
          </div>
          <div v-else>
            <label class="generic-label" for="org-name">
              Business or Organization Name
            </label>
            <v-row>
              <v-col>
                <p>
                  You can find the full legal name of an active B.C. business by entering the name
                   or incorporation number of the business, or you can type the full legal name of other types of
                  <v-tooltip
                    top
                    content-class="top-tooltip pa-5"
                    transition="fade-transition"
                    data-test-id="organization-tooltip"
                    allow-overflow
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <span
                        v-bind="attrs"
                        v-on="on"
                      ><u> organizations.</u></span>
                    </template>
                    Organizations, other than active B.C. businesses, that can be listed as owners
                    include the following:<br><br>
                    <li>Indian Bands,</li>
                    <li>Public Bodies, or</li>
                    <li>Organizations not registered in B.C.</li><br>
                    Refer to "Help with Business and Organization Owners" for more details.
                  </v-tooltip>
                </p>

                <simple-help-toggle
                  toggleButtonTitle="Help with Business and Organization Owners"
                >
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
                  <li>Extra-provincial companies registered in B.C. (corporations, societies and cooperatives)</li><br>
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
                  <hr class="mb-5 mt-6 solid"/>
                  <h3 class="text-center mb-2">
                    When B.C. Based Businesses Must be in Active Status
                  </h3>
                  <p><b>New owners:</b> Must be active at the time of registration.</p>
                  <p>
                    If you are adding a B.C. based business as a new owner, the business <b>must be active on the
                    B.C Corporate Register at the time of the registration.</b>
                  </p><br>
                  <p><b>Existing owners:</b> Must be active at the time the bill of sale was signed.</p>
                  <p>
                    If you are including a business that is already an owner of the home, the business <b>must have
                    been active on the B.C Corporate Register at the time the bill of sale was signed.</b>
                  </p>
                  <hr class="mb-5 mt-6 solid" />
                  <h3 class="text-center mb-2">
                    My Business Isn't Listed
                  </h3>
                  <p>
                    The business look-up displays the list of all active businesses in B.C. If your business is listed,
                    select the business from the look-up list.
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
                </simple-help-toggle>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-text-field
                  filled
                  id="org-name"
                  ref="orgNameSearchField"
                  label="Find or enter the Full Legal Name of the Business or Organization"
                  v-model="searchValue"
                  persistent-hint
                  :rules="orgNameRules"
                  :clearable="showClear"
                  :disabled="disableNameFields"
                  :readonly="disableNameFields"
                  @click:clear="showClear = false"
                >
                  <template v-slot:append>
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
                  :searchValue="autoCompleteSearchValue"
                  :setAutoCompleteIsActive="autoCompleteIsActive"
                  v-click-outside="setCloseAutoComplete"
                  @search-value="setSearchValue"
                  @searching="loadingSearchResults = $event"
                  :showDropdown="$refs.orgNameSearchField && $refs.orgNameSearchField.isFocused"
                />
              </v-col>
            </v-row>
          </div>

          <label class="generic-label">
            Additional Name Information
            <v-tooltip
              v-if="disableNameFields"
              top
              content-class="top-tooltip pa-5"
              transition="fade-transition"
              data-test-id="suffix-tooltip"
            >
              <template v-slot:activator="{ on }">
                <v-icon class="mt-n1" color="primary" v-on="on">
                  mdi-information-outline
                </v-icon>
              </template>
              {{ disabledNameEditTooltip }}
            </v-tooltip>
          </label>
          <v-row>
            <v-col col="12">
              <v-tooltip
                v-if="owner.partyType === HomeOwnerPartyTypes.EXECUTOR"
                right
                content-class="right-tooltip pa-5"
                transition="fade-transition"
                data-test-id="suffix-tooltip"
              >
                <template v-slot:activator="{ on }">
                  <v-text-field
                    v-on="on"
                    id="suffix"
                    v-model="owner.suffix"
                    filled
                    label="Additional Name Information (Optional)"
                    data-test-id="suffix"
                    hint="Example: Additional legal names, Jr., Sr., Executor of the will of the deceased, etc."
                    persistent-hint
                    :rules="maxLength(70)"
                    @mousedown.prevent
                  />
                </template>
                  Executor of the will is based on deceased owner with Grant of Probate
                  with Will supporting document selected.
              </v-tooltip>
              <v-text-field
                  v-else
                  id="suffix"
                  v-model="owner.suffix"
                  filled
                  label="Additional Name Information (Optional)"
                  data-test-id="suffix"
                  hint="Example: Additional legal names, Jr., Sr., Executor of the will of the deceased, etc."
                  persistent-hint
                  :rules="maxLength(70)"
                  @mousedown.prevent
                />
            </v-col>
          </v-row>

          <label class="generic-label">
            Phone Number
          </label>
          <v-row>
            <v-col cols="6">
              <v-text-field
                id="phone-number"
                v-mask="'(NNN) NNN-NNNN'"
                v-model="displayPhone"
                filled
                :rules="phoneNumberRules"
                label="Phone Number (Optional)"
                data-test-id="phone-number"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                id="phone-ext"
                v-model="owner.phoneExtension"
                filled
                :rules="phoneExtensionRules"
                label="Extension (Optional)"
                data-test-id="phone-ext"
              />
            </v-col>
          </v-row>

          <label class="generic-label">
            Mailing Address
          </label>

          <base-address
            :editing="true"
            :schema="{ ...addressSchema }"
            v-model="owner.address"
            :triggerErrors="triggerAddressErrors"
            @valid="isAddressFormValid = $event"
            class="mt-2"
            hideAddressHint
          />

          <!-- Group Add / Edit -->
          <template v-if="!isTransferDueToDeath">
            <hr class="mt-3 mb-10" />
            <HomeOwnerGroups
              :groupId="isDefinedGroup ? ownersGroupId : null"
              :isAddingHomeOwner="isAddingHomeOwner"
              @setOwnerGroupId="ownerGroupId = $event"
              :fractionalData="groupFractionalData"
              :isMhrTransfer="isMhrTransfer"
            />
          </template>
          <template v-else>
            <p class="fs-16 mt-3"><strong>Note:</strong> Group Details cannot be changed in this type of transfer.</p>
          </template>
        </v-form>
        <v-row no-gutters class="pt-5">
          <v-col>
            <div class="form__row form__btns">
              <v-btn
                outlined
                color="error"
                class="remove-btn"
                :disabled="isAddingHomeOwner"
                :ripple="false"
                @click="remove()"
              >
                <span>{{ isCurrentOwner(owner) ? 'Delete' : 'Remove' }}</span>
              </v-btn>
              <v-btn
                color="primary"
                class="ml-auto"
                :ripple="false"
                large
                @click="done()"
                data-test-id="done-btn"
              >
                Done
              </v-btn>
              <v-btn
                :ripple="false"
                large
                color="primary"
                outlined
                @click="cancel()"
                data-test-id="cancel-btn"
              >
                Cancel
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from '@vue/composition-api'
import { useInputRules } from '@/composables/useInputRules'
import { useHomeOwners, useMhrValidations } from '@/composables/mhrRegistration'
import { BusinessSearchAutocomplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { focusOnFirstError, fromDisplayPhone } from '@/utils'
import { VueMaskDirective } from 'v-mask'

/* eslint-disable no-unused-vars */
import {
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces/mhr-registration-interfaces'
/* eslint-enable no-unused-vars */
import { SimpleHelpToggle } from '@/components/common'
import HomeOwnerGroups from './HomeOwnerGroups.vue'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { find } from 'lodash'
import { useTransferOwners } from '@/composables'
import { ActionTypes, HomeOwnerPartyTypes } from '@/enums'

interface FractionalOwnershipWithGroupIdIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: number
}

let DEFAULT_OWNER_ID = 1

export default defineComponent({
  name: 'AddEditHomeOwner',
  emits: ['remove', 'cancel'],
  components: {
    BaseAddress,
    SimpleHelpToggle,
    HomeOwnerGroups,
    BusinessSearchAutocomplete
  },
  directives: {
    mask: VueMaskDirective
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
    }
  },
  setup (props, context) {
    const {
      getMhrRegistrationHomeOwnerGroups,
      getMhrTransferHomeOwnerGroups,
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationHomeOwnerGroups',
      'getMhrTransferHomeOwnerGroups',
      'getMhrRegistrationValidationModel'
    ])
    const {
      setUnsavedChanges
    } = useActions<any>(['setUnsavedChanges'])

    // Composables
    const {
      MhrSectVal,
      getStepValidation,
      setValidation,
      MhrCompVal
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

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
      getTransferOrRegistrationHomeOwners
    } = useHomeOwners(props.isMhrTransfer)

    const {
      isCurrentOwner,
      isTransferDueToDeath,
      hasCurrentOwnerChanges,
      disableNameFields
    } = useTransferOwners()

    const addressSchema = PartyAddressSchema
    const addHomeOwnerForm = ref(null)

    const getTransferOrRegistrationHomeOwnerGroups = () =>
      props.isMhrTransfer ? getMhrTransferHomeOwnerGroups.value : getMhrRegistrationHomeOwnerGroups.value

    const defaultHomeOwner: MhrRegistrationHomeOwnerIF = {
      ...props.editHomeOwner,
      ownerId: props.editHomeOwner?.ownerId || getTransferOrRegistrationHomeOwners().length + 1 || (DEFAULT_OWNER_ID++),
      phoneNumber: props.editHomeOwner?.phoneNumber || '',
      phoneExtension: props.editHomeOwner?.phoneExtension || '',
      suffix: props.editHomeOwner?.suffix || '',
      address: {
        street: props.editHomeOwner?.address.street || '',
        streetAdditional: props.editHomeOwner?.address.streetAdditional || '',
        city: props.editHomeOwner?.address.city || '',
        region: props.editHomeOwner?.address.region || '',
        country: props.editHomeOwner?.address.country || '',
        postalCode: props.editHomeOwner?.address.postalCode || '',
        deliveryInstructions: props.editHomeOwner?.address.deliveryInstructions || ''
      },
      action: props.editHomeOwner?.action || null
    }

    if (props.isHomeOwnerPerson) {
      defaultHomeOwner.individualName = {
        first: props.editHomeOwner?.individualName.first || '',
        middle: props.editHomeOwner?.individualName.middle || '',
        last: props.editHomeOwner?.individualName.last || ''
      }
    } else {
      defaultHomeOwner.organizationName = props.editHomeOwner?.organizationName || ''
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
        interestNumerator: null,
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
      showGroups: showGroups,
      isPerson: props.isHomeOwnerPerson,
      isAddingHomeOwner: props.editHomeOwner == null,
      groupFractionalData: computed((): FractionalOwnershipWithGroupIdIF =>
        find(allFractionalData, { groupId: localState.ownerGroupId || 1 })),
      isHomeOwnerFormValid: false,
      isAddressFormValid: false,
      triggerAddressErrors: false,
      isHelpPanelOpen: false,
      displayPhone: props.editHomeOwner !== null ? props.editHomeOwner.phoneNumber : '',
      firsNameRules: customRules(required('Enter a first name'), maxLength(15)),
      lastNameRules: customRules(required('Enter a last name'), maxLength(25)),
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
      disabledNameEditTooltip: `Owner name’s cannot be changed here. Name change requests should be submitted
        separately, with the appropriate supporting documents, prior to completing this transfer. See Help with
        Ownership Transfer or Change for more information. `
    })

    const done = (): void => {
      // @ts-ignore - function exists
      context.refs.addHomeOwnerForm.validate()
      if (localState.isHomeOwnerFormValid && localState.isAddressFormValid) {
        setValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID, MhrCompVal.OWNERS_VALID, true)
        if (props.editHomeOwner) {
          hasCurrentOwnerChanges(localState.owner)
          const updatedOwner = isCurrentOwner(localState.owner) ? {
            ...localState.owner, action: hasCurrentOwnerChanges(localState.owner) ? ActionTypes.CHANGED : null
          }
            : localState.owner

          editHomeOwner(
            updatedOwner as MhrRegistrationHomeOwnerIF,
            localState.ownerGroupId || 1
          )
        } else {
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
        } else if (localState.group) {
          // this condition should only occur when trying to delete a group
          // clear out any fractional info
          delete localState.group.type
          delete localState.group.interest
          delete localState.group.interestNumerator
          delete localState.group.interestDenominator
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
    }
    const cancel = (): void => {
      localState.ownerGroupId = props.editHomeOwner?.groupId
      setValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID, MhrCompVal.OWNERS_VALID, true)
      context.emit('cancel')
    }

    /** Handle Phone changes and write to store. **/
    watch(
      () => localState.displayPhone,
      () => {
        localState.owner.phoneNumber = fromDisplayPhone(localState.displayPhone)
      }
    )

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      localState.owner.organizationName = searchValueTyped
      localState.showClear = true
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    watch(
      () => localState.searchValue,
      (val: string) => {
        if (val?.length >= 3) {
          localState.autoCompleteSearchValue = val
          // show autocomplete results when there is a searchValue
          localState.autoCompleteIsActive = val !== ''
        } else {
          localState.autoCompleteSearchValue = val
          localState.autoCompleteIsActive = false
        }
        localState.owner.organizationName = val
      }
    )

    return {
      done,
      remove,
      cancel,
      addHomeOwnerForm,
      maxLength,
      minLength,
      addressSchema,
      setSearchValue,
      setCloseAutoComplete,
      getStepValidation,
      MhrSectVal,
      isCurrentOwner,
      isTransferDueToDeath,
      disableNameFields,
      HomeOwnerPartyTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .theme--light.v-icon.mdi-close {
  color: $primary-blue !important;
}

.solid {
  border: 0;
  border-top: 0.25px solid $gray4 !important;
}

u {
    border-bottom: 1px dotted #000;
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

#org-name ::v-deep .hide-results {
  .v-autocomplete__content.v-menu__content {
    display: none !important;
  }
}

.selected-radio {
  background-color: white;
  ::v-deep .theme--light.v-label:not(.v-label--is-disabled), .theme--light.v-messages {
    color: $gray9 !important;
  }
}

::v-deep {
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
  }
}
</style>
