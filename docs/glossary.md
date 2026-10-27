# Glossary

Plain explanations of the words, quantities and diagrams used in GeoChem
App. It is written for students and for researchers who are new to
geochemical data.

The glossary and **Scientific methods** work together. The glossary says
what a word means. Scientific methods gives the exact rules and formulas
that the app uses, for reviewers and for your own methods section.

## How to use this glossary

Every entry has the same pattern:

1. **What it is**: a definition in one to three sentences.
2. **In the app**: where you meet the term.
3. **Source**: the reference (author–year) to cite or read.

Type a word in the **search box** above the document to see all entries
that contain it. On the Diagrams page, the *Scientific basis* tab of every
diagram has a button that opens its glossary entry.

Rock names follow the IUGS recommendations in Le Maitre et al. (2002).

## Data and chemistry

### wt% (weight percent)

**What it is.** Grams of a component in 100 g of rock. Major oxides such as
SiO2 and MgO are given in wt%.

**In the app.** All major oxides are read and shown in wt%. Columns
without a unit are taken as wt% for oxides.

**Source.** Rollinson and Pease (2021), chapter 2.

### ppm and ppb

**What it is.** Parts per million (µg/g) and parts per billion (ng/g).
1 wt% = 10,000 ppm, and 1 ppm = 1,000 ppb. Trace elements are given in ppm.

**In the app.** Elements are converted to ppm. A column in ppb is divided
by 1,000; an element given as an oxide in wt% (for example TiO2) can be
converted to the element in ppm.

**Source.** Rollinson and Pease (2021), chapter 2.

### Major oxides and trace elements

**What it is.** Major oxides make up most of a rock (SiO2, TiO2, Al2O3,
iron, MnO, MgO, CaO, Na2O, K2O, P2O5); each is usually above 0.1 wt%.
Trace elements are present at low levels (usually below 0.1 wt%, i.e.
below 1,000 ppm), for example Rb, Sr, Zr, Nb and the rare earth elements.

**In the app.** Classification diagrams such as TAS use major oxides;
discrimination diagrams and spider diagrams mostly use trace elements.

**Source.** Rollinson and Pease (2021), chapter 2.

### LOI (loss on ignition)

**What it is.** The mass a rock powder loses when it is heated to about
1,000 °C. It is mostly water (H2O) and CO2 released from minerals such as
clays, micas, serpentine and carbonates. LOI can be **negative**: when
Fe²⁺ is oxidised to Fe³⁺ during heating, the powder gains oxygen.

**In the app.** LOI is left out of the anhydrous sum. LOI above 2.5 wt% is
used as a sign that a volcanic rock may not be fresh enough for TAS.
Serpentinites typically have LOI of 10–14 wt%.

**Source.** Le Bas et al. (1986); Rollinson and Pease (2021).

### H2O+ and H2O−

**What it is.** H2O− is moisture that leaves the powder below about
110 °C. H2O+ is water bound in minerals, released at higher temperature.

**In the app.** H2O+ above 2 wt% marks a volcanic rock as suspect for TAS.
H2O+ is used in the CIPW norm when the file has it.

**Source.** Le Bas et al. (1986).

### Detection limit

**What it is.** The lowest amount an instrument can measure reliably.
Labs write values below it as `<0.01`, `bdl` (below detection limit) or
`n.d.` (not detected).

**In the app.** Such cells become **missing values**, never zero and never
half the detection limit. The data check report lists every change.

**Source.** App convention (Scientific methods, section 1).

### Anhydrous (volatile-free) basis

**What it is.** Major oxides recalculated so that they add up to 100 wt%
without LOI, H2O, CO2 and other volatiles. It removes the dilution by
water and CO2, so altered and fresh rocks can be compared.

**In the app.** Switch *Recalculate major oxides to 100 % volatile-free
before TAS* in Settings (on by default). Diagrams marked *anhydrous* in
their scientific basis use it too. Iron is counted once per sample.

**Source.** Le Bas et al. (1986).

### FeOt and Fe2O3t (total iron)

**What it is.** All iron in a rock expressed as one oxide: as FeO (FeOt)
or as Fe2O3 (Fe2O3t). XRF measures only total iron, usually reported as
Fe2O3t. FeOt = 0.8998 × Fe2O3t, and FeOt = FeO + 0.8998 × Fe2O3.

**In the app.** You can give iron as FeO and Fe2O3, as Fe2O3t or as FeOt;
the app converts as needed. Many diagrams use FeOt.

**Source.** Stoichiometry: 2 FeO / Fe2O3 = 143.69 / 159.69.

### Iron oxidation ratio

