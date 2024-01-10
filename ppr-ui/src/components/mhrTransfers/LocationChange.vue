<template>
  <div class="mhr-location-change mt-8">
    <FormCard
      :label="content.sideLabel"
      :showErrors="false"
      :class="{'border-error-left': false}"
    >
      <template #formSlot>
        <v-select
          id="location-change-select"
          v-model="state.locationChangeType"
          :items="state.roleBasedLocationChangeTypes"
          itemTitle="title"
          itemValue="type"
          variant="filled"
          label="Location Change Type"
        />
      </template>
    </FormCard>

    <div
      v-if="state.isTransportPermitType"
      id="transport-permit-location-type"
      class="pt-7"
    >
      [Transport Permit placeholder]
    </div>
  </div>
</template>

<script setup lang="ts">

import { LocationChangeTypes } from "@/enums"
import { ContentIF } from "@/interfaces"
import { locationChangeTypes } from "@/resources/mhr-transfers/transport-permits"
import { useStore } from "@/store/store"
import { toRefs, reactive, computed, watch } from "vue"
import { FormCard } from "../common"

defineProps<{
  content?: ContentIF
}>()

const emit = defineEmits(['updateLocationType'])

const { isRoleQualifiedSupplier } = toRefs(useStore())

const state = reactive({
  locationChangeType: null,
  roleBasedLocationChangeTypes: computed(() =>
    isRoleQualifiedSupplier.value
      ? locationChangeTypes.slice(0, -1) // qualified supplier does not have the third option in menu
      : locationChangeTypes),
  isTransportPermitType: computed(() => state.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT)
})

watch(() => state.locationChangeType, val => {
  emit('updateLocationType', val)
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
