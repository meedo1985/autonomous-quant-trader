"""R-14a confirmation module, route M: the module's own drand quicknet BLS check
(seed_disclosure `verification`, R-14a item 7). Vectors are RFC 9380's published test
vectors (rfc-editor.org/rfc/rfc9380.txt, SHA-256 a2e6ab02b2117d6f52ac293020857752972b
2e23ae005c33f612e40436ff4b6d): Appendix K.1 (expand_message_xmd SHA-256) and J.9.1
(BLS12381G1_XMD:SHA-256_SSWU_RO_), plus real quicknet rounds (FP3
verifier-test-2026-10-25, where drand's own client gives the same verdicts)."""

from __future__ import annotations

import pytest

from calibration import c2_confirmation as cf

XMD_DST = b"QUUX-V01-CS02-with-expander-SHA256-128"
H2C_DST = b"QUUX-V01-CS02-with-BLS12381G1_XMD:SHA-256_SSWU_RO_"

XMD_VECTORS = [
    (
        "",
        32,
        "68a985b87eb6b46952128911f2a4412bbc302a9d759667f87f7a21d803f07235",
    ),
    (
        "abc",
        32,
        "d8ccab23b5985ccea865c6c97b6e5b8350e794e603b4b97902f53a8a0d605615",
    ),
    (
        "abcdef0123456789",
        32,
        "eff31487c770a893cfb36f912fbfcbff40d5661771ca4b2cb4eafe524333f5c1",
    ),
    (
        "q128_" + "q" * 128,
        32,
        "b23a1d2b4d97b2ef7785562a7e8bac7eed54ed6e97e29aa51bfe3f12ddad1ff9",
    ),
    (
        "a512_" + "a" * 512,
        32,
        "4623227bcc01293b8c130bf771da8c298dede7383243dc0993d2d94823958c4c",
    ),
    (
        "",
        128,
        "af84c27ccfd45d41914fdff5df25293e221afc53d8ad2ac06d5e3e29485dadbe"
        "e0d121587713a3e0dd4d5e69e93eb7cd4f5df4cd103e188cf60cb02edc3edf18"
        "eda8576c412b18ffb658e3dd6ec849469b979d444cf7b26911a08e63cf31f9dc"
        "c541708d3491184472c2c29bb749d4286b004ceb5ee6b9a7fa5b646c993f0ced",
    ),
    (
        "abc",
        128,
        "abba86a6129e366fc877aab32fc4ffc70120d8996c88aee2fe4b32d6c7b6437a"
        "647e6c3163d40b76a73cf6a5674ef1d890f95b664ee0afa5359a5c4e07985635"
        "bbecbac65d747d3d2da7ec2b8221b17b0ca9dc8a1ac1c07ea6a1e60583e2cb00"
        "058e77b7b72a298425cd1b941ad4ec65e8afc50303a22c0f99b0509b4c895f40",
    ),
    (
        "abcdef0123456789",
        128,
        "ef904a29bffc4cf9ee82832451c946ac3c8f8058ae97d8d629831a74c6572bd9"
        "ebd0df635cd1f208e2038e760c4994984ce73f0d55ea9f22af83ba4734569d4b"
        "c95e18350f740c07eef653cbb9f87910d833751825f0ebefa1abe5420bb52be1"
        "4cf489b37fe1a72f7de2d10be453b2c9d9eb20c7e3f6edc5a60629178d9478df",
    ),
    (
        "q128_" + "q" * 128,
        128,
        "80be107d0884f0d881bb460322f0443d38bd222db8bd0b0a5312a6fedb49c1bb"
        "d88fd75d8b9a09486c60123dfa1d73c1cc3169761b17476d3c6b7cbbd727acd0"
        "e2c942f4dd96ae3da5de368d26b32286e32de7e5a8cb2949f866a0b80c58116b"
        "29fa7fabb3ea7d520ee603e0c25bcaf0b9a5e92ec6a1fe4e0391d1cdbce8c68a",
    ),
    (
        "a512_" + "a" * 512,
        128,
        "546aff5444b5b79aa6148bd81728704c32decb73a3ba76e9e75885cad9def1d0"
        "6d6792f8a7d12794e90efed817d96920d728896a4510864370c207f99bd4a608"
        "ea121700ef01ed879745ee3e4ceef777eda6d9e5e38b90c86ea6fb0b36504ba4"
        "a45d22e86f6db5dd43d98a294bebb9125d5b794e9d2a81181066eb954966a487",
    ),
]

