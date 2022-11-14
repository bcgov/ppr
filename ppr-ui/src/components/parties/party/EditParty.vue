<template>
  <div id="edit-party" class="white pa-6" :class="{ 'border-error-left': showErrorBar }">
    <secured-party-dialog
      attach="#app"
      :isDuplicate="foundDuplicate"
      :defaultDialog="toggleDialog"
      :defaultParty="currentSecuredParty"
      :defaultResults="dialogResults"
      :defaultIsRegisteringParty="isRegisteringParty"
      @emitResetClose="closeAndReset"
      @emitClose="toggleDialog = false"
    />
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
          <label
            class="add-party-header generic-label ml"
            :class="{ 'error-text': invalidSection }"
          >
            <span v-if="activeIndex === -1 && (!currentSecuredParty || !currentSecuredParty.action)" class="">Add</span>
            <span v-else>
              <span v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                        && (!currentSecuredParty.action || currentSecuredParty.action !== ActionTypes.ADDED)">
                Amend
              </span>
              <span v-else>Edit</span>
            </span>
            <span v-if="isRegisteringParty"> Registering</span><span v-else> Secured</span> Party
          </label>
        </v-col>
        <v-col cols="9">
          <v-form
            ref="partyForm"
            class="party-form"
            v-on:submit.prevent="addParty"
          >
            <v-row class="pb-6" no-gutters>
              <v-col cols="12">
                <v-radio-group
                  v-model="partyType"
                  class="mt-0"
                  row
                  hide-details="true"
                >
                  <v-radio
                    :class="[
                      'individual-radio',
                      $style['party-radio-individual'],
                    ]"
                    label="Individual Person"
                    :value=SecuredPartyTypes.INDIVIDUAL
                    id="party-individual"
                  >
                  </v-radio>

                  <v-radio
                    :class="['business-radio', $style['party-radio-business']]"
                    label="Business"
                    :value=SecuredPartyTypes.BUSINESS
                    id="party-business"
                  >
                  </v-radio>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-divider class="pb-4" />
            <v-row no-gutters v-if="partyType !== SecuredPartyTypes.NONE">
              <v-col cols="12">
                <v-row v-if="partyType === SecuredPartyTypes.BUSINESS" no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Business Name</label>
                  </v-col>
                </v-row>
                <v-row v-else no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Person's Name</label>
                  </v-col>
                </v-row>
                <v-row v-if="partyType === SecuredPartyTypes.BUSINESS" no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-name-party"
                      label="Business Legal Name"
                      @keyup="validateNameField()"
                      v-model="searchValue"
                      :error-messages="
                        errors.businessName.message
                          ? errors.businessName.message
                          : ''
                      "
                      persistent-hint
                    />
                    <auto-complete
                      :searchValue="autoCompleteSearchValue"
                      :setAutoCompleteIsActive="autoCompleteIsActive"
                      v-click-outside="setCloseAutoComplete"
                      @search-value="setSearchValue"
                      @hide-details="setHideDetails"
                    >
                    </auto-complete>
                  </v-col>
                </v-row>
                <v-row v-else no-gutters>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="First Name"
                      id="txt-first-party"
                      v-model="currentSecuredParty.personName.first"
                      @keyup="validateNameField()"
                      persistent-hint
                      :error-messages="
                        errors.first.message ? errors.first.message : ''
                      "
                    />
                  </v-col>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="Middle Name (Optional)"
                      id="txt-middle-party"
                      @keyup="validateNameField()"
                      v-model="currentSecuredParty.personName.middle"
                      persistent-hint
                      :error-messages="
                      errors.middle.message ? errors.middle.message : ''
                      "
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Last Name"
                      id="txt-last-party"
                      v-model="currentSecuredParty.personName.last"
                      persistent-hint
                      @keyup="validateNameField()"
                      :error-messages="
                        errors.last.message ? errors.last.message : ''
                      "
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Email Address</label>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-email-party"
                      :label="isRegisteringParty? 'Email Address' : 'Email Address (Optional)'"
                      v-model="currentSecuredParty.emailAddress"
                      :error-messages="
                        errors.emailAddress.message
                          ? errors.emailAddress.message
                          : ''
                      "
                      @blur="onBlur('emailAddress')"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Address</label>
                  </v-col>
                </v-row>
                <base-address
                  ref="regMailingAddress"
                  v-model="currentSecuredParty.address"
                  :editing="true"
                  :schema="{ ...addressSchema }"
                  :triggerErrors="showAllAddressErrors"
                  @valid="updateValidity($event)"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <div class="form__row form__btns">
                  <v-btn
                    large
                    outlined
                    color="error"
                    v-if="!isRegisteringParty"
                    :disabled="activeIndex === -1"
                    @click="removeSecuredParty()"
                    id="remove-btn-party"
                    class="remove-btn"
                    >
                    <span v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                              && currentIndex !== -1
                              && (!currentSecuredParty.action || currentSecuredParty.action !== ActionTypes.ADDED)">
                      Delete
                    </span>
                    <span v-else>Remove</span>
                  </v-btn>

                  <v-btn
                    large
                    id="done-btn-party"
                    class="ml-auto"
                    color="primary"
                    :disabled="partyType === SecuredPartyTypes.NONE"
                    @click="onSubmitForm()"
                  >
                    Done
                  </v-btn>

                  <v-btn
                    id="cancel-btn-party"
                    large
                    outlined
                    color="primary"
                    @click="resetFormAndData(true)"
                  >
                    Cancel
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </v-form>
        </v-col>
      </v-row>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
