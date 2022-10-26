<template>
  <div id="current-user-info">
    <h4 class="header my-5">
      {{ title }}
      <v-tooltip
        if="tooltipContent"
        top
        nudge-right="3"
        content-class="top-tooltip pa-5"
        transition="fade-transition"
        data-test-id="submitting-party-tooltip"
      >
        <template v-slot:activator="{ on }">
          <v-icon class="mt-n1" color="primary" v-on="on">
            mdi-information-outline
          </v-icon>
        </template>
        {{ tooltipContent }}
      </v-tooltip>
    </h4>
    <v-card flat class="rounded">
      <v-simple-table v-if="accountInfo" data-test-id="user-info-table">
        <template v-slot:default>
          <thead>
            <tr>
              <th class="pl-6 py-4">
                Name
              </th>
              <th class="py-4">
                Mailing Address
              </th>
              <th class="py-4">
                Email Address
              </th>
              <th class="py-4">
                Phone Number
              </th>
            </tr>
          </thead>
          <tbody>
            <tr class="table-info">
              <td class="current-user-name pl-6 py-6">
                <v-icon>
                  {{ accountInfo.isBusinessAccount ? 'mdi-domain' : 'mdi-account' }}
                </v-icon>
                <span class="pt-1 font-weight-bold">
                  {{ accountInfo.name }}
                </span>
              </td>
              <td class="py-6">
                <BaseAddress
                  id="submitting-party-address"
                  :schema="PartyAddressSchema"
                  :value="accountInfo.mailingAddress"
                />
              </td>
              <td class="py-6">
                {{ accountInfo.accountAdmin.email }}
              </td>
              <td class="py-6">
                {{ toDisplayPhone(accountInfo.accountAdmin.phone) }}
                <span v-if="accountInfo.accountAdmin.phoneExtension">
                  Ext {{ accountInfo.accountAdmin.phoneExtension }}
                </span>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card>
  </div>
</template>

<script lang="ts">
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { defineComponent } from '@vue/composition-api'
import { toDisplayPhone } from '@/utils'
import { AccountInfoIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'AccountInfo',
  components: { BaseAddress },
  props: {
    title: {
      type: String,
      required: true
    },
    tooltipContent: {
      type: String,
      default: null
    },
    accountInfo: {
      type: Object as () => AccountInfoIF,
      required: true
    }
  },
  setup () {
    return { PartyAddressSchema, toDisplayPhone }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.table-info {
  vertical-align: top;
  .current-user-name,
  i {
    color: $gray9 !important;
  }
}
</style>
