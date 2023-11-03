<template>
  <v-form
    id="party-form"
    ref="partyFormRef"
    v-model="isFormValid"
  >
    <!-- Party Type Selector -->
    <!-- If the data model contains both name types, the selector will render -->
    <v-row
      v-if="requiresPartyTypeSelect"
      no-gutters
    >
      <v-col>
        <v-radio-group
          id="contact-info-type-options"
          v-model="contactInfoType"
          class="mt-0 pr-1"
          inline
          hide-details="true"
        >
          <v-radio
            id="person-option"
            class="radio-one"
            label="Individual Person"
            false="selected-radio"
            :value="ContactTypes.PERSON"
          />
          <v-radio
            id="business-option"
            class="radio-two"
            label="Business"
            false="selected-radio"
            :value="ContactTypes.BUSINESS"
          />
        </v-radio-group>
        <v-divider class="my-8 mx-0" />
      </v-col>
    </v-row>

    <!-- Person Name Input -->
    <article
      v-if="requiresPartyTypeSelect ? contactInfoType === ContactTypes.PERSON : hasPropData('personName')"
    >
      <label
        class="generic-label"
        for="first-name"
      >Person's Legal Name</label>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            id="first-name"
            v-model="partyModel.personName.first"
            variant="filled"
            class="pt-4 pr-2"
            :label="`First Name ${schema.firstName.optional ? '(Optional)' : ''}`"
            :rules="schema.firstName.rules"
          />
        </v-col>
        <v-col>
          <v-text-field
            id="middle-name"
            v-model="partyModel.personName.middle"
            variant="filled"
            class="pt-4 pr-2"
            :label="`Middle Name ${schema.middleName.optional ? '(Optional)' : ''}`"
            :rules="schema.middleName.rules"
          />
        </v-col>
        <v-col>
          <v-text-field
            id="last-name"
            v-model="partyModel.personName.last"
            variant="filled"
            class="pt-4 pr-2"
            :label="`Last Name ${schema.lastName.optional ? '(Optional)' : ''}`"
            :rules="schema.lastName.rules"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Business Name Input -->
    <article v-else-if="hasPropData('businessName') && !orgLookupConfig">
      <label
        class="generic-label"
        for="business-name"
      >Business Name</label>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            id="business-name"
            v-model="partyModel.businessName"
            variant="filled"
            class="pt-4 pr-2"
            :label="`Business Name ${schema.businessName.optional ? '(Optional)' : ''}`"
            :rules="schema.businessName.rules"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Business Name Lookup -->
    <article v-else-if="hasPropData('businessName')">
      <slot name="businessNameSlot">
        <label
          class="generic-label"
          for="business-name"
        >Business Name</label>
      </slot>

      <OrgNameLookup
        id="business-name"
        class="mt-6"
        :field-label="orgLookupConfig.fieldLabel"
        :field-hint="orgLookupConfig.fieldHint"
        :nil-search-text="orgLookupConfig.nilSearchText"
        :base-value="partyModel.businessName"
        :org-name-rules="schema.businessName.rules"
        @update-org-name="partyModel.businessName = $event"
      />
    </article>

    <!-- Email Address -->
    <article
      v-if="hasPropData('emailAddress')"
      class="mt-3"
    >
      <label
        class="generic-label"
        for="contact-info-email"
      >Email Address</label>
      <v-text-field
        id="contact-info-email"
        v-model="partyModel.emailAddress"
        variant="filled"
        class="pt-4 pr-2"
        :label="`Email Address ${schema.email.optional ? '(Optional)' : ''}`"
        :rules="schema.email.rules"
      />
    </article>

    <!-- Phone Number -->
    <article
      v-if="hasPropData('phoneNumber')"
      class="mt-3"
    >
      <label
        class="generic-label"
        for="contact-info-phone"
      >Phone Number</label>

      <v-row
        no-gutters
        class="mt-5"
      >
        <v-col>
          <v-text-field
            id="party-form-phone"
            ref="phoneNumberRef"
            v-model="partyModel.phoneNumber"
            variant="filled"
            class="pr-3"
            :label="`Phone Number ${schema.phone.optional ? '(Optional)' : ''}`"
            :rules="schema.phone.rules"
          />
        </v-col>
        <v-col>
          <v-text-field
            id="party-form-phone-ext"
            v-model="partyModel.phoneExtension"
            variant="filled"
            class="px-2"
            :label="`Extension ${schema.phoneExt.optional ? '(Optional)' : ''}`"
            :rules="schema.phoneExt.rules"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Mailing Address -->
    <article
      v-if="hasPropData('address')"
      class="mt-3"
    >
      <label
        class="generic-label"
        for="party-form-address"
      >Mailing Address</label>
      <p class="mb-n1 mt-2">
        Registry documents, if any, will be mailed to this address.
      </p>

      <BaseAddress
        id="party-form-address"
        ref="baseAddressRef"
        editing
        hide-address-hint
        class="mt-5"
        :schema="schema.address.rules"
        :value="partyModel.address"
        @valid="isAddressValid = $event"
      />
    </article>
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { FormIF, OrgLookupConfigIF, PartyIF, PartySchemaIF } from '@/interfaces'
import { BaseAddress } from '@/composables/address'
import OrgNameLookup from '@/components/common/OrgNameLookup.vue'
import { ContactTypes } from '@/enums'
// import { useIMask } from 'vue-imask'

