<template>
  <v-card flat id="unit-notes-table" class="mt-6">
    <header class="review-header notes-header py-0 align-center">
      <v-col cols="9" class="pa-0">
        <v-icon class="ml-2" color="darkBlue">mdi-message-reply-text</v-icon>
        <span class="font-weight-bold pl-2">Unit Notes</span>
      </v-col>

      <v-col cols="3" class="text-right pr-0">
        <v-menu offset-y right nudge-bottom="0" height="300" class="notes-dropdown">
          <template v-slot:activator="{ on, value }">
            <v-btn text v-on="on" color="primary" class="px-0">
              <v-icon>mdi-plus</v-icon>
              <span class="ml-1 remove-btn-text">Add Unit Note</span>
              <v-icon color="primary">
                {{ value ? 'mdi-menu-up' : 'mdi-menu-down' }}
              </v-icon>
            </v-btn>
          </template>

          <v-list class="actions-dropdown actions__more-actions">
            <v-list-item
              v-for="item in addUnitNoteDropdown"
              :key="item.unitNoteType"
              dense
              @click="initUnitNote(item.unitNoteType)">
              <v-list-item-content>
                <v-list-item-title>{{ item.textLabel }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-col>
    </header>
    <div v-if="unitNotes.length === 0" class="note-not-filed">
      A unit note has not been filed for this manufactured home.
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { useRouter } from 'vue2-helpers/vue-router'
import { unitNotes } from '@/resources/mhr-transfers/unit-notes'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { MhrUnitNoteIF } from '@/interfaces'
import { RouteNames, UnitNoteDocTypes } from '@/enums'

export default defineComponent({
  name: 'UnitNotesTable',
  setup () {
    const router = useRouter()
    const {
      setMhrUnitNoteType
    } = useStore()

    const {
      getMhrRegistrationUnitNotes
    } = storeToRefs(useStore())

    const initUnitNote =
      (documentType: UnitNoteDocTypes): void => {
        setMhrUnitNoteType(documentType)
        router.push({ path: '/' + RouteNames.MHR_INFORMATION_NOTE })
      }

    const localState = reactive({
      unitNotes: computed((): MhrUnitNoteIF[] =>
        getMhrRegistrationUnitNotes.value
      ),
      addUnitNoteDropdown: unitNotes.addUnitNoteDropdown
    })

    return {
      initUnitNote,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
#unit-notes-table {
  .notes-header {
    // padding: 10px;
    display: flex;
    justify-content: space-between;
  }

  .notes-dropdown .v-menu__content {
    max-height: 300px;
    overflow: scroll;
  }

  .note-not-filed {
    font-size: 14px;
    padding: 35px 0;
    text-align: center;
  }
}
</style>
