<template>
  <div>
    <v-card
      flat
      class="py-6 px-8 rounded"
    >
      <v-form
        ref="makeModelComboForm"
        v-model="makeModelValid"
      >
        <v-row id="mhr-home-manufacturer-name">
          <v-col cols="3">
            <label
              class="generic-label"
              for="manufacturer-name"
              :class="{ 'error-text': validate && hasError(nameRef) }"
            >
              Manufacturer's Name
            </label>
            <UpdatedBadge
              v-if="isMhrCorrection"
              :baseline="correctionState.manufacturer.baseline"
              :currentState="correctionState.manufacturer.currentState"
            />
          </v-col>
          <v-col cols="9">
            <v-text-field
              id="manufacturer-name"
              ref="nameRef"
              v-model="manufacturerName"
              variant="filled"
              color="primary"
              :disabled="isMhrManufacturerRegistration"
              :class="{ 'unselectable' : isMhrManufacturerRegistration }"
              :rules="manufacturerNameRules"
              label="Business Legal Name"
              data-test-id="manufacturer-name"
            />
          </v-col>
        </v-row>

        <ManufacturedYearInput
          v-if="!isMhrManufacturerRegistration"
          :validate="validate"
        />
        <ManufacturedYearSelect
          v-else
          :validate="validate"
        />

        <v-divider class="mt-2 mb-5 mx-0 w-100" />

        <v-row id="mhr-home-manufacturer-make">
          <v-col cols="3">
            <label
              class="generic-label"
              for="manufacturer-make"
              :class="{ 'error-text': validate && hasError(makeRef) }"
            >Make</label>
            <UpdatedBadge
              v-if="isMhrCorrection"
              :baseline="correctionState.make.baseline"
              :currentState="correctionState.make.currentState"
            />
          </v-col>
          <v-col cols="9">
            <v-text-field
              id="manufacturer-make"
              ref="makeRef"
              v-model="make"
              variant="filled"
              color="primary"
              :rules="makeRules"
              label="Make"
              data-test-id="manufacturer-make"
            />
          </v-col>
        </v-row>

        <v-row id="mhr-home-manufacturer-model">
          <v-col cols="3">
            <label
              class="generic-label"
              for="manufacturer-model"
              :class="{ 'error-text': validate && hasError(modelRef) }"
            >Model</label>
            <UpdatedBadge
              v-if="isMhrCorrection"
              :baseline="correctionState.model.baseline"
              :currentState="correctionState.model.currentState"
            />
          </v-col>
          <v-col cols="9">
            <v-text-field
              id="manufacturer-model"
              ref="modelRef"
              v-model="model"
              variant="filled"
              color="primary"
              :rules="modelRules"
              label="Model"
              data-test-id="manufacturer-model"
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue'
import { useStore } from '@/store/store'
import { useInputRules, useMhrCorrections, useMhrValidations } from '@/composables/'
import { storeToRefs } from 'pinia'
import { FormIF } from '@/interfaces'
import ManufacturedYearInput from './ManufacturedYearInput.vue'
import ManufacturedYearSelect from './ManufacturedYearSelect.vue'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  components: { ManufacturedYearInput, ManufacturedYearSelect, UpdatedBadge },
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    // Form Refs
    const makeModelComboForm = ref(null) as FormIF
    const nameRef = ref(null)

    const makeRef = ref(null)
    const modelRef = ref(null)
    const { setMhrHomeDescription, setMhrHomeBaseInformation } = useStore()
    const {
      // Getters
      getMhrRegistrationValidationModel,
      getMhrRegistrationManufacturerName,
      getMhrRegistrationHomeMake,
      isMhrManufacturerRegistration,
      getMhrRegistrationHomeModel
    } = storeToRefs(useStore())
    const {
      customRules,
      required,
      maxLength,
      greaterThan
    } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      hasError,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { correctionState, isMhrCorrection } = useMhrCorrections()

    const combinedMakeModelLengthRule = (localState): Array<()=>string|boolean> => {
      return [
        () => (0 || localState.model?.length) + (0 || localState.make?.length) <= 65 ||
          'Make and Model combined cannot exceed 65 characters'
      ]
    }

    const makeRules = computed((): Array<()=>string|boolean> =>
      customRules(
        (!localState.model ? required('Enter at least the make or the model of the home') : true),
        combinedMakeModelLengthRule(localState)
      )
    )

    const modelRules = computed((): Array<()=>string|boolean> =>
      customRules(
        (!localState.make ? required('Enter at least the make or the model of the home') : true),
        combinedMakeModelLengthRule(localState)
      )
    )

    const manufacturerNameRules = computed((): Array<()=>string|boolean> =>
      customRules(
        required("Enter a manufacturer's name or enter \"Unknown\" "),
        maxLength(65)
      )
    )

    const localState = reactive({
      makeModelValid: false,
      manufacturerName: getMhrRegistrationManufacturerName.value,
      make: getMhrRegistrationHomeMake.value || '',
      model: getMhrRegistrationHomeModel.value || ''
    })

    watch(() => localState.manufacturerName, (val: string) => {
      setMhrHomeDescription({ key: 'manufacturer', value: val })
    })

    watch(() => localState.make, (val: string) => {
      props.validate && makeModelComboForm.value?.validate()
      setMhrHomeBaseInformation({ key: 'make', value: val })
    })

    watch(() => localState.model, (val: string) => {
      props.validate && makeModelComboForm.value?.validate()
      setMhrHomeBaseInformation({ key: 'model', value: val })
    })

    watch(() => localState.makeModelValid, (val: boolean) => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.MAKE_MODEL_VALID, val)
    })

    watch(() => props.validate, () => {
      makeModelComboForm.value?.validate()
    })

    return {
      hasError,
      nameRef,
      makeRef,
      modelRef,
      makeModelComboForm,
      makeRules,
      modelRules,
      manufacturerNameRules,
      maxLength,
      greaterThan,
      isMhrManufacturerRegistration,
      isMhrCorrection,
      correctionState,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
:deep(.unselectable) {
  user-select: none;
  .v-label {
    pointer-events: none;
  }
}
</style>
