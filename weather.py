#!/usr/bin/python

# Written by Pascal Gauthier <pgauthier@nihilisme.ca>
# 06.15.2012 

import sys
import xml.sax
import urllib2
import argparse


def fetch_apidata(url):
    "Get data from API"

    return urllib2.urlopen(url)


class IP2locHandler(xml.sax.ContentHandler):
    "IP to city location"

    def __init__(self):
        "Initialize vars"

        self.data = []
        self.city_name = False 
        self.country_name = False
        self.hostip = False

    def startElement(self, name, attrs):
        "Extract city name and state/province"

        if name == "Hostip":
            self.hostip = True 
        if self.hostip and name == "gml:name":
            self.city_name = True

        if name == "countryAbbrev":
            self.country_name = True

    def endElement(self, name):
        "End of element"

        if name == "Hostip":
            self.hostip = False
            self.city_name = False 

        if name == "countryAbbrev":
            self.country_name = False 

    def characters(self, string):
        "Read element data"

        if self.hostip and self.city_name:
            self.city = string
            self.city_name = False

        if self.country_name:
            self.country = string
            self.country_name = False

    def locate_city(self):
        "Return the name of the city"

        if self.city.find("Unknown") != -1 : 
            print "Unknown city"
            sys.exit(1)

        return (self.city, self.country)


class WeatherHandler(xml.sax.ContentHandler): 
    "Superclass of ContentHandler"

    def __init__(self, forecast):
        "Initialize vars"
        
        self.i = 0
        self.city = ""
        self.temp = ""
        self.humi = ""
        self.wind = ""
        self.forecast = forecast
        self.forecast_condition = False

        self.day = None
        self.low = None
        self.high = None
        self.condition = None
        self.forecast_data = {} 

    def startElement(self, name, attrs):
        "Extract only what we want from the XML"

        if name == "city":
            self.city = attrs.getValue("data")
        if name == "temp_c":
            self.temp = attrs.getValue("data")
        if name == "humidity":
            self.humi = attrs.getValue("data")
        if name == "condition":
            self.cond = attrs.getValue("data")
        if name == "wind_condition":
            self.wind = attrs.getValue("data")

        if name == "forecast_conditions":
            self.forecast_condition = True

        if self.forecast_condition and self.forecast == True:
            if name == "day_of_week":
                self.day = attrs.getValue("data")
            if name == "low":
                self.low = self.__convert_to_celsius__(attrs.getValue("data"))
            if name == "high":
                self.high =  self.__convert_to_celsius__(attrs.getValue("data"))
            if name == "condition":
                self.condition = attrs.getValue("data")

            if self.day and self.low and self.high and self.cond:
                self.forecast_data[self.day] = {'low': self.low , 
                            'high': self.high, 'condition': self.condition}

    def endElement(self, name):
        "End of the element"

        if name == "forecast_conditions":
            self.forecast_condition = False
            self.i += 1

    def __convert_to_celsius__(self, temp):
        "Convert fahrenheit to celcius"

        return (int(temp) - 32) / (9.0 / 5.0) 

    def printWeather(self):
        "Print condition"

        if self.city:
            print "\nCurrent condition:"
            print "------------------\n"
            print "%s: %sc" % (self.city, self.temp)
            print "Condition: %s" % (self.cond)
            print self.humi 
            print self.wind

            if self.forecast == True:
                print "\nForecast condition:"
                print "-------------------\n"
                for day in self.forecast_data.keys():
                    print "%s [Low: %dc High: %dc Condition: %s]" % (day, 
                        self.forecast_data[day]['low'],
                        self.forecast_data[day]['high'],
                        self.forecast_data[day]['condition'])
        else:
            print "No data"
            sys.exit(1)


def main():
    "Main function"

    argparser = argparse.ArgumentParser() 
    argparser.add_argument("--forecast", action="store_true", 
                help="print current and forcast weather")
    argparser.add_argument("--city", help="name of the city")
    argparser.add_argument("--state", help="name of the state/country")

    args = argparser.parse_args()
    if args.city and not args.state:
        argparser.print_help()
        sys.exit(1)

    ip_handler = IP2locHandler()
    wt_handler = WeatherHandler(args.forecast)
    ip_parser = xml.sax.make_parser()
    weather_parser = xml.sax.make_parser()

    if not args.city:
        # Parse info from IP api if no city provided 
        ip_parser.setContentHandler(ip_handler)
        ip_parser.parse(fetch_apidata("http://api.hostip.info/?ip="))
        city, state = ip_handler.locate_city()

        google_api = "http://www.google.ca/ig/api?weather=" + city + "," + state 

        # Parse info from Google weather API
        weather_parser.setContentHandler(wt_handler)
        weather_parser.parse(fetch_apidata(google_api))
    else:
        google_api = "http://www.google.ca/ig/api?weather=" + args.city + "," + args.state

        # Parse info from Google weather API
        weather_parser.setContentHandler(wt_handler)
        weather_parser.parse(fetch_apidata(google_api))

    # Print result
    wt_handler.printWeather()


if __name__ == "__main__":
    main()
