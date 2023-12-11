<template>
  <div class="mhr-transfer-type mt-8">
    <BaseDialog
      :setOptions="changeTransferType"
      :setDisplay="showTransferChangeDialog"
      @proceed="handleTypeChangeDialogResp($event)"
    />

    <v-card
      flat
      class="mt-6 py-6 px-8 rounded"
      :class="{ 'border-error-left': showFormError }"
    >
      <v-form
        ref="transferTypeForm"
        v-model="isValid"
      >
        <!-- Transfer Type Selector -->
        <v-row noGutters>
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
              v-model="selectedTransferType"
              variant="filled"
              :items="transferTypesSelector"
              itemTitle="textLabel"
              itemValue="transferType"
              label="Transfer Type"
              data-test-id="transfer-type-selector"
              :rules="transferTypeRules"
              :disabled="disableSelect"
              returnObject
            >
              <template #item="{ props, item }">
                <!-- Type Header -->
                <template v-if="item.raw.class === 'transfer-type-list-header'">
                  <v-list-item
                    v-if="item.raw.class === 'transfer-type-list-header'"
                    :aria-disabled="true"
                  >
                    <v-row
                      :id="`transfer-type-drop-${item.raw.group}`"
                      noGutters
                    >
                      <v-col alignSelf="center">
                        <span class="transfer-type-list-header px-1">{{ item.raw.textLabel }}</span>
                      </v-col>
                    </v-row>
                  </v-list-item>
                </template>
                <v-list-item
                  v-else
                  :id="`list-${item.raw.transferType}`"
                  class="copy-normal gray7"
                  v-bind="props"
                  :title="null"
                >
                  <v-tooltip
                    location="right"
                    contentClass="right-tooltip pa-5"
                    transition="fade-transition"
                    data-test-id="suffix-tooltip"
                  >
                    <template #activator="{ props }">
                      <v-list-item-title
                        class="pl-5"
                        v-bind="props"
                        @click="handleTypeChange(item.raw)"
                      >
                        {{ item.raw.textLabel }}
                      </v-list-item-title>
                    </template>
                    <span class="font-weight-bold">{{ item.raw.tooltip.title }}:</span><br>
                    <li
                      v-for="(item, index) in item.raw.tooltip.bullets"
                      :key="index"
                    >
                      {{ item }}
                    </li>
                    <div v-if="item.raw.tooltip.note">
                      <br>
                      <span class="font-weight-bold">Note:</span>
                      {{ item.raw.tooltip.note }}
                    </div>
                  </v-tooltip>
                </v-list-item>
              </template>
            </v-select>
          </v-col>
        </v-row>

        <!-- Declared Value -->
        <v-row noGutters>
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
            <v-row noGutters>
              <span class="mt-4">$</span>
              <v-text-field
                id="declared-value"
                ref="declaredValueRef"
                v-model.number="declaredValue"
                class="declared-value px-2"
                variant="filled"
                label="Amount in Canadian Dollars"
                :disabled="disableSelect"
                :rules="declaredValueRules"
                :hint="declaredHomeValueHint"
                :persistentHint="true"
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
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { BaseDialog } from '@/components/dialogs'
import {
  ClientTransferTypes,
  QualifiedSupplierTransferTypes,
  StaffTransferTypes,
  transfersContent,
  transfersErrors
} from '@/resources'
import { useStore } from '@/store/store'
import { changeTransferType } from '@/resources/dialogOptions'
import { useInputRules, useTransferOwners } from '@/composables'
import { FormIF, TransferTypeSelectIF } from '@/interfaces'
import { ApiTransferTypes } from '@/enums'
import { cloneDeep } from 'lodash'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'TransferType',
  components: { BaseDialog },
  props: {
    validate: { type: Boolean, default: false },
    disableSelect: { type: Boolean, default: false }
  },
  emits: ['emitType', 'emitDeclaredValue', 'emitValid'],
  setup (props, context) {
    const { customRules, required, isNumber, maxLength, greaterThan } = useInputRules()
    const transferTypeSelectRef = ref(null)
    const declaredValueRef = ref(null)
    const transferTypeForm = ref(null) as FormIF

    const {
      // Getters
      isRoleStaffReg,
      isRoleQualifiedSupplierLawyersNotaries,
      hasUnsavedChanges,
      getMhrTransferType,
      getMhrTransferDeclaredValue
    } = storeToRefs(useStore())

    const {
      isJointTenancyStructure
    } = useTransferOwners()

    const localState = reactive({
      isValid: false,
      declaredValue: getMhrTransferDeclaredValue.value,
      selectedTransferType: getMhrTransferType.value as TransferTypeSelectIF,
      showTransferChangeDialog: false,
      previousType: null as TransferTypeSelectIF,
      declaredValueRules: computed((): Array<()=>string|boolean> => {
        return customRules(
          maxLength(7, true),
          isNumber(),
          getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL
            ? greaterThan(25000,
              transfersErrors.declaredHomeValueMax[ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL])
            : [],
          required('Enter declared value of home'))
      }),
      showFormError: computed(() => props.validate && !localState.isValid),
      declaredHomeValueHint: computed(() =>
        transfersContent.declaredHomeValueHint[getMhrTransferType.value?.transferType]
      ),
      transferTypesSelector: computed((): Array<TransferTypeSelectIF> => {
        switch (true) {
          case isRoleStaffReg.value:
            return StaffTransferTypes
          case isRoleQualifiedSupplierLawyersNotaries.value:
            return QualifiedSupplierTransferTypes
          default:
            return ClientTransferTypes
        }
      }),
      transferTypeRules: required('Select transfer type')
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    const selectTransferType = (item: TransferTypeSelectIF): void => {
      context.emit('emitType', item)
      localState.selectedTransferType = cloneDeep(item)
      transferTypeSelectRef.value?.blur()
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
      validate && transferTypeForm.value?.validate()
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

    watch(() => localState.selectedTransferType, (val:TransferTypeSelectIF) => {
      transferTypeForm.value?.resetValidation()

      switch (val.transferType) {
        case ApiTransferTypes.SALE_OR_GIFT:
        case ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL:
        case ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL:
        case ApiTransferTypes.TO_ADMIN_NO_WILL:
          localState.transferTypeRules = customRules(
            required('Select transfer type')
          )
          break
        case ApiTransferTypes.SURVIVING_JOINT_TENANT:
          localState.transferTypeRules = customRules(
            required('Select transfer type'),
            [
              () => isJointTenancyStructure.value ||
              'An owner group with joint tenancy is required for this transfer type'
            ]
          )
          break
        default:
          localState.transferTypeRules = required('Select transfer type')
      }
    })

    return {
      hasError,
      required,
      isRoleStaffReg,
      ClientTransferTypes,
      StaffTransferTypes,
      transferTypeSelectRef,
      declaredValueRef,
      selectTransferType,
      changeTransferType,
      handleTypeChange,
      handleTypeChangeDialogResp,
      transfersContent,
      transferTypeForm,
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
:deep(.theme--light.v-select .v-select__selection--disabled) {
  color: $gray9 !important;
}

</style>
