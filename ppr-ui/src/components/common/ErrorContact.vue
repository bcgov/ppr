<template>
  <v-container class="contact-container pa-0 mt-n1">
    <v-row v-for="(item, index) in contactInfo" :key="index" class="contact-item pt-1" no-gutters>
      <v-col class="contact-label" cols="auto">
        <v-icon class="contact-icon" color="darkBlue" small>{{ item.icon }}</v-icon>
        <span class="contact-key pl-2">{{ item.label }}</span>
      </v-col>
      <v-col class="pl-1" cols="auto">
        <a class="contact-value" :href="item.href">{{ item.value }}</a>
      </v-col>
    </v-row>
  </v-container>
</template>
<script lang="ts">
// external
import {
  defineComponent
} from '@vue/composition-api'

export default defineComponent({
  name: 'ErrorContact',
  setup (props) {
    const contactInfo = [
      {
        icon: 'mdi-phone',
        label: 'Canada and U.S. Toll Free:',
        value: '1-877-526-1526',
        href: 'tel:+1-877-526-1526'
      },
      {
        icon: 'mdi-phone',
        label: 'Victoria Office:',
        value: '250-952-0568',
        href: 'tel:+1-250-952-0568'
      },
      {
        icon: 'mdi-email',
        label: 'Email:',
        value: 'BCRegistries@gov.bc.ca',
        href: 'mailto:BCRegistries@gov.bc.ca'
      }
    ]
    return {
      contactInfo
    }
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.contact-container {
  color: $gray7;
  font-size: 1rem;
}
</style>
