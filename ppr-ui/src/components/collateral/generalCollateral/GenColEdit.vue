<template>
  <v-container class="pa-0">
    <v-card
      id="general-collateral"
      :class="{ 'invalid-message': showErrorComponent }"
      flat
    >
      <v-row no-gutters class="py-6">
        <v-col cols="3" class="generic-label pa-4">
          General Collateral
        </v-col>
        <v-col cols="9" class="pr-4">
          <v-textarea
            v-model="newDesc"
            id="general-collateral-new-desc"
            auto-grow
            filled
            label="Description of General Collateral"
            class="white pt-2 text-input-field"
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
  onMounted,
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local
import { RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'GenColEdit',
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { getGeneralCollateral } = useGetters<any>(['getGeneralCollateral'])
    const { getRegistrationFlowType } = useGetters<any>(['getRegistrationFlowType'])
    const { setGeneralCollateral } = useActions<any>(['setGeneralCollateral'])

    const localState = reactive({
      newDesc: '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return getGeneralCollateral.value as GeneralCollateralIF[] || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      })
    })

    onMounted(() => {
      if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
        if (localState.generalCollateral.length > 0) {
          localState.newDesc = localState.generalCollateral[0].description
        }
      }
    })

    watch(() => localState.newDesc, (val: string) => {
      if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
        if (val) {
          setGeneralCollateral([{ description: val }])
        } else {
          setGeneralCollateral([])
        }
      }
    })

    watch(() => localState.generalCollateral, (val: GeneralCollateralIF[]) => {
      if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
        if (val.length > 0 && val[0].description !== localState.newDesc) {
          localState.newDesc = val[0].description
        }
      }
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
