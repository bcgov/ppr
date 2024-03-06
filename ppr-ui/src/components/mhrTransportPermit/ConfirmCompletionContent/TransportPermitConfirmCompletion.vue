<template>
  <ol
    id="confirm-transport-permit"
    class="pl-6"
  >
    <li>
      <strong>Current home location and homeowner(s) named in the Manufactured Home Registry match</strong>
      the current home location and ownership of the home on the Transport Application form.
      <v-divider class="my-6 ml-n8" />
    </li>
    <li>
      <strong>A
        <v-tooltip
          location="top"
          contentClass="top-tooltip pa-5"
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
      showing that all local taxes for the current year have been paid is required for
      manufactured homes that:
      <ol
        type="a"
        class="mt-1"
      >
        <li>
          are not located on a manufacturer’s or a dealer's lot.
        </li>
        <li>are not moving to a different pad within the same park.</li>
      </ol>
      <v-divider class="my-6 ml-n8" />
    </li>
    <li>
      <strong>Personal Property Registry search has been completed</strong> and there are no liens that
      block the transport permit. PPR registrations that block a transport permit include the following:
      <ul
        class="mt-1"
      >
        <li>Land Tax Deferment Lien on a Manufactured Home</li>
        <li>Maintenance Lien</li>
        <li>Manufactured Home Notice</li>
      </ul>
      <v-divider class="my-6 ml-n8" />
    </li>
    <li>
      <strong>A report must be submitted to the Registrar</strong> within 3 days of expiry if either of
      the following apply:
      <ol
        type="a"
        class="mt-1"
      >
        <li>The manufactured home is not moved before the transport permit expires</li>
        <li>
          The home is permanently moved to a different location than what is specified on
          the transport permit
        </li>
      </ol>
    </li>
  </ol>
</template>
