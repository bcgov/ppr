<template>
  <BaseDialog
    :set-display="setDisplay"
    :set-options="setOptions"
    @proceed="proceed($event)"
  >
    <template #content>
      <dialog-content :set-base-text="setOptions.text" />
      <v-checkbox
        v-if="!setHideCheckbox"
        v-model="preventDialog"
        class="dialog-checkbox pt-5 ma-0"
        :error-messages="updateFailed ? 'error' : ''"
        :hide-details="!updateFailed"
        label="Don't show this message again"
      >
        <template #message>
          <p class="ma-0 pl-8">
            We were unable to update your user settings. Please try again later.
          </p>
        </template>
      </v-checkbox>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch
} from 'vue'
import { useStore } from '@/store/store'
import { DialogContent } from './common'
import type { SettingOptions } from '@/enums'
import type { DialogOptionsIF, UserSettingsIF } from '@/interfaces'
import { updateUserSettings } from '@/utils/ppr-api-helper'

export default defineComponent({
  name: 'ConfirmationDialog',
  components: {
    DialogContent
  },
  props: {
    setDisplay: {
      type: Boolean,
      default: false
    },
    setOptions: {
      type: Object as () => DialogOptionsIF,
      default: () => {}
    },
    setSettingOption: {
      type: String as () => SettingOptions,
      default: ''
    },
    setHideCheckbox: {
      type: Boolean,
      default: false
    }
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const { setUserSettings } = useStore()

    const localState = reactive({
      preventDialog: false,
      updateFailed: false
    })

    const proceed = (val: boolean) => {
      emit('proceed', val)
    }

    watch(() => localState.preventDialog, async (val) => {
      const settings: UserSettingsIF = await updateUserSettings(props.setSettingOption, !val)
      if (!settings?.error) {
        localState.updateFailed = false
        setUserSettings(settings)
      } else {
        // show error message
        localState.updateFailed = true
      }
    })

    return {
      proceed,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
:deep(.dialog-checkbox .v-input__control .v-input__slot .v-label) {
  color: $gray7;
  font-size: 1rem;
  line-height: 1.5rem;
}
</style>
