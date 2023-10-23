<template>
  <v-form id="party-form" ref="partyFormRef" v-model="isFormValid">

    <!-- Party Type Selector -->
    <!-- If the data model contains both name types, the selector will render -->
    <v-row no-gutters v-if="requiresPartyTypeSelect">
      <v-col>
        <v-radio-group
          id="contact-info-type-options"
          v-model="contactInfoType"
          class="mt-0 pr-1" row
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
        <v-divider class="my-8 mx-0"/>
      </v-col>
    </v-row>

    <!-- Person Name Input -->
    <article
      v-if="requiresPartyTypeSelect ? contactInfoType === ContactTypes.PERSON : hasPropData('personName')"
    >
      <label class="generic-label" for="first-name">Person's Legal Name</label>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            variant="filled"
            id="first-name"
            class="pt-4 pr-2"
            :label="`First Name ${schema.firstName.optional ? '(Optional)' : ''}`"
            v-model="partyModel.personName.first"
            :rules="schema.firstName.rules"
          />
        </v-col>
        <v-col>
          <v-text-field
            variant="filled"
            id="middle-name"
            class="pt-4 pr-2"
            :label="`Middle Name ${schema.middleName.optional ? '(Optional)' : ''}`"
            v-model="partyModel.personName.middle"
            :rules="schema.middleName.rules"
          />
        </v-col>
        <v-col>
          <v-text-field
            variant="filled"
            id="last-name"
            class="pt-4 pr-2"
            :label="`Last Name ${schema.lastName.optional ? '(Optional)' : ''}`"
            v-model="partyModel.personName.last"
            :rules="schema.lastName.rules"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Business Name Input -->
    <article v-else-if="hasPropData('businessName') && !orgLookupConfig">
      <label class="generic-label" for="business-name">Business Name</label>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            variant="filled"
            id="business-name"
            class="pt-4 pr-2"
            :label="`Business Name ${schema.businessName.optional ? '(Optional)' : ''}`"
            v-model="partyModel.businessName"
            :rules="schema.businessName.rules"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Business Name Lookup -->
    <article v-else-if="hasPropData('businessName')">
      <slot name="businessNameSlot">
        <label class="generic-label" for="business-name">Business Name</label>
      </slot>

        <OrgNameLookup
          class="mt-6"
          id="business-name"
          :fieldLabel="orgLookupConfig.fieldLabel"
          :fieldHint="orgLookupConfig.fieldHint"
          :nilSearchText="orgLookupConfig.nilSearchText"
          :baseValue="partyModel.businessName"
          :orgNameRules="schema.businessName.rules"
          @updateOrgName="partyModel.businessName = $event"
        />
    </article>

    <!-- Email Address -->
    <article v-if="hasPropData('emailAddress')" class="mt-3">
      <label class="generic-label" for="contact-info-email">Email Address</label>
      <v-text-field
        variant="filled"
        id="contact-info-email"
        class="pt-4 pr-2"
        :label="`Email Address ${schema.email.optional ? '(Optional)' : ''}`"
        v-model="partyModel.emailAddress"
        :rules="schema.email.rules"
      />
    </article>

    <!-- Phone Number -->
    <article v-if="hasPropData('phoneNumber')" class="mt-3">
      <label class="generic-label" for="contact-info-phone">Phone Number</label>

      <v-row no-gutters class="mt-5">
        <v-col>
          <v-text-field
            v-mask="'(NNN) NNN-NNNN'"
            variant="filled"
            id="party-form-phone"
            class="pr-3"
            :label="`Phone Number ${schema.phone.optional ? '(Optional)' : ''}`"
            v-model="partyModel.phoneNumber"
            :rules="schema.phone.rules"
          />
        </v-col>
        <v-col>
          <v-text-field
            variant="filled"
            id="party-form-phone-ext"
            class="px-2"
            :label="`Extension ${schema.phoneExt.optional ? '(Optional)' : ''}`"
            v-model="partyModel.phoneExtension"
            :rules="schema.phoneExt.rules"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Mailing Address -->
    <article v-if="hasPropData('address')" class="mt-3">
      <label class="generic-label" for="party-form-address">Mailing Address</label>
      <p class="mb-n1 mt-2">Registry documents, if any, will be mailed to this address.</p>

      <BaseAddress
        editing
        hideAddressHint
        class="mt-5"
        id="party-form-address"
        ref="baseAddressRef"
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
import { VueMaskDirective } from 'v-mask'
import OrgNameLookup from '@/components/common/OrgNameLookup.vue'
import { ContactTypes } from '@/enums'

export default defineComponent({
  name: 'PartyForm',
  emits: ['isValid'],
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
  directives: {
    mask: VueMaskDirective
  },
  setup (props, { emit }) {
    const partyFormRef = ref(null) as FormIF
    const baseAddressRef = ref(null) as FormIF

    const localState = reactive({
      isFormValid: false,
      isAddressValid: false,
      partyModel: props.baseParty as PartyIF,
      contactInfoType: ContactTypes.PERSON as ContactTypes,
      requiresPartyTypeSelect: computed(() => {
        return hasPropData('personName') && hasPropData('businessName')
      }),
      isValid: computed(() => localState.isFormValid && localState.isAddressValid)
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
