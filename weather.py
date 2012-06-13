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

    def __init__(self):
        "Initialize vars"

        self.city = ""
        self.temp = ""
        self.humi = ""
        self.wind = ""

    def startElement(self, name, attrs):
        "Extract only what we want from the XML"

        if name == "city":
            self.city = attrs.getValue("data")
        if name == "temp_c":
            self.temp = attrs.getValue("data")
        if name == "humidity":
            self.humi = attrs.getValue("data")
        if name == "wind_condition":
            self.wind = attrs.getValue("data")

    def printWeather(self):
        "Print current condition"

        if self.city:
            print "%s: %sc" % (self.city, self.temp)
            print self.humi 
            print self.wind
        else:
            print "No data"
            sys.exit(1)


def main():
    "Main function"

    argparser = argparse.ArgumentParser() 
    argparser.add_argument("city", help="name of the city")
    argparser.add_argument("country", help="name of the country")

    args = argparser.parse_args()

    handler = WeatherHandler()
    xmlparser = xml.sax.make_parser()

    xmlparser.setContentHandler(handler)
    xmlparser.parse(fetch_apidata(args.city, args.country))

    handler.printWeather()

if __name__ == "__main__":
    main()
