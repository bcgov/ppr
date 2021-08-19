<template>
  <div id="edit-party" class="white pa-6">
    <secured-party-dialog
      attach="#app"
      :defaultDialog="toggleDialog"
      :defaultParty="currentSecuredParty"
      :defaultResults="dialogResults"
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
            <span v-if="activeIndex === -1" class="">Add</span>
            <span v-else>Edit</span>
            Secured Party
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
                  v-model="partyBusiness"
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
                    value="I"
                    id="party-individual"
                  >
                  </v-radio>

                  <v-radio
                    :class="['business-radio', $style['party-radio-business']]"
                    label="Business"
                    value="B"
                    id="party-business"
                  >
                  </v-radio>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-divider class="pb-4" />
            <v-row no-gutters v-if="isPartyType">
              <v-col cols="12">
                <v-row v-if="partyBusiness === 'B'" no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Business Name</label>
                  </v-col>
                </v-row>
                <v-row v-else no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Person's Name</label>
                  </v-col>
                </v-row>
                <v-row v-if="partyBusiness === 'B'" no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-name-party"
                      label="Business Legal Name"
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
                      persistent-hint
                      @blur="onBlur('first')"
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
                      v-model="currentSecuredParty.personName.middle"
                      persistent-hint
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Last Name"
                      id="txt-last-party"
                      v-model="currentSecuredParty.personName.last"
                      persistent-hint
                      @blur="onBlur('last')"
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
                      label="Email Address (Optional)"
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
                  id="address-secured-party"
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
                    :disabled="activeIndex === -1"
                    @click="removeParty()"
                    id="remove-btn-party"
                    >Remove
                  </v-btn>

                  <v-btn
                    large
                    id="done-btn-party"
                    class="ml-auto"
                    color="primary"
                    :disabled="!isPartyType"
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
import {
  defineComponent,
  onMounted,
  reactive,
  toRefs,
  computed,
  watch
} from '@vue/composition-api'
import BaseAddress from '@/composables/address/BaseAddress.vue'
import { formatAddress } from '@/composables/address/factories'
import { useSecuredPartyValidation } from './composables/useSecuredPartyValidation'
import { useSecuredParty } from './composables/useSecuredParty'
import { SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import AutoComplete from '@/components/search/AutoComplete.vue'
import SecuredPartyDialog from '@/components/dialogs/SecuredPartyDialog.vue'
import { partyCodeSearch } from '@/utils'

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
    }
  },
  emits: ['addEditParty', 'resetEvent'],
  setup (props, context) {
    const {
      currentSecuredParty,
      currentIsBusiness,
      getSecuredParty,
      resetFormAndData,
      removeSecuredParty,
      addEditSecuredParty,
      updateAddress,
      addressSchema
    } = useSecuredParty(props, context)

    const {
      errors,
      updateValidity,
      validateSecuredPartyForm,
      validateInput
    } = useSecuredPartyValidation()

    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      partyBusiness: '',
      searchValue: '',
      hideDetails: false,
      toggleDialog: false,
      dialogResults: [],
      isPartyType: computed((): boolean => {
        if (localState.partyBusiness === '') {
          return false
        }
        return true
      }),
      showAllAddressErrors: false
    })

    const showDialog = () => {
      // eslint-disable-line no-unused-vars
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
      if (
        validateSecuredPartyForm(
          localState.partyBusiness,
          currentSecuredParty
        ) === true
      ) {
        if (props.activeIndex === -1) {
          if (currentSecuredParty.value.businessName) {
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
        }

        addEditSecuredParty()
      } else {
        localState.showAllAddressErrors = true
      }
    }

    const getPartyBusiness = () => {
      const businessValue = currentIsBusiness.value
      if (businessValue !== null) {
        localState.partyBusiness = 'I'
        if (businessValue) {
          localState.partyBusiness = 'B'
        }
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
      () => localState.partyBusiness,
      currentValue => {
        if (currentValue === 'I') {
          currentSecuredParty.value.businessName = ''
          localState.searchValue = ''
        } else {
          currentSecuredParty.value.personName.first = ''
          currentSecuredParty.value.personName.middle = ''
          currentSecuredParty.value.personName.last = ''
        }
      }
    )

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
      getSecuredParty()
      setSearchValue(currentSecuredParty.value.businessName)
      getPartyBusiness()
    })

    return {
      currentSecuredParty,
      currentIsBusiness,
      resetFormAndData,
      removeSecuredParty,
      onSubmitForm,
      onBlur,
      addressSchema,
      updateAddress,
      updateValidity,
      setSearchValue,
      setHideDetails,
      setCloseAutoComplete,
      errors,
      closeAndReset,
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
