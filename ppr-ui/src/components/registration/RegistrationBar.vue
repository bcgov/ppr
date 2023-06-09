<template>
  <v-container id="registration-bar" fluid class="registration-bar pa-0 no-gutters">
    <v-row no-gutters style="min-width: 345px">
      <v-col>
        <div class="actions">
          <v-btn
            v-if="isMhr && (!isRoleQualifiedSupplier || isRoleStaff || isRoleManufactuer)"
            filled
            class="mhr-registration-bar-btn px-5"
            @click="newRegistration(MhrRegistrationType)"
          >
            <v-icon class="pr-1">mdi-home-plus</v-icon>
            <span class="pr-2"> Register a Manufactured Home</span>
          </v-btn>
          <registration-bar-type-ahead-list
            v-else-if="hasRPPR && !isMhr"
            defaultLabel="Start a New Personal Property Registration"
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
import { computed, defineComponent } from 'vue-demi'
import { useStore } from '@/store/store'

import RegistrationBarButtonList from '@/components/registration/RegistrationBarButtonList.vue'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
import {
  AccountProductCodes, AccountProductRoles, // eslint-disable-line no-unused-vars
  APIRegistrationTypes
} from '@/enums'
import { AccountProductSubscriptionIF, RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { MhrRegistrationType } from '@/resources'
import { storeToRefs } from 'pinia'

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
    const { setRegistrationTypeOtherDesc } = useStore()
    const {
      // Getters
      getAccountProductSubscriptions,
      isRoleQualifiedSupplier,
      isRoleStaff,
      isRoleManufactuer
    } = storeToRefs(useStore())
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
      isRoleManufactuer,
      isRoleQualifiedSupplier,
      newRegistration,
      MhrRegistrationType
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