// external libraries
import {
  defineComponent,
  onMounted,
  reactive,
  toRefs,
  computed,
  watch
} from '@vue/composition-api'
// local components
import { SecuredPartyDialog } from '@/components/dialogs'
import { AutoComplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { SecuredPartyTypes } from '@/enums'
// local helpers / types / etc.
import { useSecuredParty } from '@/components/parties/composables/useSecuredParty'
import { useSecuredPartyValidation } from '@/components/parties/composables/useSecuredPartyValidation'
import { formatAddress } from '@/composables/address/factories'
import { SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { partyCodeSearch } from '@/utils'
import { useValidation } from '@/utils/validators/use-validation'

export default defineComponent({
  components: {
    BaseAddress,
    AutoComplete,
    SecuredPartyDialog
  },
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    invalidSection: {
      type: Boolean,
      default: false
    },
    setIsRegisteringParty: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditParty', 'resetEvent'],
  setup (props, context) {
    const {
      currentSecuredParty,
      currentIsBusiness,
      partyType,
      getSecuredParty,
      resetFormAndData,
      removeSecuredParty,
      addEditSecuredParty,
      registrationFlowType,
      RegistrationFlowType,
      updateAddress,
      ActionTypes,
      setRegisteringParty,
      addressSchema,
      hasMatchingSecuredParty
    } = useSecuredParty(props, context)

    const {
      errors,
      updateValidity,
      validateSecuredPartyForm,
      validateInput
    } = useSecuredPartyValidation()

    const {
      validateFirstName,
      validateMiddleName,
      validateLastName,
      validateBusinessName
    } = useValidation()

    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      foundDuplicate: false,
      searchValue: '',
      hideDetails: false,
      toggleDialog: false,
      dialogResults: [],
      showAllAddressErrors: false,
      currentIndex: computed((): number => {
        return props.activeIndex
      }),
      isRegisteringParty: computed((): boolean => {
        return props.setIsRegisteringParty
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    const showDialog = () => {
      localState.toggleDialog = true
    }

    const onBlur = fieldname => {
      validateInput(fieldname, currentSecuredParty.value[fieldname])
    }

    const closeAndReset = () => {
      localState.toggleDialog = false
      resetFormAndData(true)
    }

    const onSubmitForm = async () => {
      currentSecuredParty.value.address = formatAddress(currentSecuredParty.value.address)
      // check for duplicate
      if (hasMatchingSecuredParty(currentSecuredParty.value)) {
        // trigger duplicate secured party dialog
        localState.foundDuplicate = true
        showDialog()
        return
      }
      if (
        validateSecuredPartyForm(
          partyType.value,
          currentSecuredParty,
          localState.isRegisteringParty
        ) === true
      ) {
        if (partyType.value === SecuredPartyTypes.INDIVIDUAL) {
          currentSecuredParty.value.businessName = ''
          // localState.searchValue = ''
        } else {
          currentSecuredParty.value.personName.first = ''
          currentSecuredParty.value.personName.middle = ''
          currentSecuredParty.value.personName.last = ''
        }

        if (currentSecuredParty.value.businessName && partyType.value === SecuredPartyTypes.BUSINESS) {
          // go to the service and see if there are similar secured parties
          const response: [SearchPartyIF] = await partyCodeSearch(
            currentSecuredParty.value.businessName, false
          )
          // check if any results
          if (response?.length > 0) {
            // show secured party selection popup
            showDialog()
            localState.dialogResults = response?.slice(0, 50)
            return
          }
        }

        if (localState.isRegisteringParty) {
          setRegisteringParty(currentSecuredParty.value)
          context.emit('resetEvent')
        } else {
          addEditSecuredParty()
        }
      } else {
        // trigger show validation
        localState.showAllAddressErrors = !localState.showAllAddressErrors
      }
    }

    const validateNameField = () => {
      if (!errors.value.first.succeeded || currentSecuredParty.value.personName.first.length > 50) {
        validateFirstName(currentSecuredParty.value, errors.value)
      }
      if (!errors.value.middle.succeeded || currentSecuredParty.value.personName.middle.length > 50) {
        validateMiddleName(currentSecuredParty.value, errors.value)
      }
      if (!errors.value.last.succeeded || currentSecuredParty.value.personName.last.length > 50) {
        validateLastName(currentSecuredParty.value, errors.value)
      }
      if (!errors.value.businessName.succeeded || currentSecuredParty.value.businessName.length > 150) {
        validateBusinessName(currentSecuredParty.value, errors.value)
      }
    }

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      currentSecuredParty.value.businessName = searchValueTyped
    }

    const setHideDetails = (hideDetails: boolean) => {
      localState.hideDetails = hideDetails
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    watch(
      () => localState.searchValue,
      (val: string) => {
        localState.autoCompleteSearchValue = val
        // show autocomplete results when there is a searchValue
        localState.autoCompleteIsActive = val !== ''
        currentSecuredParty.value.businessName = val
      }
    )

    onMounted(() => {
      getSecuredParty(localState.isRegisteringParty)
      setSearchValue(currentSecuredParty.value.businessName)
    })

    return {
      currentSecuredParty,
      currentIsBusiness,
      partyType,
      SecuredPartyTypes,
      resetFormAndData,
      removeSecuredParty,
      onSubmitForm,
      onBlur,
      addressSchema,
      updateAddress,
      updateValidity,
      validateNameField,
      setSearchValue,
      setHideDetails,
      setCloseAutoComplete,
      errors,
      closeAndReset,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.party-radio-business {
  width: 50%;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
  margin-right: 0px !important;
}
.party-radio-individual {
  width: 47%;
  margin-right: 20px !important;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
}
</style>
