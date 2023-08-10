<template>
  <ol class="pl-0">
    <div
      v-for="(requirement, index) in requirements"
      :key="index"
    >
      <li class="ml-14 px-3">

        <!-- Requirement with tooltip text -->
        <p  v-if="requirement.tooltipText" class="ma-0">
          <b>
            {{ requirement.boldTextPreTooltip }}
            <v-tooltip top content-class="top-tooltip" transition="fade-transition">
              <template #activator="{ on }">
                <span v-on="on" class="dotted-underline" tabindex="0">
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
        <p class="ma-0" v-else>
          <b>{{ requirement.boldText }}</b>
          {{ requirement.regularText }}
        </p>
      </li>
      <v-divider v-if="index + 1 !== requirements.length" class="my-7 ml-0 mr-1" />
    </div>
  </ol>
</template>

<script lang="ts">
import { defineComponent } from 'vue-demi'
import { RequirementsConfigIF } from '@/interfaces'

export default defineComponent({
  name: 'ListRequirements',
  props: { requirements: { type: Array as () => Array<RequirementsConfigIF>, required: true } },
  setup () {}
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
li {
  color: $gray7;
}
</style>
