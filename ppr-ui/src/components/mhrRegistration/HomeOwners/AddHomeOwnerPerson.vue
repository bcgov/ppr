<template>
  <div>
    <v-card flat class="py-6 px-8 rounded">
      <v-row id="mhr-home-manufacturer-name">
        <v-col cols="3">
          <label
            class="generic-label"
            v-text="isAddingHomeOwner ? 'Add a Person' : 'Edit Person'"
          >
          </label>
        </v-col>
        <v-col cols="9">
          <v-form
            id="addPersonForm"
            ref="addPersonForm"
            v-model="isAddPersonFormValid"
          >
            <label class="generic-label" for="manufacturer-name">
              Person's Name
            </label>
            <v-row>
              <v-col cols="4">
                <v-text-field
                  id="first-name"
                  v-model="individualName.first"
                  filled
                  :rules="firsNameRules"
                  label="First Name"
                  data-test-id="first-name"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="middle-name"
                  v-model="individualName.middle"
                  filled
                  label="Middle Name"
                  data-test-id="middle-name"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  id="last-name"
                  v-model="individualName.last"
                  filled
                  :rules="lastNameRules"
                  label="Last Name"
                  data-test-id="last-name"
                />
              </v-col>
            </v-row>

            <label class="generic-label" for="manufacturer-name">
              Phone Number
            </label>
            <v-row>
              <v-col cols="6">
                <v-text-field
                  id="phone-number"
                  v-model="phoneNumber"
                  filled
                  :rules="phoneNumberRules"
                  label="Phone Number"
                  data-test-id="phone-number"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  id="phone-ext"
                  v-model="phoneExtension"
                  filled
                  :rules="maxLength(5, true)"
                  label="Extension (Optional)"
                  data-test-id="phone-ext"
                />
              </v-col>
            </v-row>

            <label class="generic-label" for="manufacturer-name">
              Mailing Address
            </label>

            <base-address
              :editing="true"
              :schema="{ ...addressSchema }"
              v-model="address"
              :triggerErrors="triggerAddressErrors"
              @valid="isAddressFormValid = $event"
              class="mt-2"
            />
          </v-form>

          <v-row>
            <v-col cols="6">
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
            </v-col>
            <v-col cols="3">
              <v-btn :ripple="false" width="100%" @click="cancel()">
                Cancel
              </v-btn>
            </v-col>
            <v-col cols="3">
              <v-btn
                color="primary"
                :ripple="false"
                width="100%"
                @click="done()"
              >
                Done
              </v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { useInputRules } from '@/composables/useInputRules'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { focusOnFirstError } from '@/utils'
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnersIF } from '@/interfaces/mhr-registration-interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'AddHomeOwnerPerson',
  components: {
    BaseAddress
  },
  props: {
    editHomeOwner: {
      type: Object as () => MhrRegistrationHomeOwnersIF,
      default: null
    }
  },
  setup (props, context) {
    const { required, customRules, maxLength } = useInputRules()
    const addressSchema = PartyAddressSchema
    const addPersonForm = ref(null)

    const defaultPersonOwner: MhrRegistrationHomeOwnersIF = {
      individualName: {
        first: props.editHomeOwner?.individualName.first || '',
        middle: props.editHomeOwner?.individualName.middle || '',
        last: props.editHomeOwner?.individualName.last || ''
      },
      phoneNumber: props.editHomeOwner?.phoneNumber || null,
      phoneExtension: props.editHomeOwner?.phoneExtension || null,
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

    const localState = reactive({
      ...defaultPersonOwner,
      isAddingHomeOwner: props.editHomeOwner == null,
      isAddPersonFormValid: false,
      isAddressFormValid: false,
      triggerAddressErrors: false,
      firsNameRules: customRules(required('Enter a first name'), maxLength(15)),
      lastNameRules: customRules(required('Enter a last name'), maxLength(25)),
      phoneNumberRules: customRules(
        required('Enter a phone number'),
        maxLength(10, true)
      )
    })

    const done = (): void => {
      // @ts-ignore - function exists
      context.refs.addPersonForm.validate()
      if (localState.isAddPersonFormValid && localState.isAddressFormValid) {
        context.emit('done', localState)
        cancel()
      } else {
        localState.triggerAddressErrors = !localState.triggerAddressErrors
        focusOnFirstError('addPersonForm')
      }
    }
    const remove = (): void => {
      context.emit('remove')
    }
    const cancel = (): void => {
      context.emit('cancel')
    }

    return {
      done,
      remove,
      cancel,
      addPersonForm,
      maxLength,
      addressSchema,
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
