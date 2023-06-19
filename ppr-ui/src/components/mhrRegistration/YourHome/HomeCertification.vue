<template>
  <v-card flat rounded id="mhr-home-certification" class="mt-8 pa-8 pr-6" :class="{'py-10': !showRadio}">
    <v-row no-gutters>
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': validate}">Certification</label>
      </v-col>
      <v-col cols="12" sm="10" class="pl-1">
        <template v-if="showRadio">
          <v-radio-group
            id="certification-option-btns"
            v-model="certificationOption"
            class="mt-0 pr-1" row
            hide-details="true"
          >
            <v-radio
              id="csa-option"
              class="csa-radio"
              label="CSA Number"
              active-class="selected-radio"
              :value="HomeCertificationOptions.CSA"
            />
            <v-radio
              id="engineer-option"
              class="engineer-radio"
              label="Engineer's Inspection"
              active-class="selected-radio"
              :value="HomeCertificationOptions.ENGINEER_INSPECTION"
            />
          </v-radio-group>
          <v-divider class="my-9 ml-0 mr-2" v-if="!!certificationOption"/>
        </template>

        <!-- CSA Section -->
        <div v-show="isCsaOption">
          <v-row no-gutters>
            <v-col cols="12">
              <v-form id="csa-form" ref="csaForm" v-model="isCsaValid">
                <label class="generic-label" for="csa-number">CSA Number</label>
                <v-text-field
                  filled
                  id="csa-number"
                  class="pt-4 pr-2"
                  label="CSA Number"
                  v-model="csaNumber"
                  :rules="csaNumberRules"
                />

                <label class="generic-label" for="csa-standard">CSA Standard</label>
                <v-select
                  filled
                  :items="csaStandardOptions"
                  clearable
                  id="csa-standard"
                  class="pt-4 pr-2"
                  label="CSA Standard (Optional)"
                  v-model="csaStandard"
                />
              </v-form>
            </v-col>
          </v-row>
        </div>

        <!-- Engineer Section -->
        <div v-show="isEngineerOption" v-if="showEngineerOption">
          <v-row no-gutters>
            <v-col cols="12">
              <v-form id="engineer-form" ref="engineerForm" v-model="isEngineerValid">
                <label class="generic-label" for="engineer-name">Engineer's Name</label>
                <v-text-field
                  filled
                  id="engineer-name"
                  class="pt-4 pr-2"
                  label="Engineer's Name"
                  v-model="engineerName"
                  :rules="nameRules"
                />

                <label class="generic-label" for="date-of-engineer-report">Date of Engineer's Report</label>
                <SharedDatePicker
                  v-if="isEngineerOption"
                  ref="datePicker"
                  id="date-of-engineer-report"
                  class="pt-4 pr-2"
                  title="Date of Engineer's Report"
                  :minDate="minDate"
                  :maxDate="today"
                  nudge-top="180"
                  nudge-right="150"
                  :initialValue="engineerDate"
                  :inputRules="required('Select a date of engineer\'s report')"
                  @emitDate="engineerDate = $event"
                  @emitCancel="engineerDate = ''"
                />
              </v-form>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { SharedDatePicker } from '@/components/common'
import { HomeCertificationOptions } from '@/enums'
import { useInputRules, useMhrValidations } from '@/composables'
import { useStore } from '@/store/store'
import { createUtcDate, localTodayDate } from '@/utils/date-helper'
import { storeToRefs } from 'pinia'
/* eslint-disable no-unused-vars */
import { FormIF } from '@/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'HomeCertification',
  components: {
    SharedDatePicker
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { setMhrHomeDescription } = useStore()
    const { getMhrRegistrationHomeDescription, getMhrRegistrationValidationModel,
      isMhrManufacturerRegistration } = storeToRefs(useStore())
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
    const csaForm = ref(null) as FormIF
    const engineerForm = ref(null) as FormIF
    const datePicker = ref(null) as FormIF

    const localState = reactive({
      homeCertificationValid: false,
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
      nameRules: computed((): Array<Function> => {
        return customRules(
          required('Enter the engineer\'s name'),
          maxLength(30),
          invalidSpaces()
        )
      }),
      csaNumberRules: computed((): Array<Function> => {
        return customRules(
          required('Enter a CSA number'),
          maxLength(10),
          invalidSpaces()
        )
      }),
      isHomeCertificationValid: computed((): boolean => {
        return (localState.isCsaOption && localState.isCsaValid) ||
          (localState.isEngineerOption && localState.isEngineerValid && !!localState.engineerDate)
      }),
      today: computed(() => localTodayDate()),
      minDate: computed(() => {
        // Determined by YEAR value in Manufacturers, Make, Model Section
        const utcDate = createUtcDate(getMhrRegistrationHomeDescription.value?.baseInformation.year, 0, 1)
        return localTodayDate(utcDate)
      }),
      showRadio: computed(() => !isMhrManufacturerRegistration.value),
      showEngineerOption: computed(() => !isMhrManufacturerRegistration.value)
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
    })
    watch(() => props.validate, async (val: boolean) => {
      await validateForms()
    })

    /** Clear/reset forms when select option changes. **/
    watch(() => localState.certificationOption, async () => {
      if (localState.isCsaOption) {
        // @ts-ignore - function exists
        engineerForm.value?.resetValidation()
        props.validate && await validateForms()

        localState.engineerName = ''
        localState.engineerDate = ''
      }
      if (localState.isEngineerOption) {
        // @ts-ignore - function exists
        csaForm.value?.resetValidation()
        props.validate && await validateForms()

        localState.csaNumber = ''
        localState.csaStandard = ''
      }
    })
    return {
      HomeCertificationOptions,
      required,
      ...toRefs(localState)
    }
  }
})
/* eslint-enable no-unused-vars */
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .theme--light.v-icon.mdi-close {
  color: $primary-blue !important;
}
.csa-radio {
  width: 47%;
  margin-right: 20px !important;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
}

.engineer-radio {
  width: 50%;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
  margin-right: 0px !important;
}
.selected-radio {
  border: 1px solid $app-blue;
  background-color: white;
  ::v-deep .theme--light.v-label:not(.v-label--is-disabled), .theme--light.v-messages {
    color: $gray9 !important;
  }
}

::v-deep {
  .theme--light.v-select .v-select__selection--comma {
    color: $gray9;
  }
  .v-list-item .v-list-item__title, .v-list-item .v-list-item__subtitle {
    color: $gray7;
  }
  .v-list-item--link[aria-selected='true'] {
    background-color: $blueSelected !important;
    .v-list-item__title, .v-list-item .v-list-item__subtitle {
      color: $app-blue !important;
    }
  }
  .v-list-item--link:hover {
    background-color: $gray1 !important;
    .v-list-item__title, .v-list-item .v-list-item__subtitle {
      color: $app-blue !important;
    }
  }
}
</style>
