<template>
  <div class="mhr-transfer-type mt-8">
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
              v-model="selectedTransferType"
              data-test-id="transfer-type-selector"
              :rules="required('Select transfer type')"
              :menu-props="{ bottom: true, offsetY: true }"
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
                  <v-list-item
                    :id="`list-${item.transferType}`"
                    class="copy-normal"
                    @click="selectTransferType(item)"
                  >
                    <v-list-item-title class="pl-5">
                      {{ item.textLabel }}
                    </v-list-item-title>
                  </v-list-item>
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
import { TransferTypes } from '@/resources'
import { useGetters } from 'vuex-composition-helpers'
// eslint-disable-next-line no-unused-vars
import { FormIF, TransferTypeSelectIF } from '@/interfaces'

export default defineComponent({
  name: 'TransferType',
  emits: ['emitType', 'emitDeclaredValue', 'emitValid'],
  props: { validate: { type: Boolean, default: false } },
  setup (props, context) {
    const { customRules, required, isNumber, maxLength } = useInputRules()
    const transferTypeSelectRef = ref(null)
    const declaredValueRef = ref(null)

    const {
      getMhrTransferType,
      getMhrTransferDeclaredValue
    } = useGetters<any>([
      'getMhrTransferType',
      'getMhrTransferDeclaredValue'
    ])

    const localState = reactive({
      isValid: false,
      declaredValue: getMhrTransferDeclaredValue.value,
      selectedTransferType: getMhrTransferType.value as TransferTypeSelectIF,
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

    const selectTransferType = (val: TransferTypeSelectIF): void => {
      context.emit('emitType', val)
      localState.selectedTransferType = val
      // @ts-ignore - function exists
      context.refs.transferTypeSelectRef.blur()
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

    return {
      hasError,
      required,
      TransferTypes,
      transferTypeSelectRef,
      declaredValueRef,
      selectTransferType,
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
