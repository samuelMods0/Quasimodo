# AllSync IQ Remote Connect Protocol

## Reverse-engineered protocol notes from Remote Connect JavaScript

**Scope:** AllSync IQ embedded Remote Connect web application captured through mitmproxy.

**Goal:** Provide enough protocol-level information to implement an independent Python client for Quasimodo.

> This document describes observed algorithms and protocol behavior rather than reproducing the manufacturer's JavaScript source.

---

# 1. Overall architecture

Remote Connect is an HTTP web application served directly by the AllSync IQ.

```text
Quasimodo
    │
    │ HTTP
    ▼
AllSync IQ
    │
    └── Remote Connect web application
```

The browser normally loads HTML and JavaScript from the controller and then uses those scripts to make additional HTTP requests.

There are two broad communication styles:

```text
A. Form-style / direct HTTP requests
   GET or POST
   ordinary form parameters such as t277=...

B. Encoded binary data
   application constructs a byte buffer
   ↓
   custom 6-bit encoding
   ↓
   transmitted as a t600/t601/etc. parameter
```

The event system primarily uses the second approach.

---

# 2. Authentication

The login page sends credentials to:

```text
GET /auth.htm
```

with query parameters:

```text
t997 = username
t998 = password
```

Conceptually:

```text
GET /auth.htm?t997=<username>&t998=<password>
```

The controller responds with a small HTML body containing the resulting security level.

The JavaScript then stores authentication state in cookies.

Observed security-level values include:

```text
sclock
atsman
```

The captured session also uses a security-key cookie. The actual key is intentionally omitted from this document.

## Protocol implication

A Python client should not assume that ordinary HTTP Basic Authentication is being used.

Instead, the client should reproduce the Remote Connect login/session mechanism.

---

# 3. Generic HTTP helper

The Remote Connect JavaScript contains a generic XMLHttpRequest helper.

For a GET request:

```text
if parameters exist:
    append parameters to URL

send request with no body
```

For a POST request:

```text
send parameters as the request body
```

The declared content type is:

```text
application/x-www-form-urlencoded
```

Therefore, a normal request looks conceptually like:

```http
POST /someEndpoint.htm HTTP/1.1
Content-Type: application/x-www-form-urlencoded

t123=value&t456=value
```

Remote Connect also commonly adds:

```text
X-Requested-With: A
```

to AJAX requests on the Events page.

This is potentially worth reproducing in the Python client if a particular endpoint behaves differently without it.

---

# 4. Custom binary-to-text encoding

The controller has a custom encoding scheme called `encodeThis()` in its JavaScript.

Despite the variable name `b64`, this is **not ordinary Base64**.

## Encoding alphabet

Each output character represents a 6-bit value.

The value is converted to an ASCII character by adding:

```text
0x3C
```

(decimal 60, character `<`).

Therefore:

```text
encoded_character = six_bit_value + 0x3C
```

The decoder reverses this:

```text
six_bit_value = encoded_character - 0x3C
```

## Bit packing

The algorithm consumes input bytes eight bits at a time and emits six-bit groups.

Conceptually:

```text
input:
    bytes

    ↓

combine bits into a bit stream

    ↓

take successive 6-bit groups

    ↓

add 0x3C to each group

    ↓

convert each result to an ASCII character
```

For complete groups, three input bytes become four output characters.

Therefore:

```text
3 bytes → 4 characters
18 bytes → 24 characters
```

This explains why an AllSync event's 18-byte structure becomes a 24-character encoded value.

---

# 5. Decoding

The reverse operation is:

```text
for each encoded character:
    subtract 0x3C
    append resulting 6 bits to bit buffer

whenever enough bits exist:
    extract an 8-bit byte
```

The JavaScript handles the bit boundaries explicitly.

This encoding should be implemented independently in Python in `clock/encoding.py`.

Suggested interface:

```text
encode_bytes(data: bytes) -> str

decode_string(value: str) -> bytes
```

---

# 6. Event data structure

An event is represented internally as an **18-byte buffer**.

```text
Offset    Size     Meaning
------------------------------------------------
0         4 bytes  event time
4         1 byte   schedule
5         1 byte   month
6         1 byte   day of month
7         1 byte   day-of-week mask
8         1 byte   year
9         1 byte   duration
10        1 byte   flags
11        1 byte   message number
12        1 byte   countdown duration
13        1 byte   schedule-change data
14        1 byte   device-specific/new-event data
15        1 byte   device-specific/new-event data
16        2 bytes  event index
------------------------------------------------
Total: 18 bytes
```

---

# 7. Event time

Bytes `0–3` contain a 32-bit unsigned integer.

The byte order is:

```text
big-endian
```

The value represents:

