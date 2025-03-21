<template>
  <v-card
    id="mhr-home-certification"
    class="mt-8 pa-8 pr-6"
    flat
    rounded
    :class="{ 'py-10': isMhrManufacturerRegistration }"
  >
    <v-row no-gutters>
      <v-col
        cols="12"
        sm="3"
      >
        <label
          class="generic-label"
          :class="{ 'error-text': validate }"
        >Certification</label>
        <UpdatedBadge
          v-if="showUpdatedBadge"
          :action="correctionState.action"
          :baseline="correctionState.homeCertification.baseline"
          :current-state="correctionState.homeCertification.currentState"
        />
      </v-col>
      <v-col
        cols="12"
        sm="9"
      >
        <template v-if="!isMhrManufacturerRegistration">
          <v-radio-group
            v-model="certificationOption"
            class="mt-0 certification-option-btns"
            inline
            hide-details="true"
            :disabled="hasNoCertification"
            :class="{ 'disabled-radio': hasNoCertification }"
            data-test-id="certification-option-btns"
          >
            <v-radio
              id="csa-option"
              class="radio-one"
              label="CSA Number"
              :class="{'selected-radio': certificationOption === HomeCertificationOptions.CSA }"
              :value="HomeCertificationOptions.CSA"
            />
            <v-radio
              id="engineer-option"
              class="radio-two"
              label="Engineer's Inspection"
              :class="{'selected-radio': certificationOption === HomeCertificationOptions.ENGINEER_INSPECTION }"
              :value="HomeCertificationOptions.ENGINEER_INSPECTION"
            />
          </v-radio-group>
          <v-divider
            v-if="!!certificationOption"
            class="my-9 ml-0 mr-2"
          />
        </template>

        <!-- CSA Section -->
        <div v-if="isCsaOption">
          <v-row no-gutters>
            <v-col cols="12">
              <v-form
                id="csa-form"
                ref="csaForm"
                v-model="isCsaValid"
              >
                <label
                  class="generic-label"
                  for="csa-number"
                >CSA Number</label>
                <v-text-field
                  id="csa-number"
                  v-model="csaNumber"
                  variant="filled"
                  color="primary"
                  class="pt-4 pr-2"
                  label="CSA Number"
                  :rules="csaNumberRules"
                />

                <label
                  class="generic-label"
                  for="csa-standard"
                >CSA Standard</label>
                <v-select
                  id="csa-standard"
                  v-model="csaStandard"
                  variant="filled"
                  color="primary"
                  :items="csaStandardOptions"
                  clearable
                  class="pt-4 pr-2"
                  label="CSA Standard (Optional)"
                />
              </v-form>
            </v-col>
          </v-row>
        </div>

        <!-- Engineer Section -->
        <div
          v-if="!isMhrManufacturerRegistration && isEngineerOption"
        >
          <v-row no-gutters>
            <v-col cols="12">
              <v-form
                id="engineer-form"
                ref="engineerForm"
                v-model="isEngineerValid"
              >
                <label
                  class="generic-label"
                  for="engineer-name"
                >Engineer's Name</label>
                <v-text-field
                  id="engineer-name"
                  v-model="engineerName"
                  variant="filled"
                  color="primary"
                  class="pt-4 pr-2"
                  label="Engineer's Name"
                  :rules="nameRules"
                />

                <label
                  class="generic-label"
                  for="date-of-engineer-report"
                >Date of Engineer's Report</label>

                <InputFieldDatePicker
                  v-if="isEngineerOption"
                  id="date-of-engineer-report"
                  ref="datePicker"
                  class=""
                  title="Date of Engineer's Report"
                  :min-date="minDate"
                  :max-date="today"
                  :initial-value="engineerDate"
                  :input-rules="required('Select a date of engineer\'s report')"
                  @emit-date="engineerDate = $event"
                  @emit-cancel="engineerDate = ''"
                />
              </v-form>
            </v-col>
          </v-row>
        </div>

        <!-- Home Certification Checkbox -->
        <template v-if="isRoleStaffReg">
          <v-divider
            v-if="certificationOption"
            class="mt-4 ml-0 mr-2"
          />
          <v-checkbox
            id="no-certification-checkbox"
            v-model="hasNoCertification"
            label="There is no certification available for this home."
            class="mt-8 pt-0 mb-n4 float-left"
            hide-details
          />
          <v-tooltip
            location="top"
            content-class="top-tooltip"
            transition="fade-transition"
          >
            <template #activator="{ props }">
              <v-icon
                class="ml-2 mt-12"
                color="primary"
                v-bind="props"
                data-test-id="no-certification-tooltip"
                tabindex="0"
              >
                mdi-information-outline
              </v-icon>
            </template>
            If a CSA Number or Engineer’s Inspection is not available for this home,
            select this option and enter a description of the safety evidence in the
            Other Information section.
          </v-tooltip>
        </template>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { HomeCertificationOptions } from '@/enums'
import { useStore } from '@/store/store'
import { createDateFromPacificTime, localTodayDate } from '@/utils/date-helper'
import { storeToRefs } from 'pinia'
import type { FormIF } from '@/interfaces'

