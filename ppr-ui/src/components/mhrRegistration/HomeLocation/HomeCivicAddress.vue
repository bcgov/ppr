<template>
  <v-card flat rounded id="mhr-home-civic-address" class="mt-8 pa-8">
    <v-row no-gutters class="pt-1">
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': false}">Civic Address</label>
      </v-col>
      <v-col cols="12" sm="10" class="mt-n1">
          <v-form ref="addressForm" name="address-form" lazy-validation>
              <div class="form__row">
                <v-text-field
                  autocomplete="new-password"
                  class="street-address"
                  filled
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
                    :disabled="true"
                    class="item address-region"
                    label="Province"
                    hint="Address must be in B.C."
                    persistent-hint
                    :name="Math.random()"
                    v-model="address.region"
                    :rules="[...addressSchema.region]"
                  />
                </v-col>
              </v-row>
            </div>
          </v-form>

      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { useActions } from 'vuex-composition-helpers'
/* eslint-enable no-unused-vars */
export default defineComponent({
  name: 'HomeCivicAddress',
  components: {},
  props: {
    /* used for readonly mode vs edit mode */
    editing: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const {
      setMhrLocation
    } = useActions<any>([
      'setMhrLocation'
    ])

    const addressSchema = CivicAddressSchema

    const localState = reactive({
      isValidLot: false,
      showAllAddressErrors: false,
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: 'British Columbia'
      }
    })
    localState.isValidLot = true

    /** Apply local model updates to store. **/
    watch(() => localState, async () => {
      // Set civic address data to store
      for (const [key, value] of Object.entries(localState)) {
        await setMhrLocation({ key, value })
      }
    }, { deep: true })
    /** Clear/reset forms when select option changes. **/
    return { addressSchema, ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
