<template>
  <v-card flat rounded id="mhr-home-civic-address" class="mt-8 pa-8">
    <v-row no-gutters class="pt-1">
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': false}">Civic Address</label>
      </v-col>
      <v-col cols="12" sm="10" class="mt-n1">

      <div class="base-address">
        <!-- Display fields -->
        <!-- Edit fields -->

          <v-form ref="addressForm" name="address-form" lazy-validation>
            <div class="form__row">
              <!-- NB1: AddressComplete needs to be enabled each time user clicks in this search field.
                  NB2: Only process first keypress -- assumes if user moves between instances of this
                      component then they are using the mouse (and thus, clicking). -->
              <v-text-field
                autocomplete="new-password"
                class="street-address"
                filled
                hint="Street address, PO box, rural route, or general delivery address"
                label="Street Address"
                :name="Math.random()"
                persistent-hint
                v-model="address.street"
                :rules="[...addressSchema.street]"
              />
            </div>
            <div class="form__row">
              <v-textarea
                autocomplete="new-password"
                auto-grow
                filled
                class="street-address-additional"
                label="Additional Street Address (Optional)"
                :name="Math.random()"
                rows="1"
                v-model="address.streetAdditional"
                :rules="[...addressSchema.streetAdditional]"
              />
            </div>
            <div class="form__row two-column">
              <v-row>
                <v-col>
                  <v-text-field
                    autocomplete="new-password"
                    filled
                    class="item address-city"
                    label="City"
                    :name="Math.random()"
                    v-model="address.city"
                    :rules="[...addressSchema.city]"
                  />
                </v-col>
                <v-col>
                  <v-text-field
                    filled
                    :disabled=true
                    class="item address-region"
                    label="Province"
                    hint="Address must be in B.C."
                    :name="Math.random()"
                    v-model="address.region"
                    :rules="[...addressSchema.region]"
                  />
                </v-col>
              </v-row>
            </div>
          </v-form>
      </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { AutoComplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { AddressIF } from '@/composables/address/interfaces'
import { PartyAddressSchema } from '@/schemas/party-address'

/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeCivicAddress',
  components: {
    BaseAddress,
    AutoComplete
  },
  props: {
    /* used for readonly mode vs edit mode */
    editing: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    /* const {} = useActions<any>([]) */
    const initAddress : AddressIF = {
      street: '',
      streetAdditional: '',
      city: '',
      region: 'British Columbia',
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
