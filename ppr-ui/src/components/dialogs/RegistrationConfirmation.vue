<template>
  <v-dialog
    v-model="displayValue"
    width="45rem"
    persistent
    :attach="attachValue"
  >
    <v-card>
      <v-row
        noGutters
        class="pl-10 pt-7"
      >
        <v-col cols="11">
          <p class="dialog-title">
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
            id="debtor-drop"
            v-model="userInput"
            autoSelectFirst
            :items="debtors"
            variant="filled"
            clearable
            class="debtor-drop"
            no-data-text="Debtor not found."
            label="Enter a Debtor (last name of individual person or full business name)"
            :errorMessages="validationErrors ? validationErrors : ''"
            persistentHint
            returnObject
          />
        </v-col>
        <v-col cols="1">
          <v-row noGutters>
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
        noGutters
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
// external
import {
  defineComponent,
  reactive,
  toRefs,
  watch
} from 'vue'
import { useStore } from '@/store/store'

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
  emits: ['proceed'],
  setup (props, context) {
    const { setRegistrationConfirmDebtorName } = useStore()
    const localState = reactive({
      validationErrors: '',
      userInput: null,
      debtors: [],
      optionsValue: props.options,
      attachValue: props.attach,
      displayValue: props.display,
      regNumber: props.registrationNumber,
      fullDebtorInfo: null
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
      for (const name of names) {
        if (name.businessName) {
          localState.debtors.push(name.businessName)
        }
        if (name.personName) {
          localState.debtors.push(name.personName.last)
        }
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
