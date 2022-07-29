<template>
  <v-card flat rounded id="mhr-home-civic-address" class="mt-8 pa-8">
    <v-row no-gutters class="pt-1">
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': false}">Civic Address</label>
      </v-col>
      <v-col cols="12" sm="10" class="mt-n1">
      <base-address
                  ref="civicAddress"
                  v-model="address"
                  :editing="true"
                  :schema="{ ...addressSchema }"
                  :regionDisabled="true"
                  :deliveryOptionsVisible="false"
                  :triggerErrors="showAllAddressErrors"
                  @valid="updateValidity($event)"
                />
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
import { AutoComplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { formatAddress } from '@/composables/address/factories'
import { useValidation } from '@/utils/validators/use-validation'
import { AddressIF } from '@/composables/address/interfaces'
import { PartyAddressSchema } from '@/schemas/party-address'

/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeCivicAddress',
  components: {
    BaseAddress,
    AutoComplete
  },
  props: {},
  setup (props, context) {
    /* const {} = useActions<any>([]) */
    const initAddress : AddressIF = {
      street: '',
      streetAdditional: '',
      city: '',
      region: 'BC',
      country: '',
      postalCode: ''
    }

    const address : AddressIF = {
      street: initAddress.street,
      city: initAddress.city,
      region: initAddress.region,
      postalCode: initAddress.postalCode,
      country: initAddress.country
    }

    const addressSchema = PartyAddressSchema

    const localState = reactive({
      isValidLot: false,
      showAllAddressErrors: false
    })
    localState.isValidLot = true
    /** Apply local models to store when they change. **/
    /** Clear/reset forms when select option changes. **/
    return { address, addressSchema }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
