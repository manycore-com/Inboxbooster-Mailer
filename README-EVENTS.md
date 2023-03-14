# Handling events
You need to handle unsubscribe and spam-report events. It's a legal requirement, and failing
to do so will block you from ISPs.

## General structure
The events are posted as an array of JSON objects to the webhook endpoint you configure in the
Backdata/post-url section of
[inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)

Uuid is dependent on [mail header](README-HEADERS.md) X-Uuid.

Example:
```json
[
  {
    "event": "unsubscribe",
    "uuid": "92837V498A2374",
    "timestamp": 1668716022
  }
]
```
## Events
### Delivered

| Name      | Value          | Description                                                          |
|-----------|----------------|----------------------------------------------------------------------|
| event     | delivered      | always set to delivered                                              |
| uuid      | 92837V498A2374 | from the X-Uuid header in the original mail. Matches regex [a-z0-9]+ |
| timestamp | 1668716022     | unix timestamp in seconds                                            |
| ip        | 1.2.3.4        | Optional ip address of server receiving the mail                     |

### Bounce
| Name      | Value                  | Description                                                                         |
|-----------|------------------------|-------------------------------------------------------------------------------------|
| event     | bounce                 | always set to bounce                                                                |
| uuid      | 92837V498A2374         | from the X-Uuid header in the original mail. Matches regex [a-z0-9]+                |
| timestamp | 1668716022             | unix timestamp in seconds                                                           |
| ip        | 1.2.3.4                | ip address of server refusing receiving the mail. May be empty (e.g illegal domain) |
| reason    | 550 5.1.1 User unknown | reason for bounce. May be empty.                                                    |
| type      | soft                   | any of hard, soft, unroutable, autoreply                                            |

### Error
This event is sent by any service in the system that encounters an error.
This does not include errors parsed from Postfix (e.g Bounce).

| Name        | Value          | Description                        |
|-------------|----------------|------------------------------------|
| event       | error          | always set to error                |
| msg         | X-Uuid missing | Error message                      |
| service     | backdata       | Service that encountered the error |
| stack-trace | stack trace    | Optional stack trace to help debug |
| uuid        | 92837V498A2374 | Optional, may not be available     |
| timestamp   | 1668716022     | unix timestamp in seconds          |

### Spam-Report
| Name      | Value           | Description                                                          |
|-----------|-----------------|----------------------------------------------------------------------|
| event     | spam-report     | always set to spam-report                                            |
| uuid      | 92837V498A2374  | from the X-Uuid header in the original mail. Matches regex [a-z0-9]+ |
| email     | apa@example.com | email address of spam reporter                                       |
| timestamp | 1668716022      | unix timestamp in seconds                                            |

### Unsubscribe
| Name      | Value           | Description                                                          |
|-----------|-----------------|----------------------------------------------------------------------|
| event     | unsubscribe     | always set to unsubscribe                                            |
| uuid      | 92837V498A2374  | from the X-Uuid header in the original mail. Matches regex [a-z0-9]+ |
| timestamp | 1668716022      | unix timestamp in seconds                                            |
