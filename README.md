# Limnoria plugin for WorldTime

Retrieve current time and time zone information for various locations.

Forked from https://github.com/reticulatingspline/WorldTime

## Introduction

A user contacted me about making some type of plugin to display local time around the world.
Utilizing Python's TimeZone database and google, it was pretty easy to throw together.

## Install

```
pip install -r requirements.txt 
```

or if you don't have or don't want to use root,

```
pip install -r requirements.txt --user
```

Next, load the plugin:

```
/msg bot load WorldTime
```

Enable Google [Geocoding](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com) and [Time Zone](https://console.cloud.google.com/apis/library/timezone-backend.googleapis.com) APIs. Set your [API Key](https://console.cloud.google.com/apis/credentials) using the command below

```
/msg bot config plugins.worldtime.mapsapikey <your_key_here>
```

## Example Usage

```plaintext
<spline> @worldtime New York, NY
<myybot> New York, NY, USA :: Current local time is: Sat, 09:38 (Eastern Daylight Time)
<spline> @worldtime 90210
<myybot> Beverly Hills, CA 90210, USA :: Current local time is: Sat, 06:38 (Pacific Daylight Time)
```
