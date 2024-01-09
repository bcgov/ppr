<template>
  <div class="mhr-location-change mt-8">
    <FormCard
      :label="content.sideLabel"
      :showErrors="false"
      :class="{'border-error-left': false}"
    >
      <template #formSlot>
        <v-select
          id="location-select"
          v-model="locationChangeType"
          :items="roleBasedLocationChangeTypes"
          itemTitle="title"
          itemValue="type"
          variant="filled"
          label="Location Change Type"
          color="primary"
        />
      </template>
    </FormCard>

    <div v-if="isTransportPermitType">
      [Transport Permit placeholder]
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { ContentIF } from '@/interfaces'
import { locationChangeTypes } from '@/resources/mhr-transfers/transport-permits'
import { FormCard } from '../common'
import { LocationChangeTypes } from '@/enums'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'


export default defineComponent({
  name: 'LocationChange',
  components: { FormCard },
  props: {
    content: {
      type: Object as () => ContentIF,
      default: () => {}
    },
  },
  emits: ['updateLocationType'],
  setup (props, context) {

    const { isRoleQualifiedSupplier,
      getMhrRegistrationLocation } = storeToRefs(useStore())

    const localState = reactive({
      locationChangeType: null,
      locationInfo: getMhrRegistrationLocation.value,
      roleBasedLocationChangeTypes: computed(() =>
        isRoleQualifiedSupplier.value
          ? locationChangeTypes.slice(0, -1) // qualified supplier does not have the third option in menu
          : locationChangeTypes),
      isTransportPermitType: computed(() => localState.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT)
    })

    watch(() => localState.locationChangeType, val => {
      context.emit('updateLocationType', val)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

</style>
