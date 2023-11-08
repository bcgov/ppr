<template>
  <v-row
    id="home-owners-roles"
    noGutters
  >
    <v-col cols="12">
      <label class="generic-label">
        Role
      </label>
    </v-col>
    <v-col class="pt-2 pb-9">
      <v-radio-group
        id="owner-role-options"
        v-model="selectedPartyType"
        class="mt-0 pr-2"
        inline
        hideDetails="true"
      >
        <v-tooltip
          v-for="role in HomeOwnerRoles"
          :key="role.id"
          location="top"
          contentClass="top-tooltip pa-5"
          transition="fade-transition"
        >
          <template #activator="{ props }">
            <v-radio
              :id="role.id"
              :value="role.model"
              :class="role.class"
              :disabled="isDisabledRadio(role.model)"
            >
              <template #label>
                <div
                  v-bind="props"
                  :class="{'underline' : !isDisabledRadio(role.model)}"
                >
                  {{ role.label }}
                </div>
              </template>
            </v-radio>
          </template>
          {{ role.tooltipContent }}
        </v-tooltip>
      </v-radio-group>
    </v-col>
  </v-row>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { defineComponent, PropType, reactive, toRefs, watch } from 'vue'
import { HomeOwnerPartyTypes } from '@/enums'
import { HomeOwnerRoles } from '@/resources'
import { useMhrInformation, useTransferOwners } from '@/composables'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeOwnerRoles',
  props: {
    partyType: {
      type: String as PropType<HomeOwnerPartyTypes>,
      default: null
    }
  },
  emits: ['update:partyType'],
  setup (props, context) {
    const { isFrozenMhrDueToUnitNote } = useMhrInformation()
    const {
      disableNameFields,
      isTransferDueToDeath,
      isTransferToAdminNoWill,
      isTransferDueToSaleOrGift,
      isTransferToExecutorProbateWill,
      isTransferToExecutorUnder25Will,
      isTransferToSurvivingJointTenant
    } = useTransferOwners()

    const localState = reactive({
      selectedPartyType: props.partyType
    })

    /**
     * Returns true when specific transfer type conditions are met for each respective party type
     * @param partyType The specified party type from which to retrieve the conditions
     */
    const isDisabledRadio = (partyType: HomeOwnerPartyTypes): boolean => {
      switch (partyType) {
        case HomeOwnerPartyTypes.OWNER_IND:
        case HomeOwnerPartyTypes.OWNER_BUS:
          return isTransferToExecutorProbateWill.value || isTransferToExecutorUnder25Will.value ||
            isTransferToAdminNoWill.value || isTransferToSurvivingJointTenant.value
        case HomeOwnerPartyTypes.EXECUTOR:
          return disableNameFields.value || isTransferToAdminNoWill.value || isTransferDueToSaleOrGift.value ||
            isFrozenMhrDueToUnitNote.value
        case HomeOwnerPartyTypes.ADMINISTRATOR:
          return isTransferToSurvivingJointTenant.value || isTransferToExecutorUnder25Will.value ||
            isTransferToExecutorProbateWill.value || isTransferDueToSaleOrGift.value || isFrozenMhrDueToUnitNote.value
        case HomeOwnerPartyTypes.TRUSTEE:
          return isTransferDueToDeath.value || isTransferDueToSaleOrGift.value || isFrozenMhrDueToUnitNote.value
      }
    }

    /** Apply local models to store when they change. **/
    watch(() => localState.selectedPartyType, (partyType: HomeOwnerPartyTypes) => {
      context.emit('update:partyType', partyType)
    })

    return {
      HomeOwnerRoles,
      isDisabledRadio,
      disableNameFields,
      HomeOwnerPartyTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.underline {
  border-bottom: 1px dotted $gray7;
  text-decoration: none;
}
</style>
