# Food Coupon System (Digital + Physical) — Agas

## Context Summary
- Event registration already captures food needs and per-day meal schedule via:
  - `Event Registration` (`apps/agas/agas/agas/doctype/event_registration/event_registration.json`)
  - `Event Food Day` child table (`apps/agas/agas/agas/doctype/event_food_day/event_food_day.json`)
- There is no issuance or redemption mechanism yet.

## Goal
Issue meal coupons to visitors (digital and physical), and collect/redeem them when meals are taken.

## Proposed Data Model

### 1) Meal Coupon Book (Parent DocType)
Links a registration to all coupons issued for that registration.

Fields (suggested):
- `event` (Link to Agas Event)
- `registration` (Link to Event Registration)
- `member_profile` (Link to Member Profile)
- `issue_mode` (Select: Digital / Physical / Both)
- `issued_by` (Link to User)
- `issued_on` (Datetime)
- `status` (Select: Issued / Partially Redeemed / Completed / Void)

### 2) Meal Coupon (Child DocType)
One coupon per meal per date (or per person per meal).

Fields (suggested):
- `date` (Date)
- `meal_type` (Select: Breakfast / Lunch / Dinner)
- `quantity` (Int)
- `coupon_code` (Data, unique)
- `status` (Select: Issued / Redeemed / Void)
- `redeemed_at` (Datetime)
- `redeemed_by` (Link to User)
- `redeemed_location` (Data)
- `redeem_method` (Select: Scan / Manual)

## Issuance Logic

### Trigger
When an `Event Registration` is finalized (`status = Registered/Confirmed`) and `food_required = Yes`.

### Coupon generation
Use `Event Food Day` rows to generate coupons:
- If **per-person coupons**:
  - Create a coupon per meal per person (`quantity = 1`).
- If **batch coupons**:
  - Create a coupon per meal per date with `quantity = no_of_visitors`.

### Coupon code format
Example: `EV-REG-<REG_ID>-<YYYYMMDD>-<MEAL>-<SEQ>`

## Digital Coupons
- Display QR codes in a new “My Meals” section.
- Each QR encodes `coupon_code`.
- Staff scan at counter to redeem; status set to `Redeemed`.

## Physical Coupons (No Smartphone)
- Print coupon booklets with tear-off tokens.
- Each token shows date + meal type + serial + QR for `coupon_code`.
- Staff collect tokens at meal counter and scan or batch-enter later.
- Use color coding per meal to reduce mistakes.

## Redemption Workflow
- Validate `coupon_code` exists and is `Issued`.
- Optional validation: time window or date must match meal.
- Mark `Redeemed` with `redeemed_at`, `redeemed_by`, `redeemed_location`, `redeem_method`.
- Block reuse.

## Reporting
- Issued vs Redeemed by date/meal/event.
- Unused coupons for wastage tracking.

## Integration Points (Code)
- Issuance logic in `apps/agas/agas/api.py` or a method on `Event Registration`.
- Read meal schedule from `Event Food Day` child rows.
- Add new web page for staff redemption input / QR scan.

## Open Decisions
- Per-person vs per-meal batch coupons?
- Live QR scanning at counter vs batch entry after meal?
- Enforce time windows for breakfast/lunch/dinner?
