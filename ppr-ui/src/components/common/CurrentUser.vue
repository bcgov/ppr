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
      <v-simple-table>
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
                  mdi-account
                </v-icon>
                <span class="pt-1 font-weight-bold">
                  {{ userInfo.personName.first }} {{ userInfo.personName.last }}
                </span>
              </td>
              <td class="py-6">
                <BaseAddress id="submitting-party-address" :schema="PartyAddressSchema" :value="currentUserAddress" />
              </td>
              <td class="py-6">
                {{ userInfo.emailAddress }}
              </td>
              <td class="py-6">
                {{ toDisplayPhone(userInfo.phoneNumber) }}
                <span v-if="userInfo.phoneExtension"> Ext {{ userInfo.phoneExtension }} </span>
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
import { AddressIF, SubmittingPartyIF, UserInfoIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { toDisplayPhone } from '@/utils'

export default defineComponent({
  name: 'CurrentUser',
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
    currentUserInfo: {
      type: Object as () => UserInfoIF,
      required: true
    },
    currentUserAddress: {
      type: Object as () => AddressIF,
      required: true
    }
  },
  setup (props) {
    const user = props.currentUserInfo as UserInfoIF

    const localState = reactive({
      userInfo: {
        personName: {
          first: user.firstname,
          last: user.lastname
        },
        emailAddress: user.contacts[0].email,
        phoneNumber: user.contacts[0].phone.replace(/[^0-9.]+/g, ''),
        phoneExtension: user.contacts[0].phoneExtension
      } as SubmittingPartyIF
    })

    return { PartyAddressSchema, toDisplayPhone, ...toRefs(localState) }
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
