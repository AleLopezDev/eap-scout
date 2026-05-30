# eap-scout

Small EAP method and identity inspector for 802.1X/WPA-Enterprise packet captures.

`eap-scout` is a lightweight Bash utility that parses Wi-Fi packet captures with `tshark` and extracts visible EAP methods, client identities, and quick security-oriented conclusions.

It is designed for wireless assessments, lab work, and audit notes where you need to quickly answer questions like:

- Is the network using EAP-TLS, PEAP, TTLS, LEAP or EAP-MD5?
- Did the capture expose real client identities?
- Is there likely to be a crackable MSCHAPv2 exchange?
- Is the target using certificate-based authentication?

> Use only on networks and captures you are authorized to assess.

---

## Features

- Detects visible EAP methods from `.cap`, `.pcap` and `.pcapng` files.
- Extracts EAP identities when present.
- Classifies identities as anonymous or real/possibly real.
- Separates EAP-Identity from actual authentication methods.
- Prints AP/RADIUS method proposals.
- Adds short conclusions for common enterprise Wi-Fi methods.

Supported method labels include:

```text
EAP-TLS
PEAP
EAP-TTLS
EAP-MSCHAPV2
EAP-MD5
LEAP
EAP-FAST
```

---

## Requirements

- Bash
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
chmod +x eap-scout
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
Methods observed:    EAP-TLS
Identities observed: GLOBAL\GlobalAdmin
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
| EAP-MD5 | Legacy challenge-response | Weak/obsolete |
| LEAP | Legacy Cisco method | Weak/obsolete |
| EAP-FAST | PAC-based authentication | Review provisioning mode |

---

## Spanish description

`eap-scout` es una herramienta ligera en Bash para analizar capturas 802.1X/WPA-Enterprise y extraer métodos EAP visibles, identidades de cliente y conclusiones rápidas orientadas a auditoría.

Permite diferenciar métodos como EAP-TLS, PEAP, EAP-TTLS, LEAP, EAP-MD5 y EAP-MSCHAPv2, indicando también cuándo el método interno no es visible por ir protegido dentro de un túnel TLS.

---

## License

MIT License.
