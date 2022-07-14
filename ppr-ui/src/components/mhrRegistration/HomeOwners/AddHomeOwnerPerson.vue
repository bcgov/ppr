<template>
  <div>
    <v-card flat class="py-6 px-8 rounded">
      <v-row id="mhr-home-manufacturer-name">
        <v-col cols="3">
          <label class="generic-label">
            Add a Person
          </label>
        </v-col>
        <v-col cols="9">
          <label class="generic-label" for="manufacturer-name">
            Person's Name
          </label>
          <v-row>
            <v-col cols="4">
              <v-text-field
                id="first-name"
                v-model="individualName.first"
                filled
                :rules="maxLength(15)"
                label="First Name"
                data-test-id="first-name"
              />
            </v-col>
            <v-col cols="4">
              <v-text-field
                id="middle-name"
                v-model="individualName.middle"
                filled
                :rules="maxLength(15)"
                label="Middle Name"
                data-test-id="first-name"
            /></v-col>
            <v-col cols="4">
              <v-text-field
                id="last-name"
                v-model="individualName.last"
                filled
                :rules="maxLength(15)"
                label="Last Name"
                data-test-id="first-name"
            /></v-col>
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
                :rules="maxLength(15)"
                label="Phone Number"
                data-test-id="phone-number"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                id="phone-ext"
                v-model="phoneExtension"
                filled
                :rules="maxLength(15)"
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
            class="mt-2"
          />

          <v-row>
            <v-col cols="6">
              <v-btn
                outlined
                color="error"
                class="remove-btn"
                :disabled="true"
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
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useInputRules } from '@/composables/useInputRules'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
/* eslint-disable no-unused-vars */
import { MhrRegistrationHomeOwnersIF } from '@/interfaces/mhr-registration-interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'AddHomeOwnerPerson',
  components: {
    BaseAddress
  },
  setup (props, context) {
    const { maxLength } = useInputRules()
    const addressSchema = PartyAddressSchema

    const defaultPersonOwner: MhrRegistrationHomeOwnersIF = {
      individualName: {
        first: '',
        middle: '',
        last: ''
      },
      phoneNumber: null,
      phoneExtension: null
    }

    const localState = reactive({
      ...defaultPersonOwner
    })

    const done = (): void => {
      context.emit('done', localState)
      cancel()
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
      maxLength,
      addressSchema,
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