```text
seconds since 2000-01-01 00:00:00
```

For example:

```text
00 00 D9 F8
```

is interpreted as:

```text
0x0000D9F8
```

which is:

```text
55800 seconds
```

or:

```text
15:30:00
```

The four-byte value should therefore be calculated as:

```text
seconds = timestamp - 2000-01-01T00:00:00
```

and then encoded big-endian.

---

# 8. Schedule number

Byte `4` contains the schedule number used by the controller.

The JavaScript's internal object representation is zero-based, so it performs:

```text
internal schedule index = byte 4 - 1
```

Therefore, the wire representation is apparently:

```text
schedule 1 → byte 4 = 1
schedule 2 → byte 4 = 2
...
```

while the JavaScript's array indexing is:

```text
schedule 1 → index 0
schedule 2 → index 1
...
```

This distinction should be preserved explicitly in Quasimodo rather than hidden in random arithmetic.

---

# 9. Month and day

The controller uses zero-based values.

## Month

```text
0 = January
1 = February
...
11 = December
255 = wildcard / "All"
```

## Day of month

The wire representation is also zero-based:

```text
0 = first day of month
1 = second day
...
```

The JavaScript adds one when displaying the value to the user.

`255` represents a wildcard / "All" value.

---

# 10. Day-of-week mask

Byte `7` is a seven-bit mask.

```text
Bit       Day
-----------------
0x01      Sunday
0x02      Monday
0x04      Tuesday
0x08      Wednesday
0x10      Thursday
0x20      Friday
0x40      Saturday
```

So, for example:

```text
Monday + Tuesday + Wednesday + Thursday + Friday
```

is:

```text
0x02 | 0x04 | 0x08 | 0x10 | 0x20
= 0x3E
```

If the value is `>= 0x80`, the JavaScript treats it as a wildcard/special representation rather than a normal weekday mask.

---

# 11. Year

Byte `8` stores the year in a compact form.

For ordinary years:

```text
2000 → 0
2001 → 1
2002 → 2
...
```

The JavaScript therefore converts a displayed year above 2000 into:

```text
year_on_wire = year - 2000
```

`255` is used as a wildcard value.

---

# 12. Duration

Byte `9` contains the event duration.

Ordinary values represent seconds.

There are also three special values:

```text
10 = On
11 = Off
12 = Default
```

The JavaScript also allows the corresponding flags to communicate these special states.

A duration of zero is converted to one second by the Remote Connect JavaScript.

Therefore, Quasimodo should treat zero as invalid for a normal duration rather than sending it blindly.

---

# 13. Event flags

Byte `10` is a bit field.

```text
Bit       Value    Meaning
----------------------------------------------
0         0x01     event allocated
1         0x02     event dirty/internal
2         0x04     special date
3         0x08     special weekday
4         0x10     event ON
5         0x20     event OFF
6         0x40     duration is Default
7         0x80     schedule-change event
```

The flags are independent bit values.

For example:

```text
allocated + ON
= 0x01 | 0x10
= 0x11
```

The JavaScript specifically removes/clears its internal dirty flag when constructing exported event data.

---

# 14. Message number

Byte `11` contains the event's message number.

The normal event editor reads/writes this value as an integer.

The exact relationship between message numbers and the controller's broader message system still needs additional investigation.

---

# 15. Countdown duration

Byte `12` contains countdown-duration information.

The JavaScript preserves this value when loading and saving events.

Its exact user-facing semantics should be verified with a targeted Remote Connect capture.

---

# 16. Schedule-change field

Byte `13` contains schedule-change information.

If the schedule-change flag (`0x80`) is enabled, this field becomes significant.

The exact interpretation should be tested separately before Quasimodo relies on it.

---

# 17. Bytes 14–15

These two bytes have controller-specific behavior.

For a newly created event, the Remote Connect JavaScript explicitly sets:

```text
byte 14 = 255
byte 15 = 255
```

The JavaScript comments indicate that this is what the device itself uses when creating a new event.

For existing events, the two bytes are preserved rather than blindly regenerated.

Therefore Quasimodo should:

```text
new event:
    initialize bytes 14–15 as 0xFF

existing event:
    preserve bytes 14–15
```

until further protocol analysis determines their complete meaning.

---

# 18. Event index

Bytes `16–17` contain a 16-bit big-endian event index.

Example:

```text
00 02
```

means:

```text
event index = 2
```

A new event gets its index before being saved.

The JavaScript uses the next available event index.

---

# 19. Creating or updating an event

The event editor ultimately performs:

```text
create/modify 18-byte event buffer
        ↓
encode 18-byte buffer
        ↓
POST /POST.htm
```

The request body is:

```text
t600=<encoded-event>,
```

