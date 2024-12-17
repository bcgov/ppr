<template>
  <div
    class="actions registration-bar"
    fluid
  >
    <v-btn
      v-if="isMhr && (isRoleStaffReg || isRoleManufacturer)"
      class="mhr-registration-bar-btn px-5"
      @click="newRegistration(MhrRegistrationType)"
    >
      <v-icon class="pr-1">
        mdi-home-plus
      </v-icon>
      <span class="pr-2"> Register a Manufactured Home</span>
    </v-btn>

    <RegistrationBarTypeAheadList
      v-else-if="(hasRPPR || isSecurityActNoticeEnabled) && !isMhr"
      default-label="Start a New Personal Property Registration"
      :default-dense="false"
      :default-clearable="false"
      :is-light-back-ground="!isTabView"
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
import type { AccountProductSubscriptionIF, RegistrationTypeIF } from '@/interfaces'
import { MhrRegistrationType } from '@/resources'
import { storeToRefs } from 'pinia'
import { usePprRegistration } from '@/composables'
import { debounce } from 'lodash'

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
    const { isSecurityActNoticeEnabled } = usePprRegistration()
    const { setRegistrationTypeOtherDesc } = useStore()
    const {
      // Getters
      getAccountProductSubscriptions,
      isRoleQualifiedSupplier,
      isRoleStaffReg,
      isRoleManufacturer
    } = storeToRefs(useStore())
    const hasRPPR = computed(() => {
      const productSubscriptions = getAccountProductSubscriptions.value as AccountProductSubscriptionIF
      return (
        productSubscriptions?.[AccountProductCodes.RPPR]?.roles.includes(AccountProductRoles.EDIT) || false
      )
    })
    const newRegistration = debounce((val: RegistrationTypeIF) => {
      if (val.registrationTypeAPI !== APIRegistrationTypes.OTHER) {
        setRegistrationTypeOtherDesc('')
      }
      emit('selectedRegistrationType', val)
      return
    }, 10)

    return {
      hasRPPR,
      isRoleStaffReg,
      isRoleManufacturer,
      isRoleQualifiedSupplier,
      newRegistration,
      MhrRegistrationType,
      isSecurityActNoticeEnabled
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
</style>
