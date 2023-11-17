<template>
  <!-- Lien Information -->
  <v-row id="lien-information" no-gutters class="pt-10">
    <v-card
      id="important-message"
      class="rounded-0 px-8 py-5"
      :class="lienInfo.class"
      outlined
    >
      <v-icon v-if="lienInfo.class === 'error'" color="error" class="float-left mr-2 mt-n1">
        mdi-alert
      </v-icon>
      <p :class="lienInfo.class === 'warning' ? 'mb-0' : 'mb-0 pl-8'">
        <strong>Important:</strong> {{ lienInfo.msg }}
      </p>
    </v-card>

    <v-col class="mt-5">
      <v-btn
        outlined
        color="primary"
        class="mt-2 px-6"
        :ripple="false"
        data-test-id="lien-search-btn"
        @click="quickMhrSearch(mhrNumber)"
      >
        <v-icon class="pr-1">mdi-magnify</v-icon>
        Conduct a Combined MHR and PPR Search for MHR Number
        <strong>{{ mhrNumber }}</strong>
      </v-btn>
      <v-divider class="mx-0 mt-10 mb-6" />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { useRouter } from 'vue2-helpers/vue-router'
import { useMhrInformation } from '@/composables'
import { APIMHRMapSearchTypes, APISearchTypes, RouteNames, UIMHRSearchTypes } from '@/enums'
import { useStore } from '@/store/store'
import { mhrSearch } from '@/utils'
import { storeToRefs } from 'pinia'
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue-demi'

export default defineComponent({
  name: 'LienAlert',
  props: {
    setEndDate: { type: String }
  },
  emits: ['isLoading'],
  setup (props, { emit }) {
    const router = useRouter()

    const {
      setSearchedType,
      setManufacturedHomeSearchResults
    } = useStore()

    const {
      getMhrInformation
    } = storeToRefs(useStore())

    const {
      getLienInfo
    } = useMhrInformation()

    const localState = reactive({
      mhrNumber: getMhrInformation.value.mhrNumber,
      lienInfo: computed(() => getLienInfo())
    })

    const quickMhrSearch = async (mhrNumber: string): Promise<void> => {
      emit('isLoading', true)

      // Search for current Manufactured Home Registration Number
      const results = await mhrSearch({
        type: APISearchTypes.MHR_NUMBER,
        criteria: { value: mhrNumber },
        clientReferenceId: ''
      }, '')

      emit('isLoading', false)

      if (results) {
        // Set search type to satisfy UI requirements
        await setSearchedType({
          searchTypeUI: UIMHRSearchTypes.MHRMHR_NUMBER,
          searchTypeAPI: APIMHRMapSearchTypes.MHRMHR_NUMBER
        })

        // There is only 1 result for a mhr number search
        // Include lien info by default
        results.results[0].includeLienInfo = true

        await setManufacturedHomeSearchResults(results)
        await router.replace({
          name: RouteNames.MHRSEARCH
        })
      } else {
        console.error('Error: MHR_NUMBER expected, but not found.')
      }
    }

    return {
      quickMhrSearch,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#important-message {

  &.warning {
    background-color: $backgroundWarning !important;
    border-color: $warning;
  }

  &.error {
    background-color: $backgroundError !important;
    border-color: $error;
  }

  p {
    line-height: 22px;
    font-size: $px-14;
    letter-spacing: 0.01rem;
    color: $gray7;
  }
}

</style>
