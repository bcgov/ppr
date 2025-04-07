<template>
  <div
    id="qs-access-btn"
    role="button"
    aria-label="qualified-supplier-access-request-btn"
  >
    <template v-if="hasActiveQsAccess">
      <a class="approved-qs-link">
        <v-icon
          start
          color="primary"
          class="fs-21 mt-n1"
        >mdi-account-lock</v-icon>
        <span class="text-primary fs-13">Approved Qualified Supplier</span>
      </a>
    </template>
    <template v-else>
      <v-tooltip
        location="top"
        class="request-qs-tooltip"
        content-class="top-tooltip pa-4 mr-2"
        transition="fade-transition"
        :disabled="!hasPendingQsAccess"
      >
        <template #activator="{ props }">
          <a
            class="request-qs-link"
            :class="{'pending-qs-link': hasPendingQsAccess || isUserAccessRoute }"
            v-bind="props"
            @click="goToUserAccess()"
          >
            <v-icon
              start
              color="primary"
              class="fs-21 mt-n1"
            >mdi-account-lock</v-icon>
            <span class="text-primary fs-13">Request MHR Qualified Supplier Access</span>
          </a>
        </template>
        This account has a Qualified Supplier application that is under review.
      </v-tooltip>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useUserAccess } from '@/composables'

export default defineComponent({
  name: 'QsAccessBtn',
  setup () {
    const { isRoleStaffReg, getUserEmail } = storeToRefs(useStore())
    const { hasActiveQsAccess, hasPendingQsAccess, isUserAccessRoute, goToUserAccess } = useUserAccess()

    return {
      getUserEmail,
      goToUserAccess,
      isRoleStaffReg,
      hasActiveQsAccess,
      hasPendingQsAccess,
      isUserAccessRoute
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.approved-qs-link {
  cursor: default;
  i {
    color: $gray9!important;
  }
  span {
    color: $gray7!important;
  }
}
.pending-qs-link {
  opacity: .4;
  cursor: default;
}
</style>