Notice the comma at the end.

Conceptually:

```http
POST /POST.htm
Content-Type: application/x-www-form-urlencoded

t600=<24-character encoded event>,
```

The same mechanism is used for both creating and editing an event.

The controller therefore apparently distinguishes create vs. update largely through the event data/index rather than separate endpoints.

---

# 20. Event retrieval

The Events page loads:

```text
GET /events.b64
```

The response consists of comma-separated encoded records.

Conceptually:

```text
encoded_event_1,encoded_event_2,encoded_event_3,...
```

The JavaScript:

```text
split response on comma
    ↓
decode every record
    ↓
expect an 18-byte buffer
    ↓
construct EventData from buffer
```

This gives us an important read-side protocol:

```text
GET /events.b64
```

is essentially the event database download endpoint.

This may be more useful to Quasimodo than trying to infer event state from POST responses.

---

# 21. Deleting events

Deleting selected events uses:

```text
POST /updateSet.htm
```

with:

```text
t600=0!<index1>!<index2>!<index3>#
```

For a single event:

```text
t600=0!2#
```

means:

```text
delete event index 2
```

Multiple events use additional `!` separators.

Example:

```text
t600=0!2!7!11#
```

means:

```text
delete events 2, 7, and 11
```

---

# 22. Deleting all events

The Events page uses:

```text
POST /updateSet.htm
```

with:

```text
t600=1
```

This means:

```text
delete all events
```

This is obviously a destructive operation and should not be exposed casually by Quasimodo.

---

# 23. Schedule names

The controller has 99 schedule slots.

Internal indexing is:

```text
0–98
```

The displayed schedule number is:

```text
1–99
```

Schedule data begins with:

```text
byte 0 = zero-based schedule index
byte 1 = reserved/unknown
```

The schedule name begins at:

```text
byte 2
```

and is a null-terminated ASCII-like byte string.

To save a schedule name:

```text
encode schedule buffer
        ↓
POST /updateSet.htm
```

with:

```text
t601=<encoded schedule>&,
```

---

# 24. Schedule-name retrieval

Schedule names are obtained from:

```text
GET /schnames.b64
```

The response is decoded using the same custom encoding.

Each resulting buffer represents a schedule.

---

# 25. Importing multiple events

The Events page can import many events.

Instead of issuing one request per event, it:

```text
encode each 18-byte event
        ↓
join encoded events with commas
        ↓
POST chunks to /updateSet.htm
```

The JavaScript limits each chunk to:

```text
50 events
```

The request is:

```text
t600=<event1>,<event2>,<event3>,...
```

followed by a trailing comma.

This means `updateSet.htm` is capable of accepting batches of event records.

---

# 26. Circuit-related protocol

The Circuit page uses ordinary form parameters rather than the event binary structure.

There are six wired circuits.

Some important parameter groups are:

```text
Circuit enabled:
t248 ... t253

Assigned schedule:
t254 ... t259

Default duration:
t260 ... t265

Circuit descriptions:
t365 ... t371

Manual circuit enable:
t372 ... t377

Signal durations:
t378 ... t383

Countdown durations:
t520 ... t525

Message numbers:
t514 ... t519
```

Some of these values are sent individually.

Others are condensed into summary strings before being sent.

---

# 27. Manual signal activation

Manual activation uses dedicated endpoints.

For wired activation:

```text
POST /signalStart.htm
```

Parameters include:

```text
manual-circuit summary
signal-duration summary
countdown values
message-number values
signal summary
```

For combined/wireless activation:

```text
POST /signalActivate.htm
```

The signal summary uses:

```text
1 = wired
2 = wireless
3 = both
0 = stop
```

Stopping uses:

```text
POST /signalStop.htm
```

The precise parameter encoding should be tested before implementing manual activation in Quasimodo.

---

# 28. Circuit schedule-name updates

Some circuit/schedule descriptions use:

```text
POST /schNames.htm
```

with:

```text
t537=<index>
t538=<value>
```

The response identifies the updated channel.

This appears distinct from the `t601` schedule-name mechanism.

---

# 29. Clock adjustment

The General page provides another family of endpoints.

Clock adjustment uses:

```text
POST /adjustClockSync.htm
```

with parameters including:

```text
t310 = clock code
t430 = adjustment value
```

or, for impulse-clock adjustment:

```text
t431 = adjustment hours
t432 = adjustment minutes
```

or:

```text
t433 = direct adjustment minutes
```

This area needs additional testing before being exposed through Quasimodo.

---

# 30. Time/date setting

The Set page writes the controller time using:

```text
POST /updateTime.htm
```

with fields:

```text
t003 = hour
t004 = minute
t005 = second
t006 = month
t007 = day
t008 = year
```

