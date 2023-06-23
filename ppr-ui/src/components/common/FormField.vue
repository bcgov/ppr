<template>
  <v-row no-gutters>
    <v-col cols="3">
      <label
        class="generic-label"
        :class="{ 'error-text': showErrors && hasError }"
        :data-test-id="`${sectionId}-label`"
      >
        {{ inputTitle }}
      </label>
    </v-col>
    <v-col cols="9">
      <v-text-field
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
  props: {
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
    setValue: {
      type: Function,
      required: true
    },
    showErrors: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const field = ref(null)
    const localState = reactive({
      inputModel: props.initialValue || '',
      hasError: computed(() => field.value?.hasError)
    })

    watch(() => localState.inputModel, (val: string) => {
      props.setValue(val)
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
