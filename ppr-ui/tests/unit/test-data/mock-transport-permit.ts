import { HomeLocationTypes } from "@/enums";
import { MhrRegistrationHomeLocationIF } from "@/interfaces";

export const mockTransportPermitNewLocation: MhrRegistrationHomeLocationIF = {
  address: {
    city: "CALGARY",
    country: "CA",
    postalCode: "",
    region: "AB",
    street: "123-720 COMMONWEALTH RD",
    streetAdditional: ''
  },
  leaveProvince: false,
  locationType: HomeLocationTypes.HOME_PARK,
  pad: '147',
  parkName: 'Fort York',
  permitWithinSamePark: false,
  taxCertificate: true,
  taxExpiryDate: "2024-02-06T08:01:00+00:00"
}

export const mockTransportPermitPreviousLocation: MhrRegistrationHomeLocationIF = {
    address: {
      city: 'VICTORIA',
      country: 'CA',
      postalCode: 'V1V 1G1',
      region: 'BC',
      street: '11 SKY VIEW DR',
      streetAdditional: ''
    },
    leaveProvince: false,
    legalDescription: 'THE NORTH WEST 1/4 OF SECTION 8',
    locationType: HomeLocationTypes.OTHER_STRATA,
    pidNumber: '111222333',
    taxCertificate: false
}
