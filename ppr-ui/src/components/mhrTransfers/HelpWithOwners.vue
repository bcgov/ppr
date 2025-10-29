<template>
  <div>
    <h3 class="text-center mb-7 mt-4">
      Help with Ownership Transfer or Change
    </h3>
    <h4>
      Sole Ownership
    </h4>
    <p>This applies when the home is owned by a single individual or organization.</p>
    <h4>Joint Tenancy</h4>
    <p>
      This applies when the home is owned by two or more individuals and/or organizations jointly, with rights of
      survivorship. In joint tenancy, if one joint tenant dies (or for an organization, if it ceases to exist) their
      ownership share in the home passes to the surviving joint owner(s).
    </p>
    <h4>Tenants in Common</h4>
    <p>
      This applies when the home is owned by two or more individuals and/or organizations that owns an undivided share
      in the home. Ownership will be displayed in groups of owners with their undivided portion. Each owner has the
      right to dispose of their share independently of the other owners, and in the case of the death of an individual,
      their share will belong to the estate of the individual, or through the legal process for dissolution of assets,
      in the case of an organization.
    </p>
    <h4>Definition for Groups</h4>
    <p>
      A group is one or more owners of the home that have an equal undivided share of the home. Tenants in common are
      recorded in the Manufactured Home Registry in groups. The relationship between groups will always be as tenants in
      common. The relationship between owners within each group is a joint tenancy. There may be multiple groups with
      joint tenants.
    </p>
    <h4>Recording Ownership for Multiple Groups</h4>
    <p>
      Each group’s ownership share must be recorded as a portion of the total number of equal shares in the home. For
      example, if the home is owned by two groups, and each owns half of the home, this is recorded as each group
      holding 1 of 2 shares. If the home is owned by two groups but one group holds two-thirds and one group holds
      one-third, this is recorded as the first group holding 2 of 3 shares and the second group holding 1 of 3 shares.
    </p>
    <p>
      When adding groups of owners, you must enter the total number of shares in the home (Total Available) and the
      number of shares owned by each group (Amount Owned by the Group). All groups should use the same denominator as is
      used for Total Available, preferably using the lowest common denominator for all groups.
    </p>
    <h4>Qualified Supplier Limitations</h4>
    <p>
      As indicated in the Manufactured Home Registry, some complex ownership transfers, including transfers of an
      interest in a home to a trustee or a trust of any kind or to a surviving joint tenant following an organization
      ceasing to exist, cannot be completed online.
    </p>
    <p>
      If the transfer or change of ownership you are trying to register cannot be completed online, the request must be
      sent to the Manufactured Home Registry for BC Registries staff to submit on your behalf.
    </p>
    <p>
      Send your Ownership Transfer or Change form, Bill of Sale form (if applicable), plus supporting documents and fee
      to:
    </p>
    <p>
      Manufactured Home Registry <br>
      PO Box 9431 Stn Prov Govt<br>
      Victoria, B.C.<br>
      V8W 9V3
    </p>
    <p>
      <a
        href="https://www2.gov.bc.ca/gov/content/housing-tenancy/owning-a-home/manufactured-home-registry#forms-fees"
        target="_blank"
      >
        Visit the Manufactured Home Registry forms and fees page<i class="mdi mdi-open-in-new ml-1" />
      </a>
    </p>

    <h4 class="mb-6">
      Need Help? Contact Us
    </h4>
    <ErrorContact class="mb-6" />

    <h4>Hours of Operation: </h4>
    <p>Monday to Friday, 8:30 am - 4:30 pm Pacific time</p>
  </div>
</template>

<script setup lang="ts">
import ErrorContact from '@/components/common/ErrorContact.vue'
</script>


<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;

h4 {
  font-size: 16px;
  line-height: normal;
  color: $gray7;
}

p {
  margin-bottom: 24px;
}
</style>
