
CREATE TABLE "itinerary_df" (
    "itinerary_id" text   NOT NULL,
    "itineraries" text   NOT NULL,
    CONSTRAINT "pk_itinerary_df" PRIMARY KEY (
        "itinerary_id"
     )
);

CREATE TABLE "cabin_class" (
    "cabin_class_id" varchar(5)   NOT NULL,
    "cabin_class" varchar(20)   NOT NULL,
    CONSTRAINT "pk_cabin_class" PRIMARY KEY (
        "cabin_class_id"
     )
);

CREATE TABLE "airports" (
    "name" text   NOT NULL,
    "iata_code" varchar(5)   NOT NULL,
    "city" varchar(50)   NOT NULL,
    "latitude" float   NOT NULL,
    "longitude" float   NOT NULL,
    "timezone" varchar(5)   NOT NULL,
    "departures" int   NOT NULL,
    "airport_id" varchar(100)   NOT NULL,
	"country_code_id" varchar(30)   NOT NULL,
    CONSTRAINT "pk_airports" PRIMARY KEY (
        "airport_id"
     )
);

CREATE TABLE "airlines" (
    "airline_id" varchar(100)   NOT NULL,
    "airline_name" text   NOT NULL,
    "iata" varchar(3)   NOT NULL,
    "is_airline_passenger" bool   NOT NULL,
    "total_aircrafts" int   NOT NULL,
    "average_fleet_age" float   NOT NULL,
    "accidents_last_5y" int   NOT NULL,
    "iosa_registered" bool   NOT NULL,
    "iosa_expiry" TIMESTAMPTZ   NULL,  
	"country_code_id" varchar(50)   NOT NULL,
    CONSTRAINT "pk_airlines" PRIMARY KEY (
        "airline_id"
     )
);

CREATE TABLE "country_code" (
    "country_code_id" varchar(100)   NOT NULL,
    "country_code" varchar(3)   NOT NULL,
    CONSTRAINT "pk_country_code" PRIMARY KEY (
        "country_code_id"
     )
);

CREATE TABLE "flight_numbers" (
    "flight_id" int   NOT NULL,
    "flight_number" int   NOT NULL,
    CONSTRAINT "pk_flight_numbers" PRIMARY KEY (
        "flight_id"
     )
);

CREATE TABLE "itinerary_details" (
    "departure_date_time" timestamp   NOT NULL,
    "arrival_date_time" timestamp   NOT NULL,
    "is_self_transfer" bool   NOT NULL,
    "flight_id" int   NOT NULL,
    "itinerary_id" text   NOT NULL,
    "origin_airport_id" text   NOT NULL,
    "destination_airport_id" text   NOT NULL
);

CREATE TABLE "flight_price" (
    "stop_count" int   NOT NULL,
    "duration_in_hours" float   NOT NULL,
    "one_way_price_candollar" int   NOT NULL,
    "cabin_class" varchar(20)   NOT NULL,
    "operating_airline_id" text   NOT NULL,
    "marketing_airline_id" text   NOT NULL,
    "itinerary_id" text   NOT NULL
);

ALTER TABLE "airports" ADD CONSTRAINT "fk_airports_country_code_id" FOREIGN KEY("country_code_id")
REFERENCES "country_code" ("country_code_id");

ALTER TABLE "airlines" ADD CONSTRAINT "fk_airlines_country_code_id" FOREIGN KEY("country_code_id")
REFERENCES "country_code" ("country_code_id");

ALTER TABLE "itinerary_details" ADD CONSTRAINT "fk_itinerary_details_flight_id" FOREIGN KEY("flight_id")
REFERENCES "flight_numbers" ("flight_id");

ALTER TABLE "itinerary_details" ADD CONSTRAINT "fk_itinerary_details_itinerary_id" FOREIGN KEY("itinerary_id")
REFERENCES "itinerary_df" ("itinerary_id");

ALTER TABLE "itinerary_details" ADD CONSTRAINT "fk_itinerary_details_origin_airport_id" FOREIGN KEY("origin_airport_id")
REFERENCES "airports" ("airport_id");

ALTER TABLE "itinerary_details" ADD CONSTRAINT "fk_itinerary_details_destination_airport_id" FOREIGN KEY("destination_airport_id")
REFERENCES "airports" ("airport_id");

ALTER TABLE "flight_price" ADD CONSTRAINT "fk_flight_price_cabin_class" FOREIGN KEY("cabin_class")
REFERENCES "cabin_class" ("cabin_class_id");

ALTER TABLE "flight_price" ADD CONSTRAINT "fk_flight_price_operating_airline_id" FOREIGN KEY("operating_airline_id")
REFERENCES "airlines" ("airline_id");

ALTER TABLE "flight_price" ADD CONSTRAINT "fk_flight_price_marketing_airline_id" FOREIGN KEY("marketing_airline_id")
REFERENCES "airlines" ("airline_id");

ALTER TABLE "flight_price" ADD CONSTRAINT "fk_flight_price_itinerary_id" FOREIGN KEY("itinerary_id")
REFERENCES "itinerary_df" ("itinerary_id");



