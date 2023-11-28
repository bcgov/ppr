<template>
  <div
    class="actions registration-bar"
    fluid
  >
    <v-btn
      v-if="isMhr && (isRoleStaff || isRoleManufacturer)"
      class="mhr-registration-bar-btn px-5"
      @click="newRegistration(MhrRegistrationType)"
    >
      <v-icon class="pr-1">
        mdi-home-plus
      </v-icon>
      <span class="pr-2"> Register a Manufactured Home</span>
    </v-btn>

    <RegistrationBarTypeAheadList
      v-else-if="hasRPPR && !isMhr"
      defaultLabel="Start a New Personal Property Registration"
      :defaultDense="false"
      :defaultClearable="false"
      :isLightBackGround="!isTabView"
      @selected="newRegistration($event)"
    />

    <RegistrationBarButtonList
      v-else-if="!isMhr"
      @selected="newRegistration($event)"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'
import { useStore } from '@/store/store'

import RegistrationBarButtonList from '@/components/registration/RegistrationBarButtonList.vue'
import RegistrationBarTypeAheadList from '@/components/registration/RegistrationBarTypeAheadList.vue'
import {
  AccountProductCodes, AccountProductRoles,
  APIRegistrationTypes
} from '@/enums'
import { AccountProductSubscriptionIF, RegistrationTypeIF } from '@/interfaces'
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
  emits: ['selectedRegistrationType'],
  setup (props, { emit }) {
    const { setRegistrationTypeOtherDesc } = useStore()
    const {
      // Getters
      getAccountProductSubscriptions,
      isRoleQualifiedSupplier,
      isRoleStaff,
      isRoleManufacturer
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
      emit('selectedRegistrationType', val)
    }

    return {
      hasRPPR,
      isRoleStaff,
      isRoleManufacturer,
      isRoleQualifiedSupplier,
      newRegistration,
      MhrRegistrationType
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
</style>
