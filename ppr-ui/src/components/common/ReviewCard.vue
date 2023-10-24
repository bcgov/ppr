<template>
  <v-card
    id="review-card"
    flat
    aria-label="review-card"
  >
    <!-- Header Slot -->
    <slot name="headerSlot">
      <header class="review-header">
        <v-icon
          class="ml-1"
          color="darkBlue"
        >
          mdi-account
        </v-icon>
        <label class="font-weight-bold pl-2">Common Review Card</label>
      </header>
    </slot>

    <div
      id="review-card-content"
      :class="{ 'border-error-left': showIncomplete }"
    >
      <!-- Incomplete Section Msg -->
      <section
        v-if="showIncomplete"
        class="mx-7 pt-9"
        :class="{ 'pb-9' : !hasData }"
      >
        <v-icon color="error">
          mdi-information-outline
        </v-icon>
        <span class="error-text mx-1">This step is unfinished.</span>
        <router-link :to="{ path: returnRoute }">
          Return to this step to complete it.
        </router-link>
        <v-divider
          v-if="hasData"
          class="mt-8 mx-1"
        />
      </section>

      <!-- Party Info -->
      <template v-if="hasData || showNotEntered">
        <section
          v-for="(item, index) in reviewProperties"
          :key="item.label"
        >
          <FormCard :label="item.label">
            <template #infoSlot>
              <p class="mb-0">
                {{ item.property || '(Not Entered)' }}
              </p>
            </template>
          </FormCard>
          <v-divider
            v-if="index !== reviewProperties.length - 1"
            class="mx-8"
          />
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { RouteNames } from '@/enums'
import { hasTruthyValue } from '@/utils'
import { FormCard } from '@/components/common/index'

export default defineComponent({
  name: 'ReviewCard',
  components: { FormCard },
  props: {
    reviewProperties: {
      type: Array as () => Array<{ label: string, property: any }>,
      required: false
    },
    showIncomplete: {
      type: Boolean,
      default: true
    },
    showNotEntered: {
      type: Boolean,
      default: false
    },
    returnToRoutes: {
      type: Array as () => Array<RouteNames>,
      default: () => []
    }
  },
  setup (props) {
    const localState = reactive({
      hasData: computed(() : boolean => {
        return props.reviewProperties.some(({ property }) => Boolean(property))
      }),
      returnRoute: computed(() : string => {
        let returnRoute = ''
        for (const route of props.returnToRoutes) {
          returnRoute += `/${route}`
        }
        return returnRoute
      })
    })

    const hasPropData = (propertyName: string): boolean => {
      return props.reviewProperties?.hasOwnProperty(propertyName)
    }

    return {
      RouteNames,
      hasPropData,
      hasTruthyValue,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
