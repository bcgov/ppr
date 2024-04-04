<template>
  <ol
    id="confirm-transport-permit"
    class="pl-6"
  >
    <li>
      <strong>The homeowner(s) named in the Manufactured Home Registry match</strong>
      the current ownership of the home on the Transportation Application form.
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
      which shows the following:
      <ol
        type="a"
        class="mt-1"
      >
        <li class="pb-0">
          all local taxes for the current year have been paid
        </li>
        <li class="pt-0">
          original location of the home matches the location on the tax certificate
        </li>
      </ol>
      <p class="mt-5">
        <strong>Note: </strong>A tax certificate is not required for manufactured homes that are located on a
        manufacturer or a dealer's lot, or moving to a different pad within the same park.
      </p>
      <v-divider class="my-6 ml-n8" />
    </li>
    <li>
      <strong>Personal Property Registry search has been completed</strong> and there are no liens that block
      the transport permit. PPR registrations that block the transport permit include the following:
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
      <strong>If the manufactured home is not moved before the transport permit expires</strong>,
      you must report the physical location of the manufactured home within 3 days of expiry of the permit.
      <v-divider class="my-6 ml-n8" />
    </li>
    <li class="pb-3">
      <strong>If the home is permanently moved to a different location than what is specified on the transport
        permit</strong>, you must report the physical location of the manufactured home within 3 days of the move.
    </li>
  </ol>
</template>
