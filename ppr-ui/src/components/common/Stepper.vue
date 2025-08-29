<template>
  <v-container
    id="step-buttons-container"
    class="pb-0 step-buttons-container"
  >
    <div
      v-for="(step, index) in stepConfig"
      :key="index"
      :class="isCurrentStep(step) ? 'step step__border__current' : 'step'"
      @click="goTo(step)"
      @keyup.tab="goTo(step)"
    >
      <div class="step__indicator">
        <div class="step__line" />
        <v-btn
          :id="step.id"
          variant="outlined"
          color="primary"
          :class="isCurrentStep(step) ? 'selected-btn step__btn' : 'step__btn'"
          tabindex="-1"
          :disabled="step.disabled"
          :ripple="false"
          :icon="step.icon"
          size="56"
          :aria-label="step.id"
        >
          <v-icon
            class="step-icon"
            :class="isCurrentStep(step) ? 'selected-icon step__icon' : 'step__icon'"
          >
            {{ step.icon }}
          </v-icon>
        </v-btn>
        <v-icon
          v-if="step.valid"
          class="step__btn2"
          size="30"
          color="green-darken-3"
          :data-test-id="`step-valid-${step.id}`"
        >
          mdi-check-circle
        </v-icon>
        <v-icon
          v-if="showInvalid(step)"
          class="step__btn2"
          size="30"
          color="error"
          :data-test-id="`step-invalid-${step.id}`"
        >
          mdi-close-circle
        </v-icon>
      </div>
      <v-btn
        v-if="!isCurrentStep(step)"
        class="step__label pre-line"
        variant="plain"
        color="primary"
        :ripple="false"
        :disabled="step.disabled"
        :data-test-id="step.id"
      >
        <span
          class="step__label__text"
          v-html="step.text"
        />
      </v-btn>
      <v-btn
        v-if="isCurrentStep(step)"
        class="step__label__current pre-line"
        variant="plain"
        color="primary"
        :ripple="false"
        :disabled="step.disabled"
        :data-test-id="`current-${step.id}`"
      >
        <p
          class="step__label__text__current"
          v-html="step.text"
        />
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { StepIF } from '@/interfaces'

export default defineComponent({
  name: 'Stepper',
  props: {
    stepConfig: {
      type: Array as () => Array<StepIF>,
      default: () => []
    },
    showStepErrors: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const route = useRoute()
    const router = useRouter()

    const goTo = (step) => {
      router.push(step.to).catch(error => error)
    }

    const isCurrentStep = (step): boolean => {
      return route.name === step.to
    }

    const showInvalid = (step): boolean => {
      return props.showStepErrors && !step.valid
    }

    return {
      goTo,
      isCurrentStep,
      showInvalid
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
.step-buttons-container {
  min-width: 830px;
  display: flex;
  justify-content: space-evenly;
  margin: 0;
  padding: 2rem 0 0 0;
  background: $BCgovInputBG;
  border-radius: 4px;
  box-shadow: 0 3px 1px -2px rgb(0 0 0 / 20%), 0px 2px 2px 0px rgb(0 0 0 / 14%), 0px 1px 5px 0px rgb(0 0 0 / 12%);
}
svg { // only affects custom icon sizing
  height: 29px !important;
  width: 29px !important;
}

.v-btn:before {
  background-color: $BCgovInputBG !important;
}

.step {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  align-items: center;
  justify-content: center;
  padding-bottom: 2rem;
  border-bottom: 3px solid #ffffff !important;
}

.step:hover {
  cursor: pointer;

  .step__btn {
    background: linear-gradient($primary-blue, $primary-blue),
                linear-gradient(rgba(255, 255, 255, 1), rgba(255, 255, 255, 1)); // first bg is layered on top
    color: $BCgovInputBG;
  }

  .v-btn:before {
    background-color: $primary-blue;
  }

  :deep(g) {
    transition: 0.3s cubic-bezier(0.25, 0.8, 0.5, 1), visibility 0s !important;
    fill: #fff !important; // fill for custom SVG icons
  }

  .step__icon {
    color: #fff;
    background: inherit;
  }
}

.selected-btn {
  :deep(g) {
    fill:#fff; // fill for custom SVG icons
  }
  background-color: $primary-blue !important;
}

.selected-icon {
  color: $BCgovInputBG !important;
}

.step__indicator {
  position: relative;
  width: 100%;
  text-align: center;
}

.step__line {
  position: absolute;
  top: 50%;
  left: 0;
  height: 1px;
  width: 100%;
  background-color: $gray3;
}

.step:first-child .step__line {
  transform: translateX(50%);
}

.step:last-child .step__line {
  transform: translateX(-50%);
}

.step__btn {
  position: relative;
  background-color: $BCgovInputBG;
  z-index: 2;
  .step__icon {
    font-size: 30px !important;
    color: $primary-blue;
    background-color: inherit;
  }
}

.step__btn2 {
  position: absolute !important;
  top: 29px;
  margin-top: -32px;
  margin-left: -16px;
  background: $BCgovInputBG;
  border-radius: 50%;
  z-index: 3;
}

.step__label {
  margin-top: 10px;
  text-align: center;
}

.step__label__current {
  margin-top: 10px;
  text-align: center;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.step__label__text {
  margin-bottom: 2px;
  text-align: center;
  color: $primary-blue !important;
  font-size: 14px !important;
  text-transform: none;
}

.step__label__text__current {
  text-transform: none;
  margin-bottom: 2px;
  text-align: center;
  color: #212529 !important;
  font-size: 14px !important;
  font-weight: bold !important;
}

.step__border__current {
  border-bottom: 3px solid $primary-blue !important;
}
</style>
