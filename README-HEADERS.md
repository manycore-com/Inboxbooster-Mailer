# Headers
There are a few headers you need to set in the message for the Mailer.

## Headers given to the mailer as header in the message.
Note: X-Priority, X-Uuid, and X-Stream-Id are removed before actually sending the email.
Note: X-Uuid is your internal id, that is non sensitive for you if it's spread. 
It's unique per {from, to, message}.
It's used in the [events](README-EVENTS.md) to communicate status.

| Name           | Value           | Description                                                                                                      |
|----------------|-----------------|------------------------------------------------------------------------------------------------------------------|
| X-Priority     | 0               | 0 or 1. 0 is high priority.                                                                                      |
| X-Report-Abuse |                 | You need to set the X-Report-Abuse header.                                                                       |
| X-Uuid         | 0123456789abc   | An id uniquely identifying the email sent to one recipient. Lower case (headers are case insensitive). [a-z0-9]+ |
| X-Stream-Id    | 0123-456789-abc | Optional: Template Id and Campaign Id concatenated, to help identify deliverability.                             |

## Headers set by the mailer
| Name        | Value               | Description                                                                                                                       |
|-------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------|
 | Message-ID  | a@b                 | Set to a@b. a is X-Uuid. b is the domain of From header. If there already is a message id in the email, it's will be overwritten. |
 | X-Mailer    | Inboxbooster-Mailer | Value is in inboxbooster-mailer-global.yaml transformer/x-mailer                                                                  |
 | Feedback-ID | a:b:c               | Set by settings in inboxbooster-mailer-customer.yaml transformer/feedback-id: campaign:mayl-type:senderid                         |

