# -*- coding: utf-8 -*-
import base64
import requests
from bs4 import BeautifulSoup
from odoo import api, fields, models, _

class RoomBooking(models.Model):
    _inherit = "room.booking"

    booking_source = fields.Selection([
        ('walk_in', 'Khách vãng lai (Walk-in)'),
        ('booking_com', 'Booking.com'),
        ('agoda', 'Agoda'),
        ('website', 'Website khách sạn'),
        ('hotline', 'Hotline/Zalo'),
        ('other', 'Nguồn khác')
    ], string='Nguồn đặt phòng', default='walk_in', tracking=True)

    def auth_booking_com(self, url):
        username = self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.username_booking_com')
        password = self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.password_booking_com')
        credentials = f"{username}:{password}".encode('utf-8')
        encoded_credentials = base64.b64encode(credentials).decode('utf-8')
        headers = {
            'Authorization': f'Basic {encoded_credentials}'
        }
        response = requests.get(url, headers=headers)
        return r"""<?xml version="1.0" encoding="UTF-8"?>
                    <OTA_HotelResNotifRQ xmlns="http://www.opentravel.org/OTA/2003/05" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opentravel.org/OTA/2003/05 OTA_HotelResNotifRQ.xsd" TimeStamp="2025-03-11T15:02:38+00:00" Target="Production" Version="2.001">
                        <HotelReservations>
                            <HotelReservation abc="1111">
                                <RoomStays>
                                    <RoomStay IndexNumber="460">
                                        <RoomTypes>
                                            <RoomType RoomTypeCode="1296364403">
                                                <RoomDescription Name="Deluxe Double Room - General">
                                                    <Text>This double room features a bathrobe, hot tub and game console.</Text>
                                                    <MealPlan>Breakfast is included in the room rate.</MealPlan>
                                                    <MaxChildren>0</MaxChildren>
                                                </RoomDescription>
                                                <Amenities>
                                                    <Amenity>Bath</Amenity>
                                                    <Amenity>TV</Amenity>
                                                    <Amenity>Hot tub</Amenity>
                                                    <Amenity>Bathrobe</Amenity>
                                                    <Amenity>Free toiletries</Amenity>
                                                    <Amenity>Infinity pool</Amenity>
                                                    <Amenity>Bottle of water</Amenity>
                                                    <Amenity>Chocolate or cookies</Amenity>
                                                </Amenities>
                                                </RoomDescription>
                                            </RoomType>
                                        </RoomTypes>
                                        <RatePlans>
                                            <RatePlan>
                                                <Commission>
                                                    <CommissionPayableAmount Amount="0" DecimalPlaces="2" CurrencyCode="USD"/>
                                                </Commission>
                                            </RatePlan>
                                        </RatePlans>
                                        <RoomRates>
                                            <RoomRate EffectiveDate="2025-03-29" RatePlanCode="49111777">
                                                <Rates>
                                                    <Rate>
                                                        <Total AmountBeforeTax="500" CurrencyCode="USD" DecimalPlaces="2"/>
                                                    </Rate>
                                                </Rates>
                                            </RoomRate>
                                            <TPA_Extensions>
                                                <BookingCondition>Breakfast is included in the room rate. Children and Extra Bed Policy: All children are welcome. There is no capacity for extra beds in the room. The maximum number of total guests in a room is 2. There is no capacity for cots in the room.  Deposit Policy: No prepayment is needed.  Cancellation Policy: The guest can cancel free of charge at any time. </BookingCondition>
                                            </TPA_Extensions>
                                        </RoomRates>
                                        <GuestCounts>
                                            <GuestCount Count="2" AgeQualifyingCode="10"/>
                                        </GuestCounts>
                                        <Occupancy>4</Occupancy>
                                        <CancelPenalties>
                                            <CancelPenalty PolicyCode="152" From="2025-03-10T10:33:37+00:00">
                                                <AmountPercent Amount="0" DecimalPlaces="2" CurrencyCode="EUR"/>
                                            </CancelPenalty>
                                        </CancelPenalties>
                                        <Total AmountBeforeTax="500" CurrencyCode="USD" DecimalPlaces="2"/>
                                        <BasicPropertyInfo HotelCode="12963644"/>
                                        <ResGuestRPHs>
                                            <ResGuestRPH RPH="2"/>
                                        </ResGuestRPHs>
                                        <Comments>
                                            <Comment>
                                                <Text>I need a wakeup service</Text>
                                            </Comment>
                                        </Comments>
                                        <SpecialRequests>
                                            <SpecialRequest Name="smoking preference">
                                                <Text>Non-Smoking</Text>
                                            </SpecialRequest>
                                        </SpecialRequests>
                                        <PriceDetails>
                                            <GuestView>
                                                <Taxes>
                                                    <Tax Amount="6" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Inclusive">
                                                        <TaxDescription>
                                                            <Text>CO County Sales &amp; Use Tax (Withheld Tax) (1.23%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="5" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Inclusive">
                                                        <TaxDescription>
                                                            <Text>CO Special Sales &amp; Use Tax (Withheld Tax) (1.00%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="14" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Inclusive">
                                                        <TaxDescription>
                                                            <Text>CO State Sales &amp; Use Tax (Withheld Tax) (2.90%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                </Taxes>
                                                <Total Amount="526" DecimalPlaces="2"/>
                                            </GuestView>
                                            <HotelView>
                                                <Taxes>
                                                    <Tax Amount="6" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Exclusive">
                                                        <TaxDescription>
                                                            <Text>CO County Sales &amp; Use Tax (Withheld Tax) (1.23%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="5" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Exclusive">
                                                        <TaxDescription>
                                                            <Text>CO Special Sales &amp; Use Tax (Withheld Tax) (1.00%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="14" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Exclusive">
                                                        <TaxDescription>
                                                            <Text>CO State Sales &amp; Use Tax (Withheld Tax) (2.90%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                </Taxes>
                                                <Total Amount="500" DecimalPlaces="2"/>
                                            </HotelView>
                                        </PriceDetails>
                                    </RoomStay>
                                </RoomStays>
                                <Services>
                                    <Service ServiceRPH="1" ServiceInventoryCode="22" ServicePricingType="3">
                                        <ServiceDetails>
                                            <TimeSpan Duration="1" />
                                            <Fees>
                                                <Fee Amount="5" />
                                            </Fees>
                                        </ServiceDetails>
                                    </Service>
                                </Services>
                                <ResGuests>
                                    <ResGuest ResGuestRPH="1">
                                        <Profiles>
                                            <ProfileInfo>
                                                <Profile>
                                                    <Customer>
                                                        <PersonName>
                                                            <Surname>Lisa K</Surname>
                                                        </PersonName>
                                                    </Customer>
                                                </Profile>
                                            </ProfileInfo>
                                        </Profiles>
                                    </ResGuest>
                                </ResGuests>
                                <TPA_Extensions>
                                    <flags>
                                        <flag name="booker_is_genius"/>
                                    </flags>
                                </TPA_Extensions>
                                <ResGlobalInfo>
                                    <Comments>
                                        <Comment ParagraphNumber="1">
                                            <Text>You have received a virtual credit card for this reservation.You may charge it as of 2025-03-29. ** Genius Booker **</Text>
                                        </Comment>
                                    </Comments>
                                    <Guarantee>
                                        <GuaranteesAccepted>
                                            <GuaranteeAccepted>
                                                <PaymentCard CardCode="MC" CardNumber="1111000011110000" SeriesCode="720" ExpireDate="0326" EffectiveDate="2025-03-29" CurrentBalance="0" DecimalPlaces="2" CurrencyCode="USD" VCCExpirationDate="2026-03-01">
                                                    <CardHolderName>Test Name</CardHolderName>
                                                </PaymentCard>
                                            </GuaranteeAccepted>
                                        </GuaranteesAccepted>
                                    </Guarantee>
                                    <Total AmountBeforeTax="500" CurrencyCode="USD" DecimalPlaces="2"/>
                                    <HotelReservationIDs>
                                        <HotelReservationID ResID_Value="4705950059" ResID_Date="2025-03-10T10:33:37"/>
                                    </HotelReservationIDs>
                                    <Profiles>
                                        <ProfileInfo>
                                            <Profile>
                                                <Customer>
                                                    <PersonName>
                                                        <GivenName>lisa</GivenName>
                                                        <Surname>K</Surname>
                                                    </PersonName>
                                                    <Telephone PhoneNumber="+31 6 14901111"/>
                                                    <Email>feature.794761@guest.booking.com</Email>
                                                    <Address>
                                                        <AddressLine>Park Avenue</AddressLine>
                                                        <CityName>Amsterdam</CityName>
                                                        <PostalCode>1234ABC</PostalCode>
                                                        <CountryName Code="NL"/>
                                                        <CompanyName/>
                                                    </Address>
                                                </Customer>
                                            </Profile>
                                        </ProfileInfo>
                                    </Profiles>
                                    <TotalCommissions>
                                        <CommissionPayableAmount Amount="0000" DecimalPlaces="2" CurrencyCode="EUR"/>
                                        <Comment>This is the total commission amount calculated by Booking.com</Comment>
                                    </TotalCommissions>
                                </ResGlobalInfo>
                            </HotelReservation>
                            <HotelReservation abc="2222">
                                <RoomStays>
                                    <RoomStay IndexNumber="460">
                                        <RoomTypes>
                                            <RoomType RoomTypeCode="1296364403">
                                                <RoomDescription Name="Deluxe Double Room - General">
                                                    <Text>This double room features a bathrobe, hot tub and game console.</Text>
                                                    <MealPlan>Breakfast is included in the room rate.</MealPlan>
                                                    <MaxChildren>0</MaxChildren>
                                                </RoomDescription>
                                                <Amenities>
                                                    <Amenity>Bath</Amenity>
                                                    <Amenity>TV</Amenity>
                                                    <Amenity>Hot tub</Amenity>
                                                    <Amenity>Bathrobe</Amenity>
                                                    <Amenity>Free toiletries</Amenity>
                                                    <Amenity>Infinity pool</Amenity>
                                                    <Amenity>Bottle of water</Amenity>
                                                    <Amenity>Chocolate or cookies</Amenity>
                                                </Amenities>
                                                </RoomDescription>
                                            </RoomType>
                                        </RoomTypes>
                                        <RatePlans>
                                            <RatePlan>
                                                <Commission>
                                                    <CommissionPayableAmount Amount="0" DecimalPlaces="2" CurrencyCode="USD"/>
                                                </Commission>
                                            </RatePlan>
                                        </RatePlans>
                                        <RoomRates>
                                            <RoomRate EffectiveDate="2025-03-29" RatePlanCode="49111777">
                                                <Rates>
                                                    <Rate>
                                                        <Total AmountBeforeTax="500" CurrencyCode="USD" DecimalPlaces="2"/>
                                                    </Rate>
                                                </Rates>
                                            </RoomRate>
                                            <TPA_Extensions>
                                                <BookingCondition>Breakfast is included in the room rate. Children and Extra Bed Policy: All children are welcome. There is no capacity for extra beds in the room. The maximum number of total guests in a room is 2. There is no capacity for cots in the room.  Deposit Policy: No prepayment is needed.  Cancellation Policy: The guest can cancel free of charge at any time. </BookingCondition>
                                            </TPA_Extensions>
                                        </RoomRates>
                                        <GuestCounts>
                                            <GuestCount Count="2" AgeQualifyingCode="10"/>
                                        </GuestCounts>
                                        <Occupancy>4</Occupancy>
                                        <CancelPenalties>
                                            <CancelPenalty PolicyCode="152" From="2025-03-10T10:33:37+00:00">
                                                <AmountPercent Amount="0" DecimalPlaces="2" CurrencyCode="EUR"/>
                                            </CancelPenalty>
                                        </CancelPenalties>
                                        <Total AmountBeforeTax="500" CurrencyCode="USD" DecimalPlaces="2"/>
                                        <BasicPropertyInfo HotelCode="12963644"/>
                                        <ResGuestRPHs>
                                            <ResGuestRPH RPH="2"/>
                                        </ResGuestRPHs>
                                        <Comments>
                                            <Comment>
                                                <Text>I need a wakeup service</Text>
                                            </Comment>
                                        </Comments>
                                        <SpecialRequests>
                                            <SpecialRequest Name="smoking preference">
                                                <Text>Non-Smoking</Text>
                                            </SpecialRequest>
                                        </SpecialRequests>
                                        <PriceDetails>
                                            <GuestView>
                                                <Taxes>
                                                    <Tax Amount="6" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Inclusive">
                                                        <TaxDescription>
                                                            <Text>CO County Sales &amp; Use Tax (Withheld Tax) (1.23%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="5" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Inclusive">
                                                        <TaxDescription>
                                                            <Text>CO Special Sales &amp; Use Tax (Withheld Tax) (1.00%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="14" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Inclusive">
                                                        <TaxDescription>
                                                            <Text>CO State Sales &amp; Use Tax (Withheld Tax) (2.90%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                </Taxes>
                                                <Total Amount="526" DecimalPlaces="2"/>
                                            </GuestView>
                                            <HotelView>
                                                <Taxes>
                                                    <Tax Amount="6" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Exclusive">
                                                        <TaxDescription>
                                                            <Text>CO County Sales &amp; Use Tax (Withheld Tax) (1.23%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="5" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Exclusive">
                                                        <TaxDescription>
                                                            <Text>CO Special Sales &amp; Use Tax (Withheld Tax) (1.00%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                    <Tax Amount="14" ChargeFrequency="12" Code="17" CurrencyCode="USD" DecimalPlaces="2" Type="Exclusive">
                                                        <TaxDescription>
                                                            <Text>CO State Sales &amp; Use Tax (Withheld Tax) (2.90%)</Text>
                                                        </TaxDescription>
                                                    </Tax>
                                                </Taxes>
                                                <Total Amount="500" DecimalPlaces="2"/>
                                            </HotelView>
                                        </PriceDetails>
                                    </RoomStay>
                                </RoomStays>
                                <Services>
                                    <Service ServiceRPH="1" ServiceInventoryCode="22" ServicePricingType="3">
                                        <ServiceDetails>
                                            <TimeSpan Duration="1" />
                                            <Fees>
                                                <Fee Amount="5" />
                                            </Fees>
                                        </ServiceDetails>
                                    </Service>
                                </Services>
                                <ResGuests>
                                    <ResGuest ResGuestRPH="1">
                                        <Profiles>
                                            <ProfileInfo>
                                                <Profile>
                                                    <Customer>
                                                        <PersonName>
                                                            <Surname>Lisa K</Surname>
                                                        </PersonName>
                                                    </Customer>
                                                </Profile>
                                            </ProfileInfo>
                                        </Profiles>
                                    </ResGuest>
                                </ResGuests>
                                <TPA_Extensions>
                                    <flags>
                                        <flag name="booker_is_genius"/>
                                    </flags>
                                </TPA_Extensions>
                                <ResGlobalInfo>
                                    <Comments>
                                        <Comment ParagraphNumber="1">
                                            <Text>You have received a virtual credit card for this reservation.You may charge it as of 2025-03-29.
                    ** Genius Booker **</Text>
                                        </Comment>
                                    </Comments>
                                    <Guarantee>
                                        <GuaranteesAccepted>
                                            <GuaranteeAccepted>
                                                <PaymentCard CardCode="MC" CardNumber="1111000011110000" SeriesCode="720" ExpireDate="0326" EffectiveDate="2025-03-29" CurrentBalance="0" DecimalPlaces="2" CurrencyCode="USD" VCCExpirationDate="2026-03-01">
                                                    <CardHolderName>Test Name</CardHolderName>
                                                </PaymentCard>
                                            </GuaranteeAccepted>
                                        </GuaranteesAccepted>
                                    </Guarantee>
                                    <Total AmountBeforeTax="500" CurrencyCode="USD" DecimalPlaces="2"/>
                                    <HotelReservationIDs>
                                        <HotelReservationID ResID_Value="4705950059" ResID_Date="2025-03-10T10:33:37"/>
                                    </HotelReservationIDs>
                                    <Profiles>
                                        <ProfileInfo>
                                            <Profile>
                                                <Customer>
                                                    <PersonName>
                                                        <GivenName>lisa</GivenName>
                                                        <Surname>K</Surname>
                                                    </PersonName>
                                                    <Telephone PhoneNumber="+31 6 14901111"/>
                                                    <Email>feature.794761@guest.booking.com</Email>
                                                    <Address>
                                                        <AddressLine>Park Avenue</AddressLine>
                                                        <CityName>Amsterdam</CityName>
                                                        <PostalCode>1234ABC</PostalCode>
                                                        <CountryName Code="NL"/>
                                                        <CompanyName/>
                                                    </Address>
                                                </Customer>
                                            </Profile>
                                        </ProfileInfo>
                                    </Profiles>
                                    <TotalCommissions>
                                        <CommissionPayableAmount Amount="0000" DecimalPlaces="2" CurrencyCode="EUR"/>
                                        <Comment>This is the total commission amount calculated by Booking.com</Comment>
                                    </TotalCommissions>
                                </ResGlobalInfo>
                            </HotelReservation>
                        </HotelReservations>
                    </OTA_HotelResNotifRQ>"""

    def end_point_Booking_Com_Reservation(self):
        response = self.auth_booking_com(
            "https://secure-supply-xml.booking.com/hotels/ota/OTA_HotelResNotif?hotel_ids=8011855&last_change=2025-03-31+11%3A00%3A00&limit=200"
        )
        soup = BeautifulSoup(response, 'xml')
        # print(soup.select('RoomStays'))
        return soup