**What it is.** How much of the iron is ferric (Fe³⁺) rather than ferrous
(Fe²⁺). It is written in several ways: Fe³⁺/Fe(total) (atomic), Fe2O3/FeO
(weight ratio) or Ox = FeO/(FeO + Fe2O3) (weight ratio, Le Maitre 1976).
Oxidation by weathering, alteration or serpentinization raises Fe³⁺.

**In the app.** Needed when FeO and Fe2O3 must be separate (CIPW norm,
Verma et al. 2006) but only total iron was measured. See *Iron split*.

**Source.** Le Maitre (1976); Middlemost (1989).

### Iron split

**What it is.** Dividing total iron into FeO and Fe2O3 with an assumed
oxidation ratio. Three approaches exist: a fixed ratio; the Le Maitre
(1976) equations, where the ratio depends on SiO2 and Na2O + K2O; and the
standard ratios of Middlemost (1989) for each TAS field.

**In the app.** Settings → *Iron split when only total iron is measured*.
Default: Le Maitre (1976), volcanic equation, as Le Bas et al. (1986)
recommend. Measured FeO and Fe2O3 are kept unless you switch on *Also
replace measured FeO and Fe2O3*. No method is valid for serpentinised
rocks; measure FeO by titration for them.

**Source.** Le Bas et al. (1986); Le Maitre (1976); Middlemost (1989);
Le Maitre et al. (2002, p. 34).

### Molar proportion

**What it is.** The amount of an oxide in moles: wt% divided by the molar
mass. Many indices compare atoms, not masses, so they use molar values.

**In the app.** A/CNK, A/NK, Mg# and the Frost et al. indices use molar
proportions.

**Source.** Rollinson and Pease (2021).

### Millications

**What it is.** Cation proportions × 1,000: the number of cations in the
oxide (for example 2 Al in Al2O3) times wt% divided by the molar mass,
times 1,000.

**In the app.** The R1–R2 diagrams (De la Roche et al. 1980) and the
alkalinity index of Frost and Frost (2008).

**Source.** De la Roche et al. (1980); Janoušek et al. (2006).

### Mg# (magnesium number)

**What it is.** 100 × Mg/(Mg + Fe²⁺), molar. It measures how primitive a
magma or rock is: mantle olivine has Mg# about 90; evolved melts have
lower values.

**In the app.** The Data page computes Mg# with all iron as Fe²⁺. The MgO
variation diagrams can show lines of equal Mg#.

**Source.** Rollinson and Pease (2021), section 3.3.2.

### Normalisation

**What it is.** Dividing each element by its value in a reference material
such as CI chondrite, primitive mantle or MORB. The result shows
enrichment (> 1) or depletion (< 1) relative to the reference and removes
the natural zig-zag of element abundances.

**In the app.** Spider diagrams; the Saccani (2015) and Martin (1986)
diagrams use normalised values. The app offers 35 sets of normalising
values compiled by Janoušek et al. (2006).

**Source.** McDonough and Sun (1995); Sun and McDonough (1989).

### Closure

**What it is.** Because oxide percentages must add up to 100, they are not
independent: when one goes up, the others must go down. This creates
correlations that are not geological.

**In the app.** Ratios (for example MgO/SiO2) do not change with closure
or with the anhydrous recalculation, which is why several diagrams use
ratios.

**Source.** Rollinson and Pease (2021), sections 2.2 and 3.3.2.2.

### Log-ratio

**What it is.** The logarithm of one component divided by another (or by
the geometric mean of all). Log-ratios remove the closure problem and are
the basis of modern statistics of compositions.

**In the app.** The discriminant functions of Verma et al. (2006) and
Agrawal et al. (2008) use natural-log ratios. More log-ratio tools are
planned.

**Source.** Aitchison (1986).

## Petrology

### Volcanic, plutonic and hypabyssal rocks

**What it is.** Volcanic rocks cooled at or near the surface (lavas,
pyroclastic rocks) and are fine grained. Plutonic rocks crystallised
slowly at depth and are coarse grained. Hypabyssal rocks (dykes, sills)
are in between.

**In the app.** Choose diagrams for the right type: TAS and R1–R2
volcanic for volcanic rocks; Middlemost (1985) TAS for plutonic rocks and
R1–R2 plutonic for plutonic rocks.

**Source.** Le Maitre et al. (2002).

### Ultramafic and ultrabasic

**What it is.** *Ultramafic* describes a rock made of more than 90 %
mafic minerals (olivine, pyroxene, hornblende), for example peridotite and
dunite. *Ultrabasic* is a chemical word: SiO2 below 45 wt%. A rock can be
one without being the other.

