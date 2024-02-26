# v1.0.0
First release

# v1.0.1

## Postfix
* Use postfixlog/string-replacer/main-cf/myhostname instead of adding file
  /configs/myhostname (latter is still supported).
  See 
  [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)
  for an example.
* Use postfixlog/string-replacer/main-cf/mailname instead of adding file
  /configs/mailname (latter is still supported).
  See 
  [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)
  for an example.
* Use postfixlog/string-replacer/master-cf/smtpd-port if you want to 
  override what port the internal Postfix daemon listens to. This is
  never publicly visible but it interfered with MxServer in the Single Docker
  build.
  See 
  [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)
  for an example.
* Added event=bounce type=unroutable event if target domain does not exist. Ie if Postfix
  says " does not accept mail (nullMX)" or
  "Host or domain name not found. Name service error for name".
* added streamid to all events going to BackData. Not set if null.

## BackData
* BackData will send streamid back (if one is provided by Postfix module).
  It will only add streamid if it is not null.

# v1.0.3
## Transformer
* Transformer now uses X-Stream-Id as campaign in first part of feedback-id. If not set, 
  it reverts to transformer.feedback-campaign in the customer-config-file.
