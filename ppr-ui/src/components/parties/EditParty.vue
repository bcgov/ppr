<template>
  <div id="edit-party" class="white pa-6">
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
            <label
              class="add-party-header general-label"
              :class="{ 'error-text': invalidSection }"
            >
              <span v-if="activeIndex === -1" class="pl-5">Add</span>
              <span v-else>Edit</span>
              Secured Party
            </label>
        </v-col>
        <v-col cols="9">
              <v-form
                ref="partyForm"
                class="party-form"
                v-on:submit.prevent="addParty"
              >
              <v-row no-gutters>
                    <v-col cols="4">
                    <v-radio class="years-radio pa-0 ma-0"
                        :hide-details="false"
                        label=""
                        value="false"
                        @click="setBusiness('false')">
                    </v-radio>
                    Individual Person
                    </v-col>
                    <v-col cols="4">
                      <v-radio class="infinite-radio pt-15 ma-0"
                        :hide-details="false"
                        label=""
                        value="true"
                        @click="setBusiness('true')">
                    Business
                    </v-col>
                </v-row>
                <v-row v-if="currentIsBusiness" no-gutters>
                    <v-col>
                     <label class="general-label">Business Name</label>
                    </v-col>
                </v-row>
                <v-row v-if="currentIsBusiness" no-gutters>
                    <v-col>
                     <label class="general-label">Person's Name</label>
                    </v-col>
                </v-row>
                <v-row v-if="currentIsBusiness" no-gutters>
                    <v-col>
                     <v-text-field
                      filled
                      id="txt-name"
                      label="Business Legal Name"
                      v-model="businessName"
                      :error-messages="errors.businessName.message ?
                      errors.businessName.message : ''"
                      persistent-hint
                      :hide-details="hideDetails"
                    />
                    </v-col>
                </v-row>
                <v-row v-else no-gutters>
                    <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="First Name"
                      id="txt-first"
                      v-model="currentParty.personName.first"
                      persistent-hint
                      @blur="onBlur('first')"
                      :error-messages="errors.first.message ? errors.first.message : ''"
                    />
                  </v-col>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="Middle Name (Optional)"
                      id="txt-middle"
                      v-model="currentParty.personName.middle"
                      persistent-hint
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Last Name"
                      id="txt-last"
                      v-model="currentParty.personName.last"
                      persistent-hint
                      @blur="onBlur('last')"
                      :error-messages="errors.last.message ? errors.last.message : ''"
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                    <v-col>
                      <label class="general-label">Email Address</label>
                    </v-col>
                </v-row>
                <v-row no-gutters>
                    <v-col>
                     <v-text-field
                      filled
                      id="txt-email"
                      label="Email Address"
                      v-model="email"
                      :error-messages="errors.email.message ?
                      errors.email.message : ''"
                      persistent-hint
                    />
                    </v-col>
                </v-row>
                <v-row no-gutters>
                    <v-col>
                      <label class="general-label">Address</label>
                    </v-col>
                </v-row>
                <!-- <base-address ref="regMailingAddress"
                    id="address-Party"
                    :address="currentParty.address"
                    :editing="true"
                    :schema="addressSchema"
                    @update:address="updateAddress($event)"
                    @valid="updateValidity($event)"
                  /> -->

                <v-row>
                  <v-col>
                  <div class="form__row form__btns">
                    <v-btn
                      large
                      outlined
                      color="error"
                      :disabled="activeIndex === -1"
                      @click="removeParty()"
                      id="remove-btn"
                      >Remove
                    </v-btn>

                    <v-btn
                      large
                      id="done-btn"
                      class="m1-auto"
                      color="primary"
                      @click="onSubmitForm()"
                    >
                      Done
                    </v-btn>

                    <v-btn
                      id="cancel-btn"
                      large
                      outlined
                      color="primary"
                      @click="resetFormAndData(true)"
                    >
                      Cancel
                    </v-btn>
                  </div>
                  </v-col>
                </v-row>
              </v-form>
        </v-col>
      </v-row>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  onMounted,
  watch,
  reactive,
  toRefs
} from '@vue/composition-api'
// import BaseAddress from 'sbc-common-components/src/components/BaseAddress.vue'
import { usePartyValidation } from './composables/usePartyValidation'
import { useParty } from './composables/useSecuredParty'

export default defineComponent({
  components: {
    // BaseAddress,
  },
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    isBusiness: {
      type: Boolean,
      default: true
    },
    invalidSection: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditParty', 'resetEvent'],
  setup (props, context) {
    const {
      currentParty,
      currentIsBusiness,
      getParty,
      resetFormAndData,
      removeParty,
      addParty,
      updateAddress,
      addressSchema
    } = useParty(props, context)

    const { errors, updateValidity } = usePartyValidation()

    const localState = reactive({
    })

    const onBlur = (fieldname) => {
    }

    const onSubmitForm = async () => {
      addParty()
    }

    onMounted(() => {
      getParty()
    })

    return {
      currentParty,
      currentIsBusiness,
      resetFormAndData,
      removeParty,
      onSubmitForm,
      onBlur,
      addressSchema,
      updateAddress,
      updateValidity,
      errors,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import "@/assets/styles/theme.scss";
::v-deep .theme--light.v-btn.v-btn--disabled {
  color: rgba(211, 39, 44, .4) !important;
}
</style>
