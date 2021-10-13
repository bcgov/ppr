<template>
  <v-container class="pa-0">
    <v-card
      id="general-collateral-amendment"
      :class="{ 'invalid-message': showErrorComponent }"
      flat
    >
      <v-row no-gutters class="py-6">
        <v-col class="generic-label pa-4">
          General Collateral
        </v-col>
      </v-row>
      <v-row>
        <v-col
          >Indicate the General Collater to be deleted from or added to this
          registration. To view the existing General Collateral for this
          registration, conduct a seperate search.
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          General Collateral to be Deleted
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="9" class="pr-4">
          <v-textarea
            v-model="delDesc"
            id="general-collateral-delete-desc"
            auto-grow
            counter="4000"
            filled
            label="Enter the General Collateral to be deleted from this registration."
            class="white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          General Collateral to be Added
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="9" class="pr-4">
          <v-textarea
            v-model="addDesc"
            id="general-collateral-add-desc"
            auto-grow
            counter="4000"
            filled
            label="Enter the General Collateral to be added to this registration."
            class="white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    }
  },
  emits: ['valid'],
  setup (props, { emit }) {
    const { getGeneralCollateral } = useGetters<any>(['getGeneralCollateral'])
    const { setGeneralCollateral } = useActions<any>(['setGeneralCollateral'])

    const localState = reactive({
      delDesc: '',
      addDesc: '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      }),
      valid: computed((): boolean => {
        return (localState.delDesc?.length || 0) <= 4000
      })
    })

    watch(
      () => localState.addDesc,
      (val: string) => {
        setGeneralCollateral([{ descriptionAdd: val }])
      }
    )

    watch(
      () => localState.delDesc,
      (val: string) => {
        setGeneralCollateral([{ descriptionDelete: val }])
      }
    )

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
