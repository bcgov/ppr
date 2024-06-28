<template>
  <v-table id="simple-table">
    <thead>
      <tr>
        <th
          v-for="(header, index) in tableHeaders"
          :key="`${header.name}-${index}`"
          :class="header?.class"
        >
          {{ header.name }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(item, index) in tableData"
        :key="`${item.name}-${index}`"
      >
        <td>{{ item.name }}</td>
      </tr>
    </tbody>
  </v-table>
</template>

<script setup lang="ts">
// import { onMounted, ref } from 'vue'
// import { getMhrHistory, pacificDate } from '@/utils'
// import { useAuth, useNavigation } from '@/composables'
// import { getFeatureFlag } from '@/utils'
// import { storeToRefs } from 'pinia'
// import { useStore } from '@/store/store'
// import { TabbedContainer } from '@/components/common'
//
// /** Composables **/
// const { isAuthenticated } = useAuth()
// const { goToDash } = useNavigation()
// const { getMhrInformation } = storeToRefs(useStore())

/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  tableHeaders: Array<any>,
  tableData: Array<any>
}>(), {
  tableHeaders: null,
  tableData: null
})


// /** Local Properties **/
// const dataLoaded = ref(true)
// const loading = ref(false)
// const mhrHistory = ref({})
//
//
// onMounted(async (): Promise<void> => {
//   // do not proceed if app is not ready
//   // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
//   if (!props.appReady || !isAuthenticated.value || !getFeatureFlag('mhr-history-enabled')) {
//     await goToDash()
//     return
//   }
//
//   // Fetch Manufactured Home History
//   loading.value = true
//   mhrHistory.value = await getMhrHistory(getMhrInformation.value?.mhrNumber)
//   loading.value = false
// })

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';

</style>