**In the app.** A sample counts as ultramafic when its anhydrous MgO is at
or above the Settings threshold (default 30 wt%) or when its Rock type
names an ultramafic rock. Ultramafic samples get warnings on diagrams made
for other rocks.

**Source.** Le Maitre et al. (2002).

### High-Mg volcanic rocks

**What it is.** Picrite, komatiite, meimechite and boninite. They are rich
in MgO and are named by special IUGS rules **before** TAS, because TAS
would give them misleading names.

**In the app.** The Results tab of TAS applies these rules first and
shows the IUGS name.

**Source.** Le Bas (2000) as cited in Le Maitre et al. (2002).

### Magma series: tholeiitic, calc-alkaline, shoshonitic

**What it is.** Families of related magmas. Tholeiitic magmas become
richer in iron as they evolve. Calc-alkaline magmas do not show this iron
enrichment and are typical of subduction zones. Shoshonitic rocks are very
rich in K2O.

**In the app.** AFM, SiO2–K2O, SiO2–FeOt/MgO and Co–Th diagrams.

**Source.** Irvine and Baragar (1971); Miyashiro (1974); Peccerillo and
Taylor (1976).

### Alkaline and subalkaline

**What it is.** Alkaline rocks have high Na2O + K2O for their SiO2 and
usually contain feldspathoids (such as nepheline) in their norm.
Subalkaline rocks are the rest; they include tholeiitic and calc-alkaline
series.

**In the app.** The dashed line on TAS separates the two.

**Source.** Irvine and Baragar (1971).

### Metaluminous, peraluminous and peralkaline

**What it is.** Groups based on alumina saturation. Peraluminous:
Al2O3 > CaO + Na2O + K2O (molar). Metaluminous: Al2O3 is below that sum
but above Na2O + K2O. Peralkaline: Al2O3 < Na2O + K2O.

**In the app.** The Shand (1943) A/CNK–A/NK diagram; ASI in Frost and
Frost (2008).

**Source.** Shand (1943); Maniar and Piccoli (1989).

### CIPW norm

**What it is.** An ideal set of minerals calculated from a chemical
analysis by fixed rules. It allows rocks to be compared by "mineralogy"
even when they are glassy or fine grained. Normative quartz shows silica
oversaturation; normative nepheline shows undersaturation.

**In the app.** The Data page (CIPW norm tab), the nephelinite test before
TAS and the FSSI of Frost and Frost (2008). The result depends on the iron
split.

**Source.** Hutchison (1974, 1975), ported from Janoušek et al. (2006).

### Alteration and weathering

**What it is.** Changes in a rock after it formed. Weathering happens at
the Earth's surface; alteration is caused by hot fluids (hydrothermal) or
by sea water. Both add water and CO2, remove mobile elements and oxidise
iron.

**In the app.** Freshness checks before TAS, the F–M–W diagram of Ohta
and Arai (2007) and warnings on diagrams that need fresh rocks.

**Source.** Le Bas et al. (1986); Ohta and Arai (2007).

### Serpentinization

**What it is.** The reaction of olivine and pyroxene in ultramafic rocks
with water, forming serpentine, magnetite and brucite. It adds 10–14 wt%
water, oxidises Fe²⁺ to Fe³⁺ (which produces hydrogen, H2) and can remove
CaO and MgO.

**In the app.** The Paulick et al. (2006) diagram, MgO variation diagrams,
the MgO deficit and the ultramafic warnings. Diagrams that assume fresh
igneous rocks are not valid for serpentinites.

**Source.** Deschamps et al. (2013); Paulick et al. (2006).

### Mobile and immobile elements

**What it is.** Mobile elements move easily with fluids during alteration:
Na, K, Rb, Sr, Ba, Ca and often Si. Immobile elements stay in place: Ti,
Zr, Nb, Y, Th, Al, the heavy rare earths and often Cr and V.

**In the app.** Diagrams based on immobile elements (Pearce 1996,
Hastie et al. 2007, Pearce 2008, Saccani 2015) are preferred for altered
rocks.

**Source.** Rollinson and Pease (2021); Pearce (1996).

### MORB, OIB, IAB and other setting codes

**What it is.** Short names for tectonic settings of basalts. MORB:
mid-ocean ridge basalt (N-MORB normal, E-MORB enriched, G-MORB
garnet-influenced). OIB: ocean island basalt. IAB: island arc basalt. IAT:
island arc tholeiite. CAB:
calc-alkaline basalt. WPB: within-plate basalt. CRB: continental rift
basalt.

**In the app.** Field names of the discrimination diagrams for basalts.

**Source.** Pearce and Cann (1973); Verma et al. (2006).

## Plot types

### Binary diagram

