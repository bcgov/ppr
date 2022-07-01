<template>
  <v-card flat rounded id="mhr-home-certification" class="mt-8 pa-8 pr-6">
    <v-row no-gutters>
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': false}">Certification</label>
      </v-col>
      <v-col cols="12" sm="10" class="pl-2">
        <v-radio-group
          id="certification-option-btns"
          v-model="certificationOption"
          class="mt-0" row
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

        <!-- CSA Section -->
        <template v-if="isCsaOption">
          <v-divider class="my-9 mx-0" />
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
                  id="csa-standard"
                  class="pt-4 pr-2"
                  label="CSA Standard (Optional)"
                  v-model="csaStandard"
                />
              </v-form>
            </v-col>
          </v-row>
        </template>

        <!-- Engineer Section -->
        <template v-if="isEngineerOption">
          <v-divider class="my-9 mx-0" />
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
                  ref="datePicker"
                  id="date-of-engineer-report"
                  class="pt-4 pr-2"
                  title="Date of Engineer's Report"
                  :minDate="minDate"
                  :maxDate="today"
                  :nudge-top="180"
                  :nudge-right="150"
                  :inputRules="engineerReportDate ? required('Select a date of engineer\'s report'): []"
                  @emitDate="engineerReportDate = $event "
                />
              </v-form>
            </v-col>
          </v-row>
        </template>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { SharedDatePicker } from '@/components/common'
import { HomeCertificationOptions } from '@/enums'
import { useInputRules } from '@/composables'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { createUtcDate, dateToYyyyMmDd } from '@/utils'

export default defineComponent({
  name: 'HomeCertification',
  components: {
    SharedDatePicker
  },
  props: {},
  setup (props, context) {
    const {
      setMhrHomeDescription
    } = useActions<any>([
      'setMhrHomeDescription'
    ])
    const {
      getMhrRegistrationHomeDescription
    } = useGetters<any>([
      'getMhrRegistrationHomeDescription'
    ])

    // Composable(s)
    const {
      customRules,
      invalidSpaces,
      maxLength,
      required
    } = useInputRules()

    const localState = reactive({
      homeCertificationValid: false,
      certificationOption: null as HomeCertificationOptions,
      csaNumber: '',
      csaStandard: '',
      csaStandardOptions: ['A277', 'Z240'],
      engineerName: '',
      engineerReportDate: '',
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
          (localState.isEngineerOption && localState.isEngineerValid)
      }),
      today: computed(() => {
        const todayDate = new Date()
        return todayDate.toLocaleDateString('en-CA')
      }),
      minDate: computed(() => {
        // Determined by YEAR value in Manufacturers, Make, Model Section
        const utcDate = createUtcDate(getMhrRegistrationHomeDescription.value?.baseInformation.year, 0, 1)
        return dateToYyyyMmDd(utcDate)
      })
    })

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
    watch(() => localState.engineerReportDate, () => {
      setMhrHomeDescription({ key: 'engineerReportDate', value: localState.engineerReportDate })
    })

    /** Clear/reset forms when select option changes. **/
    watch(() => localState.certificationOption, async () => {
      if (localState.isCsaOption) {
        // @ts-ignore - function exists
        await context.refs.engineerForm?.resetValidation()
        localState.engineerName = ''
        localState.engineerReportDate = ''
      }
      if (localState.isEngineerOption) {
        // @ts-ignore - function exists
        await context.refs.csaForm?.resetValidation()
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
