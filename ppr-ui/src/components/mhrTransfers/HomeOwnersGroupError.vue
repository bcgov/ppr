<template>
  <!-- Transfer to Executor error messages -->
  <span v-if="isTransferToExecutorProbateWill || isTransferToExecutorUnder25Will">
    <span v-if="!TransToExec.hasAddedExecutorsInGroup(groupId) &&
      !TransToExec.hasDeletedOwnersWithProbateGrantOrAffidavit()">
      {{ transfersErrors.allOwnersHaveDeathCerts[getMhrTransferType.transferType] }}
    </span>
    <span v-else-if="!TransToExec.hasAllCurrentOwnersRemoved(groupId) &&
      !TransToExec.hasAddedExecutorsInGroup(groupId) &&
      !TransToExec.hasAtLeastOneExecInGroup(groupId)">
      {{ transfersErrors.ownersMustBeDeceasedAndExecutorAdded }}
    </span>
    <span v-else-if="!TransToExec.hasAddedExecutorsInGroup(groupId) && hasOneHomeOwnerGroup">
      {{ transfersErrors.mustContainOneExecutor }}
    </span>
    <span v-else-if="!TransToExec.hasAddedExecutorsInGroup(groupId) &&
      TransToExec.hasAllCurrentOwnersRemoved(groupId)">
      {{ transfersErrors.mustContainOneExecutorInGroup }}
    </span>
    <span v-else-if="!TransToExec.hasAllCurrentOwnersRemoved(groupId) &&
      TransToExec.hasAddedExecutorsInGroup(groupId)">
      {{ transfersErrors.ownersMustBeDeceased }}
    </span>
    <span v-else-if="TransToExec.isAllGroupOwnersWithDeathCerts(groupId)">
      {{ transfersErrors.allOwnersHaveDeathCerts[getMhrTransferType.transferType] }}
    </span>
  </span>
  <!-- Transfer Sale or Gift error messages -->
  <span v-else-if="isTransferDueToSaleOrGift && TransSaleOrGift.hasMixedOwnersInGroup(groupId)">
    {{ hasOneHomeOwnerGroup ?
      MixedRolesErrors.hasMixedOwnerTypes :
      MixedRolesErrors.hasMixedOwnerTypesInGroup }}
  </span>
  <!-- Transfer to Admin error messages -->
  <span v-else-if="isTransferToAdminNoWill">
    <span v-if="!TransToAdmin.hasAddedAdministratorsInGroup(groupId) &&
      !TransToExec.hasDeletedOwnersWithProbateGrantOrAffidavit()">
      {{ transfersErrors.allOwnersHaveDeathCerts[getMhrTransferType.transferType] }}
    </span>
    <span v-else-if="!TransToExec.hasAllCurrentOwnersRemoved(groupId) &&
      !TransToAdmin.hasAddedAdministratorsInGroup(groupId) &&
      !TransToAdmin.hasAtLeastOneAdminInGroup(groupId)">
      {{ transfersErrors.ownersMustBeDeceasedAndAdminAdded }}
    </span>
    <span v-else-if="!TransToAdmin.hasAddedAdministratorsInGroup(groupId) && hasOneHomeOwnerGroup">
      {{ transfersErrors.mustContainOneAdmin }}
    </span>
    <span v-else-if="!TransToAdmin.hasAddedAdministratorsInGroup(groupId) &&
      TransToExec.hasAllCurrentOwnersRemoved(groupId)">
      {{ transfersErrors.mustContainOneAdminInGroup }}
    </span>
    <span v-else-if="!TransToExec.hasAllCurrentOwnersRemoved(groupId) &&
      TransToAdmin.hasAddedAdministratorsInGroup(groupId)">
      {{ transfersErrors.ownersMustBeDeceased }}
    </span>
    <span v-else-if="TransToExec.isAllGroupOwnersWithDeathCerts(groupId)">
      {{ transfersErrors.allOwnersHaveDeathCerts[getMhrTransferType.transferType] }}
    </span>
  </span>
  <!-- Other error messages -->
  <span v-else>
    Group must contain at least one owner.
  </span>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { transfersErrors, MixedRolesErrors } from '@/resources'
import { useGetters } from 'vuex-composition-helpers'
import { useTransferOwners } from '@/composables/mhrInformation'

export default defineComponent({
  name: 'HomeOwnersGroupError',
  props: {
    groupId: {
      type: Number,
      required: true
    }
  },
  setup () {
    const {
      TransSaleOrGift,
      TransToExec,
      TransToAdmin,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      getMhrTransferType
    } = useTransferOwners()

    const {
      getMhrTransferHomeOwnerGroups
    } = useGetters<any>([
      'getMhrTransferHomeOwnerGroups'
    ])

    const localState = reactive({
      hasOneHomeOwnerGroup: computed(() => getMhrTransferHomeOwnerGroups.value.length === 1)
    })

    return {
      TransSaleOrGift,
      TransToExec,
      TransToAdmin,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToAdminNoWill,
      getMhrTransferType,
      MixedRolesErrors,
      transfersErrors,
      ...toRefs(localState)
    }
  }
})

</script>

<style lang="scss" scoped>
  @import '@/assets/styles/theme.scss';
</style>
