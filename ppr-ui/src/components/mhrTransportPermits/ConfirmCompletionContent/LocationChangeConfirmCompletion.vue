<template>
  <ol
    id="confirm-location-change"
    class="pl-6"
  >
    <li>
      <strong>Current home location and homeowner(s) named in the Manufactured Home Registry match</strong>
      the registered home location and ownership of the home on the Registered Location form.
      <v-divider class="my-6 ml-n8" />
    </li>
    <li>
      <strong>A
        <v-tooltip
          location="top"
          content-class="top-tooltip pa-5"
          transition="fade-transition"
        >
          <template #activator="{ props }">
            <span
              class="underline"
              v-bind="props"
            >tax collector’s clearance certificate for transport purposes</span>
          </template>
          A certificate or confirmation in electronic format that confirms that no
          property taxes are unpaid. Reference Manufactured Home Act sections 25 and 26(2).
        </v-tooltip></strong>
      showing that all local taxes for the current year have been paid is required in most cases for
      manufactured homes that:
      <ol
        type="a"
        class="mt-1"
      >
        <li class="pb-0">
          is not located on a manufacturer’s or a dealer's lot.
        </li>
        <li class="pt-0">
          has not moved to a different pad within the same park.
        </li>
      </ol>
      <v-divider class="my-6 ml-n8" />
    </li>
    <li>
      <strong>Personal Property Registry search has been completed</strong> and there are no liens that
      block the transport permit. PPR registrations that block the transport permit include the following:
      <ul
        class="mt-1"
      >
        <li>Land Tax Deferment Lien on a Manufactured Home</li>
        <li>Maintenance Lien</li>
        <li>Manufactured Home Notice</li>
      </ul>
    </li>
  </ol>
</template>
