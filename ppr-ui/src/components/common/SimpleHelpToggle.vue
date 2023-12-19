<template>
  <div id="help-toggle-container">
    <v-btn
      variant="plain"
      color="primary"
      class="help-btn px-0"
      :ripple="false"
      data-test-id="help-toggle-btn"
      @click="isHelpContentOpen = !isHelpContentOpen"
    >
      <v-icon class="mr-1">
        mdi-help-circle-outline
      </v-icon>
      {{ title }}
    </v-btn>
    <v-expand-transition>
      <div
        v-show="isHelpContentOpen"
        class="help-content mb-10"
      >
        <hr class="my-4">
        <slot
          name="content"
          class="content"
        />
        <div
          v-if="hasBottomHideToggle"
          class="hide-help-btn-wrapper"
        >
          <v-btn
            variant="plain"
            color="primary"
            class="hide-help-btn px-0"
            :ripple="false"
            @click="isHelpContentOpen = !isHelpContentOpen"
          >
            Hide Help
          </v-btn>
        </div>
        <hr class="mt-6 mb-4">
      </div>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'

export default defineComponent({
  name: 'SimpleHelpToggle',
  props: {
    toggleButtonTitle: {
      type: String,
      default: ''
    },
    /* show or hide secondary toggle within content */
    hasBottomHideToggle: {
      type: Boolean,
      default: true
    }
  },
  setup (props) {
    const localState = reactive({
      isHelpContentOpen: false,
      hideText: props.toggleButtonTitle ? 'Hide ' + props.toggleButtonTitle : 'Hide Help',
      title: computed(() : string => localState.isHelpContentOpen ? localState.hideText : props.toggleButtonTitle)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#help-toggle-container {
  // Remove background on hover
  .help-btn::before,
  .hide-help-btn::before {
    display: none;
  }

  .help-btn {
    font-size: 16px;
    height: 24px;
  }

  .hide-help-btn-wrapper {
    display: flex;
    flex-direction: row-reverse;
  }

  .hide-help-btn {
    font-size: 14px;
    text-decoration: underline;
    height: 25px;
  }

  .help-content {
    h3 {
      color: $gray9;
    }
    h4,
    p {
      color: $gray7;
    }
    hr {
      border-top: 1px dashed $gray6;
    }
  }
}
</style>
