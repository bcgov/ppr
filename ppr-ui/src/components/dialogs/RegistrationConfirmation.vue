<template>
  <v-dialog
    v-model="displayValue"
    width="45rem"
    persistent
    :attach="attachValue"
  >
    <v-card>
      <v-row
        no-gutters
        class="pl-10 pt-7"
      >
        <v-col cols="11">
          <p class="dialog-title">
            <b>{{ optionsValue.title }}
              <span v-if="isRlReg && !isDischarge(optionsValue.label)">as Commercial Lien</span>
            </b>
          </p>

          <template v-if="isRlReg">
            <p
              v-if="!isDischarge(optionsValue.label)"
              class="dialog-text py-5 ma-0"
            >
              A Repairers Lien (RL) to be {{ getRegistrationLabel(optionsValue.label) }} will be registered as a
              Commercial Lien (CL) and must comply with
              {{ optionsValue.label.split(' ').slice(1).join(' ').toLowerCase() }} requirements under the Commercial
              Liens Act and Personal Property Security Regulation.
            </p>
            <p v-else class="dialog-text py-5 ma-0">
              The Repairers Lien (RL) will be discharged as a Commercial Lien (CL) under the Commercial Liens Act and
              Personal Property Security Regulation.
            </p>
            <v-divider class="horizontal-divider mx-1 my-1" />
          </template>

          <p class="dialog-text py-5 ma-0">
            To ensure you are performing {{ optionsValue.label }} on the correct
            registration (Base Registration Number: {{ regNumber }}) please
            enter the
            <b>individual person's last name or full business name</b> of any
            <b>Debtor</b> associated with this registration.
          </p>
          <v-autocomplete
            id="debtor-drop"
            v-model="userInput"
            auto-select-first
            :items="debtors"
            variant="filled"
            clearable
            class="debtor-drop"
            no-data-text="Debtor not found."
            label="Enter a Debtor (last name of individual person or full business name)"
            :error-messages="validationErrors ? validationErrors : ''"
            persistent-hint
            return-object
          />
        </v-col>
        <v-col cols="1">
          <v-row no-gutters>
            <v-btn
              id="close-btn"
              color="primary"
              variant="plain"
              :ripple="false"
              @click="exit()"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row
        no-gutters
        justify="center"
        class="pt-1 pb-7"
      >
        <v-col
          v-if="options.cancelText"
          cols="auto"
          class="pr-3"
        >
          <v-btn
            id="cancel-btn"
            class="outlined dialog-btn"
            variant="outlined"
            @click="exit()"
          >
            {{ optionsValue.cancelText }}
          </v-btn>
        </v-col>
        <v-col
          v-if="optionsValue.acceptText"
          cols="auto"
        >
          <v-btn
            id="accept-btn"
            class="bg-primary dialog-btn"
            elevation="0"
            @click="submit()"
          >
            {{ optionsValue.acceptText }} <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed
} from 'vue'
import { useStore } from '@/store/store'
import type { DebtorNameIF, DialogOptionsIF } from '@/interfaces'
import { debtorNames } from '@/utils/ppr-api-helper'
import { APIRegistrationTypes } from '@/enums'

export default defineComponent({
  props: {
    attach: {
      type: String,
      default: ''
    },
    display: {
      type: Boolean,
      default: false
    },
    options: {
      type: Object as () => DialogOptionsIF,
      default: () => {}
    },
    registrationNumber: {
     type: String,
      default: ''
    }
  },
  emits: ['proceed'],
  setup (props, context) {
    const { setRegistrationConfirmDebtorName } = useStore()
    const { getRegTableBaseRegs } = storeToRefs(useStore())
    const localState = reactive({
      validationErrors: '',
      userInput: null,
      debtors: [],
      optionsValue: props.options as DialogOptionsIF,
      attachValue: props.attach,
      displayValue: props.display,
      regNumber: props.registrationNumber,
      fullDebtorInfo: null,
      isRlReg: computed(() => {
        return getRegTableBaseRegs.value?.some(reg =>
           reg.baseRegistrationNumber === props.registrationNumber &&
            reg.registrationType === APIRegistrationTypes.REPAIRERS_LIEN)
      })
    })

    const submit = (): void => {
      if (localState.userInput) {
        if (
          localState.debtors.find(c => c === localState.userInput)
        ) {
          const chosenDebtor = localState.fullDebtorInfo.find(
            c =>
              c.businessName === localState.userInput ||
              c.personName?.last === localState.userInput
          )
          setRegistrationConfirmDebtorName(chosenDebtor)
          context.emit('proceed', true)
        }
      } else {
        localState.validationErrors = 'This field is required'
      }
    }

    const exit = () => {
      // Reset to initial state on cancel.
      if (localState.userInput) {
        localState.userInput = null
      }
      localState.debtors = []
      context.emit('proceed', false)
    }

    const getDebtors = async () => {
      localState.debtors = []
      const names: Array<DebtorNameIF> = await debtorNames(
        props.registrationNumber
      )
      if (names.length) {
        for (const name of names) {
          if (name.businessName) {
            localState.debtors.push(name.businessName)
          }
          if (name.personName) {
            localState.debtors.push(name.personName.last)
          }
        }
      }

      localState.debtors.sort((a, b) =>
        a.text < b.text ? 1 : b.text < a.text ? -1 : 0
      )
      localState.fullDebtorInfo = names
    }

    /** Get the registration label for the dialog title. */
    const getRegistrationLabel = (label: string): string => {
      switch (label) {
        case 'an Amendment':
          return 'amended'
        case 'a Renewal':
          return 'renewed'
        default:
          return ''
      }
    }

    /** Get the registration label for the dialog title. */
    const isDischarge = (label: string): boolean => {
      return label.includes('Discharge')
    }

    watch(
      () => props.registrationNumber,
      (val: string) => {
        if (val) {
          localState.regNumber = props.registrationNumber
          getDebtors()
        }
      }
    )

    watch(
      () => localState.userInput,
      (val: object) => {
        if (!val) {
          localState.validationErrors = 'This field is required'
        } else {
          localState.validationErrors = ''
        }
      }
    )

    watch(
      () => props.display,
      (val: boolean) => {
        localState.displayValue = val
        if (val === false) {
          localState.validationErrors = ''
        }
      }
    )

    watch(
      () => props.options,
      (val: DialogOptionsIF) => {
        localState.optionsValue = val
      }
    )

    return {
      submit,
      exit,
      isDischarge,
      getRegistrationLabel,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.v-btn.primary {
  font-weight: normal;
}
</style>
