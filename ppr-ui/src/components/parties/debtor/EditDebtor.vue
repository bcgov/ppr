<template>
  <div
    id="edit-debtor"
    class="bg-white pa-6"
    :class="{ 'border-error-left': showErrorBar }"
  >
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
          <label
            class="add-debtor-header generic-label ml"
            :class="{ 'error-text': invalidSection }"
          >
            <span v-if="activeIndex === -1">Add</span>
            <span v-else>
              <span
                v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                  && (!currentDebtor.action || currentDebtor.action !== ActionTypes.ADDED)"
              >
                Amend
              </span>
              <span v-else>Edit</span>
            </span>
            <span v-if="currentIsBusiness"> a Business<br>Debtor</span>
            <span v-else> an Individual<br>Debtor</span>
          </label>
        </v-col>
        <v-col cols="9">
          <v-form
            ref="debtorForm"
            class="debtor-form"
          >
            <v-row
              v-if="currentIsBusiness"
              no-gutters
              class="pb-4"
            >
              <v-col>
                <label class="generic-label">Business Legal Name</label>
              </v-col>
            </v-row>
            <v-row
              v-else
              no-gutters
              class="pb-4"
            >
              <v-col>
                <label class="generic-label">Person's Legal Name</label>
              </v-col>
            </v-row>
            <v-row
              v-if="currentIsBusiness"
              no-gutters
            >
              <v-col>
                <v-text-field
                  id="txt-name-debtor"
                  ref="debtorNameSearchField"
                  v-model="searchValue"
                  variant="filled"
                  color="primary"
                  label="Find or enter the Full Legal Name of the Business"
                  :error-messages="
                    errors.businessName.message
                      ? errors.businessName.message
                      : ''
                  "
                  persistent-hint
                  persistent-clear
                  :clearable="showClear"
                  :clear-icon="'mdi-close'"
                  @click:clear="showClear = false"
                  @keyup="validateNameField()"
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
                  :show-dropdown="$refs.debtorNameSearchField && $refs.debtorNameSearchField.isFocused"
                  is-p-p-r
                  @search-value="setSearchValue"
                  @searching="loadingSearchResults = $event"
                />
              </v-col>
            </v-row>
            <v-row
              v-else
              no-gutters
            >
              <v-col
                cols="4"
                class="pr-4"
              >
                <v-text-field
                  id="txt-first-debtor"
                  v-model="currentDebtor.personName.first"
                  variant="filled"
                  color="primary"
                  label="First Name"
                  persistent-hint
                  :error-messages="
                    errors.first.message ? errors.first.message : ''
                  "
                  @keyup="validateNameField()"
                />
              </v-col>
              <v-col
                cols="4"
                class="pr-4"
              >
                <v-text-field
                  id="txt-middle-debtor"
                  v-model="currentDebtor.personName.middle"
                  variant="filled"
                  color="primary"
                  label="Middle Name"
                  hint="Required if person has middle name"
                  persistent-hint
                  :error-messages="
                    errors.middle.message ? errors.middle.message : ''
                  "
                  @keyup="validateNameField()"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="txt-last-debtor"
                  v-model="currentDebtor.personName.last"
                  variant="filled"
                  color="primary"
                  label="Last Name"
                  persistent-hint
                  :error-messages="
                    errors.last.message ? errors.last.message : ''
                  "
                  @keyup="validateNameField()"
                />
              </v-col>
            </v-row>
            <v-row
              v-if="!currentIsBusiness"
              class="pb-4"
              no-gutters
            >
              <v-col>
                <label class="generic-label">Birthdate</label> (Optional)
              </v-col>
            </v-row>
            <v-row
              v-if="!currentIsBusiness"
              no-gutters
            >
              <v-col
                cols="4"
                class="pr-4"
              >
                <v-autocomplete
                  id="txt-month"
                  v-model="month"
                  auto-select-first
                  :items="months"
                  variant="filled"
                  color="primary"
                  clearable
                  label="Month"
                  :error-messages="
                    errors.month.message ? errors.month.message : ''
                  "
                  persistent-hint
                  return-object
                  @keyup="validateBirthdateIfAlreadyValidated"
                  @blur="validateBirthdateIfAlreadyValidated"
                />
              </v-col>
              <v-col
                cols="4"
                class="pr-4"
              >
                <v-text-field
                  id="txt-day"
                  v-model="day"
                  variant="filled"
                  color="primary"
                  label="Day"
                  :error-messages="errors.day.message ? errors.day.message : ''"
                  persistent-hint
                  @keyup="validateBirthdateIfAlreadyValidated"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="txt-year"
                  v-model="year"
                  variant="filled"
                  color="primary"
                  label="Year"
                  :error-messages="
                    errors.year.message ? errors.year.message : ''
                  "
                  persistent-hint
                  @keyup="validateBirthdateIfAlreadyValidated"
                />
              </v-col>
            </v-row>
            <v-row
              no-gutters
              class="pb-4"
            >
              <v-col>
                <label class="generic-label">Address</label>
              </v-col>
            </v-row>
            <base-address
              id="address-debtor"
              ref="regMailingAddress"
              :value="currentDebtor.address"
              :editing="true"
              :schema="{ ...addressSchema }"
              :trigger-errors="showAllAddressErrors"
              @valid="updateValidity($event)"
              @update-address="currentDebtor.address = $event"
            />

            <v-row>
              <v-col>
                <div class="form__row form__btns">
                  <v-btn
                    id="remove-btn-debtor"
                    size="large"
                    variant="outlined"
                    color="error"
                    :disabled="activeIndex === -1"
                    class="remove-btn float-left"
                    @click="removeDebtor()"
                  >
                    <span
                      v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                        && currentIndex !== -1
                        && (!currentDebtor.action || currentDebtor.action !== ActionTypes.ADDED)"
                    >
                      Delete
                    </span>
                    <span v-else>Remove</span>
                  </v-btn>

                  <span class="float-right">
                    <v-btn
                      id="done-btn-debtor"
                      size="large"
                      class="ml-auto mr-2"
                      color="primary"
                      @click="onSubmitForm()"
                    >
                      Done
                    </v-btn>

                    <v-btn
                      id="cancel-btn-debtor"
                      size="large"
                      variant="outlined"
                      color="primary"
                      @click="resetFormAndData(true)"
                    >
                      Cancel
                    </v-btn>
                  </span>
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
  watch,
  computed,
  reactive,
  toRefs
} from 'vue'
import { BusinessSearchAutocomplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { useDebtor, useDebtorValidation } from '@/composables/parties'
import { formatAddress } from '@/composables/address/factories'
import { useValidation } from '@/utils/validators/use-validation'

export default defineComponent({
  name: 'EditDebtor',
  components: {
    BaseAddress,
    BusinessSearchAutocomplete
  },
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    isBusiness: {
      type: Boolean,
      default: true
    },
    invalidSection: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditDebtor', 'resetEvent'],
  setup (props, context) {
    const {
      currentDebtor,
      year,
      day,
      monthValue,
      months,
      currentIsBusiness,
      getDebtor,
      getMonthObject,
      resetFormAndData,
      removeDebtor,
      addDebtor,
      addressSchema,
      RegistrationFlowType,
      registrationFlowType,
      ActionTypes
    } = useDebtor(props, context)

    const {
      errors,
      updateValidity,
      validateDebtorForm,
      validateBirthdate,
      validateEmail
    } = useDebtorValidation()

    const {
      validateFirstName,
      validateMiddleName,
      validateLastName,
      validateBusinessName
    } = useValidation()

    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      searchValue: '',
      loadingSearchResults: false,
      showClear: false,
      month: null,
      showAllAddressErrors: false,
      currentIndex: computed((): number => {
        return props.activeIndex
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    const onSubmitForm = async () => {
      currentDebtor.value.address = formatAddress(currentDebtor.value.address)
      if (
        validateDebtorForm(
          currentIsBusiness,
          currentDebtor,
          year,
          monthValue,
          day
        ) === true
      ) {
        addDebtor()
      } else {
        // trigger show validation
        localState.showAllAddressErrors = !localState.showAllAddressErrors
      }
    }

    const validateNameField = () => {
      if (!errors.value.first.succeeded || currentDebtor.value.personName?.first.length > 50) {
        validateFirstName(currentDebtor.value, errors.value)
      }
      if (!errors.value.last.succeeded || currentDebtor.value.personName?.last.length > 50) {
        validateLastName(currentDebtor.value, errors.value)
      }
      if (!errors.value.middle.succeeded || currentDebtor.value.personName?.middle.length > 50) {
        validateMiddleName(currentDebtor.value, errors.value)
      }
      if (!errors.value.businessName?.succeeded || currentDebtor.value.businessName?.length > 150) {
        validateBusinessName(currentDebtor.value, errors.value)
      }
    }

    const validateBirthdateIfAlreadyValidated = () => {
      if (
        !errors.value.year.succeeded ||
        !errors.value.month.succeeded ||
        !errors.value.day.succeeded
      ) {
        validateBirthdate(year.value, monthValue.value, day.value)
      }
    }

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      currentDebtor.value.businessName = searchValueTyped
      localState.showClear = true
      validateNameField()
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    onMounted(() => {
      getDebtor()
      currentDebtor.value.businessName && setSearchValue(currentDebtor.value.businessName)
      localState.month = getMonthObject() || null
    })

    watch(
      () => localState.searchValue,
      (val: string) => {
        localState.autoCompleteSearchValue = val

        // only open if debtor name changed
        if (currentDebtor.value.businessName !== val) {
          // show autocomplete results when there is a searchValue
          currentDebtor.value.businessName = val
          localState.autoCompleteIsActive = val !== ''
        }
      }
    )

    watch(
      () => localState.month,
      currentValue => {
        monthValue.value = currentValue?.value || 0
      }
    )

    return {
      currentDebtor,
      year,
      day,
      months,
      currentIsBusiness,
      resetFormAndData,
      removeDebtor,
      onSubmitForm,
      validateBirthdateIfAlreadyValidated,
      setSearchValue,
      setCloseAutoComplete,
      addressSchema,
      updateValidity,
      validateEmail,
      validateNameField,
      errors,
      RegistrationFlowType,
      registrationFlowType,
      ActionTypes,
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
</style>
