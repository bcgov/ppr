<template>
  <div id="contact-info-container">
    <h2>
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${content.title}` }}
    </h2>
    <p class="mb-6">
      {{ content.description }}
    </p>

    <slot name="preForm" />

    <v-expand-transition>
      <div v-show="!isHidden">
        <PartySearch
          v-if="!hidePartySearch"
          is-mhr-party-search
          class="mb-8"
          @selectItem="handlePartySelect($event)"
        />

        <v-card
          v-if="!isHidden"
          id="contact-info"
          flat
          rounded
          class="pa-8 pr-6"
          :class="{ 'border-error-left': showBorderError }"
        >
          <v-row no-gutters>
            <v-col
              cols="12"
              sm="3"
              class="mt-1"
            >
              <label
                class="generic-label"
                :class="{ 'error-text': showBorderError }"
              >
                {{ content.sideLabel }}
              </label>
            </v-col>
            <v-col
              cols="12"
              sm="9"
            >
              <v-radio-group
                id="contact-info-type-options"
                v-model="contactInfoType"
                class="mt-0 pr-1"
                row
                hide-details="true"
              >
                <v-radio
                  id="person-option"
                  class="person-radio"
                  label="Individual Person"
                  false="selected-radio"
                  :value="ContactTypes.PERSON"
                />
                <v-radio
                  id="business-option"
                  class="business-radio"
                  label="Business"
                  false="selected-radio"
                  :value="ContactTypes.BUSINESS"
                />
              </v-radio-group>

              <v-divider class="my-9 ml-0 mr-2" />

              <CautionBox
                v-if="contactInfoModel.hasUsedPartyLookup"
                class="mb-9"
                set-msg="If you make changes to the submitting party information below, the changes will
                  only be applicable to this registration. The party code information will not be updated."
              />

              <v-form
                id="contact-info-form"
                ref="contactInfoForm"
                v-model="isContactInfoFormValid"
              >
                <!-- Person Name Input -->
                <div v-if="isPersonOption">
                  <label
                    class="generic-label"
                    for="first-name"
                  >Person's Name</label>
                  <v-row no-gutters>
                    <v-col>
                      <v-text-field
                        id="first-name"
                        v-model="contactInfoModel.personName.first"
                        variant="filled"
                        class="pt-4 pr-2"
                        :class="{ 'long-error-message': enableCombinedNameValidation }"
                        label="First Name"
                        :error="hasLongCombinedName"
                        :error-messages="longCombinedNameErrorMsg"
                        :rules="isPersonOption ? firstNameRules : []"
                      />
                    </v-col>
                    <v-col>
                      <v-text-field
                        id="middle-name"
                        v-model="contactInfoModel.personName.middle"
                        variant="filled"
                        class="pt-4 px-2"
                        label="Middle Name (Optional)"
                        :error="hasLongCombinedName"
                        :hide-details="hasLongCombinedName"
                        :rules="isPersonOption ? middleNameRules : []"
                      />
                    </v-col>
                    <v-col>
                      <v-text-field
                        id="last-name"
                        v-model="contactInfoModel.personName.last"
                        variant="filled"
                        class="pt-4 px-2"
                        label="Last Name"
                        :error="hasLongCombinedName"
                        :hide-details="hasLongCombinedName"
                        :rules="isPersonOption ? lastNameRules : []"
                      />
                    </v-col>
                  </v-row>
                </div>

                <!-- Business Name Input -->
                <div v-if="isBusinessOption">
                  <label
                    class="generic-label"
                    for="business-name"
                  >Business Name</label>
                  <v-row no-gutters>
                    <v-col>
                      <v-text-field
                        id="business-name"
                        v-model="contactInfoModel.businessName"
                        variant="filled"
                        class="pt-4 pr-2"
                        label="Business Name"
                        :rules="isBusinessOption ? businessNameRules : []"
                      />
                    </v-col>
                  </v-row>
                </div>

                <!-- Email Address -->
                <label
                  class="generic-label"
                  for="contact-info-email"
                >Email Address</label>
                <v-text-field
                  id="contact-info-email"
                  v-model="contactInfoModel.emailAddress"
                  variant="filled"
                  class="pt-4 pr-2"
                  label="Email Address (Optional)"
                  :rules="emailRules"
                />

                <!-- Phone Number -->
                <label
                  class="generic-label"
                  for="contact-info-phone"
                >Phone Number</label>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      id="contact-info-phone"
                      v-model="contactInfoModel.phoneNumber"
                      v-mask="'(NNN) NNN-NNNN'"
                      variant="filled"
                      class="pt-4 pr-3"
                      label="Phone Number (Optional)"
                      :rules="phoneRules"
                    />
                  </v-col>
                  <v-col>
                    <v-text-field
                      id="contact-info-phone-ext"
                      v-model="contactInfoModel.phoneExtension"
                      variant="filled"
                      class="pt-4 px-2"
                      label="Extension (Optional)"
                      :rules="phoneExtensionRules"
                    />
                  </v-col>
                </v-row>

                <!-- Mailing Address -->
                <article class="pt-4 pr-1">
                  <label
                    class="generic-label"
                    for="contact-info-address"
                  >Mailing Address</label>
                  <p
                    v-if="content && content.mailAddressInfo"
                    class="mt-2"
                  >
                    {{ content.mailAddressInfo }}
                  </p>

                  <base-address
                    id="contact-info-address"
                    ref="contactAddress"
                    class="mt-2"
                    editing
                    hide-address-hint
                    :hide-delivery-address="hideDeliveryAddress"
                    :schema="PartyAddressSchema"
                    :value="contactInfoModel.address"
                    :trigger-errors="validate"
                    @valid="isAddressValid = $event"
                  />
                </article>
              </v-form>
            </v-col>
          </v-row>
        </v-card>
      </div>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { useInputRules } from '@/composables'
import { ContactTypes } from '@/enums'
import { ContactInformationContentIF, FormIF, PartyIF, SubmittingPartyIF } from '@/interfaces'
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { PartyAddressSchema, OptionalPartyAddressSchema } from '@/schemas'
import { VueMaskDirective } from 'v-mask'
import { BaseAddress } from '@/composables/address'
import { PartySearch } from '../parties/party'
import { CautionBox } from '@/components/common'
import { emptyContactInfo } from '@/resources'
import { cloneDeep } from 'lodash'

export default defineComponent({
  name: 'ContactInformation',
  components: {
    BaseAddress,
    CautionBox,
    PartySearch
  },
  directives: {
    mask: VueMaskDirective
  },
  props: {
    contactInfo: {
      type: Object as () => PartyIF | SubmittingPartyIF,
      required: true
    },
    validate: {
      type: Boolean,
      default: false
    },
    sectionNumber: {
      type: Number,
      required: false
    },
    content: {
      type: Object as () => ContactInformationContentIF,
      default: () => {}
    },
    hidePartySearch: {
      type: Boolean,
      default: false
    },
    hideDeliveryAddress: {
      type: Boolean,
      default: false
    },
    enableCombinedNameValidation: {
      type: Boolean,
      default: false
    },
    isHidden: { // form isHidden
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid', 'setStoreProperty'],
  setup (props, { emit }) {
    const {
      customRules,
      invalidSpaces,
      maxLength,
      required,
      isNumber,
      isEmailOptional,
      isPhone
    } = useInputRules()

    const contactInfoForm = ref(null) as FormIF
    const contactAddress = ref(null)

    const localState = reactive({
      // Clone deep to ensure sub objects don't get overwritten
      contactInfoModel: cloneDeep({ ...emptyContactInfo, ...props.contactInfo as SubmittingPartyIF | PartyIF }),
      contactInfoType: (props.contactInfo as PartyIF)?.businessName
        ? ContactTypes.BUSINESS
        : ContactTypes.PERSON,
      isContactInfoFormValid: false,
      isAddressValid: false,
      hasLongCombinedName: false,
      longCombinedNameErrorMsg: computed((): string =>
        localState.hasLongCombinedName ? 'Person\'s Legal Name combined cannot exceed 40 characters' : ''),
      isPersonOption: computed((): boolean =>
        localState.contactInfoType === ContactTypes.PERSON
      ),
      isBusinessOption: computed((): boolean =>
        localState.contactInfoType === ContactTypes.BUSINESS
      ),
      showBorderError: computed((): boolean => !props.isHidden && props.validate &&
        !(localState.isContactInfoFormValid && localState.isAddressValid))
    })

    const handlePartySelect = async (party: SubmittingPartyIF) => {
      localState.contactInfoType = party.businessName ? ContactTypes.BUSINESS : ContactTypes.PERSON
      party.hasUsedPartyLookup = true
      localState.contactInfoModel.address.country = party.address.country // Deals with bug (13637)
      await nextTick()
      localState.contactInfoModel = party
    }

    watch(() => localState.contactInfoType, async (val) => {
      if (val === ContactTypes.BUSINESS) {
        localState.contactInfoModel.personName = {
          first: '',
          middle: '',
          last: ''
        }
      } else {
        localState.contactInfoModel.businessName = ''
      }
      if (props.validate) {
        await nextTick()
        await contactInfoForm.value?.validate()
      } else {
        // Deals with lingering validation errors when switching between person and business
        if (contactInfoForm.value?.errorMessages?.length > 0) {
          await contactInfoForm.value?.resetValidation()
        }
      }
    })
    watch(() => [localState.isContactInfoFormValid, localState.isAddressValid], () => {
      if (!props.isHidden) emit('isValid', localState.isContactInfoFormValid && localState.isAddressValid)
    })

    watch(() => localState.contactInfoModel, (val) => {
      emit('setStoreProperty', val)
    }, { deep: true, immediate: true })

    watch(() => props.validate, async () => {
      contactInfoForm.value?.validate()
    })

    watch(() => localState.contactInfoModel.personName, async () => {
      localState.hasLongCombinedName =
        props.enableCombinedNameValidation &&
        (0 || localState.contactInfoModel.personName?.first?.length) +
        (0 || localState.contactInfoModel.personName?.middle?.length) +
        (0 || localState.contactInfoModel.personName?.last?.length) > 40
    }, { deep: true })

    watch(() => props.isHidden, async (isHidden: boolean) => {
      if (isHidden) {
        localState.contactInfoType = ContactTypes.PERSON
        localState.contactInfoModel = cloneDeep(emptyContactInfo)
      } else if (props.validate) {
        await nextTick()
        contactInfoForm.value?.validate()
        contactAddress.value?.validate()
      }
    })

    const firstNameRules = customRules(
      required('Enter a first name'),
      maxLength(15),
      invalidSpaces()
    )

    const emailRules = customRules(
      maxLength(250),
      isEmailOptional(),
      invalidSpaces()
    )

    const phoneRules = customRules(
      isPhone(14)
    )

    const middleNameRules = customRules(maxLength(15), invalidSpaces())

    const lastNameRules = customRules(
      required('Enter a last name'),
      maxLength(25),
      invalidSpaces())

    const businessNameRules = customRules(
      required('Business name is required'),
      maxLength(150),
      invalidSpaces()
    )

    const phoneExtensionRules = customRules(
      isNumber(null, null, null, 'Enter numbers only'),
      invalidSpaces(),
      maxLength(5, true)
    )

    return {
      handlePartySelect,
      contactInfoForm,
      contactAddress,
      emailRules,
      firstNameRules,
      middleNameRules,
      lastNameRules,
      businessNameRules,
      phoneRules,
      phoneExtensionRules,
      ContactTypes,
      PartyAddressSchema,
      OptionalPartyAddressSchema,
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

  .long-error-message:deep(.v-messages.error--text) {
    position: absolute;
    width: 350px;
  }

</style>
