<template>
  <v-row id="pid-number" class="pid-text-input" no-gutters>
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
      />
    </v-col>

    <v-divider class="horizontal-divider pb-1" />

    <v-col cols="12" sm="3">
      <v-text-field
        id="pid-three-input"
        ref="pidThreeRef"
        class=""
        filled
        maxlength="3"
        :readonly="enablePidLoader"
        v-model="pidThree"
      />
    </v-col>

    <v-col cols="12" sm="1">
      <v-progress-circular
        v-if="enablePidLoader"
        indeterminate
        color="primary"
      ></v-progress-circular>
    </v-col>
  </v-row>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import vue from 'vue'
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useInputRules } from '@/composables'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'PidNumber',
  components: {},
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
      pidNumber: computed(() => {
        return `${localState.pidOne}-${localState.pidTwo}-${localState.pidThree}`
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

    const emitPid = (): void => { context.emit('setPid', localState.pidNumber) }

    watch(() => localState.pidOne, () => {
      // @ts-ignore - function exists
      if (localState.pidOne.length === 3) vue.nextTick(() => { context.refs.pidTwoRef.focus() })
    })
    watch(() => localState.pidTwo, () => {
      // @ts-ignore - function exists
      if (localState.pidTwo.length === 3) vue.nextTick(() => { context.refs.pidThreeRef.focus() })
    })
    watch(() => localState.enablePidLoader, () => {
      context.emit('verifyingPid', localState.enablePidLoader)
    })
    watch(() => localState.pidNumber, () => {
      if (localState.isValidPid) {
        localState.enablePidLoader = localState.pidNumber.length === 11

        // *** TO REMOVE: MOCKED REQUEST FOR PID VERIFICATION ***
        setTimeout(() => {
          localState.enablePidLoader = false
          emitPid() // Mock Set if Verified
        }, 5000)
        // *******************************************
      }
    })

    return {
      isNumber,
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
