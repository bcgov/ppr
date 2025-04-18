<template>
  <v-row
    id="home-owners-roles"
    no-gutters
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
        hide-details="true"
      >
        <v-tooltip
          v-for="role in HomeOwnerRoles"
          :key="role.id"
          location="top"
          content-class="top-tooltip pa-5"
          transition="fade-transition"
        >
          <template #activator="{ props }">
            <v-radio
              :id="role.id"
              :value="role.model"
              :class="role.class"
              :disabled="(isDisabledRadio(role.model) && selectedPartyType !== role.model) ||
                (disableRoles && selectedPartyType !== role.model)"
            >
              <template #label>
                <div
                  v-bind="props"
                  :class="{'underline' : !isDisabledRadio(role.model) || selectedPartyType === role.model}"
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
import type { PropType} from 'vue';
import { defineComponent, reactive, toRefs, watch } from 'vue'
import { HomeOwnerPartyTypes } from '@/enums'
import { HomeOwnerRoles } from '@/resources'
import { useTransferOwners } from '@/composables'


export default defineComponent({
  name: 'HomeOwnerRoles',
  props: {
    partyType: {
      type: String as PropType<HomeOwnerPartyTypes>,
      default: null
    },
    disableRoles: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:partyType'],
  setup (props, context) {
    const {
      disableNameFields,
      isTransferWithoutBillOfSale
    } = useTransferOwners()

    const localState = reactive({
      selectedPartyType:
        // treat BUS type as IND to properly display selected role
        props.partyType === HomeOwnerPartyTypes.OWNER_BUS ? HomeOwnerPartyTypes.OWNER_IND : props.partyType
    })

    /**
     * Returns true when specific transfer type conditions are met for each respective party type
     */
    const isDisabledRadio = (): boolean => {
      return disableNameFields.value && !isTransferWithoutBillOfSale.value
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
