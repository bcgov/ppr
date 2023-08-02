<template>
  <v-form id="party-form" ref="partyFormRef" v-model="isFormValid">

    <!-- Person Name Input -->
    <article v-if="hasPropData('personName')">
      <label class="generic-label" for="first-name">Person's Name</label>
      <!-- Placeholder for Persons Name: To build out with radio options locally or slotted -->
    </article>

    <!-- Business Name Input -->
    <article v-else-if="hasPropData('businessName') && !orgLookupConfig">
      <label class="generic-label" for="business-name">Business Name</label>

      <v-row no-gutters>
        <v-col>
          <v-text-field
            filled
            id="business-name"
            class="pt-4 pr-2"
            label="Business Name"
            v-model="partyModel.businessName"
            :rules="schema.businessName"
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
          :orgNameRules="schema.businessName"
          @updateOrgName="partyModel.businessName = $event"
        />
    </article>

    <!-- Email Address -->
    <article v-if="hasPropData('emailAddress')" class="mt-3">
      <label class="generic-label" for="contact-info-email">Email Address</label>
      <v-text-field
        filled
        id="contact-info-email"
        class="pt-4 pr-2"
        label="Email Address (Optional)"
        v-model="partyModel.emailAddress"
        :rules="schema.email"
      />
    </article>

    <!-- Phone Number -->
    <article v-if="hasPropData('phoneNumber')" class="mt-3">
      <label class="generic-label" for="contact-info-phone">Phone Number</label>

      <v-row no-gutters class="mt-5">
        <v-col>
          <v-text-field
              v-mask="'(NNN) NNN-NNNN'"
              filled
              id="party-form-phone"
              class="pr-3"
              label="Phone Number"
              v-model="partyModel.phoneNumber"
              :rules="schema.phone"
          />
        </v-col>
        <v-col>
          <v-text-field
              filled
              id="party-form-phone-ext"
              class="px-2"
              label="Extension (Optional)"
              v-model="partyModel.phoneExtension"
              :rules="schema.phoneExt"
          />
        </v-col>
      </v-row>
    </article>

    <!-- Mailing Address -->
    <article v-if="hasPropData('address')" class="mt-3">
      <label class="generic-label" for="party-form-address">Mailing Address</label>

      <BaseAddress
        editing
        class="mt-5"
        id="party-form-address"
        ref="baseAddressRef"
        :schema="schema.address"
        :value="partyModel.address"
        @valid="isAddressValid = $event"
      />
    </article>
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { FormIF, OrgLookupConfigIF, PartyIF, PartySchemaIF } from '@/interfaces'
import { BaseAddress } from '@/composables/address'
import { VueMaskDirective } from 'v-mask'
import OrgNameLookup from '@/components/common/OrgNameLookup.vue'

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
      isValid: computed(() => localState.isFormValid && localState.isAddressValid)
    })

    const hasPropData = (propertyName: string): boolean => {
      return props.baseParty?.hasOwnProperty(propertyName)
    }

    /** Validation function exposed for parent use **/
    const validatePartyForm = async () => {
      await partyFormRef.value?.validate()
      await baseAddressRef.value?.validate()
    }

    watch(() => localState.isValid, (isValid: boolean) => {
      emit('isValid', isValid)
    })

    return {
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
