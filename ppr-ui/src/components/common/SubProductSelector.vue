<template>
  <v-form id="sub-product-selector" ref="productSelectorFormRef">
    <v-radio-group
      hide-details
      v-model="selectedProduct"
      class="sub-product-radio-group pt-0 mt-0"
    >
      <div
        v-for="(subProduct, index) in subProductConfig"
        class="sub-product-radio-wrapper"
        :key="subProduct.type"
      >
        <v-radio
          class="sub-product-radio-btn"
          :value="subProduct.type"
        >
          <template v-slot:label>
            <v-row no-gutters>
              <v-col cols="12">
                <label class="sub-product-label generic-label">{{ subProduct.label }}</label>
              </v-col>
              <v-col class="mt-2">
                <p>
                  <ul class="ml-n2">
                    <li v-for="(bullet, index) in subProduct.productBullets" :key="index" class="bullet mt-2">
                      <span :class="{ 'font-weight-bold': isImportantBullet(subProduct, index) }">
                        {{ bullet }}
                      </span>
                    </li>
                  </ul>
                </p>
              </v-col>
            </v-row>
          </template>
        </v-radio>
        <!-- Attached Selection Notes -->
        <p v-if="subProduct.note" class="sub-product-note mt-n2 ml-8 mb-6">
          <strong>Note:</strong> <span v-html="subProduct.note"></span>
        </p>
        <v-divider v-if="index !== subProductConfig.length - 1" class="ml-n1 mb-6" />
      </div>
    </v-radio-group>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { SubProductConfigIF } from '@/interfaces'
import { MhrSubTypes } from '@/enums'

export default defineComponent({
  name: 'SubProductSelector',
  emits: ['updateSubProduct'],
  props: {
    subProductConfig: {
      type: Array as () => Array<SubProductConfigIF>,
      default: () => []
    },
    defaultProduct: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const productSelectorFormRef = ref(null)
    const localState = reactive({
      selectedProduct: props.defaultProduct
    })

    const isImportantBullet = (subProduct: SubProductConfigIF, index: string|number) => {
      return subProduct.hasImportantBullet && index === subProduct.productBullets.length - 1
    }

    /** Update product radio option on prop change **/
    watch(() => props.defaultProduct, (val: string) => {
      localState.selectedProduct = val
    })

    /** Emit the sub-product as it updates **/
    watch(() => localState.selectedProduct, (subProduct: string) => {
      emit('updateSubProduct', subProduct as MhrSubTypes)
    })

    return {
      productSelectorFormRef,
      isImportantBullet,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#sub-product-selector {
  margin-top: 2px;
}
.sub-product-label {
  cursor: pointer;
}
.sub-product-note {
  font-size: 14px;
  line-height: 22px;
  cursor: default;
  color: $gray7;
}

// TODO: Move this to Base
:deep() {
  a {
    color: $app-blue!important;
    text-decoration: underline;
  }
  .v-divider {
    border-color: $gray3!important;
  }
  .v-radio {
    align-items: unset;
  }
  .v-input .v-label {
    font-size: 16px;
    color: $gray9;
    font-weight: bold;
  }
  li {
    color: $gray7;
    font-size: 16px;
  }
}
</style>
