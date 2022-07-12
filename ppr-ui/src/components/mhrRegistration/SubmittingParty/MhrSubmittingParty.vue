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
                  v-model="submittingParty.personName.first"
                  :rules="firstNameRule"
                />
              </v-col>
              <v-col>
                <v-text-field
                  filled
                  id="middle-name"
                  class="pt-4 px-2"
                  label="Middle Name (Optional)"
                  v-model="submittingParty.personName.middle"
                  :rules="middleNameRule"
                />
              </v-col>
              <v-col>
                <v-text-field
                  filled
                  id="last-name"
                  class="pt-4 px-2"
                  label="Last Name"
                  v-model="submittingParty.personName.last"
                  :rules="lastNameRule"
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
                  v-model="submittingParty.businessName"
                  :rules="businessNameRule"
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
            v-model="submittingParty.emailAddress"
            :rules="emailRule"
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
                v-model="submittingParty.phoneNumber"
                :rules="phoneRule"
              />
            </v-col>
            <v-col>
              <v-text-field
                filled
                id="submitting-party-phone-ext"
                class="pt-4 px-2"
                label="Extension (Optional)"
                v-model="submittingParty.phoneExtension"
                :rules="phoneExtensionRule"
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
              :value="submittingParty.address"
              :trigger-errors="isReviewing"
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
import { computed, defineComponent, reactive, toRefs, watch, ref } from '@vue/composition-api'
import { useInputRules } from '@/composables'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { BaseAddress } from '@/composables/address'
import { SubmittingPartyTypes } from '@/enums'
import { PartyAddressSchema } from '@/schemas'
import { cloneDeep } from 'lodash'
import { getMhrRegistrationReviewing } from '@/store/getters'

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
      getMhrRegistrationSubmittingParty,
      getMhrRegistrationReviewing
    } = useGetters<any>([
      'getMhrRegistrationSubmittingParty',
      'getMhrRegistrationReviewing'
    ])

    // InputField Rules
    const {
      customRules,
      invalidSpaces,
      maxLength,
      required,
      isStringOrNumber,
      isNumber
    } = useInputRules()

    const localState = reactive({
      enableLookUp: true,
      submittingPartyType: '',
      submittingPartyValid: '',
      submittingParty: {
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
      addressValid: true,
      isPersonOption: computed((): boolean => {
        return localState.submittingPartyType === SubmittingPartyTypes.PERSON
      }),
      isBusinessOption: computed((): boolean => {
        return localState.submittingPartyType === SubmittingPartyTypes.BUSINESS
      }),
      isReviewing: computed((): boolean => {
        return getMhrRegistrationReviewing.value
      })
    })

    const firstNameRule = computed(() => {
      const rule = customRules(
        isStringOrNumber(),
        maxLength(15),
        invalidSpaces()
      )
      if (localState.isReviewing === true) {
        rule.unshift(...required('Enter a first name'))
      }
      return rule
    })

    const middleNameRule = computed(() => {
      return customRules(
        isStringOrNumber(),
        maxLength(15),
        invalidSpaces()
      )
    })

    const lastNameRule = computed(() => {
      const rule = customRules(
        isStringOrNumber(),
        maxLength(25),
        invalidSpaces()
      )
      if (localState.isReviewing === true) {
        rule.unshift(...required('Enter a last name'))
      }
      return rule
    })

    const businessNameRule = computed(() => {
      const rule = customRules(
        isStringOrNumber(),
        invalidSpaces()
      )
      if (localState.isReviewing === true) {
        rule.unshift(...required('Business name is required'))
      }
      return rule
    })

    const emailRule = computed(() => {
      const rule = customRules(
        invalidSpaces()
      )
      if (localState.isReviewing === true) {
        rule.unshift(...required('Email address is required'))
      }
      return rule
    })

    const phoneRule = computed(() => {
      const rule = customRules(
        isNumber(),
        invalidSpaces()
      )
      if (localState.isReviewing === true) {
        rule.unshift(...required('Phone number is required'))
      }
      return rule
    })

    const phoneExtensionRule = computed(() => {
      return customRules(
        isNumber(),
        invalidSpaces()
      )
    })

    const updateValidity = (valid) => {
      localState.addressValid = valid
    }

    const submittingPartyForm = ref(null)

    watch(() => getMhrRegistrationReviewing.value, () => {
      if (getMhrRegistrationReviewing.value) {
        submittingPartyForm.value.validate()
      }
    })

    /** Apply store properties to local model. **/
    watch(() => getMhrRegistrationSubmittingParty.value, () => {
      if (localState.enableLookUp) {
        // Copy submitting party to local model if data is retrieved through the look-up
        localState.submittingParty = cloneDeep({
          ...localState.submittingParty,
          ...getMhrRegistrationSubmittingParty.value
        })

        // Apply party type if data is retrieved through the look-up
        localState.submittingParty.businessName
          ? localState.submittingPartyType = SubmittingPartyTypes.BUSINESS
          : localState.submittingPartyType = SubmittingPartyTypes.PERSON
      }
    }, { deep: true, immediate: true })

    /** Apply local model updates to store. **/
    watch(() => localState.submittingParty, async () => {
      // Disable look up during local model changes
      localState.enableLookUp = false

      // Set submitting party data to store
      for (const [key, value] of Object.entries(localState.submittingParty)) {
        await setMhrSubmittingParty({ key, value })
      }

      // Enable lookup once local model is updated in store
      localState.enableLookUp = true
    }, { deep: true })

    /** Handle party type changes. **/
    watch(() => localState.submittingPartyType, () => {
      if (localState.isPersonOption) {
        localState.submittingParty.businessName = ''
      }
      if (localState.isBusinessOption) {
        localState.submittingParty.personName = {
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
      firstNameRule,
      middleNameRule,
      lastNameRule,
      businessNameRule,
      emailRule,
      phoneRule,
      phoneExtensionRule,
      submittingPartyForm,
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
