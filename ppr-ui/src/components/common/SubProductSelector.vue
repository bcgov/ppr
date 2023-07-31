<template>
  <v-card flat class="px-8 py-8">
    <v-row no-gutters>
      <v-col cols="2">
        <label
          class="generic-label"
          for="sub-product-selector"
          :class="{ 'error-text': false }"
        >
          Select Access Type
        </label>
      </v-col>
      <v-col class="ml-8">
        <!-- Access Type Form -->
        <v-form
          id="sub-product-selector"
          ref="productSelectorFormRef"
        >
          <v-radio-group
            hide-details
            v-model="selectedProduct"
            class="sub-product-radio-group pt-0 mt-0"
          >
            <div
              v-for="(subProduct, index) in subProductConfig"
              :key="subProduct.type"
              class="sub-product-radio-wrapper"
            >
              <v-radio
                class="sub-product-radio-btn"
                :value="subProduct.type"
              >
                <template v-slot:label>
                  <v-row no-gutters>
                    <v-col cols="12">
                      <label class="sub-product-label">{{ subProduct.label }}</label>
                    </v-col>
                    <v-col class="mt-1">
                      <p>
                        <ul class="ml-n1">
                          <li v-for="(bullet, index) in subProduct.productBullets" :key="index" class="bullet mt-2">
                            <span :class="{ 'font-weight-bold': isImportantBullet(subProduct, index) }">
                              {{ bullet }}
                            </span>
                          </li>
                        </ul>
                      </p>
                      <p v-if="subProduct.note" class="sub-product-note pr-3">
                        <strong>Note:</strong> <span v-html="subProduct.note"></span>
                      </p>
                    </v-col>
                  </v-row>
                </template>
              </v-radio>
              <v-divider v-if="index !== subProductConfig.length - 1" class="ml-n1 mb-6" />
            </div>
          </v-radio-group>
        </v-form>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { SubProductConfigIF } from '@/interfaces'

export default defineComponent({
  name: 'SubProductSelector',
  emits: ['updateSubProduct'],
  props: {
    subProductConfig: {
      type: Array as () => Array<SubProductConfigIF>,
      default: () => []
    }
  },
  setup (props, { emit }) {
    const productSelectorFormRef = ref(null)
    const localState = reactive({
      selectedProduct: ''
    })

    const isImportantBullet = (subProduct: SubProductConfigIF, index: string|number) => {
      return subProduct.hasImportantBullet && index === subProduct.productBullets.length - 1
    }

    /** Emit the sub-product as it updates **/
    watch(() => localState.selectedProduct, (subProduct: string) => {
      emit('updateSubProduct', subProduct)
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
.sub-product-label {
  cursor: pointer;
}
.sub-product-note {
  font-size: 14px;
  line-height: 22px;
  cursor: default;
}

::v-deep {
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
