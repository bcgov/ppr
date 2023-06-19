<template>
  <div>
    <v-card flat class="py-6 px-8 rounded">
      <v-form ref="makeModelComboForm" v-model="makeModelValid">
        <v-row id="mhr-home-manufacturer-name">
          <v-col cols="2">
            <label
              class="generic-label"
              for="manufacturer-name"
              :class="{ 'error-text': validate && hasError(nameRef) }"
            >
              Manufacturer's Name
            </label>
          </v-col>
          <v-col cols="10">
            <v-text-field
              id="manufacturer-name"
              ref="nameRef"
              v-model="manufacturerName"
              filled
              :disabled="isMhrManufacturerRegistration"
              :class="{ 'unselectable' : isMhrManufacturerRegistration }"
              :rules="manufacturerNameRules"
              label="Business Legal Name"
              data-test-id="manufacturer-name"
            />
          </v-col>
        </v-row>

        <ManufacturedYearInput v-if="!isMhrManufacturerRegistration" :validate="validate" />
        <ManufacturedYearSelect v-else :validate="validate" />

        <v-divider class="mt-2 mb-5 mx-0 w-100" />

        <v-row id="mhr-home-manufacturer-make">
          <v-col cols="2">
            <label
              class="generic-label"
              for="manufacturer-make"
              :class="{ 'error-text': validate && hasError(makeRef) }"
            >Make</label>
          </v-col>
          <v-col cols="10">
            <v-text-field
              id="manufacturer-make"
              ref="makeRef"
              v-model="make"
              filled
              :rules="makeRules"
              label="Make"
              data-test-id="manufacturer-make"
            />
          </v-col>
        </v-row>

        <v-row id="mhr-home-manufacturer-model">
          <v-col cols="2">
            <label
              class="generic-label"
              for="manufacturer-model"
              :class="{ 'error-text': validate && hasError(modelRef) }"
            >Model</label>
          </v-col>
          <v-col cols="10">
            <v-text-field
              id="manufacturer-model"
              ref="modelRef"
              v-model="model"
              filled
              :rules="modelRules"
              label="Model"
              data-test-id="manufacturer-model"
            >
            </v-text-field>
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
} from 'vue-demi'
import { useStore } from '@/store/store'
import { useInputRules, useMhrValidations } from '@/composables/'
import { storeToRefs } from 'pinia'
import { FormIF } from '@/interfaces'
import ManufacturedYearInput from './ManufacturedYearInput.vue'
import ManufacturedYearSelect from './ManufacturedYearSelect.vue'

export default defineComponent({
  components: { ManufacturedYearInput, ManufacturedYearSelect },
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

    const combinedMakeModelLengthRule = (localState): Array<Function> => {
      return [
        () => (0 || localState.model?.length) + (0 || localState.make?.length) <= 65 ||
          'Make and Model combined cannot exceed 65 characters'
      ]
    }

    const makeRules = computed((): Array<Function> =>
      customRules(
        required('Enter a make'),
        combinedMakeModelLengthRule(localState)
      )
    )

    const modelRules = computed((): Array<Function> =>
      customRules(
        required('Enter a model'),
        combinedMakeModelLengthRule(localState)
      )
    )

    const manufacturerNameRules = computed((): Array<Function> =>
      customRules(
        required("Enter a manufacturer's name or enter \"Unknown\" "),
        maxLength(65)
      )
    )

    const localState = reactive({
      makeModelValid: false,
      manufacturerName: getMhrRegistrationManufacturerName.value,
      make: getMhrRegistrationHomeMake.value,
      model: getMhrRegistrationHomeModel.value
    })

    watch(() => localState.manufacturerName, (val: string) => {
      setMhrHomeDescription({ key: 'manufacturer', value: val })
    })

    watch(() => localState.make, (val: string) => {
      setMhrHomeBaseInformation({ key: 'make', value: val })
    })

    watch(() => localState.model, (val: string) => {
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
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
::v-deep .unselectable {
  user-select: none;
}
</style>