export default defineComponent({
  name: 'PartyForm',
  components: {
    BaseAddress,
    OrgNameLookup
  },
  props: {
    baseParty: {
      type: Object as () => PartyIF,
      required: true
    },
    schema: {
      type: Object as () => PartySchemaIF,
      default: null
    },
    orgLookupConfig: {
      type: Object as () => OrgLookupConfigIF,
      default: null
    },
    showErrors: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid'],
  setup (props, { emit }) {
    const partyFormRef = ref(null) as FormIF
    const baseAddressRef = ref(null) as FormIF
    // Mask Composable
    // const { el: phoneNumberRef } = useIMask({
    //   mask: '(000) 000-0000',
    //   radix: '.',
    // })

    const localState = reactive({
      isFormValid: false,
      isAddressValid: false,
      partyModel: props.baseParty as PartyIF,
      contactInfoType: ContactTypes.PERSON as ContactTypes,
      requiresPartyTypeSelect: computed(() => {
        return hasPropData('personName') && hasPropData('businessName')
      }),
      isValid: computed(() => (localState.isFormValid && localState.isAddressValid) || false)
    })

    const hasPropData = (propertyName: string): boolean => {
      return localState.partyModel?.hasOwnProperty(propertyName)
    }

    /** Validation function exposed for parent use **/
    const validatePartyForm = async () => {
      await partyFormRef.value?.validate()
      await baseAddressRef.value?.validate()
    }

    watch(() => props.baseParty, (party: PartyIF) => {
      localState.contactInfoType = party.businessName ? ContactTypes.BUSINESS : ContactTypes.PERSON
      localState.partyModel = party
    })
    watch(() => localState.isValid, (isValid: boolean) => {
      emit('isValid', isValid)
    })
    watch(() => props.showErrors, async () => {
      await validatePartyForm()
    })
    /** Clear the name values on contact type changes **/
    watch(() => localState.contactInfoType, (type: ContactTypes) => {
      partyFormRef.value?.resetValidation()
      if (type === ContactTypes.PERSON) {
        localState.partyModel.businessName = ''
      } else {
        localState.partyModel.personName.first = ''
        localState.partyModel.personName.middle = ''
        localState.partyModel.personName.last = ''
      }
    })

    return {
      ContactTypes,
      hasPropData,
      partyFormRef,
      baseAddressRef,
      validatePartyForm,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
