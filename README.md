Cabot Hipchat Plugin
=====

This is an alert plugin for the cabot service monitoring tool. It allows you to alert users by their user handle with xoxzo telephony services.

## Installation

Install using pip

    pip install https://codeload.github.com/XuryaX/cabot_alert_xoxzo/zip/master

Edit `conf/production.env` in your Cabot clone to include the plugin:

    CABOT_PLUGINS_ENABLED=cabot_alert_xoxzo...,<other plugins>

## Configuration

The plugin requires the following environment variables to be set:

    XOXZO_API_SID=<your xoxzo api sid>
    XOXZO_API_KEY=<your xoxzo api key>
    XOXZO_ORIGIN_NUMBER=<originating phone number>
