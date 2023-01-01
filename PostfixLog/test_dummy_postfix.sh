#!/bin/bash

aiosmtpd -c aiosmtpd.handlers.Debugging stdout -n -l localhost:8026 -d
