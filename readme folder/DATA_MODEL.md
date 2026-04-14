# Data Model

## Users
- id
- role
- name
- phone
- password

## Vendors
- user_id
- national_id
- status

## Stalls
- id
- owner_id
- category
- description
- status
- start_date
- end_date
- qr_code

## Stall Images
- id
- stall_id
- image_url

## Locations
- id
- lat
- lng
- radius
- allowed_categories
- allowed_days
- start_time
- end_time

## Violations
- id
- stall_id
- officer_id
- type
- description
- image
- created_at

## Subscriptions
- stall_id
- amount
- expiry_date
- status