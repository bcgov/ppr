<template>
  <v-card flat rounded id="submitting-party" class="mt-8 pa-8 pr-6">
    <v-row no-gutters>
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': false}">Add Submitting Party</label>
      </v-col>
      <v-col cols="12" sm="10" class="px-1">
        <v-radio-group
          id="submitting-party-type-options"
          v-model="submittingPartyType"
          class="mt-0 pr-1" row
          hide-details="true"
        >
          <v-radio
            id="person-option"
            class="person-radio"
            label="Individual Person"
            active-class="selected-radio"
            :value="SubmittingPartyTypes.PERSON"
          />
          <v-radio
            id="business-option"
            class="business-radio"
            label="Business"
            active-class="selected-radio"
            :value="SubmittingPartyTypes.BUSINESS"
          />
        </v-radio-group>

        <v-divider class="my-9 ml-0 mr-2" />

        <v-form id="submitting-party-form" ref="submittingPartyForm" v-model="submittingPartyValid">
          <!-- Person Name Input -->
          <template v-if="isPersonOption">
            <label class="generic-label" for="first-name">Person's Name</label>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  id="first-name"
                  class="pt-4 pr-2"
                  label="First Name"
                  v-model="registeringParty.personName.first"
                  :rules="[]"
                />
              </v-col>
              <v-col>
                <v-text-field
                  filled
                  id="middle-name"
                  class="pt-4 px-2"
                  label="Middle Name (Optional)"
                  v-model="registeringParty.personName.middle"
                  :rules="[]"
                />
              </v-col>
              <v-col>
                <v-text-field
                  filled
                  id="last-name"
                  class="pt-4 px-2"
                  label="Last Name"
                  v-model="registeringParty.personName.last"
                  :rules="[]"
                />
              </v-col>
            </v-row>
          </template>

          <!-- Business Name Input -->
          <template v-if="isBusinessOption">
            <label class="generic-label" for="business-name">Business Name</label>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  id="business-name"
                  class="pt-4 pr-2"
                  label="Business Name"
                  v-model="registeringParty.businessName"
                  :rules="[]"
                />
              </v-col>
            </v-row>
          </template>

          <!-- Email Address -->
          <label class="generic-label" for="submitting-party-email">Email Address</label>
          <v-text-field
            filled
            id="submitting-party-email"
            class="pt-4 pr-2"
            label="Email Address"
            v-model="registeringParty.emailAddress"
            :rules="[]"
          />

          <!-- Phone Number -->
          <label class="generic-label" for="submitting-party-phone">Phone Number</label>
          <v-row no-gutters>
            <v-col>
              <v-text-field
                filled
                id="submitting-party-phone"
                class="pt-4 pr-3"
                label="Phone Number"
                v-model="registeringParty.phoneNumber"
                :rules="[]"
              />
            </v-col>
            <v-col>
              <v-text-field
                filled
                id="submitting-party-phone-ext"
                class="pt-4 px-2"
                label="Extension (Optional)"
                v-model="registeringParty.phoneExtension"
                :rules="[]"
              />
            </v-col>
          </v-row>

          <!-- Mailing Address -->
          <article class="pr-1">
            <label class="generic-label" for="submitting-party-address">Mailing Address</label>
            <p class="py-1">The registration verification statement and the decals will be mailed to this address.</p>

            <base-address
              editing
              ref="submittingPartyAddress"
              id="submitting-party-address"
              :schema="PartyAddressSchema"
              :value="registeringParty.address"
              @valid="updateValidity($event)"
            />
          </article>
        </v-form>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useInputRules } from '@/composables'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { BaseAddress } from '@/composables/address'
import { SubmittingPartyTypes } from '@/enums'
import { PartyAddressSchema } from '@/schemas'
import { cloneDeep } from 'lodash'

export default defineComponent({
  name: 'MhrSubmittingParty',
  components: {
    BaseAddress
  },
  props: {},
  setup (props, context) {
    const {
      setMhrSubmittingParty
    } = useActions<any>([
      'setMhrSubmittingParty'
    ])
    const {
      getMhrRegistrationSubmittingParty
    } = useGetters<any>([
      'getMhrRegistrationSubmittingParty'
    ])

    // InputField Rules
    const {
      customRules,
      invalidSpaces,
      maxLength,
      required
    } = useInputRules()

    const localState = reactive({
      enableLookUp: true,
      submittingPartyType: '',
      submittingPartyValid: '',
      registeringParty: {
        personName: {
          first: '',
          last: '',
          middle: ''
        },
        businessName: '',
        emailAddress: '',
        phoneNumber: '',
        phoneExtension: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: '',
          country: '',
          postalCode: '',
          deliveryInstructions: ''
        }
      },
      isPersonOption: computed((): boolean => {
        return localState.submittingPartyType === SubmittingPartyTypes.PERSON
      }),
      isBusinessOption: computed((): boolean => {
        return localState.submittingPartyType === SubmittingPartyTypes.BUSINESS
      })
    })

    const updateValidity = (valid) => {
    }

    /** Apply store properties to local model. **/
    watch(() => getMhrRegistrationSubmittingParty.value, () => {
      if (localState.enableLookUp) {
        // Copy submitting party to local model if data is retrieved through the look-up
        localState.registeringParty = cloneDeep({
          ...localState.registeringParty,
          ...getMhrRegistrationSubmittingParty.value
        })

        // Apply party type if data is retrieved through the look-up
        localState.registeringParty.businessName
          ? localState.submittingPartyType = SubmittingPartyTypes.BUSINESS
          : localState.submittingPartyType = SubmittingPartyTypes.PERSON
      }
    }, { deep: true, immediate: true })

    /** Apply local model updates to store. **/
    watch(() => localState.registeringParty, async () => {
      // Disable look up during local model changes
      localState.enableLookUp = false

      // Set submitting party data to store
      for (const [key, value] of Object.entries(localState.registeringParty)) {
        await setMhrSubmittingParty({ key, value })
      }

      // Enable lookup once local model is updated in store
      localState.enableLookUp = true
    }, { deep: true })

    /** Handle party type changes. **/
    watch(() => localState.submittingPartyType, () => {
      if (localState.isPersonOption) {
        localState.registeringParty.businessName = ''
      }
      if (localState.isBusinessOption) {
        localState.registeringParty.personName = {
          first: '',
          middle: '',
          last: ''
        }
      }
    })

    return {
      getMhrRegistrationSubmittingParty,
      updateValidity,
      PartyAddressSchema,
      SubmittingPartyTypes,
      ...toRefs(localState)
    }
  }
})
/* eslint-enable no-unused-vars */
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
p {
  color: $gray7
}
.person-radio {
  width: 47%;
  margin-right: 20px !important;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
}
.business-radio {
  width: 50%;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
  margin-right: 0px !important;
}
.selected-radio {
  border: 1px solid $app-blue;
  background-color: white;
  ::v-deep .theme--light.v-label:not(.v-label--is-disabled), .theme--light.v-messages {
    color: $gray9 !important;
  }
}
::v-deep {
  .v-list-item .v-list-item__title, .v-list-item .v-list-item__subtitle {
    color: $gray7;
  }
  .v-list-item--link[aria-selected='true'] {
    background-color: $blueSelected !important;
    .v-list-item__title, .v-list-item .v-list-item__subtitle {
      color: $app-blue !important;
    }
  }
  .v-list-item--link:hover {
    background-color: $gray1 !important;
    .v-list-item__title, .v-list-item .v-list-item__subtitle {
      color: $app-blue !important;
    }
  }
}
</style>
