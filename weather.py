#!/usr/bin/python

# Written by Pascal Gauthier <pgauthier@nihilisme.ca>
# 06.15.2012 

import sys
import xml.sax
import urllib2
import argparse


def fetch_apidata(url):
    """Get data from API"""

    return urllib2.urlopen(url)


class IP2locHandler(xml.sax.ContentHandler):
    """IP to city location"""

    def __init__(self):
        """Initialize vars"""

        self.data = []
        self.city_name = False 
        self.country_name = False
        self.hostip = False

    def startElement(self, name, attrs):
        """Extract city name and state/province"""

        if name == "Hostip":
            self.hostip = True 
        if self.hostip and name == "gml:name":
            self.city_name = True

        if name == "countryName":
            self.country_name = True

    def endElement(self, name):
        """End of element"""

        if name == "Hostip":
            self.hostip = False
            self.city_name = False 

        if name == "countryName":
            self.country_name = False 

    def characters(self, string):
        """Read element data"""

        if self.hostip and self.city_name:
            self.city = string
            self.city_name = False

        if self.country_name:
            self.country = string
            self.country_name = False

    def locate_city(self):
        """Return the name of the city"""

        if self.city.find("Unknown") != -1:
            print "Unknown city"
            sys.exit(1)

        return self.city, self.country


class WeatherHandler(xml.sax.ContentHandler): 
    """Superclass of ContentHandler"""

    def __init__(self, forecast):
        """Initialize vars"""
        
        self.city = [] 
        self.temp = [] 
        self.feel = []
        self.humi = [] 
        self.wind = [] 
        self.cond = []
        self.forecast = forecast
        self.forecast_condition = False

        self.i = 0
        self.forecast_data = {} 

    def startElement(self, name, attrs):
        """Extract only what we want from the XML"""

        self.element = name
        if name == "forecastday":
            self.forecast_condition = True 

    def endElement(self, name):
        """End of the element"""

        if name == "forecastday":
            self.forecast_condition = False 

    def characters(self, chrs):
        """Extract data from <> elements"""

        # Current condition
        if self.element == "city" and not len(self.city):
            self.city = chrs
        if self.element == "temp_c" and not len(self.temp):
            self.temp = chrs
        if self.element == "feelslike_c" and not len(self.feel):
            self.feel = chrs
        if self.element == "relative_humidity" and not len(self.humi):
            self.humi = chrs
        if self.element == "weather" and not len(self.cond):
            self.cond = chrs
        if self.element == "wind_string" and not len(self.wind):
            self.wind = chrs

        # Forecast condition
        if self.forecast_condition and self.forecast == True:
            if self.element == "title" and \
                    not self.forecast_data.has_key(chrs) \
                    and len(chrs.strip()):
                self.day = chrs.strip()
            if self.element == "fcttext_metric" and len(chrs.strip()) > 1:
                # I use a compter for getting array order
                self.forecast_data[self.i] = {'day': self.day, 
                    'forecast': chrs.strip()} 
                self.i += 1

    def printWeather(self):
        """Print condition"""

        if self.city:
            print "\nCurrent condition:"
            print "------------------\n"
            print "%s: %sc (humidex %sc)" % (self.city, self.temp,
                self.feel)
            print "Condition: %s" % (self.cond)
            print "Wind: %s" % (self.wind)
            print "Relative humidity: %s" % (self.humi) 

            if self.forecast == True:
                print "\nForecast condition:"
                print "-------------------\n"
                for i in range(self.i):
                    print "%s:\n%s\n" % (self.forecast_data[i]['day'], 
                        self.forecast_data[i]['forecast']) 
        else:
            print "No data"
            sys.exit(1)


def main():
    """Main function"""

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

        if not args.forecast:
            wunderground_api = "http://api.wunderground.com/api/6325d73d2d8816df/conditions/q/" + state + "/" + city + ".xml"
        else:
            wunderground_api = "http://api.wunderground.com/api/6325d73d2d8816df/conditions/forecast/q/" + state + "/" + city + ".xml"
    else:
        if not args.forecast:
            wunderground_api = "http://api.wunderground.com/api/6325d73d2d8816df/conditions/q/" + args.state + "/" + args.city + ".xml"
        else:
            wunderground_api = "http://api.wunderground.com/api/6325d73d2d8816df/conditions/forecast/q/" + args.state + "/" + args.city + ".xml"

    # Parse info from Google weather API
    weather_parser.setContentHandler(wt_handler)
    weather_parser.parse(fetch_apidata(wunderground_api))

    # Print result
    wt_handler.printWeather()


if __name__ == "__main__":
    main()
