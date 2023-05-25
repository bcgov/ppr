<template>
  <v-card flat rounded id="mhr-home-land-ownership" class=" mhr-home-land-ownership">
    <v-row no-gutters>
      <v-col cols="12" sm="2">
        <label class="generic-label" for="ownership">
        Land Lease or Ownership
        </label>
      </v-col>
      <v-col cols="12" sm="10">
        <v-checkbox
          id="ownership"
          label="The manufactured home is located on land that the homeowners own,
                or on which they have a registered lease of 3 years or more."
          v-model="isOwnLand"
          class="my-0 py-0 px-0 ownership-checkbox"
          data-test-id="ownership-checkbox"
        />
       </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'HomeLandOwnership',
  setup () {
    const {
      getMhrRegistrationOwnLand
    } = useGetters<any>([
      'getMhrRegistrationOwnLand'
    ])

    const {
      setMhrRegistrationOwnLand
    } = useActions<any>([
      'setMhrRegistrationOwnLand'
    ])

    const localState = reactive({
      isOwnLand: Boolean(getMhrRegistrationOwnLand.value || false)
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
.mhr-home-land-ownership::v-deep {
  padding: 40px 30px 32px;

  .ownership-checkbox {
    margin-left: 70px;
    label {
      line-height: 24px;
    }
    .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
