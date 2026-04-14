# QR System

## Purpose
Enable instant inspection verification

## Structure
QR → Secure URL:
example.com/verify/{token}

## When Scanned

### Citizen View
- Stall info
- Images
- Schedule

### Officer View
- Full validation data
- Status flags:
  - valid_location
  - valid_time
  - valid_activity
  - valid_subscription

## Security
- Tokenized QR
- Not guessable