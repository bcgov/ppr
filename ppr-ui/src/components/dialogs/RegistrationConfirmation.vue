<template>
  <v-dialog v-model="displayValue" width="45rem" persistent attach="#app">
    <v-card>
      <v-row no-gutters class="pl-10 pt-7">
        <v-col cols="11">
          <p class="dialog-title ma-0">
            <b>{{ optionsValue.title }}</b>
          </p>
          <p class="dialog-text py-5 ma-0">
            To ensure you are performing {{ optionsValue.label }} on the correct
            registration (Base Registration Number: {{ regNumber }}) please
            enter the
            <b>individual person's last name or full business name</b> of any
            <b>Debtor</b> associated with this registration.
          </p>
          <v-autocomplete
            auto-select-first
            :items="debtors"
            filled
            clearable
            class="debtor-drop"
            no-data-text="Debtor not found."
            label="Enter a Debtor (last name of individual person or full business name)"
            id="debtor-drop"
            v-model="userInput"
            :error-messages="validationErrors ? validationErrors : ''"
            persistent-hint
            return-object
          ></v-autocomplete>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters>
            <v-btn
              id="close-btn"
              color="primary"
              icon
              :ripple="false"
              @click="exit()"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters justify="center" class="pt-1 pb-7">
        <v-col v-if="options.cancelText" cols="auto" class="pr-3">
          <v-btn
            id="cancel-btn"
            class="outlined dialog-btn"
            outlined
            @click="exit()"
          >
            {{ optionsValue.cancelText }}
          </v-btn>
        </v-col>
        <v-col v-if="optionsValue.acceptText" cols="auto">
          <v-btn id="accept-btn" class="primary dialog-btn" elevation="0" @click="submit()"
            >{{ optionsValue.acceptText }} <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
// external
import {
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'

// local
import { DebtorNameIF, DialogOptionsIF } from '@/interfaces' // eslint-disable-line
import { debtorNames } from '@/utils'

export default defineComponent({
  props: {
    attach: String,
    display: Boolean,
    options: {
      type: Object as () => DialogOptionsIF
    },
    registrationNumber: String
  },
  emits: ['proceed', 'confirmationClose'],
  setup (props, context) {
    const { setRegistrationConfirmDebtorName } = useActions<any>([
      'setRegistrationConfirmDebtorName'
    ])
    const localState = reactive({
      validationErrors: '',
      userInput: { value: 0, text: '' },
      debtors: [],
      optionsValue: props.options,
      attachValue: props.attach,
      displayValue: props.display,
      regNumber: props.registrationNumber,
      fullDebtorInfo: null
    })

    const submit = (): void => {
      if (localState.userInput.value) {
        if (
          localState.debtors.find(c => c.value === localState.userInput.value)
        ) {
          const chosenDebtor = localState.fullDebtorInfo.find(
            c =>
              c.businessName === localState.userInput.value ||
              c.personName?.last === localState.userInput.value
          )
          setRegistrationConfirmDebtorName(chosenDebtor)
          context.emit('proceed')
        }
      } else {
        localState.validationErrors = 'This field is required'
      }
    }

    const exit = () => {
      // Reset to initial state on cancel.
      if (localState.userInput) {
        localState.userInput.value = 0
        localState.userInput.text = ''
      }
      localState.debtors = []
      context.emit('confirmationClose')
    }

    const getDebtors = async () => {
      const names: Array<DebtorNameIF> = await debtorNames(
        props.registrationNumber
      )
      for (let i = 0; i < names.length; i++) {
        let dropdownValue = ''
        if (names[i].businessName) {
          dropdownValue = names[i].businessName
        }
        if (names[i].personName) {
          dropdownValue = names[i].personName.last
        }
        localState.debtors.push({ text: dropdownValue, value: dropdownValue })
      }
      localState.debtors.sort((a, b) =>
        a.text < b.text ? 1 : b.text < a.text ? -1 : 0
      )
      localState.fullDebtorInfo = names
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
      (val: Object) => {
        if (!val) localState.validationErrors = 'This field is required'
      }
    )

    watch(
      () => props.display,
      (val: boolean) => {
        localState.displayValue = val
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
