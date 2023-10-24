<template>
  <v-card
    id="mhr-home-land-ownership"
    flat
    rounded
    class="mhr-home-land-ownership pa-8"
  >
    <v-row no-gutters>
      <v-col
        cols="12"
        sm="3"
      >
        <label
          class="generic-label"
          for="ownership"
        >
          Land Lease or Ownership
        </label>
      </v-col>
      <v-col
        cols="12"
        sm="9"
      >
        <v-checkbox
          id="ownership"
          v-model="isOwnLand"
          label="The manufactured home is located on land that the homeowners own,
                 or on which they have a registered lease of 3 years or more."
          class="my-0 py-0 px-0 ownership-checkbox"
          data-test-id="ownership-checkbox"
        />
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'HomeLandOwnership',
  setup () {
    const {
      setMhrRegistrationOwnLand
    } = useStore()
    const {
      getMhrRegistrationOwnLand
    } = storeToRefs(useStore())

    const localState = reactive({
      isOwnLand: !!getMhrRegistrationOwnLand.value
    })

    watch(() => localState.isOwnLand, (val: boolean) => {
      setMhrRegistrationOwnLand(val)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(.mhr-home-land-ownership) {

  .ownership-checkbox {
    label {
      line-height: 24px;
    }
    .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
