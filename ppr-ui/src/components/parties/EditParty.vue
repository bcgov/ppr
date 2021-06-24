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
            <v-row class="pb-6" no-gutters>
              <v-col cols="auto">
                <v-radio-group v-model="partyBusiness" row hide-details="true">
                  <v-radio
                    class="business-radio"
                    label="Individual Person"
                    value="I"
                  >
                  </v-radio>

                  <v-radio
                    class="individual-radio ml-8"
                    label="Business"
                    value="B"
                  >
                  </v-radio>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-row no-gutters v-if="isPartyType">
              <v-col cols="12">
                <v-row v-if="partyBusiness === 'B'" no-gutters>
                  <v-col>
                    <label class="general-label">Business Name</label>
                  </v-col>
                </v-row>
                <v-row v-else no-gutters>
                  <v-col>
                    <label class="general-label">Person's Name</label>
                  </v-col>
                </v-row>
                <v-row v-if="partyBusiness === 'B'" no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-name"
                      label="Business Legal Name"
                      v-model="currentSecuredParty.businessName"
                      :error-messages="
                        errors.businessName.message
                          ? errors.businessName.message
                          : ''
                      "
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row v-else no-gutters>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="First Name"
                      id="txt-first"
                      v-model="currentSecuredParty.personName.first"
                      persistent-hint
                      @blur="onBlur('first')"
                      :error-messages="
                        errors.first.message ? errors.first.message : ''
                      "
                    />
                  </v-col>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="Middle Name (Optional)"
                      id="txt-middle"
                      v-model="currentSecuredParty.personName.middle"
                      persistent-hint
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Last Name"
                      id="txt-last"
                      v-model="currentSecuredParty.personName.last"
                      persistent-hint
                      @blur="onBlur('last')"
                      :error-messages="
                        errors.last.message ? errors.last.message : ''
                      "
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
                      v-model="currentSecuredParty.emailAddress"
                      :error-messages="
                        errors.emailAddress.message ? errors.emailAddress.message : ''
                      "
                      @blur="onBlur('emailAddress')"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <label class="general-label">Address</label>
                  </v-col>
                </v-row>
                <base-address
                  ref="regMailingAddress"
                  id="address-secured-party"
                  v-model="currentSecuredParty.address"
                  :editing="true"
                  :schema="addressSchema"
                  @valid="updateValidity($event)"
                />
              </v-col>
            </v-row>
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
  reactive,
  toRefs,
  computed,
  watch
} from '@vue/composition-api'
import BaseAddress from '@/composables/address/BaseAddress.vue'
import { useSecuredPartyValidation } from './composables/useSecuredPartyValidation'
import { useSecuredParty } from './composables/useSecuredParty'

export default defineComponent({
  components: {
    BaseAddress
  },
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    invalidSection: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditParty', 'resetEvent'],
  setup (props, context) {
    const {
      currentSecuredParty,
      currentIsBusiness,
      getSecuredParty,
      resetFormAndData,
      removeSecuredParty,
      addSecuredParty,
      updateAddress,
      addressSchema
    } = useSecuredParty(props, context)

    const { errors, updateValidity, validateSecuredPartyForm, validateInput } = useSecuredPartyValidation()

    const localState = reactive({
      partyBusiness: '',
      isPartyType: computed((): boolean => {
        if (localState.partyBusiness === '') {
          return false
        }
        return true
      })
    })

    const onBlur = (fieldname) => {
      validateInput(fieldname, currentSecuredParty.value[fieldname])
    }

    const onSubmitForm = async () => {
      if (validateSecuredPartyForm(localState.partyBusiness, currentSecuredParty) === true) {
        addSecuredParty()
      }
    }

    const getPartyBusiness = () => {
      const businessValue = currentIsBusiness.value
      if (businessValue !== null) {
        localState.partyBusiness = 'I'
        if (businessValue) {
          localState.partyBusiness = 'B'
        }
      }
    }

    watch(
      () => localState.partyBusiness,
      currentValue => {
        if (currentValue === 'I') {
          currentSecuredParty.value.businessName = ''
        } else {
          currentSecuredParty.value.personName.first = ''
          currentSecuredParty.value.personName.middle = ''
          currentSecuredParty.value.personName.last = ''
        }
      }
    )

    onMounted(() => {
      getSecuredParty()
      getPartyBusiness()
    })

    return {
      currentSecuredParty,
      currentIsBusiness,
      resetFormAndData,
      removeSecuredParty,
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
@import '@/assets/styles/theme.scss';
</style>
