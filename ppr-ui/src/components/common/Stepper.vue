<template>
  <v-container id="step-buttons-container" :class="$style['step-buttons-container']" pb-0>
    <template v-for="(step, index) in getSteps">
      <div
        :class="isCurrentStep(step) ? [$style['step__border__current'], $style['step']]: $style['step']"
        :key="index"
        @click="goTo(step)"
        v-on:keyup.tab="goTo(step)"
        >
        <div :class="$style['step__indicator']">
          <div :class="$style['step__line']"></div>
          <v-btn
            outlined fab
            color="primary"
            :id=step.id
            :class="isCurrentStep(step) ? [$style['selected-btn'], $style['step__btn']] : $style['step__btn']"
            tabindex="-1"
            :disabled=step.disabled
            :ripple="false">
            <v-icon class="step-icon" :class="isCurrentStep(step) ?
              [$style['selected-icon'], $style['step__icon']]: $style['step__icon']">
              {{ step.icon }}
            </v-icon>
          </v-btn>
          <v-icon :class="$style['step__btn2']" size="30" color="green darken-3" v-show=step.valid>
            mdi-check-circle
          </v-icon>
          <v-icon :class="$style['step__btn2']" size="30" color="error" v-show=showInvalid(step)>
            mdi-close-circle
          </v-icon>
        </div>
        <v-btn :class="[$style['step__label'], $style['pre-line']]" text color="primary" :ripple="false"
          :disabled=step.disabled v-show=!isCurrentStep(step)>
          <span :class="$style['step__label__text']" v-html="step.text"></span>
        </v-btn>
        <v-btn :class="[$style['step__label__current'], $style['pre-line']]" text color="primary" :ripple="false"
          :disabled=step.disabled v-show=isCurrentStep(step)>
          <span :class="$style['step__label__text__current']" v-html="step.text"></span>
        </v-btn>
      </div>
    </template>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'Stepper',
  components: {},
  props: {
    showStepErrorsFlag: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { getSteps, showStepErrors } = useGetters<any>([
      'getSteps', 'showStepErrors'
    ])

    const goTo = (step) => {
      context.root.$router.push(step.to).catch(error => error)
    }

    const isCurrentStep = (step): boolean => {
      return context.root.$route.name === step.to
    }

    const showInvalid = (step): boolean => {
      return ((showStepErrors.value || props.showStepErrorsFlag) && (!step.valid))
    }

    const localState = reactive({})

    return {
      getSteps,
      goTo,
      isCurrentStep,
      showInvalid,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';

.step-buttons-container {
  min-width: 830px;
  display: flex;
  justify-content: space-evenly;
  margin: 0;
  padding: 2rem 0 0 0;
  background: $BCgovInputBG;
  border-radius: 4px;
  box-shadow: 0px 3px 1px -2px rgb(0 0 0 / 20%), 0px 2px 2px 0px rgb(0 0 0 / 14%), 0px 1px 5px 0px rgb(0 0 0 / 12%);
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

  g {
    transition: 0.3s cubic-bezier(0.25, 0.8, 0.5, 1), visibility 0s;
    fill: #fff; // fill for custom SVG icons
  }

  .step__icon {
    color: #fff;
    background: inherit;
  }
}

.selected-btn {
  g {
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
  border-bottom-left-radius: 0px;
  border-bottom-right-radius: 0px;
}

.step__label__text {
  margin-bottom: 2px;
  text-align: center;
  color: $primary-blue !important;
  font-size: 14px !important;
}

.step__label__text__current {
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