export default defineComponent({
  name: 'HomeCertification',
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { setMhrHomeDescription } = useStore()
    const {
      getMhrRegistrationHomeDescription, getMhrRegistrationValidationModel,
      isMhrManufacturerRegistration, isRoleStaffReg
    } = storeToRefs(useStore())
    // Composable(s)
    const {
      customRules,
      invalidSpaces,
      maxLength,
      required
    } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { correctionState } = useMhrCorrections()
    const { showUpdatedBadge } = useUpdatedBadges()

    const csaForm = ref(null) as FormIF
    const engineerForm = ref(null) as FormIF
    const datePicker = ref(null) as FormIF

    const localState = reactive({
      certificationOption: getMhrRegistrationHomeDescription.value?.certificationOption || null,
      csaNumber: getMhrRegistrationHomeDescription.value?.csaNumber || '',
      csaStandard: getMhrRegistrationHomeDescription.value?.csaStandard || '',
      csaStandardOptions: ['A277', 'Z240'],
      engineerName: getMhrRegistrationHomeDescription.value?.engineerName || '',
      engineerDate: getMhrRegistrationHomeDescription.value?.engineerDate || '',
      isCsaValid: false,
      isEngineerValid: false,
      isCsaOption: computed((): boolean => {
        return localState.certificationOption === HomeCertificationOptions.CSA
      }),
      isEngineerOption: computed((): boolean => {
        return localState.certificationOption === HomeCertificationOptions.ENGINEER_INSPECTION
      }),
      nameRules: computed((): Array<()=>string|boolean> => {
        return customRules(
          required('Enter the engineer\'s name'),
          maxLength(30),
          invalidSpaces()
        )
      }),
      csaNumberRules: computed((): Array<()=>string|boolean> => {
        return customRules(
          required('Enter a CSA number'),
          maxLength(10),
          invalidSpaces()
        )
      }),
      isHomeCertificationValid: computed((): boolean => {
        return (localState.isCsaOption && localState.isCsaValid) ||
          (localState.isEngineerOption && localState.isEngineerValid && !!localState.engineerDate) ||
          localState.hasNoCertification
      }),
      today: computed(() => localTodayDate(new Date(), true)),
      minDate: computed(() => {
        // Determined by YEAR value in Manufacturers, Make, Model Section
        const ptDate = createDateFromPacificTime(getMhrRegistrationHomeDescription.value?.baseInformation.year, 0, 1)
        return localTodayDate(ptDate)
      }),
      hasNoCertification: getMhrRegistrationHomeDescription.value?.hasNoCertification || false
    })

    const validateForms = async () => {
      if (localState.isCsaOption) {
        csaForm.value?.validate()
      }
      if (localState.isEngineerOption) {
        engineerForm.value?.validate()
        await datePicker.value?.validate()
      }
    }

    /** Apply local models to store when they change. **/
    watch(() => localState.certificationOption, () => {
      setMhrHomeDescription({ key: 'certificationOption', value: localState.certificationOption })
    })
    watch(() => localState.csaNumber, () => {
      setMhrHomeDescription({ key: 'csaNumber', value: localState.csaNumber })
    })
    watch(() => localState.csaStandard, () => {
      setMhrHomeDescription({ key: 'csaStandard', value: localState.csaStandard })
    })
    watch(() => localState.engineerName, () => {
      setMhrHomeDescription({ key: 'engineerName', value: localState.engineerName })
    })
    watch(() => localState.engineerDate, () => {
      setMhrHomeDescription({ key: 'engineerDate', value: localState.engineerDate })
    })
    watch(() => localState.isHomeCertificationValid, (val: boolean) => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.HOME_CERTIFICATION_VALID, val)
    }, { immediate: true })
    watch(() => props.validate, async () => {
      await validateForms()
    })

    /** Clear/reset forms when select option changes. **/
    watch(() => localState.certificationOption, async () => {
      if (localState.isCsaOption) {
        engineerForm.value?.resetValidation()
        props.validate && await validateForms()

        localState.engineerName = ''
        localState.engineerDate = ''
      }
      if (localState.isEngineerOption) {
        csaForm.value?.resetValidation()
        props.validate && await validateForms()

        localState.csaNumber = ''
        localState.csaStandard = ''
      }
    })

    watch(() => localState.hasNoCertification, () => {
      setMhrHomeDescription({ key: 'hasNoCertification', value: localState.hasNoCertification })
      localState.certificationOption = null
      engineerForm.value?.resetValidation()
      csaForm.value?.resetValidation()
      localState.engineerName = ''
      localState.engineerDate = ''
      localState.csaNumber = ''
      localState.csaStandard = ''
    })

    return {
      csaForm,
      engineerForm,
      datePicker,
      HomeCertificationOptions,
      isMhrManufacturerRegistration,
      isRoleStaffReg,
      required,
      correctionState,
      showUpdatedBadge,
      ...toRefs(localState)
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(.theme--light.v-icon.mdi-close) {
  color: $primary-blue !important;
}
.certification-option-btns {
  :deep(.v-selection-control--dirty) {
    border: 1px solid $app-blue;
    background-color: white;
    color: $app-blue;
  }
}
</style>
