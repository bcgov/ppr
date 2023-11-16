<template>
  <v-card flat rounded id="mhr-home-land-ownership"
          class="mhr-home-land-ownership pa-8">
    <v-form ref="leaseOrOwnForm">
      <v-row no-gutters>
        <v-col cols="12" sm="3">
          <label class="generic-label" :class="{'error-text': validate}">
            Land Lease or Ownership
          </label>
        </v-col>
        <v-col cols="12" sm="9">
          <p>
            Is the manufactured home located on land that the homeowners own or on land that
            they have a registered lease of 3 years or more?
          </p>
        </v-col>
        <v-row class="mt-0 mb-n5">
          <v-col cols="10" offset="3">
            <v-radio-group
              id="lease-own-option"
              v-model="isOwnLand"
              class="mt-2 ml-n2 mb-3"
              row
            >
              <v-radio
                id="yes-option"
                class="yes-radio"
                label="Yes"
                active-class="selected-radio"
                :value="true"
              />
              <v-radio
                id="no-option"
                class="no-radio"
                label="No"
                active-class="selected-radio"
                :value="false"
              />
            </v-radio-group>
          </v-col>
        </v-row>
        <v-row v-if="isOwnLand">
          <v-col cols="9" offset="3">
            <v-divider class="mx-0 divider-mt" />
            <p class="mb-n2 paragraph-mt">
              <b>Note:</b> Land ownership or registered lease of the land for 3 years or more
              must be verifiable through the BC Land Title and Survey Authority (LTSA)
              or other authorized land authority.
            </p>
          </v-col>
        </v-row>
        <v-row v-if="!isOwnLand && isOwnLand!=null">
          <v-col cols="9" offset="3">
            <v-divider class="mx-0 divider-mt" />
            <p class="mb-n2 paragraph-mt">
              <b>Note:</b> Written permission and tenancy agreements from the landowner
              may be required for the home to remain on the land.
              <br><br>
              Relocation of the home onto land that the homeowner does not own or hold a
              registered lease of 3 years or more may require additional permits from
              authorities such as the applicable Municipality, Regional District, First
              Nation, or Provincial Crown Land Office.
            </p>
          </v-col>
        </v-row>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { useMhrValidations } from '@/composables'
import { FormIF } from '@/interfaces'

export default defineComponent({
  name: 'HomeLandOwnership',
  components: {},
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const {
      setMhrRegistrationOwnLand
    } = useStore()
    const { getMhrRegistrationValidationModel } = storeToRefs(useStore())
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const {
      getMhrRegistrationOwnLand
    } = storeToRefs(useStore())
    const leaseOrOwnForm = ref(null) as FormIF

    const localState = reactive({
      isOwnLand: null || getMhrRegistrationOwnLand.value,
      isValidHomeLandOwnership: computed((): boolean => {
        if (localState.isOwnLand === null) return false
        else return true
      })
    })

    const validateForm = (): void => {
      if (props.validate) {
        leaseOrOwnForm.value?.validate()
      }
    }

    watch(() => localState.isOwnLand, (val: boolean) => {
      setMhrRegistrationOwnLand(val)
    })

    watch(() => localState.isValidHomeLandOwnership, async (val: boolean) => {
      setValidation(MhrSectVal.LOCATION_VALID, MhrCompVal.LAND_DETAILS_VALID, val)
    })

    watch(() => props.validate, () => {
      validateForm()
    })

    return {
      leaseOrOwnForm,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.yes-radio {
  width: 44%;
  margin-right: 24px !important;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding-left: 10px;
}

.no-radio {
  width: 44%;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
  margin-right: 0px !important;
}

.paragraph-mt{
  margin-top: 39px;
}

.divider-mt{
  margin-top: 14px;
}
</style>
