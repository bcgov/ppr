<template>
  <v-card flat rounded id="mhr-home-certification" class="mt-8 pa-8">
    <v-row no-gutters>
      <v-col cols="12" sm="2">
        <label class="generic-label" :class="{'error-text': false}">Certification</label>
      </v-col>
      <v-col cols="12" sm="10" class="pl-2">
        <v-radio-group
          v-model="certificationOption"
          class="mt-0" row
          hide-details="true"
        >
          <v-radio
            class="csa-radio"
            label="CSA Number"
            :value="HomeCertificationOptions.CSA"
            id="csa-option"
          />
          <v-radio
            class="engineer-radio"
            label="Engineer's Inspection"
            :value="HomeCertificationOptions.ENGINEER_INSPECTION"
            id="engineer-option"
          />
        </v-radio-group>

        <!-- CSA Section -->
        <template v-if="isCsaOption">
          <v-divider class="my-9 mx-0" />
          <v-form>
            <v-row no-gutters>
              <v-col cols="12">
                <v-form ref="csaForm" v-model="isCsaValid">
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
          </v-form>
        </template>

        <!-- Engineer Section -->
        <template v-if="isEngineerOption">
          <v-divider class="my-9 mx-0" />
          <v-form>
            <v-row no-gutters>
              <v-col cols="12">
                <v-form ref="engineerForm" v-model="isEngineerValid">
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
                    :minDate="minDate"
                    :maxDate="today"
                    :inputRules="required('Select a date of engineer\'s report')"
                    @emitDate="engineerReportDate = $event "
                  />
                </v-form>
              </v-col>
            </v-row>
          </v-form>
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
import { useDateHelper, useInputRules } from '@/composables'
import { useActions, useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'HomeCertification',
  components: {
    SharedDatePicker
  },
  props: {},
  setup (props, context) {
    const {
      setMhrHomeCertification
    } = useActions<any>([
      'setMhrHomeCertification'
    ])
    const {
      getMhrRegistrationHomeDescription
    } = useGetters<any>([
      'getMhrRegistrationHomeDescription'
    ])

    // Composable(s)
    const { createUtcDate, dateToYyyyMmDd } = useDateHelper()
    const {
      customRules,
      invalidSpaces,
      maxLength,
      isNumber,
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
          invalidSpaces(),
          isNumber()
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
      setMhrHomeCertification({ key: 'certificationOption', value: localState.certificationOption })
    })
    watch(() => localState.csaNumber, () => {
      setMhrHomeCertification({ key: 'csaNumber', value: localState.csaNumber })
    })
    watch(() => localState.csaStandard, () => {
      setMhrHomeCertification({ key: 'csaStandard', value: localState.csaStandard })
    })
    watch(() => localState.engineerName, () => {
      setMhrHomeCertification({ key: 'engineerName', value: localState.engineerName })
    })
    watch(() => localState.engineerReportDate, () => {
      setMhrHomeCertification({ key: 'engineerReportDate', value: localState.engineerReportDate })
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
</style>