**What it is.** A plot of one quantity against another (x–y plot).

**In the app.** XY plot page and most catalogue diagrams.

**Source.** Rollinson and Pease (2021), chapter 3.

### Ternary diagram

**What it is.** A triangle that shows three components that are
recalculated to add up to 100 %. Each corner is 100 % of one component.

**In the app.** Ternary plot page; AFM, Jensen, Pearce and Cann (1973),
Meschede (1986), Wood (1980) and F–M–W diagrams.

**Source.** Rollinson and Pease (2021).

### Logarithmic scale

**What it is.** An axis where each step is a factor of ten. It shows
values that range over several orders of magnitude, as trace elements do.

**In the app.** Spider diagrams and many trace-element diagrams. Zero and
negative values cannot be shown on a log axis.

**Source.** Rollinson and Pease (2021).

### Spider diagram

**What it is.** Normalised element concentrations plotted in a fixed order
and joined by lines. REE diagrams show only the rare earth elements;
multi-element diagrams add other trace elements.

**In the app.** Spider diagrams page. Dotted segments bridge elements
that are missing.

**Source.** Sun and McDonough (1989); McDonough and Sun (1995).

### Harker diagram and variation diagrams

**What it is.** Variation diagrams plot oxides or elements against an
index of differentiation. Harker diagrams use SiO2; MgO diagrams are
better for basalts and ultramafic rocks.

