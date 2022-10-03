<template>
  <v-container id="registration-bar" fluid no-gutters class="registration-bar pa-0">
    <v-row no-gutters style="min-width: 345px">
      <v-col>
        <div class="actions">
          <v-btn
            v-if="isMhr && (!isRoleQualifiedSupplier || isRoleStaff)"
            filled
            class="mhr-registration-bar-btn px-5"
            @click="newRegistration(MhrRegistrationType)"
          >
            <v-icon class="pr-1">mdi-home-plus</v-icon>
            <span class="pr-2"> Register a Manufactured Home</span>
          </v-btn>
          <registration-bar-type-ahead-list
            v-else-if="hasRPPR"
            :defaultLabel="labelText"
            :defaultDense="false"
            :defaultClearable="false"
            :isLightBackGround="!isTabView"
            @selected="newRegistration($event)"
            />
          <registration-bar-button-list v-else-if="!isMhr" @selected="newRegistration($event)"/>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'

import RegistrationBarButtonList from '@/components/registration/RegistrationBarButtonList.vue'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
import {
  AccountProductCodes, AccountProductRoles, // eslint-disable-line no-unused-vars
  APIRegistrationTypes
} from '@/enums'
import { AccountProductSubscriptionIF, RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { MhrRegistrationType } from '@/resources'

export default defineComponent({
  components: {
    RegistrationBarButtonList,
    RegistrationBarTypeAheadList
  },
  props: {
    isMhr: {
      type: Boolean,
      default: false
    },
    isTabView: {
      type: Boolean,
      default: false
    }
  },
  emits: ['selected-registration-type'],
  setup (props, { emit }) {
    const { getAccountProductSubscriptions, isRoleQualifiedSupplier, isRoleStaff } =
      useGetters<any>(['getAccountProductSubscriptions', 'isRoleQualifiedSupplier', 'isRoleStaff'])
    const { setRegistrationTypeOtherDesc } = useActions<any>(['setRegistrationTypeOtherDesc'])
    const localState = reactive({
      labelText: 'Start a New Personal Property Registration'
    })
    const hasRPPR = computed(() => {
      const productSubscriptions = getAccountProductSubscriptions.value as AccountProductSubscriptionIF
      return (
        productSubscriptions?.[AccountProductCodes.RPPR]?.roles.includes(AccountProductRoles.EDIT) || false
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
      isRoleStaff,
      isRoleQualifiedSupplier,
      newRegistration,
      MhrRegistrationType,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";

.mhr-registration-bar-btn {
  background-color: $app-blue !important;
  color: white;
  box-shadow: none;
}
</style>
