<template>
  <v-card flat class="py-6 px-8 rounded">
    <v-row id="mhr-home-add-person">
      <v-col cols="3">
        <label class="generic-label"> {{ getSideTitle }} </label>
      </v-col>
      <v-col cols="9">
        <v-form
          id="addHomeOwnerForm"
          ref="addHomeOwnerForm"
          v-model="isHomeOwnerFormValid"
        >
          <div v-if="isPerson">
            <label class="generic-label">
              Person's Name
            </label>
            <v-row>
              <v-col cols="4">
                <v-text-field
                  id="first-name"
                  v-model="owner.individualName.first"
                  filled
                  :rules="firsNameRules"
                  label="First Name"
                  data-test-id="first-name"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="middle-name"
                  v-model="owner.individualName.middle"
                  filled
                  label="Middle Name (Optional)"
                  :rules="maxLength(15)"
                  data-test-id="middle-name"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="last-name"
                  v-model="owner.individualName.last"
                  filled
                  :rules="lastNameRules"
                  label="Last Name"
                  data-test-id="last-name"
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
                  You can look-up a B.C. business by entering the name of the
                  business or the incorporation number (including Societies and
                  extra-provincial companies registered in B.C.). If the name of
                  the organization does not appear in the look-up, enter the
                  full legal name of the organization.
                </p>

                <simple-help-toggle
                  toggleButtonTitle="Help with Sole Proprietorships and Partnerships"
                >
                  <h3 class="text-center mb-2">
                    Help with Sole Proprietorships and Partnerships
                  </h3>
                  <p>
                    Registered owners of a manufactured home cannot be a sole
                    proprietorship, partnership or limited partnership. The home
                    must be registered in the name of the sole proprietor or
                    partner (person or business).
                  </p>
                </simple-help-toggle>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-text-field
                  filled
                  id="org-name"
                  label="Full Legal Name of Business or Organization"
                  v-model="owner.organizationName"
                  :rules="orgNameRules"
                />
                <!--
                  TODO: Finish this auto-complete
                  <auto-complete
                  :searchValue="autoCompleteSearchValue"
                  :setAutoCompleteIsActive="autoCompleteIsActive"
                  v-click-outside="setCloseAutoComplete"
                  @search-value="setSearchValue"
                >
                </auto-complete> -->
              </v-col>
            </v-row>
          </div>

          <label class="generic-label">
            Suffix
            <v-tooltip
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
              If necessary, type a suffix such as Junior or Senior, or a title
              indicating a role, such as Executor of the will of the deceased.
              This field can also be used to record further given names, if they
              are provided.
            </v-tooltip>
          </label>
          <v-row>
            <v-col col="12">
              <v-text-field
                id="suffix"
                v-model="owner.suffix"
                filled
                :rules="maxLength(70)"
                label="Suffix (Optional)"
                data-test-id="suffix"
                hint="Example: Executor, Jr., Sr."
                persistent-hint
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
                v-mask="'(###) ###-####'"
                v-model="owner.phoneNumber"
                filled
                :rules="phoneNumberRules"
                label="Phone Number"
                data-test-id="phone-number"
                validate-on-blur
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                id="phone-ext"
                v-model="owner.phoneExtension"
                filled
                :rules="maxLength(5, true)"
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
        </v-form>

        <v-row>
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
                Remove
              </v-btn>
              <v-btn
                color="primary"
                class="ml-auto"
                :ripple="false"
                large
                @click="done()"
              >
                Done
              </v-btn>
              <v-btn
                :ripple="false"
                large
                color="primary"
                outlined
                @click="cancel()"
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
import { defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { useInputRules } from '@/composables/useInputRules'
import { useHomeOwners } from '@/composables/mhrRegistration'

import { AutoComplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { focusOnFirstError } from '@/utils'
import { VueMaskDirective } from 'v-mask'

/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnersIF } from '@/interfaces/mhr-registration-interfaces'
import { SimpleHelpToggle } from '@/components/common'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'AddEditHomeOwner',
  components: {
    AutoComplete,
    BaseAddress,
    SimpleHelpToggle
  },
  directives: {
    mask: VueMaskDirective
  },
  props: {
    editHomeOwner: {
      type: Object as () => MhrRegistrationHomeOwnersIF,
      default: null
    },
    isHomeOwnerPerson: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { required, customRules, maxLength, minLength } = useInputRules()

    const { getSideTitle } = useHomeOwners(
      props.isHomeOwnerPerson,
      props.editHomeOwner == null
    )
    const addressSchema = PartyAddressSchema
    const addHomeOwnerForm = ref(null)

    const defaultHomeOwner: MhrRegistrationHomeOwnersIF = {
      phoneNumber: props.editHomeOwner?.phoneNumber || '',
      phoneExtension: props.editHomeOwner?.phoneExtension || null,
      suffix: props.editHomeOwner?.suffix || '',
      address: {
        street: props.editHomeOwner?.address.street || '',
        streetAdditional: props.editHomeOwner?.address.streetAdditional || '',
        city: props.editHomeOwner?.address.city || '',
        region: props.editHomeOwner?.address.region || '',
        country: props.editHomeOwner?.address.country || '',
        postalCode: props.editHomeOwner?.address.postalCode || '',
        deliveryInstructions:
          props.editHomeOwner?.address.deliveryInstructions || ''
      }
    }

    if (props.isHomeOwnerPerson) {
      defaultHomeOwner.individualName = {
        first: props.editHomeOwner?.individualName.first || '',
        middle: props.editHomeOwner?.individualName.middle || '',
        last: props.editHomeOwner?.individualName.last || ''
      }
    } else {
      defaultHomeOwner.organizationName =
        props.editHomeOwner?.organizationName || ''
    }

    const localState = reactive({
      owner: { ...defaultHomeOwner },
      isPerson: props.isHomeOwnerPerson,
      isAddingHomeOwner: props.editHomeOwner == null,
      isHomeOwnerFormValid: false,
      isAddressFormValid: false,
      triggerAddressErrors: false,
      isHelpPanelOpen: false,
      firsNameRules: customRules(required('Enter a first name'), maxLength(15)),
      lastNameRules: customRules(required('Enter a last name'), maxLength(25)),
      orgNameRules: customRules(
        required('Enter an organization name'),
        maxLength(150)
      ),
      phoneNumberRules: customRules(
        required('Enter a phone number'),
        minLength(14)
      )
    })

    const done = (): void => {
      // @ts-ignore - function exists
      context.refs.addHomeOwnerForm.validate()
      if (localState.isHomeOwnerFormValid && localState.isAddressFormValid) {
        context.emit('done', localState.owner)
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
      context.emit('cancel')
    }

    return {
      getSideTitle,
      done,
      remove,
      cancel,
      addHomeOwnerForm,
      maxLength,
      minLength,
      addressSchema,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped></style>