**In the app.** Variation diagrams page (Harker and MgO plates; optional
iso-Mg# and olivine lines).

**Source.** Harker (1909) as cited in Rollinson and Pease (2021).

### Classification and discrimination diagrams

**What it is.** A classification diagram gives a **rock name** (TAS).
A discrimination diagram suggests a **tectonic setting** or magma type
(Pearce and Cann 1973). Discrimination diagrams are guides, not proofs:
fields overlap and were built from limited data sets.

**In the app.** Diagrams page, grouped by category.

**Source.** Rollinson and Pease (2021); Verma et al. (2010).

### Discriminant function

**What it is.** A weighted sum of several variables (for example log
ratios) that separates groups as well as possible. DF1 and DF2 are the
axes of such diagrams.

**In the app.** Verma et al. (2006) and Agrawal et al. (2008).

**Source.** Verma et al. (2006).

### Field and boundary

**What it is.** A field is the region of a diagram that carries a name;
boundaries are the lines between fields. A sample that falls in a field
receives its name.

**In the app.** Boundaries are taken from the templates of Janoušek et
al. (2006). The Results tab lists the field of every sample, with a bar
chart of the number of samples in each field; points on a boundary count
as inside.

**Source.** Janoušek et al. (2006).

## Diagrams: classification

### TAS (Le Bas et al. 1986)

**What it shows.** Rock names of volcanic rocks from SiO2 against Na2O +
K2O (wt%, anhydrous).

**Use for.** Fresh volcanic rocks. **Do not use** for plutonic rocks,
cumulates, strongly altered rocks (H2O+ > 2 wt%, CO2 > 0.5 wt%) or
ultramafic rocks. High-Mg rocks and nephelinites are named first by IUGS
rules.

**Reading.** The field gives the root name; the dashed line separates
alkaline and subalkaline rocks.

**Source.** Le Bas et al. (1986); Le Maitre et al. (2002).

### TAS for plutonic rocks (Middlemost 1985)

**What it shows.** Chemical names for plutonic rocks on SiO2 against
Na2O + K2O, the plutonic counterpart of TAS.

**Use for.** Plutonic rocks when modal data are not available. **Do not
use** for cumulates.

**Source.** Middlemost (1985).

### Nb/Y - Zr/Ti (Pearce 1996)

**What it shows.** Rock types from immobile element ratios: Nb/Y
(alkalinity) against Zr/Ti (degree of evolution).

**Use for.** Altered and metamorphosed volcanic rocks, where TAS fails.
Field names are a guide only: tests show many misnamed rocks (Verma et al.
2010).

**Source.** Pearce (1996), after Winchester and Floyd (1977).

### Jensen cation plot (Jensen 1976)

**What it shows.** A ternary of Al, Fe(total) + Ti and Mg (cation %).
Separates komatiites, tholeiites and calc-alkaline rocks.

**Use for.** Subalkaline volcanic rocks, especially Archean greenstone
belts. **Do not use** for alkaline rocks; Mg and Fe can move during
alteration.

**Source.** Jensen (1976); boundaries after Rickwood (1989).

### R1 - R2 volcanic (De la Roche et al. 1980)

**What it shows.** Names of volcanic rocks from two parameters that use
all major elements: R1 = 4Si − 11(Na + K) − 2(Fe + Ti) and R2 = 6Ca + 2Mg
+ Al (millications, total iron as Fe²⁺).

**Use for.** Volcanic rocks with a complete major-element analysis.

**Source.** De la Roche et al. (1980).

### R1 - R2 plutonic (De la Roche et al. 1980)

**What it shows.** The same R1 and R2 parameters with field names for
plutonic rocks (granite, gabbro, ...).

**Use for.** Plutonic rocks. Ultramafic rocks plot high on R2, in or above
the "ultramafic rock" field.

**Source.** De la Roche et al. (1980).

## Diagrams: magma series

### AFM (Irvine and Baragar 1971)

**What it shows.** A ternary of A = Na2O + K2O, F = FeOt and M = MgO
(wt%). The curved line separates tholeiitic (iron-enriched) from
calc-alkaline rocks.

**Use for.** Subalkaline volcanic rocks. **Do not use** for alkaline
rocks or for cumulates.

**Source.** Irvine and Baragar (1971).

### SiO2 - K2O (Peccerillo and Taylor 1976)

**What it shows.** SiO2 against K2O with fields for low-K (tholeiitic),
calc-alkaline, high-K calc-alkaline and shoshonite series.

**Use for.** Fresh subalkaline volcanic rocks, mainly from arcs. K2O is
mobile: for altered rocks use Co–Th (Hastie et al. 2007).

**Source.** Peccerillo and Taylor (1976); boundaries after Rickwood
(1989).

### SiO2 - FeOt/MgO (Miyashiro 1974)

**What it shows.** SiO2 against FeOt/MgO. A straight line separates
tholeiitic from calc-alkaline rocks.

**Use for.** Subalkaline volcanic rocks of arcs and continental margins.

**Source.** Miyashiro (1974).

### Co - Th (Hastie et al. 2007)

**What it shows.** Th against Co, an immobile-element replacement for the
SiO2–K2O diagram. The Co axis runs from high to low.

**Use for.** Altered arc volcanic rocks. The rock-name regions are coarse;
the main use is the series name.

**Source.** Hastie et al. (2007).

## Diagrams: granitoids

### A/CNK - A/NK (Shand 1943)

**What it shows.** Alumina saturation: A/CNK = Al2O3/(CaO + Na2O + K2O)
against A/NK = Al2O3/(Na2O + K2O), molar. Fields: metaluminous,
peraluminous, peralkaline.

**Use for.** Granitoids and other felsic rocks.

**Source.** Shand (1943); plot after Maniar and Piccoli (1989).

### Frost and Frost (2008)

**What it shows.** Four panels against SiO2: Fe-number (ferroan or
magnesian), MALI = Na2O + K2O − CaO (alkalic to calcic), ASI (alumina
saturation) and FSSI (silica saturation from the CIPW norm).

**Use for.** Feldspathic igneous rocks (granitoids and their volcanic
equivalents).

**Source.** Frost and Frost (2008).

### Pearce et al. (1984) granite discrimination

**What it shows.** Tectonic setting of granites from Rb, Y, Nb, Yb and
Ta: VAG volcanic-arc, syn-COLG syn-collisional, WPG within-plate, ORG
ocean-ridge granites.

**Use for.** Granitoids. Post-collisional granites often plot across
fields; read the result together with geology.

**Source.** Pearce et al. (1984).

### A-type granites (Whalen et al. 1987)

**What it shows.** A-type (anorogenic) granites against other granites,
using Ga/Al and Zr + Nb + Ce + Y.

**Use for.** Granitoids. Most panels need Ga.

**Source.** Whalen et al. (1987).

### YbN - LaN/YbN, TTG and adakite (Martin 1986)

**What it shows.** Chondrite-normalised (La/Yb)N against YbN. TTG and
adakites have steep REE patterns (high La/Yb) and low Yb because garnet
held back the heavy REE.

**Use for.** Tonalite–trondhjemite–granodiorite (TTG), adakites and other
granitoids.

**Source.** Martin (1986).

### R1 - R2 tectonic setting (Batchelor and Bowden 1985)

**What it shows.** The R1–R2 parameters of De la Roche et al. (1980)
with fields for granitoid settings: mantle fractionates, pre-collision,
post-collision uplift, late-orogenic, anorogenic, syn-collision and
post-orogenic.

**Use for.** Granitoid series.

**Source.** Batchelor and Bowden (1985).

## Diagrams: basalts and ophiolites

### Nb/Yb - Th/Yb (Pearce 2008)

**What it shows.** Th/Yb against Nb/Yb. Unaltered mantle melts lie on the
MORB–OIB array; samples above it gained Th from subduction or crust.

**Use for.** Basalts and ophiolites, also when altered (immobile
elements).

**Source.** Pearce (2008).

### Nb/Yb - TiO2/Yb (Pearce 2008)

**What it shows.** TiO2/Yb against Nb/Yb. Separates basalts from deep
melting (OIB array, garnet in the source) from shallow melting (MORB
array).

**Use for.** Basalts and ophiolites.

**Source.** Pearce (2008).

### NbN - ThN (Saccani 2015)

**What it shows.** Th against Nb, both normalised to N-MORB (Nb 2.33, Th
0.12 ppm; Sun and McDonough 1989). Separates types of ophiolitic basalts
(MORB, back-arc, arc, within-plate).

**Use for.** Post-Archean ophiolitic basalts. Two pairs of rock types
overlap here and are separated in a second step: G-MORB and N-MORB with
(Ce/Yb)N – (Dy/Yb)N, and boninite and IAT with DyN – YbN.

**Source.** Saccani (2015).

### (Ce/Yb)N - (Dy/Yb)N, G-MORB vs N-MORB (Saccani 2015)

**What it shows.** Chondrite-normalised (Dy/Yb)N against (Ce/Yb)N. A
straight line separates G-MORB (garnet-influenced MORB, higher (Dy/Yb)N)
from normal N-MORB. Garnet keeps the heavy REE (Yb) in the mantle, so
melts of a garnet-bearing source are richer in the middle and light REE
relative to Yb.

**Use for.** Ophiolitic basalts that fall in the N-MORB field of the NbN –
ThN diagram. G-MORB are typical of ocean–continent transition zones. The
line was drawn by eye; read the result as a guide.

**Source.** Saccani (2015), Fig. 8; chondrite values of Sun and McDonough
(1989).

### DyN - YbN, boninite vs IAT (Saccani 2015)

**What it shows.** Chondrite-normalised YbN against DyN. Boninites (low Dy
and Yb, from strongly depleted mantle or high degrees of melting) plot left
of the line; island-arc tholeiites (IAT) plot right of it.

**Use for.** Ophiolitic basalts that fall in the IAT field of the NbN – ThN
diagram. A boninite name also needs the IUGS high-Mg rules (TAS Results
tab).

**Source.** Saccani (2015), Fig. 9; chondrite values of Sun and McDonough
(1989).

### Ti - V (Shervais 1982)

**What it shows.** V against Ti/1000 with lines of equal Ti/V. Low Ti/V
(about 10–20) is typical of arc lavas, 20–50 of MORB and back-arc basalts,
and above 50 of ocean island and alkaline basalts.

**Use for.** Basalts, also altered (Ti and V are fairly immobile).

**Source.** Shervais (1982).

### Pearce and Cann (1973)

**What it shows.** Three diagrams (Ti–Zr–Y, Ti–Zr–Sr and Zr–Ti) with
fields for island-arc tholeiites, calc-alkaline basalts, MORB and
within-plate basalts.

**Use for.** Fresh basalts. Sr is mobile, so the Ti–Zr–Sr panel needs
fresh rocks.

**Source.** Pearce and Cann (1973).

### Zr/4 - 2Nb - Y (Meschede 1986)

**What it shows.** A ternary of Zr/4, 2Nb and Y. Separates within-plate
alkali basalts and tholeiites, E-MORB, N-MORB and volcanic-arc basalts.

**Use for.** Basalts.

**Source.** Meschede (1986).

### Th - Hf - Ta - Zr - Nb (Wood 1980)

**What it shows.** Three ternaries (Th–Hf/3–Ta, Th–Hf/3–Nb/16,
Th–Zr/117–Nb/16) that separate N-MORB, E-MORB, within-plate and arc
basalts.

**Use for.** Basalts and their differentiates.

**Source.** Wood (1980).

### Agrawal et al. (2008), La-Sm-Yb-Nb-Th

**What it shows.** Discriminant functions from natural-log ratios of La,
Sm, Yb and Nb to Th. Five diagrams separate island arc, continental rift,
ocean island and mid-ocean ridge basalts.

**Use for.** Basic and ultrabasic volcanic rocks (SiO2 < 52 wt%); other
samples are not plotted.

**Source.** Agrawal et al. (2008).

### Verma et al. (2006), major elements

**What it shows.** Discriminant functions from log ratios of major
elements to SiO2 (with FeO and Fe2O3 separate). Five diagrams for the same
four settings as Agrawal et al. (2008).

**Use for.** Fresh basic and ultrabasic volcanic rocks (SiO2 < 52 wt%).
**Do not use** for serpentinised rocks. Depends on the iron split.

**Source.** Verma et al. (2006).

## Diagrams: ultramafic rocks and weathering

### (LOI x 10) - SiO2 - sum of oxides (Deschamps et al. 2013)

**What it shows.** A ternary of LOI × 10 (top), SiO2 (right) and the sum of
the other oxides (left), with the oxides on an anhydrous basis. It shows
how much water a rock gained without changing its rock chemistry. Most
serpentinites lie along one line, SiO2/Sum ≈ 0.81: serpentinization adds
water but hardly changes the major elements. Talc-altered rocks move to
higher SiO2; brucite-rich rocks to lower SiO2 and higher LOI.

**Use for.** Serpentinites and serpentinised peridotites with LOI.
**Do not** read LOI as the degree of serpentinization: brucite, talc,
chlorite and clays also hold water.

**Source.** Deschamps et al. (2013), Fig. 3a.

### LOI - SiO2 and LOI - MgO (Deschamps et al. 2013)

**What it shows.** LOI (as measured) against anhydrous SiO2 and MgO, with
ideal mineral points for serpentine, talc, forsterite and enstatite.

**Use for.** Serpentinites: comparing the water content of samples and
spotting talc alteration (high SiO2, low LOI) or brucite (low SiO2, high
LOI).

**Source.** Deschamps et al. (2013), Figs. 4d and 4f.

### Fe redox in serpentinites (Paulick et al. 2006)

**What it shows.** Three panels: Fe2O3 against measured FeO, Fe2O3 against
LOI, and Fe³⁺/Fe(total) against LOI. During serpentinization, Fe²⁺ from
olivine and pyroxene is oxidised to Fe³⁺ in magnetite and serpentine (this
reaction makes hydrogen, H2). Samples move along lines of equal total iron
towards the magnetite ratio (Fe2O3/FeO = 2.22; Fe³⁺/Fe(total) = 2/3).

**Use for.** Serpentinites with FeO measured by titration **and** Fe2O3.
Samples with total iron only are not plotted: a split ratio would only
show the setting chosen in Settings.

**Source.** Paulick et al. (2006), Figs. 6D and 11A.

### Trace elements vs Yb in serpentinites (Deschamps et al. 2013)

**What it shows.** Eleven log–log panels against Yb: Ti and La/Yb (how
depleted the protolith was by melting), and the fluid-mobile elements Li,
B, Cs, Sr, Ba, U, Pb, As and Sb. Yb hardly moves during serpentinization,
so a sample far above the mantle value at the same Yb has gained that
element from seawater, slab fluids or sediments.

**Use for.** Serpentinites and peridotites with trace-element data. Ti – Yb
helps to separate depleted mantle-wedge serpentinites (low Ti) from more
fertile subducted serpentinites. Reference points: PM primitive mantle,
DM depleted mantle.

**Source.** Deschamps et al. (2013), Figs. 7a, 7d and 11; McDonough and
Sun (1995); Salters and Stracke (2004).

### Al2O3/SiO2 - MgO/SiO2 (Paulick et al. 2006)

**What it shows.** MgO/SiO2 against Al2O3/SiO2 with the terrestrial array
(melting trend) and the oceanic array of abyssal peridotites. Samples
below the array have lost MgO (seafloor weathering); dunites and
brucite-bearing rocks plot above it.

**Use for.** Mantle peridotites and serpentinites. Ratios do not change
with LOI. It cannot tell abyssal, mantle-wedge and subducted
serpentinites apart.

**Source.** Paulick et al. (2006); Niu (2004); Deschamps et al. (2013).

### F - M - W weathering (Ohta and Arai 2007)

**What it shows.** A ternary of three statistical scores: M (mafic source),
F (felsic source) and W (weathering intensity).

**Use for.** Weathered igneous rocks and sediments derived from them.
**Do not use** for ultramafic or serpentinised rocks: their low CaO and
alkalis push W up without weathering.

**Source.** Ohta and Arai (2007).

## Other plots

### Variation diagrams (Harker and MgO plates)

**What it shows.** Each oxide (and chosen trace elements) against SiO2
or MgO, as a plate of small panels.

**Use for.** Following differentiation, mixing or alteration trends in a
suite of related samples. Use MgO for basalts and ultramafic rocks.

**Source.** Rollinson and Pease (2021), section 3.3.

### Spider diagrams

**What it shows.** Normalised trace-element patterns (see *Spider
diagram* and *Normalisation*).

**Use for.** Comparing samples with each other and with reference
compositions.

**Source.** Sun and McDonough (1989); McDonough and Sun (1995).

### XY plot and ternary plot

**What it shows.** Free plots of any columns of your file, with log scales
(XY) or with any three groups of columns as apices (ternary).

**Use for.** Exploring your own data before choosing a published diagram.

**Source.** —

## References

- Agrawal S., Guevara M., Verma S.P. (2008) International Geology Review
  50, 1057–1079.
- Aitchison J. (1986) The Statistical Analysis of Compositional Data.
  Chapman and Hall, London.
- Batchelor R.A., Bowden P. (1985) Chemical Geology 48, 43–55.
- De la Roche H., Leterrier J., Grandclaude P., Marchal M. (1980) Chemical
  Geology 29, 183–210.
- Deschamps F., Godard M., Guillot S., Hattori K. (2013) Lithos 178,
  96–127.
- Frost B.R., Frost C.D. (2008) Journal of Petrology 49, 1955–1969.
- Hastie A.R., Kerr A.C., Pearce J.A., Mitchell S.F. (2007) Journal of
  Petrology 48, 2341–2357.
- Hutchison C.S. (1974) Laboratory Handbook of Petrographic Techniques.
  Wiley, New York. Hutchison C.S. (1975) Schweizerische Mineralogische und
  Petrographische Mitteilungen 55, 243–256.
- Irvine T.N., Baragar W.R.A. (1971) Canadian Journal of Earth Sciences 8,
  523–548.
- Janoušek V., Farrow C.M., Erban V. (2006) Journal of Petrology 47,
  1255–1259.
- Jensen L.S. (1976) Ontario Geological Survey Miscellaneous Paper 66.
- Le Bas M.J., Le Maitre R.W., Streckeisen A., Zanettin B. (1986) Journal
  of Petrology 27, 745–750.
- Le Maitre R.W. (1976) Contributions to Mineralogy and Petrology 56,
  181–189.
- Le Maitre R.W. (ed.) (2002) Igneous Rocks: A Classification and Glossary
  of Terms, 2nd edition. Cambridge University Press.
- Maniar P.D., Piccoli P.M. (1989) Geological Society of America Bulletin
  101, 635–643.
- Martin H. (1986) Geology 14, 753–756.
- McDonough W.F., Sun S.-s. (1995) Chemical Geology 120, 223–253.
- Meschede M. (1986) Chemical Geology 56, 207–218.
- Middlemost E.A.K. (1985) Magmas and Magmatic Rocks. Longman, London.
- Middlemost E.A.K. (1989) Chemical Geology 77, 19–26.
- Miyashiro A. (1974) American Journal of Science 274, 321–355.
- Niu Y. (2004) Journal of Petrology 45, 2423–2458.
- Ohta T., Arai H. (2007) Chemical Geology 240, 280–297.
- Paulick H., Bach W., Godard M., De Hoog J.C.M., Suhr G., Harvey J. (2006)
  Chemical Geology 234, 179–210.
- Pearce J.A. (1996) In: Wyman D.A. (ed.) Trace Element Geochemistry of
  Volcanic Rocks. Geological Association of Canada Short Course Notes 12,
  79–113.
- Pearce J.A. (2008) Lithos 100, 14–48.
- Pearce J.A., Cann J.R. (1973) Earth and Planetary Science Letters 19,
  290–300.
- Pearce J.A., Harris N.B.W., Tindle A.G. (1984) Journal of Petrology 25,
  956–983.
- Peccerillo A., Taylor S.R. (1976) Contributions to Mineralogy and
  Petrology 58, 63–81.
- Rickwood P.C. (1989) Lithos 22, 247–263.
- Rollinson H., Pease V. (2021) Using Geochemical Data: To Understand
  Geological Processes, 2nd edition. Cambridge University Press.
- Saccani E. (2015) Geoscience Frontiers 6, 481–501.
- Salters V.J.M., Stracke A. (2004) Geochemistry, Geophysics, Geosystems 5,
  Q05B07.
- Shand S.J. (1943) Eruptive Rocks. Wiley, New York.
- Shervais J.W. (1982) Earth and Planetary Science Letters 59, 101–118.
- Sun S.-s., McDonough W.F. (1989) Geological Society, London, Special
  Publications 42, 313–345.
- Verma S.P., Guevara M., Agrawal S. (2006) Journal of Earth System Science
  115, 485–528.
- Verma S.P., Rodríguez-Ríos R., González-Ramírez R. (2010) Turkish Journal
  of Earth Sciences 19, 239–265.
- Whalen J.B., Currie K.L., Chappell B.W. (1987) Contributions to
  Mineralogy and Petrology 95, 407–419.
- Winchester J.A., Floyd P.A. (1977) Chemical Geology 20, 325–343.
- Wood D.A. (1980) Earth and Planetary Science Letters 50, 11–30.
