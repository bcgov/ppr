<template>
  <div>
    <template v-if="isRoleQualifiedSupplier">
      <a class="approved-qs-link">
        <v-icon left color="primary" class="fs-21 mt-n1">mdi-account-lock</v-icon>
        <span class="primary--text fs-13">Approved Qualified Supplier</span>
      </a>
    </template>
    <template v-else>
      <v-tooltip
        top
        content-class="top-tooltip pa-4 mr-2"
        transition="fade-transition"
        :disabled="!isPendingQsAccess"
      >
        <template v-slot:activator="{ on }">
          <a v-on="on" :class="{'pending-qs-link': isPendingQsAccess || isUserAccessRoute }" @click="goToUserAccess()">
            <v-icon left color="primary" class="fs-21 mt-n1">mdi-account-lock</v-icon>
            <span class="primary--text fs-13">Request MHR Qualified Supplier Access</span>
          </a>
        </template>
        This account has a Qualified Supplier application that is under review.
      </v-tooltip>
    </template>
  </div>

</template>

<script lang="ts">
import { defineComponent } from 'vue-demi'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useUserAccess } from '@/composables'

export default defineComponent({
  name: 'QsAccessBtn',
  setup () {
    const { isRoleQualifiedSupplier, isRoleStaffReg } = storeToRefs(useStore())
    const { isPendingQsAccess, isUserAccessRoute, goToUserAccess } = useUserAccess()

    return {
      goToUserAccess,
      isRoleStaffReg,
      isPendingQsAccess,
      isUserAccessRoute,
      isRoleQualifiedSupplier
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
