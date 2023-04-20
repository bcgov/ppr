<template>
  <v-card flat rounded id="submitting-party" class="mt-8 pa-8 pr-6">
    <v-row no-gutters>
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': validate}">Add Submitting Party</label>
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

        <v-card v-if="isBusinessLookup" outlined id="important-message" class="rounded-0 mb-9">
          <p>
            <strong>Important:</strong> If you make changes to the submitting party information below, the changes will
            only be applicable to this registration. The party code information will not be updated.
          </p>
        </v-card>

        <v-form id="submitting-party-form" ref="submittingPartyForm" v-model="submittingPartyValid">
          <!-- Person Name Input -->
          <div v-show="isPersonOption">
            <label class="generic-label" for="first-name">Person's Name</label>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  id="first-name"
                  class="pt-4 pr-2"
                  label="First Name"
                  v-model="submittingParty.personName.first"
                  :rules="isPersonOption ? firstNameRules : []"
                />
              </v-col>
              <v-col>
                <v-text-field
                  filled
                  id="middle-name"
                  class="pt-4 px-2"
                  label="Middle Name (Optional)"
                  v-model="submittingParty.personName.middle"
                  :rules="isPersonOption ? middleNameRules : []"
                />
              </v-col>
              <v-col>
                <v-text-field
                  filled
                  id="last-name"
                  class="pt-4 px-2"
                  label="Last Name"
                  v-model="submittingParty.personName.last"
                  :rules="isPersonOption ? lastNameRules : []"
                />
              </v-col>
            </v-row>
          </div>

          <!-- Business Name Input -->
          <div v-show="isBusinessOption">
            <label class="generic-label" for="business-name">Business Name</label>
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled
                  id="business-name"
                  class="pt-4 pr-2"
                  label="Business Name"
                  v-model="submittingParty.businessName"
                  :rules="isBusinessOption ? businessNameRules : []"
                />
              </v-col>
            </v-row>
          </div>

          <!-- Email Address -->
          <label class="generic-label" for="submitting-party-email">Email Address</label>
          <v-text-field
            filled
            id="submitting-party-email"
            class="pt-4 pr-2"
            label="Email Address"
            v-model="submittingParty.emailAddress"
            :rules="emailRules"
          />

          <!-- Phone Number -->
          <label class="generic-label" for="submitting-party-phone">Phone Number</label>
          <v-row no-gutters>
            <v-col>
              <v-text-field
                v-mask="'(NNN) NNN-NNNN'"
                filled
                id="submitting-party-phone"
                class="pt-4 pr-3"
                label="Phone Number (Optional)"
                v-model="displayPhone"
                :rules="phoneRules"
            />
            </v-col>
            <v-col>
              <v-text-field
                filled
                id="submitting-party-phone-ext"
                class="pt-4 px-2"
                label="Extension (Optional)"
                v-model="submittingParty.phoneExtension"
                :rules="phoneExtensionRules"
              />
            </v-col>
          </v-row>

          <!-- Mailing Address -->
          <article class="pt-4 pr-1">
            <label class="generic-label" for="submitting-party-address">Mailing Address</label>
            <p v-if="content && content.mailAddressInfo" class="py-1">
              {{ content.mailAddressInfo }}
            </p>
            <p v-else class="py-1">
              Registry documents and decal will be mailed to this address.
            </p>

            <base-address
              editing
              hideAddressHint
              ref="submittingPartyAddress"
              id="submitting-party-address"
              :schema="PartyAddressSchema"
              :value="submittingParty.address"
              :triggerErrors="validate"
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
import { useInputRules, useMhrValidations } from '@/composables'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { BaseAddress } from '@/composables/address'
import { SubmittingPartyTypes } from '@/enums'
import { PartyAddressSchema } from '@/schemas'
import { cloneDeep } from 'lodash'
import { VueMaskDirective } from 'v-mask'
import { fromDisplayPhone, toDisplayPhone } from '@/utils'
import { ContentIF, SubmittingPartyIF } from '@/interfaces'