H2C_VECTORS = [  # msg, P.x, P.y, Q0.x, Q0.y
    (
        "",
        0x052926ADD2207B76CA4FA57A8734416C8DC95E24501772C814278700EED6D1E4E8CF62D9C09DB0FAC349612B759E79A1,
        0x08BA738453BFED09CB546DBB0783DBB3A5F1F566ED67BB6BE0E8C67E2E81A4CC68EE29813BB7994998F3EAE0C9C6A265,
        0x11A3CCE7E1D90975990066B2F2643B9540FA40D6137780DF4E753A8054D07580DB3B7F1F03396333D4A359D1FE3766FE,
        0x0EEAF6D794E479E270DA10FDAF768DB4C96B650A74518FC67B04B03927754BAC66F3AC720404F339ECDCC028AFA091B7,
    ),
    (
        "abc",
        0x03567BC5EF9C690C2AB2ECDF6A96EF1C139CC0B2F284DCA0A9A7943388A49A3AEE664BA5379A7655D3C68900BE2F6903,
        0x0B9C15F3FE6E5CF4211F346271D7B01C8F3B28BE689C8429C85B67AF215533311F0B8DFAAA154FA6B88176C229F2885D,
        0x125435ADCE8E1CBD1C803E7123F45392DC6E326D292499C2C45C5865985FD74FE8F042ECDEEEC5ECAC80680D04317D80,
        0x0E8828948C989126595EE30E4F7C931CBD6F4570735624FD25AEF2FA41D3F79CFB4B4EE7B7E55A8CE013AF2A5BA20BF2,
    ),
    (
        "abcdef0123456789",
        0x11E0B079DEA29A68F0383EE94FED1B940995272407E3BB916BBF268C263DDD57A6A27200A784CBC248E84F357CE82D98,
        0x03A87AE2CAF14E8EE52E51FA2ED8EEFE80F02457004BA4D486D6AA1F517C0889501DC7413753F9599B099EBCBBD2D709,
        0x08834484878C217682F6D09A4B51444802FDBA3D7F2DF9903A0DDADB92130EBBFA807FFFA0EABF257D7B48272410AFFF,
        0x0B318F7ECF77F45A0F038E62D7098221D2DBBCA2A394164E2E3FE953DC714AC2CDE412D8F2D7F0C03B259E6795A2508E,
    ),
    (
        "q128_" + "q" * 128,
        0x15F68EAA693B95CCB85215DC65FA81038D69629F70AEEE0D0F677CF22285E7BF58D7CB86EEFE8F2E9BC3F8CB84FAC488,
        0x1807A1D50C29F430B8CAFC4F8638DFEEADF51211E1602A5F184443076715F91BB90A48BA1E370EDCE6AE1062F5E6DD38,
        0x0CBD7F84AD2C99643FEA7A7AC8F52D63D66CEFA06D9A56148E58B984B3DD25E1F41FF47154543343949C64F88D48A710,
        0x052C00E4ED52D000D94881A5638AE9274D3EFC8BC77BC0E5C650DE04A000B2C334A9E80B85282A00F3148DFDFACE0865,
    ),
    (
        "a512_" + "a" * 512,
        0x082AABAE8B7DEDB0E78AEB619AD3BFD9277A2F77BA7FAD20EF6AABDC6C31D19BA5A6D12283553294C1825C4B3CA2DCFE,
        0x05B84AE5A942248EEA39E1D91030458C40153F3B654AB7872D779AD1E942856A20C438E8D99BC8ABFBF74729CE1F7AC8,
        0x0CF97E6DBD0947857F3E578231D07B309C622ADE08F2C08B32FF372BD90DB19467B2563CC997D4407968D4AC80E154F8,
        0x127F0CDDF2613058101A5701F4CB9D0861FD6C2A1B8E0AFE194FCCF586A3201A53874A2761A9AB6D7220C68661A35AB3,
    ),
]


@pytest.mark.parametrize(("msg", "n", "expected"), XMD_VECTORS)
def test_expand_message_xmd_matches_rfc_9380(msg: str, n: int, expected: str) -> None:
    assert cf._expand_xmd(msg.encode(), XMD_DST, n).hex() == expected


@pytest.mark.parametrize(("msg", "px", "py", "q0x", "q0y"), H2C_VECTORS)
def test_hash_to_g1_matches_rfc_9380(
    msg: str, px: int, py: int, q0x: int, q0y: int
) -> None:
    u = cf._expand_xmd(msg.encode(), H2C_DST, 128)
    q0 = cf._iso_map(*cf._sswu(int.from_bytes(u[:64], "big") % cf._P))
    assert cf._affine1(q0) == (q0x, q0y)  # map_to_curve, isogeny included
    assert cf._affine1(cf._hash_to_g1(msg.encode(), H2C_DST)) == (px, py)


