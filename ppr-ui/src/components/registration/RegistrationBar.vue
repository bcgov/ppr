<template>
  <v-container id="registration-bar" fluid no-gutters class="registration-bar pa-0">
    <v-row no-gutters class="px-6">
      <v-col class="ml-n6" cols="4">
        <div class="actions">
          <registration-bar-type-ahead-list v-if="hasRPPR" @selected="newRegistration($event)" />
          <registration-bar-button-list v-else @selected="newRegistration($event)"/>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'

import RegistrationBarButtonList from '@/components/registration/RegistrationBarButtonList.vue'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
import {
  AccountProductCodes, AccountProductRoles, // eslint-disable-line no-unused-vars
  APIRegistrationTypes
} from '@/enums'
import { AccountProductSubscriptionIF, RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  components: {
    RegistrationBarButtonList,
    RegistrationBarTypeAheadList
  },
  emits: ['selected-registration-type'],
  setup (props, { emit }) {
    const { getAccountProductSubscriptions } = useGetters<any>(['getAccountProductSubscriptions'])
    const { setRegistrationTypeOtherDesc } = useActions<any>(['setRegistrationTypeOtherDesc'])
    const hasRPPR = computed(() => {
      const productSubscriptions = getAccountProductSubscriptions.value as AccountProductSubscriptionIF
      return (
        productSubscriptions?.[AccountProductCodes.RPPR].roles.includes(AccountProductRoles.EDIT) || false
      )
    })
    const newRegistration = (val: RegistrationTypeIF) => {
      if (val.registrationTypeAPI !== APIRegistrationTypes.OTHER) {
        setRegistrationTypeOtherDesc('')
      }
      emit('selected-registration-type', val)
    }

    return {
      hasRPPR,
      newRegistration
    }
  }
})
</script>
