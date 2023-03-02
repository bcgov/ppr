<template>
  <div class="mhr-transfer-type mt-8">

    <BaseDialog
      :setOptions="changeTransferType"
      :setDisplay="showTransferChangeDialog"
      @proceed="handleTypeChangeDialogResp($event)"
    />

    <p class="gray7">
      To change the ownership of this home, first select the Transfer Type and enter the Declared Value of Home.
    </p>

    <v-card flat class="mt-6 py-6 px-8 rounded" :class="{ 'border-error-left': showFormError }">
      <v-form ref="transferTypeForm" v-model="isValid">

        <!-- Transfer Type Selector -->
        <v-row no-gutters>
          <v-col cols="3">
            <label
              class="generic-label"
              for="transfer-type-selector"
              :class="{ 'error-text': showFormError && hasError(transferTypeSelectRef) }"
            >Transfer Type</label>
          </v-col>

          <v-col cols="9">
            <v-select
              id="transfer-type-selector"
              ref="transferTypeSelectRef"
              filled
              :items="TransferTypes"
              item-disabled="selectDisabled"
              item-text="textLabel"
              item-value="transferType"
              label="Transfer Type"
              data-test-id="transfer-type-selector"
              v-model="selectedTransferType"
              :rules="required('Select transfer type')"
              :menu-props="{ bottom: true, offsetY: true }"
              return-object
            >
              <template v-slot:item="{ item }">

                <!-- Type Header -->
                <template v-if="item.class === 'transfer-type-list-header'">
                  <v-list-item-content :aria-disabled="true">
                    <v-row :id="`transfer-type-drop-${item.group}`" no-gutters>
                      <v-col align-self="center">
                        <span class="transfer-type-list-header px-1">{{ item.textLabel }}</span>
                      </v-col>
                    </v-row>
                  </v-list-item-content>
                </template>

                <!-- Type Selections -->
                <template v-else>
                  <v-tooltip
                    right
                    content-class="right-tooltip pa-5"
                    transition="fade-transition"
                    data-test-id="suffix-tooltip"
                    nudge-left="20"
                    allow-overflow
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-list-item
                        :id="`list-${item.transferType}`"
                        class="copy-normal"
                        @click="handleTypeChange(item)"
                        v-bind="attrs" v-on="on"
                      >
                        <v-list-item-title class="pl-5">
                          {{ item.textLabel }}
                        </v-list-item-title>
                      </v-list-item>
                    </template>
                    <span class="font-weight-bold">{{ item.tooltip.title }}:</span><br>
                    <li v-for="(item, index) in item.tooltip.bullets" :key="index">{{ item }}</li>
                  </v-tooltip>
                </template>
              </template>
            </v-select>
          </v-col>
        </v-row>

        <!-- Declared Value -->
        <v-row no-gutters>
          <v-col cols="3">
            <label
              class="generic-label"
              for="declared-value"
              :class="{ 'error-text': showFormError && hasError(declaredValueRef) }"
            >
              Declared Value of Home
            </label>
          </v-col>

          <v-col cols="9">
            <v-row no-gutters>
              <span class="mt-4">$</span>
              <v-text-field
                id="declared-value"
                class="declared-value px-2"
                ref="declaredValueRef"
                v-model.number="declaredValue"
                filled
                :rules="declaredValueRules"
                label="Amount in Canadian Dollars"
                validate-on-blur
                data-test-id="declared-value"
              />
              <span class="mt-4">.00</span>
            </v-row>
          </v-col>
        </v-row>

      </v-form>
    </v-card>
  </div>
</template>

<script lang="ts">
import { useInputRules } from '@/composables'
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { BaseDialog } from '@/components/dialogs'
import { TransferTypes } from '@/resources'
import { useGetters } from 'vuex-composition-helpers'
import { changeTransferType } from '@/resources/dialogOptions'
import { cloneDeep } from 'lodash'
// eslint-disable-next-line no-unused-vars
import { FormIF, TransferTypeSelectIF } from '@/interfaces'

export default defineComponent({
  name: 'TransferType',
  emits: ['emitType', 'emitDeclaredValue', 'emitValid'],
  props: { validate: { type: Boolean, default: false } },
  components: { BaseDialog },
  setup (props, context) {
    const { customRules, required, isNumber, maxLength } = useInputRules()
    const transferTypeSelectRef = ref(null)
    const declaredValueRef = ref(null)

    const {
      hasUnsavedChanges,
      getMhrTransferType,
      getMhrTransferDeclaredValue
    } = useGetters<any>([
      'hasUnsavedChanges',
      'getMhrTransferType',
      'getMhrTransferDeclaredValue'
    ])

    const localState = reactive({
      isValid: false,
      declaredValue: getMhrTransferDeclaredValue.value,
      selectedTransferType: getMhrTransferType.value as TransferTypeSelectIF,
      showTransferChangeDialog: false,
      previousType: null as TransferTypeSelectIF,
      declaredValueRules: computed((): Array<Function> => {
        return customRules(
          maxLength(7, true),
          isNumber(),
          required('Enter declared value of home'))
      }),
      showFormError: computed(() => props.validate && !localState.isValid)
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    const selectTransferType = (item: TransferTypeSelectIF): void => {
      context.emit('emitType', item)
      localState.selectedTransferType = cloneDeep(item)

      // @ts-ignore - function exists
      context.refs.transferTypeSelectRef.blur()
    }

    const handleTypeChange = async (item: TransferTypeSelectIF): Promise<void> => {
      if (item.transferType !== localState.previousType?.transferType &&
        (hasUnsavedChanges.value || !!getMhrTransferDeclaredValue.value)) {
        localState.showTransferChangeDialog = true
      } else {
        localState.previousType = cloneDeep(item)
        selectTransferType(item)
      }
    }

    const handleTypeChangeDialogResp = (val: boolean): void => {
      if (!val) {
        selectTransferType(cloneDeep(localState.previousType))
      } else {
        selectTransferType(cloneDeep(localState.selectedTransferType))
      }
      localState.showTransferChangeDialog = false
    }

    watch(() => props.validate, (validate: boolean) => {
      validate && (context.refs.transferTypeForm as FormIF).validate()
    })

    watch(() => localState.isValid, () => {
      return context.emit('emitValid', localState.isValid)
    })

    watch(() => localState.declaredValue, async (val: number) => {
      return context.emit('emitDeclaredValue', val)
    })

    watch(() => getMhrTransferDeclaredValue.value, async (val: number) => {
      localState.declaredValue = val
    })

    return {
      hasError,
      required,
      TransferTypes,
      transferTypeSelectRef,
      declaredValueRef,
      selectTransferType,
      changeTransferType,
      handleTypeChange,
      handleTypeChangeDialogResp,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.transfer-type-list-header {
  color: $gray9 !important;
  font-weight: bold;
  pointer-events: all;
}
</style>
