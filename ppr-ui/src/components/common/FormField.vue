<template>
  <v-row no-gutters>
    <v-col :cols="labelColWidth">
      <label
        class="generic-label"
        :class="{ 'error-text': showErrors && hasError }"
        :data-test-id="`${sectionId}-label`"
      >
        {{ inputTitle }}
      </label>
    </v-col>
    <v-col :cols="inputColWidth">
      <v-text-field
        class="px-1"
        ref="field"
        filled
        :label="inputLabel"
        v-model="inputModel"
        :rules="rules"
        :data-test-id="`${sectionId}-text-field`"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue-demi'

export default defineComponent({
  name: 'FormField',
  emits: ['updateValue'],
  props: {
    labelColWidth: {
      type: Number,
      default: 3
    },
    inputColWidth: {
      type: Number,
      default: 9
    },
    initialValue: {
      type: String,
      required: false
    },
    inputTitle: {
      type: String,
      required: true
    },
    inputLabel: {
      type: String,
      required: true
    },
    rules: {
      type: Array,
      required: true
    },
    sectionId: {
      type: String,
      required: true
    },
    showErrors: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const field = ref(null)
    const localState = reactive({
      inputModel: props.initialValue || '',
      hasError: computed(() => field.value?.hasError)
    })

    watch(() => localState.inputModel, (val: string) => {
      emit('updateValue', val)
    })

    return {
      field,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
