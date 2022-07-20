<template>
    <v-card flat class="py-6 px-8 rounded">
      <v-row id="mhr-home-add-org">
        <v-col cols="3">
          <label class="generic-label">
            Add an Organization
          </label>
        </v-col>
        <v-col cols="9">
          <label class="generic-label" for="org-name">
            Organization Legal Name
          </label>
          <v-row>
            <v-col>
              <p>
                You can look-up a B.C. business by entering the name of the
                business or the incorporation number (including Societies and
                extra-provincial companies registered in B.C.). If the name of
                the organization does not appear in the look-up, enter the full
                legal name of the organization.
              </p>
              <p>
                <v-expansion-panels>
                  <v-expansion-panel>
                    <v-expansion-panel-header
                      class="pa-0 primary--text"
                      :hide-actions="true"
                    >
                      <div>
                        <v-icon color="primary" v-on="on">mdi-information-outline</v-icon>
                        Help with Proprietorships / Partnerships
                      </div>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content class="help-toggle-content">
                      Registered owners of a manufactured home cannot be a sole
                      proprietorship, partnership or limited partnership. The
                      home must be registered in the name of the proprietor or
                      partner (person or organization).
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </p>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-text-field
                filled
                id="org-name"
                label="Full legal name of the organization"
                v-model="searchValue"
                :hide-details="hideDetails"
              />
              <auto-complete
                :searchValue="autoCompleteSearchValue"
                :setAutoCompleteIsActive="autoCompleteIsActive"
                v-click-outside="setCloseAutoComplete"
                @search-value="setSearchValue"
              >
              </auto-complete>
            </v-col>
          </v-row>
          <label class="generic-label">
            Phone Number
          </label>
          <v-row>
            <v-col cols="6">
              <v-text-field
                id="phone-number"
                filled
                :rules="maxLength(15)"
                label="Phone Number"
                data-test-id="phone-number"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                id="phone-ext"
                filled
                :rules="maxLength(15)"
                label="Extension (Optional)"
                data-test-id="phone-ext"
              />
            </v-col>
          </v-row>

          <label class="generic-label">
            Mailing Address
          </label>
          <base-address
            :editing="true"
            :schema="{ ...addressSchema }"
            class="mt-2"
          />

          <v-row>
            <v-col cols="6">
              <v-btn
                outlined
                color="error"
                class="remove-btn"
                :disabled="true"
                :ripple="false"
                @click="remove()"
              >
                Remove
              </v-btn>
            </v-col>
            <v-col cols="3">
              <v-btn :ripple="false" width="100%" @click="cancel()">
                Cancel
              </v-btn>
            </v-col>
            <v-col cols="3">
              <v-btn
                color="primary"
                :ripple="false"
                width="100%"
                @click="done()"
              >
                Done
              </v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useInputRules } from '@/composables/useInputRules'
import {
  useCountriesProvinces,
  useCountryRegions
} from '@/composables/address/factories'
import { AutoComplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'

import { PartyAddressSchema } from '@/schemas'

export default defineComponent({
  name: 'AddHomeOwnerOrganization',
  components: {
    AutoComplete,
    BaseAddress
  },
  setup (props, context) {
    const { maxLength } = useInputRules()
    const countryProvincesHelpers = useCountriesProvinces()

    const addressSchema = PartyAddressSchema

    const localState = reactive({
      organizationName: '',
      country: '',
      hideDetails: false,
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      searchValue: ''
    })

    const setHideDetails = (hideDetails: boolean) => {
      localState.hideDetails = hideDetails
    }

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      //   currentDebtor.value.businessName = searchValueTyped
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    const done = (): void => {
      context.emit('done', {})
    }
    const remove = (): void => {
      context.emit('remove')
    }
    const cancel = (): void => {
      context.emit('cancel')
    }

    watch(
      () => localState.searchValue,
      (val: string) => {
        localState.autoCompleteSearchValue = val
        // only open if debtor name changed
        // if (organizationName.value.businessName !== val) {
        //   // show autocomplete results when there is a searchValue
        //   localState.autoCompleteIsActive = val !== ''
        //   organizationName.value.businessName = val
        // }
      }
    )

    return {
      ...countryProvincesHelpers,
      useCountryRegions,
      done,
      remove,
      cancel,
      maxLength,
      addressSchema,
      setHideDetails,
      setSearchValue,
      setCloseAutoComplete,
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped lang="scss">
::v-deep .help-toggle-content {
  div {
    padding: 0;
  }
}
</style>