The month and day use the controller's zero-based conventions when the request is constructed.

---

# 31. External synchronization

External time synchronization uses:

```text
POST /externalSync.htm
```

with a selected synchronization source.

The observed values include:

```text
1 = CDMA
2 = Ethernet
4 = GPS
8 = WLS
```

Status is subsequently polled with:

```text
GET /externalSync.htm
```

The response is a comma-separated status structure.

---

# 32. Ethernet configuration

The Ethernet page assigns controller configuration fields to parameters such as:

```text
t277 = controller IP
t278 = master IP
t279 = subnet mask
t280 = gateway
t281 = MAC address
t282 = port
t283 = packets received
t284 = packets transmitted
t285 = Ethernet client state
t295 = DNS server
t296 = DNS time-server name
t297 = client-IP enabled
t429 = Ethernet server state
t530 = alternate IP
t544 = DHCP
```

Resetting packet counters uses:

```text
POST /resetPackets.htm
```

with:

```text
t283=<value>
t284=<value>
```

---

# 33. Firmware update protocol

The firmware JavaScript contains a separate binary transfer mechanism using:

```text
t616
t618
```

and endpoints including:

```text
POST /POST.htm
GET /status616.htm
POST /status616.htm
GET /status618.htm
POST /status618.htm
```

`t616` appears to carry encoded firmware chunks.

`t618` controls firmware-programming state.

This should be considered **outside Quasimodo's normal application protocol** and should not be implemented unless firmware management becomes an explicit requirement.

---

# 34. Current protocol map

The most relevant endpoints discovered so far are:

```text
Authentication
------------
GET  /auth.htm

Events
------------
GET  /events.b64
POST /POST.htm       t600=<encoded event>,
POST /updateSet.htm  t600=0!<indices>#
POST /updateSet.htm  t600=1

Schedules
------------
GET  /schnames.b64
POST /updateSet.htm  t601=<encoded schedule>&,

Circuits
------------
POST /schNames.htm
POST /signalStart.htm
POST /signalActivate.htm
POST /signalStop.htm

Time
------------
POST /updateTime.htm
POST /externalSync.htm
GET  /externalSync.htm
POST /adjustClockSync.htm

Ethernet
------------
POST /resetPackets.htm

Firmware
------------
POST /POST.htm
GET/POST /status616.htm
GET/POST /status618.htm
```

---

# 35. Recommended Quasimodo architecture

Based on this protocol, the `clock` Django app should have at least two conceptual layers.

```text
clock/
│
├── client.py
│
│   HTTP/session layer
│   ├── login()
│   ├── get_events()
│   ├── post_event()
│   ├── delete_events()
│   └── ...
│
├── encoding.py
│
│   AllSync binary protocol
│   ├── encode_bytes()
│   ├── decode_bytes()
│   ├── encode_event()
│   └── decode_event()
│
└── views.py
    Django/UI layer
```

The dependency direction should be:

```text
Django views
      │
      ▼
High-level clock operations
      │
      ├───────────────┐
      ▼               ▼
  encoding.py      client.py
                       │
                       ▼
                   HTTP
                       │
                       ▼
                 AllSync IQ
```

The key design principle is:

> Django should deal in Quasimodo objects. `client.py` and `encoding.py` should deal in AllSync protocol details.

---

# 36. What is confirmed vs. what still needs testing

## Strongly confirmed

```text
HTTP is used.
Authentication endpoint and parameter names.
Event endpoint: /POST.htm.
Event read endpoint: /events.b64.
Event delete protocol.
Schedule-name endpoint: /schnames.b64.
Schedule-name save parameter: t601.
18-byte event structure.
Big-endian integer fields.
Custom 6-bit encoding.
Event flag definitions.
Day-of-week bit mask.
Special duration values.
Event index location.
```

## Needs targeted testing

```text
Exact behavior of message_number.
Exact meaning of countdown_duration.
Exact behavior of schedule-change events.
Meaning of bytes 14–15 for existing events.
How the controller assigns/reassigns event indices.
Whether every POST requires the same headers.
Whether session cookies are required on every operation.
Exact failure/error responses.
Circuit form submission structure.
Manual signal activation behavior.
How schedule changes are represented on the wire.
```

---

# 37. Recommended next implementation step

Do **not** start with Django views.

The best first implementation target is:

```text
clock/encoding.py
```

Build and unit-test the custom encoder/decoder first.

Then build:

```text
clock/client.py
```

with only read-only operations initially:

```text
login()
get_events()
get_schedule_names()
```

Once those work, add the first write operation:

```text
create_event()
```

and verify it against the real controller.

That gives Quasimodo a small, testable protocol layer before Django's UI becomes involved.
