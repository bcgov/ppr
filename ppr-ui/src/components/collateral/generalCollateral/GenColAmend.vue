<template>
  <v-container class="pa-0">
    <v-card
      id="general-collateral-amendment"
      :class="{ 'invalid-message': showErrorComponent }"
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
          registration. To view the existing General Collateral for this
          registration, conduct a seperate search.
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
            counter="4000"
            filled
            label="Enter the General Collateral to be deleted from this registration."
            class="white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
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
            counter="4000"
            filled
            label="Enter the General Collateral to be added to this registration."
            class="white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
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
    }
  },
  emits: ['valid'],
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
      valid: computed((): boolean => {
        return (localState.delDesc?.length || 0) <= 4000
      })
    })

    const onSubmitForm = () => {
      const newGeneralCollateral = localState.generalCollateral
      const amendedGC = {
        descriptionAdd: localState.addDesc,
        descriptionDelete: localState.delDesc
      }
      if (newGeneralCollateral.length > 0) {
        if (newGeneralCollateral[newGeneralCollateral.length - 1].addedDateTime !== undefined) {
          newGeneralCollateral.push(amendedGC)
        } else {
          newGeneralCollateral[newGeneralCollateral.length - 1] = amendedGC
        }
      } else {
        newGeneralCollateral.push(amendedGC)
      }
      setGeneralCollateral(newGeneralCollateral)
      emit('closeGenColAmend')
    }

    const resetFormAndData = () => {
      emit('closeGenColAmend')
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
