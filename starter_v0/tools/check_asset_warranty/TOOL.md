---
name: check_asset_warranty
track: bonus
kind: local_inventory
provider: mock_device_inventory
requires_env: []
inputs: [asset_id]
outputs: [asset_id, model, purchase_date, warranty_until, warranty_status, days_remaining]
side_effect: false
---
# check_asset_warranty

Checks the warranty status and expiration date for a company asset.
Returns purchase date, warranty end date, current warranty status (active/expired/expiring_soon),
and days remaining until warranty expiration. A warranty within 30 days of expiration is marked
as "expiring_soon". Does not modify any state and does not require confirmation.