def test_g2_generator_is_on_the_twist_and_of_order_r() -> None:
    g2 = (cf._F2(cf._G2_X), cf._F2(cf._G2_Y), cf._F2.of(1))
    assert g2[1] * g2[1] == g2[0] * g2[0] * g2[0] + cf._F2((4, 4))
    assert cf._mul(g2, cf._R)[2].zero()
    tx, ty, _ = cf._twist(g2)
    assert ty * ty == tx * tx * tx + 4  # the twist lands on y^2 = x^3 + 4


KEY = (
    "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c"
    "8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb"
    "5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a"
)
SIG_1M = (
    "83ad29e4c409f9470fc2ef02f90214df49e02b441a1a241a82d622d9f608ef98"
    "fd8b11a029f1bee9d9e83b45088abe72"
)
SIG_1M1 = (
    "a5bd91e5e2d8c0bf51bffdfad87eef34348fd9c0b2df2bee39db90bdef7e1399"
    "b1a77bb2fe98b24d84c0936a306c4218"
)


def test_real_rounds_verify_and_swaps_do_not() -> None:
    assert cf.bls_verify(KEY, 1_000_000, SIG_1M) is True
    assert cf.bls_verify(KEY, 1_000_001, SIG_1M1) is True
    assert cf.bls_verify(KEY, 1_000_000, SIG_1M1) is False
    assert cf.bls_verify(KEY, 1_000_001, SIG_1M) is False
    assert cf.bls_verify(KEY, 999_999, SIG_1M) is False


def _first_point_off_subgroup() -> int:
    """The smallest x giving a curve point outside G1 (the cofactor is large)."""
    x = 0
    while True:
        y = cf._sqrt(x**3 + 4)
        if y is not None and not cf._mul(cf._g1(x, y), cf._R)[2].zero():
            return x
        x += 1


@pytest.mark.parametrize(
    ("sig", "match"),
    [
        (SIG_1M[:-2], "compressed G1"),  # 47 bytes
        ("0" + SIG_1M[1:], "compressed G1"),  # compression flag cleared
        ("c0" + "00" * 47, "compressed G1"),  # infinity
        ("9a" + "ff" * 47, "curve"),  # x >= p
        (SIG_1M[:3] + "e" + SIG_1M[4:], "G1"),  # FP3's one changed digit
    ],
)
def test_malformed_signatures_are_refused(sig: str, match: str) -> None:
    with pytest.raises(cf.SeedError, match=match):
        cf.bls_verify(KEY, 1_000_000, sig)


def test_a_curve_point_outside_the_subgroup_is_refused() -> None:
    x = _first_point_off_subgroup()
    sig = bytearray(x.to_bytes(48, "big"))
    sig[0] |= 0x80
    with pytest.raises(cf.SeedError, match="subgroup"):
        cf.bls_verify(KEY, 1_000_000, sig.hex())


@pytest.mark.parametrize(
    ("key", "match"),
    [
        (KEY[:-2], "compressed G2"),
        ("0" + KEY[1:], "compressed G2"),
        ("c0" + "00" * 95, "compressed G2"),
        ("9a" + "ff" * 95, "range"),
        (SIG_1M, "compressed G2"),  # a G1 point is not a key
    ],
)
def test_malformed_keys_are_refused(key: str, match: str) -> None:
    with pytest.raises(cf.SeedError, match=match):
        cf.bls_verify(key, 1_000_000, SIG_1M)


def test_the_other_sign_of_the_key_does_not_verify() -> None:
    other = bytearray(bytes.fromhex(KEY))
    other[0] ^= 0x20  # same x, the negated point: a valid key, the wrong one
    assert cf.bls_verify(other.hex(), 1_000_000, SIG_1M) is False


def test_a_g2_key_outside_the_subgroup_is_refused() -> None:
    # x = (0, 1), i.e. c1 = 1, c0 = 0: on the twist, not in G2 (R14SM-S-2)
    key = bytearray((1).to_bytes(48, "big") + bytes(48))
    key[0] |= 0x80
    with pytest.raises(cf.SeedError, match="G2 subgroup"):
        cf.bls_verify(key.hex(), 1_000_000, SIG_1M)
