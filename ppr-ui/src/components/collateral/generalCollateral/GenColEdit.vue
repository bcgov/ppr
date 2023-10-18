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
        <v-col cols="9" class="pr-6">
          <WysiwygEditor
            v-if="isTiptapEnabled"
            placeHolderText="Description of General Collateral"
            :editorContent="newDesc"
            @emitEditorContent="newDesc = $event"
          />

          <p class="summary-text mt-8">
            Note: If you are pasting text,
            <strong>we recommend pasting plain text</strong>
            to avoid formatting and font issues with PDF and printed
            registrations. If you have pasted text other than plain text, verify
            that your documents are correct. If they are not correct, they will
            need to be amended.
          </p>
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
} from 'vue'
import { useStore } from '@/store/store'
// local
import { RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { storeToRefs } from 'pinia'

import { WysiwygEditor } from '@/components/common'

export default defineComponent({
  name: 'GenColEdit',
  components: {
    WysiwygEditor
  },
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { setGeneralCollateral } = useStore()
    const { getGeneralCollateral, getRegistrationFlowType, isTiptapEnabled } = storeToRefs(useStore())

    const localState = reactive({
      newDesc: getGeneralCollateral.value[0]?.description || '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
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

    watch(
      () => localState.newDesc,
      (val: string) => {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (val) {
            setGeneralCollateral([{ description: val }])
          } else {
            setGeneralCollateral([])
          }
        }
      }
    )

    watch(
      () => localState.generalCollateral,
      (val: GeneralCollateralIF[]) => {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (val.length > 0 && val[0].description !== localState.newDesc) {
            localState.newDesc = val[0].description
          }
        }
      }
    )

    return {
      isTiptapEnabled,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
