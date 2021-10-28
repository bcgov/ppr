<template>
  <v-container class="contact-container pa-0 mt-n1">
    <v-row v-for="(item, index) in contactInfo" :key="index" class="contact-item pt-1" no-gutters>
      <v-col class="contact-label" cols="auto">
        <v-icon class="contact-icon" color="primary" small>{{ item.icon }}</v-icon>
        <span class="contact-key font-weight-bold pl-1">{{ item.label }}</span>
      </v-col>
      <v-col cols="auto">
        <a class="contact-value" :href="item.href">{{ item.value }}</a>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
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
        label: 'BC Registries Email:',
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
.contact-container {
  font-size: 0.9rem;
}
.contact-label {
  width: 215px;
}
</style>
