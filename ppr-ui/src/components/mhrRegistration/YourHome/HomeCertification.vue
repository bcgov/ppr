<template>
  <v-card flat rounded id="mhr-home-certification-form" class="mt-8 pa-8">
    <v-form ref="homeCertificationForm" v-model="homeCertificationValid">
      <v-row no-gutters>
        <v-col cols="12" sm="2">
          <label class="generic-label">Certification</label>
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
              value="csa"
              id="csa-option"
            />
            <v-radio
              class="engineer-radio"
              label="Engineer's Inspection"
              value="engineer"
              id="engineer-option"
            />
          </v-radio-group>

          <!-- CSA Section -->
          <template v-if="isCsaOption">
            <v-divider class="my-9 mx-0" />
            <v-form>
              <v-row no-gutters>
                <v-col cols="12">
                  <label class="generic-label" for="csa-number">CSA Number</label>
                  <v-text-field
                    filled
                    id="csa-number"
                    class="pt-4 pr-2"
                    label="CSA Number"
                    v-model="csaNumber"
                    :rules="[]"
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
                  <label class="generic-label" for="engineer-name">Engineer's Name</label>
                  <v-text-field
                    filled
                    id="engineer-name"
                    class="pt-4 pr-2"
                    label="Engineer's Name"
                    v-model="engineerName"
                    :rules="[]"
                  />

                  <label class="generic-label" for="date-of-engineer-report">Date of Engineer's Report</label>
                  <SharedDatePicker
                    ref="datePicker"
                    id="date-of-engineer-report"
                    class="pt-4 pr-2"
                    :setEndDate="null"
                    :setStartDate="null"
                    @submit="updateDateRange($event)"
                  />

                </v-col>
              </v-row>
            </v-form>
          </template>
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { SharedDatePicker } from '@/components/common'
import { useActions, useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'HomeCertification',
  components: {
    SharedDatePicker
  },
  props: {},
  setup (props, context) {
    // const {
    //   setHomeSections
    // } = useActions<any>([
    //   'setHomeSections'
    // ])
    // const {
    //   getMhrHomeSections
    // } = useGetters<any>([
    //   'getMhrHomeSections'
    // ])
    const localState = reactive({
      homeCertificationValid: false,
      certificationOption: '',
      csaNumber: '',
      csaStandard: '',
      csaStandardOptions: ['A277', 'Z240'],
      engineerName: '',
      engineerReportDate: '',
      isCsaOption: computed((): boolean => {
        return localState.certificationOption === 'csa'
      }),
      isEngineerOption: computed((): boolean => {
        return localState.certificationOption === 'engineer'
      })
    })

    const updateDateRange = (date): void => { localState.engineerReportDate = date }
    watch(() => localState.certificationOption, () => {
      if (localState.isCsaOption) {
        localState.engineerName = ''
        localState.engineerReportDate = ''
      }
      if (localState.isEngineerOption) {
        localState.csaNumber = ''
        localState.csaStandard = ''
      }
    })
    return {
      updateDateRange,
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
