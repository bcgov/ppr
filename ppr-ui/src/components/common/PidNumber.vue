<template>
  <v-row
    id="pid-number"
    class="pid-text-input"
    no-gutters
  >
    <BaseDialog
      :set-options="dialogOptions"
      :set-display="showNotFoundDialog"
      @proceed="dialogRetry($event)"
    />

    <v-col cols="12">
      <p class="font-weight-bold pb-3">
        PID Number
      </p>
    </v-col>
    <v-col
      cols="12"
      sm="3"
    >
      <v-text-field
        id="pid-one-input"
        ref="pidOneRef"
        v-model="pidOne"
        maxlength="3"
        variant="filled"
        color="primary"
        persistent-hint
        autofocus
        hint="Parcel identifier must contain 9 digits"
        :readonly="enablePidLoader"
        :error-messages="invalidPidMsg"
        :disabled="disable"
        @paste="parsePaste($event)"
      />
    </v-col>

    <v-divider class="horizontal-divider mx-1 mt-n5" />

    <v-col
      cols="12"
      sm="3"
    >
      <v-text-field
        id="pid-two-input"
        ref="pidTwoRef"
        v-model="pidTwo"
        variant="filled"
        color="primary"
        maxlength="3"
        :readonly="enablePidLoader"
        :disabled="disable"
        @paste="parsePaste($event)"
      />
    </v-col>

    <v-divider class="horizontal-divider mx-1 mt-n5" />

    <v-col
      cols="12"
      sm="3"
    >
      <v-text-field
        id="pid-three-input"
        ref="pidThreeRef"
        v-model="pidThree"
        variant="filled"
        color="primary"
        maxlength="3"
        :readonly="enablePidLoader"
        :disabled="disable"
        @paste="parsePaste($event)"
      />
    </v-col>

    <v-col
      cols="12"
      sm="1"
    >
      <v-progress-circular
        v-if="enablePidLoader"
        indeterminate
        color="primary"
        class="my-0 mt-n5"
        :size="25"
        :width="3"
      />

      <v-btn
        v-else-if="isCompletePid && isValidPid && !showNotFoundDialog"
        variant="plain"
        color="primary"
        class="ml-3 my-0 mt-n5"
        :ripple="false"
        @click="clearPid()"
      >
        Cancel <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-col>
  </v-row>
</template>

<script lang="ts">

import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { useInputRules } from '@/composables'
import { ltsaDetails } from '@/utils/ltsa-api-helper'
import { pidNotFoundDialog } from '@/resources/dialogOptions'
import type { LtsaDetailsIF, PidInfoIF } from '@/interfaces/ltsa-api-interfaces'
import type { FormIF } from '@/interfaces'


export default defineComponent({
  name: 'PidNumber',
  props: {
    pidNumber: { type: String, default: '' },
    disable: { type: Boolean, default: false },
    required: { type: Boolean, default: false }
  },
  emits: ['setPid', 'verifyingPid'],
  setup (props, context) {
    const { isNumber } = useInputRules()
    const pidOneRef = ref(null) as FormIF
    const pidTwoRef = ref(null) as FormIF
    const pidThreeRef = ref(null) as FormIF

    const localState = reactive({
      pidOne: props.pidNumber?.slice(0, 3) || '',
      pidTwo: props.pidNumber?.slice(3, 6) || '',
      pidThree: props.pidNumber?.slice(6, 9) || '',
      enablePidLoader: false,
      dialogOptions: pidNotFoundDialog,
      showNotFoundDialog: false,
      legalDescription: '',
      isCompletePid: computed((): boolean => {
        return localState.pidNumber.length === 9
      }),
      pidNumber: computed((): string => {
        return `${localState.pidOne}${localState.pidTwo}${localState.pidThree}`
      }),
      requestParcelIdentified: computed((): string => {
        return `${localState.pidOne}-${localState.pidTwo}-${localState.pidThree}`
      }),
      isRequired: computed((): boolean => props.required && !localState.isCompletePid),
      isValidPid: computed((): boolean => {
        return (
          !localState.isRequired &&
          (localState.pidOne ? /^\d+$/g.test(localState.pidOne) : true) &&
          (localState.pidTwo ? /^\d+$/g.test(localState.pidTwo) : true) &&
          (localState.pidThree ? /^\d+$/g.test(localState.pidThree) : true)
        )
      }),
      invalidPidMsg: computed(() => {
        return localState.isValidPid ? [] : ['Enter a valid 9 digit PID']
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
      const { legalDescription } = await ltsaDetails(localState.requestParcelIdentified) as LtsaDetailsIF
      localState.legalDescription = legalDescription || ''
      localState.enablePidLoader = false
      return !!legalDescription
    }

    const clearPid = (): void => {
      localState.pidOne = ''
      localState.pidTwo = ''
      localState.pidThree = ''
      localState.legalDescription = ''
      emitPid()
      // Wait for pidThree watcher to complete and got to first field
      setTimeout(() => {
        pidOneRef.value?.focus()
      }, 10)
    }
    const emitPid = (): void => {
      context.emit('setPid',
        { pidNumber: localState.pidNumber, legalDescription: localState.legalDescription } as PidInfoIF)
    }

    watch(() => localState.pidOne, () => {
      if (localState.pidOne.length === 3) nextTick(() => { pidTwoRef.value?.focus() })
    })
    watch(() => localState.pidTwo, () => {
      if (localState.pidTwo.length === 3) nextTick(() => { pidThreeRef.value?.focus() })
      if (localState.pidTwo.length === 0) nextTick(() => { pidOneRef.value?.focus() })
    })
    watch(() => localState.pidThree, () => {
      if (localState.pidThree.length === 0) nextTick(() => { pidTwoRef.value?.focus() })
    })
    watch(() => localState.enablePidLoader, () => {
      context.emit('verifyingPid', localState.enablePidLoader)
    })
    watch(() => localState.pidNumber, async () => {
      if (localState.isValidPid && localState.isCompletePid) {
        await validatePid() ? emitPid() : localState.showNotFoundDialog = true
      }
    })
    watch(() => props.disable, (val: boolean) => {
      if (val) clearPid()
    })

    return {
      pidOneRef,
      pidTwoRef,
      pidThreeRef,
      parsePaste,
      isNumber,
      dialogRetry,
      clearPid,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#pid-number{
  align-items: center;
}
.pid-text-input {
  max-width: 300px;
}
.horizontal-divider {
  opacity: 1;
  border-color: $gray7;
  max-width: 4px;
}
:deep(.v-text-field input) {
  text-align: center;
}
:deep(.v-input__details) {
  padding-inline-start: 0px!important;
  white-space: nowrap;
  overflow: visible;
  padding-left: 0;
}
:deep(.v-progress-circular) {
  margin: 2rem;
}
:deep(.v-icon.mdi-close) {
  padding-left: 2px;
  font-size: 20px;
}
</style>
