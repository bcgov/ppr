<template>
  <ol class="pl-0">
    <div
      v-for="(requirement, index) in requirements"
      :key="index"
    >
      <li class="ml-6 px-3">
        <!-- Requirement with tooltip text -->
        <p
          v-if="requirement.tooltipText"
          class="ma-0"
        >
          <b>
            {{ requirement.boldTextPreTooltip }}
            <v-tooltip
              location="top"
              contentClass="top-tooltip"
              transition="fade-transition"
            >
              <template #activator="{ props }">
                <span
                  class="dotted-underline"
                  tabindex="0"
                  v-bind="props"
                >
                  {{ requirement.underlinedText }}
                </span>
              </template>
              <div class="py-2">{{ requirement.tooltipText }}</div>
            </v-tooltip>
            {{ requirement.boldTextPostTooltip }}
          </b>
          {{ requirement.regularText }}
        </p>

        <!-- Requirement without tooltip text -->
        <p
          v-else
          class="ma-0"
        >
          <b>{{ requirement.boldText }}</b>
          {{ requirement.regularText }}
        </p>

        <!-- Requirements with bullets -->
        <ul
          v-if="requirement.bullets"
          class="mt-4 ml-1"
        >
          <li
            v-for="(bullet, index) in requirement.bullets"
            :key="index"
            class="pt-1"
          >
            {{ bullet }}
          </li>
        </ul>

        <!-- Requirement Notes -->
        <p
          v-if="requirement.note"
          class="mt-4"
        >
          <span class="font-weight-bold">Note:</span>
          <span class="fs-14">{{ requirement.note }}</span>
        </p>
      </li>
      <v-divider
        v-if="index + 1 !== requirements.length"
        class="my-7 ml-0 mr-1"
      />
    </div>
  </ol>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { RequirementsConfigIF } from '@/interfaces'

export default defineComponent({
  name: 'ListRequirements',
  props: { requirements: { type: Array as () => Array<RequirementsConfigIF>, required: true } },
  setup () {}
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
