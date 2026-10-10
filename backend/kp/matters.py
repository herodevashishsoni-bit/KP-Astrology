"""Catalogue of life matters (kp-rules §3).

Every matter lists one or more *variants*. Where the sources disagree, each
variant is computed and shown with its source (user policy, §8). The first
variant is listed first; it is not preferred in any other way.

Fields of a variant:
  houses      houses whose significators give the event
  promise     (cusp, good houses, bad houses) – the cusp-sub-lord test
  negate      houses whose significance by the same planet cancels (12ths)
  source      citation
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .constants import SIGN_QUALITY


@dataclass
class Variant:
    houses: list[int]
    source: str
    promise: tuple[int, list[int], list[int]] | None = None
    negate: list[int] = field(default_factory=list)
    note: str = ""
    weights: dict[int, float] = field(default_factory=dict)   # house → weight (default 1)


@dataclass
class Matter:
    key: str
    title: str
    group: str
    variants: list[Variant]
    one_time: bool = False
    karaka: str | None = None
    description: str = ""


def rel(base: int, n: int) -> int:
    """House n counted from house base (base itself = 1)."""
    return (base - 1 + n - 1) % 12 + 1


def badhaka_from(chart, base: int) -> int:
    """Badhaka house counted from a house: movable → 11th, fixed → 9th, common → 7th (R2/R3)."""
    q = SIGN_QUALITY[int(chart.cusps[base - 1] // 30)]
    return rel(base, {"movable": 11, "fixed": 9, "common": 7}[q])


def death_houses(chart, base: int) -> list[int]:
    """Badhaka + marakas (2nd, 7th) counted from base (R6 p.83–86)."""
    return sorted({badhaka_from(chart, base), rel(base, 2), rel(base, 7)})


def catalogue(chart) -> list[Matter]:
    """Matters for one chart (death houses depend on the cusp signs)."""
    own_death = death_houses(chart, 1)
    M = []
    add = M.append

    # ---------------- longevity & death -------------------------------
    add(Matter("death", "Death of the native", "Longevity", [
        Variant(own_death, "R3 p.157–169; R6 p.154–160 (badhaka + marakas 2, 7)",
                promise=(1, [1, 5, 9, 10, 11], [6, 8, 12]), negate=[1, 3],
                weights={badhaka_from(chart, 1): 2.0},
                note="Promise = span from the Ascendant sub lord; window = conjoined period of badhaka/maraka "
                     "significators, badhaka first (R3 l.~7270). Lords also signifying longevity houses 1, 3 are weakened (R3: judge 1, 8, 3 then 2, 7, 12)."),
    ], one_time=True))
    relatives = [
        ("death_father", "Death of father", 9, "R2; R6 p.254 (father = 9th always)"),
        ("death_mother", "Death of mother", 4, "R3 l.10117; R6 p.254"),
        ("death_spouse", "Death of spouse", 7, "R3; R4 p.86, 208; R6 p.254"),
        ("death_child1", "Death of first child", 5, "R3 p.145; R6 p.254"),
        ("death_ysib", "Death of first younger sibling", 3, "R3 l.9909"),
        ("death_esib", "Death of elder sibling", 11, "R6 p.254"),
    ]
    for key, title, base, src in relatives:
        vs = [Variant(death_houses(chart, base), f"{src} — badhaka + marakas counted from house {base}",
                      negate=[base, rel(base, 3)], weights={badhaka_from(chart, base): 2.0})]
        if key == "death_spouse":
            vs.append(Variant([1, 6, 8, 12], "R6 p.254 table (spouse: 1, 6, 8, 12)"))
            vs.append(Variant([1, 6, 10], "KSK, Indira Gandhi case (magazines): 1, 6, 10"))
        if key == "death_father":
            vs.append(Variant([8, 10, 3, 12], "R6 p.254 table (father: 8, 10, 3, 12)"))
        if key == "death_mother":
            vs.append(Variant([3, 5, 10, 12], "R6 p.254 table (mother: 3, 5, 10, 12)"))
        if key == "death_child1":
            vs.append(Variant([4, 6, 11, 12], "R6 p.254 table (children: 4, 6, 11, 12)"))
        if key == "death_esib":
            vs.append(Variant([5, 10, 12], "R6 p.254 table (elder sibling: 5, 10, 12)"))
        add(Matter(key, title, "Family", vs, one_time=True))

    # ---------------- health ------------------------------------------
    add(Matter("illness", "Illness", "Health", [
        Variant([6, 1], "R3 l.~7620; R6 p.158 (6 with 1; +12 hospital)", promise=(1, [1, 5, 11], [6, 8, 12]))]))
    add(Matter("hospital", "Hospitalisation / surgery", "Health", [
        Variant([6, 8, 12], "R3; R6 p.159 (6, 8, 12)")]))
    add(Matter("cure", "Recovery from illness", "Health", [
        Variant([11, 5, 1], "R3 (11, sure if also 5); KSK MC_059–060")]))
    add(Matter("accident", "Accident / danger", "Health", [
        Variant([8, 6, 12], "R6 p.159; R3 (8 with 6, 12)"),
        Variant([4, 6, 8, 12], "Magazine contributor (4, 6, 8, 12)")]))

    # ---------------- marriage ----------------------------------------
    add(Matter("marriage", "Marriage", "Marriage", [
        Variant([2, 7, 11], "R3 l.13078+; R4 p.108 (blocking 1, 6, 10)", promise=(7, [2, 7, 11], [1, 6, 10]),
                negate=[1, 6, 10]),
        Variant([2, 7, 11], "R3 p.430; R4 elsewhere (blocking 1, 6, 10, 12)", promise=(7, [2, 7, 11], [1, 6, 10, 12]),
                negate=[1, 6, 10, 12]),
    ], one_time=True, karaka="Venus"))
    add(Matter("second_marriage", "Second marriage", "Marriage", [
        Variant([2, 7, 11], "R4 p.181; R6 p.165 (7th sub lord in dual sign + 2 or 11)", promise=(7, [2, 11], [])),
        Variant([2, 8, 11], "Magazine case (2, 8, 11)")]))
    add(Matter("separation", "Disharmony / separation / divorce", "Marriage", [
        Variant([1, 6, 10], "R4 p.153 (divorce 1, 6, 10)"),
        Variant([6, 10, 12], "R4 p.69 (dispute: sub lord signifying 6, 10, 12)")]))
    add(Matter("love", "Love affair", "Marriage", [Variant([5, 11], "R4 p.171 (5th sub lord; 5 with 11)")]))
    add(Matter("intimacy", "Extra-marital / illegal intimacy (11th only)", "Marriage", [
        Variant([11, 5], "KSK MC_059 (11th = illegal intimacy); 2nd sub lord connected with 11 (magazines)")]))

    # ---------------- children ----------------------------------------
    add(Matter("child", "Birth of a child", "Children", [
        Variant([2, 5, 11], "R2; R3 l.~18412; R4 p.203–280", promise=(5, [2, 5, 11], [1, 4, 10]), negate=[1, 4, 10]),
    ], karaka="Jupiter"))

    # ---------------- profession --------------------------------------
    add(Matter("job", "Employment / getting a job", "Profession", [
        Variant([2, 6, 10], "R3; KSK magazines (2, 6, 10)", promise=(10, [2, 6, 10, 11], [5, 9, 12])),
        Variant([2, 6, 10, 11], "R3 (2, 6, 10, 11)", promise=(10, [2, 6, 10, 11], [5, 9, 12]))]))
    add(Matter("promotion", "Promotion / rise in status", "Profession", [
        Variant([2, 6, 10, 11], "R3; R6 p.287 (11th sub lord)", promise=(11, [2, 6, 10, 11], [5, 9, 12]))]))
    add(Matter("business", "Independent business", "Profession", [
        Variant([2, 7, 10], "R3 l.~15700 (2, 7, 10)"),
        Variant([1, 7, 10], "R3 (2nd cusp sub lord 1, 7, 10 → business)")]))
    add(Matter("transfer", "Transfer", "Profession", [
        Variant([3, 9, 12, 10], "R3 p.375 (3, 9, 12 with 6 or 10)"),
        Variant([3, 10, 12], "R6 (3, 10, 12)"),
        Variant([2, 5, 6, 9, 10, 3], "Magazine contributor (2, 5, 6, 9, 10, +3)")]))
    add(Matter("job_change", "Change of job", "Profession", [
        Variant([3, 5, 9], "R6 (3, 5, 9)"), Variant([3, 9, 12], "R3 l.~15080 (3, 9, 12)"),
        Variant([9, 12], "KSK MC_058 (thorough change 9, 12)")]))
    add(Matter("suspension", "Suspension / termination", "Profession", [
        Variant([1, 5, 9, 12], "R3 (1, 5, 9 — 12ths of 2, 6, 10; +12)")]))
    add(Matter("retirement", "Retirement", "Profession", [
        Variant([3, 5, 9], "R3 l.~16570"), Variant([1, 5, 9], "R3 l.~8680"),
        Variant([1, 5, 9, 12], "KSK magazine"), Variant([9, 12], "KSK MC_060")], one_time=True))
    add(Matter("seniority", "Competition / seniority / election win", "Profession", [
        Variant([1, 2, 3, 6, 10, 11], "R3 l.~8700; KSK MC_060–061", negate=[4, 5, 7, 8, 9, 12])]))
    add(Matter("litigation", "Litigation begins", "Profession", [
        Variant([6, 7], "Magazine (6 = litigation, 7 = opponent)")]))

    # ---------------- finance -----------------------------------------
    add(Matter("wealth", "Financial gains", "Finance", [
        Variant([2, 6, 11, 10], "R3 l.~7720 (2, 6, 10, 11)", promise=(11, [2, 6, 11], [5, 8, 12])),
        Variant([2, 10, 11], "Magazine (6 excluded: loans)")]))
    add(Matter("loss", "Financial loss / expenditure", "Finance", [Variant([12, 8, 5], "R3 (12; 5 & 8 → loss)")]))
    add(Matter("loan", "Raising a loan", "Finance", [Variant([6, 2, 11], "R3 (6)")]))
    add(Matter("debt_clear", "Repayment of debts", "Finance", [Variant([8, 12, 4, 5], "R3 (4, 5, 8, 12)")]))
    add(Matter("windfall", "Lottery / speculation / sudden gain", "Finance", [
        Variant([5, 6, 11], "R5 p.224 (3rd sub lord with 5, 6, 11; 11th sub lord promise)", promise=(11, [5, 6, 11], [8, 12]))]))
    add(Matter("legacy", "Legacy / insurance / arrears", "Finance", [Variant([8, 6, 11], "R3 (8 with 6/11)")]))

    # ---------------- property ----------------------------------------
    add(Matter("house_buy", "Buying property / house", "Property", [
        Variant([4, 11, 12], "R3 l.10232; R6 (4, 11, 12)", promise=(4, [4, 11, 12], [3, 5, 10])),
        Variant([2, 4, 11], "R3 (acquisition 2, 4, 11)")], karaka="Mars"))
    add(Matter("house_sale", "Sale of property", "Property", [
        Variant([3, 5, 10], "R3 (3, 5, 10)"), Variant([3, 5, 8, 10], "Contributor MC_055 (3, 5, 8, 10 + Mars)")]))
    add(Matter("vehicle", "Buying a vehicle", "Property", [
        Variant([4, 11], "R3 (4 + Venus)", promise=(4, [4, 11], [3, 12])),
        Variant([4, 9, 10, 11], "KP Vol II p.151 via magazines (4, 9, 10, 11 + Venus)")], karaka="Venus"))
    add(Matter("vehicle_sale", "Sale of a vehicle", "Property", [
        Variant([3, 4, 5, 10], "KSK 1967 (3, 4, 5, 10)"), Variant([1, 3, 8, 10], "Contributor MC_055 (1, 3, 8, 10)")]))
    add(Matter("residence", "Change of residence", "Property", [
        Variant([3, 9, 12], "R6 p.305 (3 = 12th to 4, with 9/12)")]))

    # ---------------- education ---------------------------------------
    add(Matter("education", "Education / studies", "Education", [
        Variant([4, 9, 11], "R3 l.11329 (4, 9; 11 success)", promise=(4, [4, 9, 11], [3, 8])),
        Variant([4, 9], "KSK MC_059 (4 and 9)")]))
    add(Matter("education_end", "End of studies", "Education", [Variant([3, 5, 8], "R3 (3, 5, 8)")]))

    # ---------------- travel ------------------------------------------
    add(Matter("foreign", "Foreign travel / living abroad", "Travel", [
        Variant([3, 9, 12], "R3 l.~13585; R6 (12th cusp sub lord)", promise=(12, [3, 9, 12], []))]))
    add(Matter("return_home", "Return home from abroad", "Travel", [
        Variant([3, 9, 11], "R4 p.205"), Variant([3, 9, 11, 12], "R3"),
        Variant([2, 4, 11], "KSK MC_059 (2, 11 reunion; 4 home)"),
        Variant([3, 5, 6, 8, 11], "Contributor (3, 5, 6, 8, 11)")]))

    # ---------------- siblings, friends, enemies ----------------------
    add(Matter("sibling", "Gain / help through siblings", "Family", [
        Variant([3, 11, 1], "R3 l.9909 (3 with 11 and 1)", promise=(3, [3, 11], [8, 10]))]))
    add(Matter("imprisonment", "Imprisonment / detention", "Legal", [
        Variant([2, 3, 8, 12], "R6 p.313 (12th sub lord Rahu)"), Variant([2, 12], "R3 l.~17527"),
        Variant([3, 8, 12], "R3 l.~18215")]))
    add(Matter("release", "Release", "Legal", [Variant([2, 11], "R3; MC_058 (2, 11)")]))

    # ---------------- spiritual ---------------------------------------
    add(Matter("spiritual", "Spiritual initiation / progress", "Mind", [
        Variant([5, 10, 11], "R3 l.~17625 (initiation 5, practice 10, progress 11)")]))
    add(Matter("courage", "Bold, confident periods", "Mind", [Variant([3, 5], "KSK MC_059 (3, 5)")]))
    add(Matter("fear", "Fear / timid, worried periods", "Mind", [Variant([8, 12], "KSK MC_059 (8 fear; 12)")]))
    return M
