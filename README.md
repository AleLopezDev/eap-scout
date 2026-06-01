# eap-scout

Small EAP method and identity inspector for 802.1X/WPA-Enterprise packet captures.

`eap-scout` is a lightweight Bash utility that parses Wi-Fi packet captures with `tshark` and extracts visible EAP methods, client identities, negotiation hints, and quick security-oriented conclusions.

It is designed for wireless assessments, lab work, and audit notes where you need to quickly answer questions like:

- Is the network using EAP-TLS, PEAP, TTLS, LEAP or EAP-MD5?
- Did the capture expose real client identities?
- Is there likely to be a crackable MSCHAPv2 or EAP-MD5 exchange?
- Is the target using certificate-based authentication?
- Did a client reject the proposed EAP method with a Legacy Nak?

> Use only on networks and captures you are authorized to assess.

---

## Features

- Detects visible EAP methods from `.cap`, `.pcap` and `.pcapng` files.
- Extracts EAP identities when present.
- Classifies identities as anonymous or real/possibly real.
- Separates EAP-Identity from actual authentication methods.
- Detects Legacy Nak responses and extracts the desired EAP type when available.
- Prints AP/RADIUS method proposals.
- Adds short conclusions for common enterprise Wi-Fi methods.
- Includes a small EAP-MD5 offline cracking helper.

Supported method labels include:

```text
EAP-TLS
PEAP
EAP-TTLS
EAP-MSCHAPV2
EAP-MD5
LEAP
EAP-FAST
Legacy Nak
```

---

## Requirements

- Bash
- Python 3, only for `tools/crack-eap-md5.py`
- `tshark`

Install `tshark`:

```bash
# Debian / Ubuntu / Kali
sudo apt install tshark

# Arch Linux
sudo pacman -S wireshark-cli
```

---

## Installation

```bash
git clone https://github.com/AleLopezDev/eap-scout.git
cd eap-scout
chmod +x eap-scout tools/crack-eap-md5.py
```

Optional system-wide install:

```bash
sudo cp eap-scout /usr/local/bin/eap-scout
```

---

## Usage

```bash
./eap-scout capture.cap
```

Example:

```bash
./eap-scout /tmp/wifi-global-01.cap
```

---

## Example output

```text
[*] Reading capture: /tmp/wifi-global-01.cap

------------------------------------------------------------
Clients
------------------------------------------------------------

Client: 64:32:a8:ba:18:42
  Identities:
    - GLOBAL\GlobalAdmin (real/possibly real)
  EAP methods:
    - EAP-TLS
      Client certificate required. No MSCHAPv2 password hash is exposed.
  Verdict: EAP-TLS observed. Valid client certificate and private key are required for authentication.

------------------------------------------------------------
AP/RADIUS proposals
------------------------------------------------------------
f0:9f:c2:71:22:17 -> 64:32:a8:ba:18:42: EAP-TLS

------------------------------------------------------------
Summary
------------------------------------------------------------
Methods observed:       EAP-TLS
Identities observed:    GLOBAL\GlobalAdmin
Legacy Nak observed:    0
Nak Desired Auth Types: not observed
```

Legacy Nak example:

```text
Client: 64:32:a8:ad:ab:53
  Identities:
    - WORKGROUP\administrator (real/possibly real)
  EAP methods:
    - not detected
  Negotiation:
    - Legacy Nak observed at frame 19
      Desired Auth Type: MD5-Challenge EAP (EAP-MD5-CHALLENGE) (4)
      The client rejected the proposed EAP method. This is not an authentication method and will not produce a hash by itself.
```

---

## EAP-MD5 helper

If an EAP-MD5 challenge/response exchange is captured, extract the values with `tshark`:

```bash
tshark -r capture.cap \
  -Y "eap.type == 4" \
  -T fields \
  -e frame.number \
  -e wlan.sa \
  -e wlan.da \
  -e eap.code \
  -e eap.id \
  -e eap.md5.value
```

Example:

```text
37  02:00:00:00:03:00  64:32:a8:ad:ab:53  1  235  fae977627339890b9ba7f5dd87c484a6
38  64:32:a8:ad:ab:53  02:00:00:00:03:00  2  235  0dd1a9c1b1f01ba00f3a63effd9ea973
```

Interpretation:

```text
code=1 -> EAP Request-MD5  -> challenge
code=2 -> EAP Response-MD5 -> response
id     -> EAP identifier used in the MD5 calculation
```

Crack offline:

```bash
python3 tools/crack-eap-md5.py \
  235 \
  fae977627339890b9ba7f5dd87c484a6 \
  0dd1a9c1b1f01ba00f3a63effd9ea973 \
  /path/to/wordlist.txt
```

EAP-MD5 computes:

```text
MD5(EAP_ID + password + challenge) = response
```

---

## Important notes

Passive captures usually expose the **outer EAP method**.

For tunneled methods like PEAP or EAP-TTLS, the inner method is commonly protected inside TLS:

```text
PEAP       -> inner method may be MSCHAPv2/GTC/etc.
EAP-TTLS   -> inner method may be PAP/CHAP/MSCHAPv2/GTC/etc.
```

That means a passive capture may show only:

```text
PEAP
```

but not necessarily:

```text
PEAP-MSCHAPv2
```

To confirm PEAP-MSCHAPv2, use additional evidence such as:

- `wpa_supplicant -dd` logs.
- Eaphammer / hostapd-mana output showing MSCHAPv2 challenge-response.
- EAP method enumeration tools.

---

## Interpretation quick reference

| Method | Meaning | Practical note |
|---|---|---|
| EAP-TLS | Client and server certificates | Requires valid client certificate and private key |
| PEAP | Outer TLS tunnel | Inner method may not be visible passively |
| EAP-TTLS | Outer TLS tunnel | Inner PAP/CHAP/MSCHAPv2/GTC usually hidden |
| EAP-MSCHAPV2 | MSCHAPv2 visible | Challenge-response may be crackable if complete |
| EAP-MD5 | Legacy challenge-response | Weak/obsolete; response can be cracked offline with the EAP ID and challenge |
| LEAP | Legacy Cisco method | Weak/obsolete |
| EAP-FAST | PAC-based authentication | Review provisioning mode |
| Legacy Nak | Method rejection | Inspect Desired Auth Type and try a compatible EAP method |

---

## Spanish description

`eap-scout` es una herramienta ligera en Bash para analizar capturas 802.1X/WPA-Enterprise y extraer métodos EAP visibles, identidades de cliente, pistas de negociación y conclusiones rápidas orientadas a auditoría.

Permite diferenciar métodos como EAP-TLS, PEAP, EAP-TTLS, LEAP, EAP-MD5 y EAP-MSCHAPv2, indicando también cuándo el método interno no es visible por ir protegido dentro de un túnel TLS. Además, incluye una utilidad pequeña para crackear offline intercambios EAP-MD5 capturados.

---

## License

MIT License.