/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'MhrSubmittingParty',
  emits: ['isValid'],
  components: {
    BaseAddress
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    },
    isMhrTransfer: {
      type: Boolean,
      default: false
    }
  },
  directives: {
    mask: VueMaskDirective
  },
  setup (props, context) {
    const {
      setMhrRegistrationSubmittingParty,
      setMhrTransferSubmittingParty
    } = useActions<any>([
      'setMhrRegistrationSubmittingParty',
      'setMhrTransferSubmittingParty'
    ])
    const {
      getMhrRegistrationSubmittingParty,
      getMhrTransferSubmittingParty,
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationSubmittingParty',
      'getMhrTransferSubmittingParty',
      'getMhrRegistrationValidationModel'
    ])

    // InputField Rules
    const {
      customRules,
      invalidSpaces,
      maxLength,
      isStringOrNumber,
      required,
      isNumber,
      isEmail,
      isPhone
    } = useInputRules()

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      enableLookUp: true,
      submittingPartyType: null as SubmittingPartyTypes,
      submittingPartyValid: false,
      addressValid: false,
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
      } as SubmittingPartyIF,
      isBusinessLookup: false,
      isPersonOption: computed((): boolean => {
        return localState.submittingPartyType === SubmittingPartyTypes.PERSON
      }),
      isBusinessOption: computed((): boolean => {
        return localState.submittingPartyType === SubmittingPartyTypes.BUSINESS
      }),
      isSubmitterValid: computed(() => {
        return localState.submittingPartyValid && localState.addressValid
      }),
      displayPhone: ''
    })

    const firstNameRules = customRules(
      required('Enter a first name'),
      isStringOrNumber(),
      maxLength(15),
      invalidSpaces()
    )

    const emailRules = customRules(
      maxLength(250),
      isEmail(),
      invalidSpaces()
    )

    const phoneRules = customRules(
      isPhone(14)
    )

    const middleNameRules = customRules(isStringOrNumber(), maxLength(15), invalidSpaces())

    const lastNameRules = customRules(
      required('Enter a last name'),
      isStringOrNumber(),
      maxLength(25),
      invalidSpaces())

    const businessNameRules = customRules(
      required('Business name is required'),
      maxLength(70),
      invalidSpaces()
    )

    const phoneExtensionRules = customRules(isNumber(null, null, null, 'Enter numbers only'),
      invalidSpaces(),
      maxLength(5, true)
    )

    const updateValidity = (valid) => {
      localState.addressValid = valid
    }

    /** Apply store properties to local model. **/
    watch(
      [getMhrRegistrationSubmittingParty, getMhrTransferSubmittingParty],
      () => {
        if (localState.enableLookUp) {
          const submittingParty = (props.isMhrTransfer
            ? getMhrTransferSubmittingParty.value
            : getMhrRegistrationSubmittingParty.value) as SubmittingPartyIF
          // Copy submitting party to local model if data is retrieved through the look-up
          localState.submittingParty = cloneDeep({
            ...localState.submittingParty,
            ...submittingParty
          })
          localState.displayPhone = toDisplayPhone(localState.submittingParty.phoneNumber)
          // Apply party type if data is retrieved through the look-up
          localState.submittingParty.businessName
            ? localState.submittingPartyType = SubmittingPartyTypes.BUSINESS
            : localState.submittingPartyType = SubmittingPartyTypes.PERSON

          if (submittingParty.businessName) {
            localState.isBusinessLookup = true
          }
        }
      }, { deep: true, immediate: true })

    /** Apply local model updates to store. **/
    watch(() => [localState.submittingParty, localState.submittingPartyType], async () => {
      // Disable look up during local model changes
      localState.enableLookUp = false
      // Set submitting party data to store
      props.isMhrTransfer
        ? await setMhrTransferSubmittingParty(localState.submittingParty)
        : await setMhrRegistrationSubmittingParty(localState.submittingParty)
      // Enable lookup once local model is updated in store
      localState.enableLookUp = true
    }, { deep: true })

    /** Handle Phone changes and write to store. **/
    watch(() => localState.displayPhone, () => {
      localState.submittingParty.phoneNumber = fromDisplayPhone(localState.displayPhone)
    })

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

    watch(() => props.validate, async () => {
      // @ts-ignore - function exists
      await context.refs.submittingPartyForm.validate()
    })

    watch(() => localState.isSubmitterValid, (val: boolean) => {
      context.emit('isValid', val)
      setValidation(MhrSectVal.SUBMITTING_PARTY_VALID, MhrCompVal.SUBMITTER_VALID, val)
    })

    return {
      getMhrRegistrationSubmittingParty,
      updateValidity,
      PartyAddressSchema,
      SubmittingPartyTypes,
      emailRules,
      firstNameRules,
      middleNameRules,
      lastNameRules,
      businessNameRules,
      phoneRules,
      phoneExtensionRules,
      ...toRefs(localState)
    }
  }
})
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
#important-message {
  background-color: $BCgovGold0 !important;
  border-color: $BCgovGold5 !important;
  border-radius: 0;

  p {
    margin: 1.25rem;
    padding: 0;
    font-size: $px-14;
    letter-spacing: 0.01rem;
    color: $gray7;
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
