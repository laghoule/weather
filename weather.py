#!/usr/bin/python

import sys
import xml.sax
import urllib2
import argparse

def fetch_apidata(city, country):
    "Get data from google weather api"

    google_api = "http://www.google.ca/ig/api?weather=" + city + "," + country

    return urllib2.urlopen(google_api) 

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
                self.low = attrs.getValue("data")
            if name == "high":
                self.high = attrs.getValue("data")
            if name == "condition":
                self.condition = attrs.getValue("data")

            if self.day and self.low and self.high and self.cond:
                self.forecast_data[self.day] = {'low': self.low , 'high': self.high, 'condition': self.condition}

    def endElement(self, name):
        "End of the element"

        if name == "forecast_conditions":
            self.forecast_condition = False
            self.i += 1

    def printWeather(self):
        "Print condition"

        if self.city:
            print "\nCurrent condition:"
            print "%s: %sc" % (self.city, self.temp)
            print "Condition: %s" % (self.cond)
            print self.humi 
            print self.wind

            if self.forecast == True:
                print "\nForecast condition:"
                for day in self.forecast_data.keys():
                    print "%s [Low: %s High: %s Condition: %s]" % (day, self.forecast_data[day]['low'], self.forecast_data[day]['high'], self.forecast_data[day]['condition'])
        else:
            print "No data"
            sys.exit(1)


def main():
    "Main function"

    argparser = argparse.ArgumentParser() 
    argparser.add_argument("--forecast", action="store_true", 
                help="print current and forcast weather")
    argparser.add_argument("city", help="name of the city")
    argparser.add_argument("country", help="name of the country")

    args = argparser.parse_args()

    handler = WeatherHandler(args.forecast)
    xmlparser = xml.sax.make_parser()

    xmlparser.setContentHandler(handler)
    xmlparser.parse(fetch_apidata(args.city, args.country))

    handler.printWeather()

if __name__ == "__main__":
    main()
