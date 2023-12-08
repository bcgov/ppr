<template>
  <v-container
    class="pa-0"
    :class="{ 'border-error-left': showErrorBar }"
  >
    <v-card
      id="general-collateral-amendment"
      :class="cardClass"
      flat
    >
      <v-row
        noGutters
        class="py-4"
      >
        <v-col class="generic-label">
          General Collateral
        </v-col>
      </v-row>
      <v-row noGutters>
        <v-col class="summary-text">
          Indicate the General Collateral to be deleted from or added to this
          registration.
          <p class="pt-2 mb-0 mr-2">
            Note: If you are pasting text, <strong>we recommend pasting plain text</strong> to avoid formatting and font
            issues with PDF and printed registrations. If you have pasted text other than plain text, verify that your
            documents are correct. If they are not correct, they will need to be amended.
          </p>
        </v-col>
      </v-row>
      <v-row
        noGutters
        class="pt-8"
      >
        <v-col class="generic-label">
          General Collateral to be Deleted
        </v-col>
      </v-row>
      <v-row noGutters>
        <v-col class="pr-4">
          <WysiwygEditor
            class="mt-4"
            placeHolderText="Enter the General Collateral to be deleted from this registration"
            :editorContent="delDesc"
            @emitEditorContent="delDesc = $event"
          />
        </v-col>
      </v-row>
      <v-row
        noGutters
        class="mt-4"
      >
        <v-col class="generic-label">
          General Collateral to be Added
        </v-col>
      </v-row>
      <v-row noGutters>
        <v-col class="pr-4">
          <WysiwygEditor
            placeHolderText="Enter the General Collateral to be added to this registration"
            :editorContent="addDesc"
            @emitEditorContent="addDesc = $event"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pr-7">
          <div class="form__row form__btns float-right">
            <v-btn
              id="done-btn-gen-col"
              size="large"
              class="ml-auto mr-2"
              color="primary"
              @click="onSubmitForm()"
            >
              Done
            </v-btn>

            <v-btn
              id="cancel-btn-gen-col"
              size="large"
              variant="outlined"
              color="primary"
              @click="resetFormAndData()"
            >
              Cancel
            </v-btn>
          </div>
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
  computed,
  watch
} from 'vue'
import { useStore } from '@/store/store'
// local
import { GeneralCollateralIF } from '@/interfaces'
import { storeToRefs } from 'pinia'
import { WysiwygEditor } from '@/components/common'

export default defineComponent({
  components: {
    WysiwygEditor
  },
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'closeGenColAmend'
  ],
  setup (props, { emit }) {
    const { setGeneralCollateral } = useStore()
    const { getGeneralCollateral } = storeToRefs(useStore())

    const localState = reactive({
      delDesc: '',
      addDesc: '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      }),
      cardClass: computed((): string => {
        if (localState.showErrorComponent) {
          return 'invalid-message'
        }
        if (localState.showErrorBar) {
          return 'border-over'
        }
        return ''
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    const onSubmitForm = () => {
      const newGeneralCollateral = localState.generalCollateral

      if (localState.addDesc || localState.delDesc) {
        if (localState.addDesc?.replace(/(<([^>]+)>)/ig, '').trim().length === 0) localState.addDesc = ''
        if (localState.delDesc?.replace(/(<([^>]+)>)/ig, '').trim().length === 0) localState.delDesc = ''
        const amendedGC = {
          descriptionAdd: localState.addDesc,
          descriptionDelete: localState.delDesc
        }
        if (newGeneralCollateral.length > 0) {
          // if there is no general collateral at the end of the array with a blank date time,
          // we know we are adding
          if (newGeneralCollateral[newGeneralCollateral.length - 1].addedDateTime !== undefined) {
            newGeneralCollateral.push(amendedGC)
          } else {
            // otherwise, pop the old general collateral off the end of the array, and push the new one
            // one (pop and push required to keep refs)
            newGeneralCollateral.pop()
            newGeneralCollateral.push(amendedGC)
          }
        } else {
          newGeneralCollateral.push(amendedGC)
        }
        if (localState.addDesc === '' && localState.delDesc === '') { // remove empty collateral altogether
          newGeneralCollateral.pop()
        }
        setGeneralCollateral(newGeneralCollateral)
      }
      emit('closeGenColAmend', true)
    }

    const resetFormAndData = () => {
      emit('closeGenColAmend', true)
    }

    /** Called when general collateral updates */
    watch(() => localState.generalCollateral, async (gc: GeneralCollateralIF[]) => {
      if (gc.length > 0) {
        if (gc[gc.length - 1].addedDateTime === undefined) {
          localState.addDesc = gc[gc.length - 1].descriptionAdd || ''
          localState.delDesc = gc[gc.length - 1].descriptionDelete || ''
        }
      }
    }, { deep: true, immediate: true })

    return {
      onSubmitForm,
      resetFormAndData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.border-error-left {
  margin-left: -31px;
}

.border-over {
  margin-left: 25px;
}
</style>
