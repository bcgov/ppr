<template>
  <v-row id="pid-number" class="pid-text-input" no-gutters>
    <base-dialog
      :setOptions="dialogOptions"
      :setDisplay="showNotFoundDialog"
      @proceed="dialogRetry($event)"
    />

    <v-col cols="12">
      <p class="font-weight-bold">PID Number</p>
    </v-col>
    <v-col cols="12" sm="3">
      <v-text-field
        id="pid-one-input"
        ref="pidOneRef"
        maxlength="3"
        filled persistent-hint autofocus
        hint="Parcel identifier must contain 9 digits"
        :readonly="enablePidLoader"
        :error-messages="invalidPidMsg"
        v-model="pidOne"
        @paste="parsePaste($event)"
      />
    </v-col>

    <v-divider class="horizontal-divider pb-1" />

    <v-col cols="12" sm="3">
      <v-text-field
        id="pid-two-input"
        ref="pidTwoRef"
        filled
        maxlength="3"
        :readonly="enablePidLoader"
        v-model="pidTwo"
        @paste="parsePaste($event)"
      />
    </v-col>

    <v-divider class="horizontal-divider pb-1" />

    <v-col cols="12" sm="3">
      <v-text-field
        id="pid-three-input"
        ref="pidThreeRef"
        filled
        maxlength="3"
        :readonly="enablePidLoader"
        v-model="pidThree"
        @paste="parsePaste($event)"
      />
    </v-col>

    <v-col cols="12" sm="1">
      <v-progress-circular
        v-if="enablePidLoader"
        indeterminate
        color="primary"
        class="my-0"
        :size="25"
        :width="3"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import vue from 'vue'
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useInputRules } from '@/composables'
import { ltsaSummary } from '@/utils/ltsa-api-helper'
import { BaseDialog } from '@/components/dialogs'
import { pidNotFoundDialog } from '@/resources/dialogOptions'
import { TitleSummariesIF } from '@/interfaces/ltsa-api-interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'PidNumber',
  components: {
    BaseDialog
  },
  props: {},
  setup (props, context) {
    // Composable(s)
    const {
      isNumber
    } = useInputRules()

    const localState = reactive({
      pidOne: '',
      pidTwo: '',
      pidThree: '',
      enablePidLoader: false,
      dialogOptions: pidNotFoundDialog,
      showNotFoundDialog: false,
      pidNumber: computed(() => {
        return `${localState.pidOne}${localState.pidTwo}${localState.pidThree}`
      }),
      isValidPid: computed(() => {
        return (
          (localState.pidOne ? /^\d+$/g.test(localState.pidOne) : true) &&
          (localState.pidTwo ? /^\d+$/g.test(localState.pidTwo) : true) &&
          (localState.pidThree ? /^\d+$/g.test(localState.pidThree) : true)
        )
      }),
      invalidPidMsg: computed(() => {
        return localState.isValidPid ? [] : ['Enter a valid PID']
      })
    })

    /** Handle pasted event into Pid Input Fields **/
    const parsePaste = (event: any): void => {
      // Capture pasted text from event and clean spaces/special chars
      const pasteInput = event.clipboardData.getData('text').replace(/[^A-Z\d]+/ig, '')
      // Break the value down into 3x3 sections and apply to local model
      const pidNumberArr = pasteInput.match(/.{1,3}/g)
      localState.pidOne = pidNumberArr[0]
      localState.pidTwo = pidNumberArr[1]
      localState.pidThree = pidNumberArr[2]
    }

    const dialogRetry = async (retry: boolean): Promise<void> => {
      localState.showNotFoundDialog = false
      if (retry) {
        await validatePid() ? emitPid() : localState.showNotFoundDialog = true
      } else clearPid()
    }

    const validatePid = async (): Promise<boolean> => {
      localState.enablePidLoader = true
      const { titleSummaries } = await ltsaSummary(localState.pidNumber) as TitleSummariesIF
      localState.enablePidLoader = false
      return titleSummaries?.length > 0
    }

    const clearPid = (): void => {
      localState.pidOne = ''
      localState.pidTwo = ''
      localState.pidThree = ''
      emitPid()
    }
    const emitPid = (): void => { context.emit('setPid', localState.pidNumber) }

    watch(() => localState.pidOne, () => {
      // @ts-ignore - function exists
      if (localState.pidOne.length === 3) vue.nextTick(() => { context.refs.pidTwoRef.focus() })
    })
    watch(() => localState.pidTwo, () => {
      // @ts-ignore - function exists
      if (localState.pidTwo.length === 3) vue.nextTick(() => { context.refs.pidThreeRef.focus() })
      // @ts-ignore - function exists
      if (localState.pidTwo.length === 0) vue.nextTick(() => { context.refs.pidOneRef.focus() })
    })
    watch(() => localState.pidThree, () => {
      // @ts-ignore - function exists
      if (localState.pidThree.length === 0) vue.nextTick(() => { context.refs.pidTwoRef.focus() })
    })
    watch(() => localState.enablePidLoader, () => {
      context.emit('verifyingPid', localState.enablePidLoader)
    })
    watch(() => localState.pidNumber, async () => {
      if (localState.isValidPid && localState.pidNumber.length === 9) {
        await validatePid() ? emitPid() : localState.showNotFoundDialog = true
      }
    })

    return {
      parsePaste,
      isNumber,
      dialogRetry,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#pid-number{
  align-items: baseline;
}
.pid-text-input {
  max-width: 300px;
}
.horizontal-divider {
  border-color: $gray7;
  max-width: 4px;
}

::v-deep {
  .v-text-field input {
    text-align: center;
  }
  .v-text-field.v-text-field--enclosed .v-text-field__details {
    white-space: nowrap;
    overflow: visible;
    padding-left: 0;
  }
  .v-progress-circular {
    margin: 2rem;
  }
}
</style>
