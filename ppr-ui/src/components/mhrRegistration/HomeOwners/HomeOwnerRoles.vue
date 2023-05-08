<template>
  <v-row no-gutters id="home-owners-roles">
    <v-col cols="12">
      <label class="generic-label">
        Role
      </label>
    </v-col>
    <v-col class="pt-2 pb-9">
      <v-radio-group
        id="owner-role-options"
        class="mt-0 pr-2" row
        hide-details="true"
        v-model="selectedPartyType"
      >
        <v-tooltip
          v-for="role in HomeOwnerRoles"
          :key="role.id"
          top
          nudge-right="18"
          content-class="top-tooltip pa-5"
          transition="fade-transition"
        >
          <template v-slot:activator="{ on }">
            <v-radio
              v-on="on"
              :id="role.id"
              :class="role.class"
              active-class="selected-radio"
              :disabled="isDisabledRadio(role.model)"
              v-model="role.model"
            >
              <template v-slot:label>
                <div :class="{'underline' : !isDisabledRadio(role.model)}">{{ role.label }}</div>
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
import { defineComponent, PropType, reactive, toRefs, watch } from '@vue/composition-api'
import { HomeOwnerPartyTypes } from '@/enums'
import { HomeOwnerRoles } from '@/resources'
import { useMhrInformation, useTransferOwners } from '@/composables'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeLocationType',
  props: {
    partyType: {
      type: String as PropType<HomeOwnerPartyTypes>,
      default: null
    }
  },
  emits: ['update:partyType'],
  setup (props, context) {
    const { isFrozenMhr } = useMhrInformation()
    const {
      disableNameFields,
      isTransferDueToDeath,
      isTransferToAdminNoWill,
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
            isTransferToAdminNoWill.value
        case HomeOwnerPartyTypes.EXECUTOR:
          return disableNameFields.value || isTransferToAdminNoWill.value || isFrozenMhr.value
        case HomeOwnerPartyTypes.ADMINISTRATOR:
          return isTransferToSurvivingJointTenant.value || isTransferToExecutorUnder25Will.value ||
            isTransferToExecutorProbateWill.value || isFrozenMhr.value
        case HomeOwnerPartyTypes.TRUSTEE:
          return isTransferDueToDeath.value || isFrozenMhr.value
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
