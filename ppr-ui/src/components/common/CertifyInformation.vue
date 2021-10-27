<template>
  <v-container flat class="pa-0" id="certify-summary">
    <v-row no-gutters>
      <v-col class="generic-label"><h2>2. Certify</h2></v-col>
    </v-row>
    <v-row no-gutters class="pb-6 pt-4">
      <v-col>
        Enter the legal name of the persion authorized to complete and submit this registration.
      </v-col>
    </v-row>
    <v-row class="no-gutters">
      <v-col cols="12" class="pa-0" :class="showErrorComponent ? 'border-error-left': ''">
        <v-card flat>
          <v-row no-gutters style="padding: 0 30px;">
            <v-col cols="3" class="generic-label pt-10"
              >Legal Name</v-col
            >
            <v-col cols="9" class="pt-8">
              <v-text-field
                filled
                id="txt-legal-name"
                label=""
                :error-messages="legalNameMessage || ''"
                v-model="legalName"
                persistent-hint
                :rules="rules"
              />
              <v-row no-gutters class="pt-3">
                <v-col cols="12">
                  <v-checkbox
                      class="pa-0 ma-0"
                      :hide-details="false"
                      id="checkbox-certified"
                      :error-messages="checkboxMessage || ''"
                      v-model="certified">
                      <template v-slot:label>
                        <div class="summary-text">
                          I, <span class="generic-label">{{ legalName }}</span>, certify that I have relevant
                          knowledge of this registration and I am authorized to make this filing.
                        </div>
                      </template>
                  </v-checkbox>
                </v-col>
              </v-row>
              <v-row no-gutters class="pt-3">
                  <v-col cols="12">
                    <span class="generic-label">Date: </span><span class="summary-text">{{ currentDate }}</span>
                  </v-col>
              </v-row>
              <v-row no-gutters class="pt-5 pb-5">
                  <v-col cols="12" class="summary-text">
                      <span class="invalid-color">
                          {{ warningText }}
                      </span>
                  </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// local
import { convertDate } from '@/utils'
import { CertifyIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  props: {
    setShowErrors: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { setCertifyInformation } = useActions<any>([
      'setCertifyInformation'
    ])
    const { getCertifyInformation } = useGetters<any>([
      'getCertifyInformation'
    ])

    const localState = reactive({
      legalName: '',
      certified: false,
      warningText: 'Note: It is an offence to make a false or misleading statement in respect of a material fact ' +
                   'in arecord submitted to the Corporate Registry for filing. See section XX of the Personal ' +
                   'Property Security Act.',
      // showErrors: props.setShowErrors,
      showErrors: computed((): boolean => {
        return props.setShowErrors
      }),
      showErrorComponent: computed((): boolean => {
        return (localState.showErrors && !localState.valid)
      }),
      certifyInformation: null,
      currentDate: computed((): string => {
        return convertDate(new Date(), false, false)
      }),
      legalNameMessage: computed((): string => {
        if (localState.showErrors && localState.legalName.trim().length < 1) {
          return 'Enter a Legal Name.'
        }
        return ''
      }),
      checkboxMessage: computed((): string => {
        if (localState.showErrors && !localState.certified) {
          return 'Check the box.'
        }
        return ''
      }),
      valid: computed((): boolean => {
        return (localState.certified &&
                localState.legalName &&
                localState.legalName.trim().length > 1 &&
                localState.legalName.length <= 100)
      }),
      rules: [
        (v: string) => !v || v.length <= 100 || 'Maximum 100 characters reached' // maximum character count
      ]
    })

    /* watch(() => props.setShowErrors, (val) => {
      localState.showErrors = val
    })
    */
    watch(
      () => localState.legalName,
      (val: string) => {
        emit('certifyValid', localState.valid)
        localState.certifyInformation.legalName = val
        localState.certifyInformation.valid = localState.valid
        setCertifyInformation(localState.certifyInformation)
      }
    )
    watch(
      () => localState.certified,
      (val: boolean) => {
        emit('certifyValid', localState.valid)
        localState.certifyInformation.certified = val
        localState.certifyInformation.valid = localState.valid
        setCertifyInformation(localState.certifyInformation)
      }
    )

    onMounted(() => {
      localState.certifyInformation = getCertifyInformation.value
      localState.legalName = localState.certifyInformation.legalName
      localState.certified = localState.certifyInformation.certified
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
