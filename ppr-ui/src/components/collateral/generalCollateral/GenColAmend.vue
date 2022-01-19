<template>
  <v-container class="pa-0" :class="{ 'border-error-left': showErrorBar }">
    <v-card
      id="general-collateral-amendment"
      :class="cardClass"
      flat
    >
      <v-row no-gutters class="py-6">
        <v-col class="generic-label">
          General Collateral
        </v-col>
      </v-row>
      <v-row>
        <v-col
          >Indicate the General Collateral to be deleted from or added to this
          registration.
        </v-col>
      </v-row>
      <v-row>
        <v-col class="generic-label">
          General Collateral to be Deleted
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pr-4">
          <v-textarea
            v-model="delDesc"
            id="general-collateral-delete-desc"
            auto-grow
            filled
            label="Enter the General Collateral to be deleted from this registration."
            class="white pt-2 text-input-field"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="generic-label">
          General Collateral to be Added
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pr-4">
          <v-textarea
            v-model="addDesc"
            id="general-collateral-add-desc"
            auto-grow
            filled
            label="Enter the General Collateral to be added to this registration."
            class="white pt-2 text-input-field"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <div class="form__row form__btns">
            <v-btn
              large
              id="done-btn-gen-col"
              class="ml-auto"
              color="primary"
              @click="onSubmitForm()"
            >
              Done
            </v-btn>

            <v-btn
              id="cancel-btn-gen-col"
              large
              outlined
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
  onMounted,
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
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { getGeneralCollateral } = useGetters<any>([
      'getGeneralCollateral'
    ])
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
      cardClass: computed((): string => {
        if (localState.showErrorComponent) {
          return 'invalid-message'
        } 
        if (localState.showErrorBar) {
          return 'border-over'
        }
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    const onSubmitForm = () => {
      const newGeneralCollateral = localState.generalCollateral
      const amendedGC = {
        descriptionAdd: localState.addDesc,
        descriptionDelete: localState.delDesc
      }
      if (localState.addDesc || localState.delDesc) {
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
        setGeneralCollateral(newGeneralCollateral)
      }
      emit('closeGenColAmend', true)
    }

    const resetFormAndData = () => {
      emit('closeGenColAmend', true)
    }

    onMounted(() => {
      const gc = localState.generalCollateral
      if (gc.length > 0) {
        if (gc[gc.length - 1].addedDateTime === undefined) {
          localState.addDesc = gc[gc.length - 1].descriptionAdd
          localState.delDesc = gc[gc.length - 1].descriptionDelete
        }
      }
    })

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
.border-error-left
{
  margin-left: -20px;
}
.border-over
{
  margin-left: 25px;
}
</style>
