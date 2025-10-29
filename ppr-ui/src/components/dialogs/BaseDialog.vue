<template>
  <v-dialog
    v-model="display"
    :width="width"
    persistent
    :attach="attach"
  >
    <v-card
      v-if="options"
      class="pa-10"
    >
      <v-row no-gutters>
        <v-col cols="11">
          <h2 class="dialog-title">
            {{ options.title }}
          </h2>
          <div class="mt-10">
            <!-- can be replaced with <template v-slot:content> -->
            <slot name="content">
              <DialogContent
                :set-base-text="options.text"
                :set-extra-text="options.textExtra"
                :set-has-contact-info="options.hasContactInfo"
              />
            </slot>
          </div>
        </v-col>
        <v-col cols="1">
          <v-btn
            class="close-btn pa-0 ma-0"
            color="primary"
            variant="plain"
            :ripple="false"
            @click="proceed(closeAction)"
          >
            <v-icon size="32px">
              mdi-close
            </v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row v-if="setConfirmActionLabel">
        <v-col>
          <v-checkbox
            id="confirm-action-checkbox"
            v-model="isActionConfirmed"
            class="confirm-action-checkbox"
            :error="showConfirmedError && !isActionConfirmed"
            :label="setConfirmActionLabel"
            :ripple="false"
            density="compact"
            hide-details
            data-test-id="confirm-action-checkbox"
          />
        </v-col>
      </v-row>
      <v-row v-if="showDismissDialogCheckbox">
        <v-col>
          <v-checkbox
            id="dismiss-dialog-checkbox"
            v-model="isDismissDialogChecked"
            class="ma-0 pt-4"
            hide-details
          >
            <template #label>
              <p class="ma-0">
                Do not show this message again.
              </p>
            </template>
          </v-checkbox>
        </v-col>
      </v-row>
      <div class="mt-10 action-buttons">
        <!-- can be replaced with <template v-slot:buttons> -->
        <slot name="buttons">
          <DialogButtons
            :set-accept-text="options.acceptText"
            :set-cancel-text="options.cancelText"
            :reverse-buttons="reverseActionButtons"
            @proceed="proceed($event)"
          />
        </slot>
      </div>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
    watch
} from 'vue'
// local components
import DialogButtons from './common/DialogButtons.vue'
import DialogContent from './common/DialogContent.vue'
// local types/helpers/etc.
import type { DialogOptionsIF } from '@/interfaces'
import { SettingOptions } from '@/enums'
import { useUserAccess } from '@/composables'

export default defineComponent({
  name: 'BaseDialog',
  props: {
    setAttach: { type: String, default: '' },
    setDisplay: { type: Boolean, default: false },
    width: { type: String, default: '720px' },
    setOptions: { type: Object as () => DialogOptionsIF, default: () => null },
    closeAction: { type: Boolean, default: false },
    reverseActionButtons: {
      type: Boolean,
      default: false
    },
    showDismissDialogCheckbox: { // display the checkbox to dismiss dialog for all future sessions
      type: Boolean,
      default: false
    },
    setConfirmActionLabel: { // label for checkbox to confirm and proceed
      type: String,
      default: ''
    }
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const localState = reactive({
      attach: computed(() => {
        return props.setAttach
      }),
      display: computed(() => {
        return props.setDisplay
      }),
      options: computed(() => {
        return props.setOptions
      }),
      isDismissDialogChecked: false,
      isActionConfirmed: false,
      showConfirmedError: false
    })

    const proceed = (val: boolean) => {
      if (props.setConfirmActionLabel && !localState.isActionConfirmed && val) {
        localState.showConfirmedError = true
      } else {
        localState.showConfirmedError = false
        emit('proceed', val)
      }
    }

    watch(
      () => localState.isDismissDialogChecked,
      async (val: boolean) => {
        await useUserAccess().updateUserMiscSettings(SettingOptions.SUCCESSFUL_REGISTRATION_DIALOG_HIDE, val)
      }
    )

    return {
      proceed,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
.close-btn, .close-btn:hover, .close-btn::before {
  background-color: transparent;
  height: 24px;
  width: 24px;
}
.close-btn {
  position: fixed;
  right: 20px;
  top: 35px;
}
:deep(.confirm-action-checkbox) {
  .v-label {
    margin-left: 5px;
  }
}
</style>
