"""
Pit-Wall Radio Terminology — Strategy Knowledge Base

Maps the shorthand engineers use on pit-wall radio to plain-English
definitions grounded in FIA 2026 regulations. Indexed into the strategy
history collection so RAGStore can answer fan queries about what they
just heard on the broadcast.

Usage:
    from data.pitwall_terminology import STRATEGY_DOCS
    n = rag_store.index_strategy_history(STRATEGY_DOCS)
"""

STRATEGY_DOCS = [
    {
        "text": (
            "Z-Mode means the car's active aerodynamic system is set to its high-downforce "
            "configuration. The FIA 2026 regulations permit movable bodywork that can shift "
            "between positions to trade downforce for drag. Z-Mode locks the bodywork in the "
            "position that maximises downforce — used in slow corners and wet conditions. "
            "When a driver is in Z-Mode, they have more grip but higher drag on the straights, "
            "so top speed is reduced. Engineers call it Z-Mode because the downforce vector "
            "acts in the Z (vertical) axis of the car's reference frame."
        ),
        "race": "TerminologyGuide",
        "year": 2026,
        "outcome": "Z-Mode: high-downforce active aero configuration, more grip, less top speed",
    },
    {
        "text": (
            "X-Mode means the car's active aerodynamic system is set to its low-drag "
            "configuration. The movable bodywork rotates to reduce frontal area and aerodynamic "
            "resistance on straights. X-Mode is deployed on long straights to maximise top speed "
            "and reduce energy consumption. The driver has less downforce and grip in corners "
            "when in X-Mode. Engineers call it X-Mode because it reduces drag along the X "
            "(longitudinal) axis of the car. Switching from Z-Mode to X-Mode at the end of a "
            "corner is a key part of the 2026 active aero strategy."
        ),
        "race": "TerminologyGuide",
        "year": 2026,
        "outcome": "X-Mode: low-drag active aero configuration, more top speed, less corner grip",
    },
    {
        "text": (
            "Harvest phase means the MGU-K (Motor Generator Unit — Kinetic) is recovering energy "
            "rather than deploying it. Under FIA 2026 Article C5.2, teams can store up to 4MJ per "
            "lap in the Energy Store. During the harvest phase the driver feels reduced acceleration "
            "on straights because the electrical system is taking power from the drivetrain rather "
            "than adding to it. Engineers call it 'harvest phase' or 'recharge phase'. After a "
            "harvest phase, the Energy Store is fuller and the team can deploy more power in the "
            "following laps. Fans hear this as a reason Leclerc 'lifted' on a straight — he was "
            "not losing pace, he was banking energy for later laps."
        ),
        "race": "TerminologyGuide",
        "year": 2026,
        "outcome": "Harvest phase: MGU-K recovering energy, driver lifts on straight, banking for later",
    },
    {
        "text": (
            "Deploy mode or attack mode means the MGU-K is deploying maximum electrical power to "
            "supplement the internal combustion engine. The FIA 2026 regulations allow up to 120kW "
            "of continuous MGU-K deployment. In deploy mode, the car accelerates harder out of "
            "corners. Teams use deploy mode for qualifying laps, overtake attempts, or defending "
            "position. After a deploy phase, the Energy Store needs time to recharge, which is why "
            "a driver may enter harvest phase immediately after an attack."
        ),
        "race": "TerminologyGuide",
        "year": 2026,
        "outcome": "Deploy/attack mode: full 120kW MGU-K deployment, maximum acceleration",
    },
    {
        "text": (
            "Undercut strategy: Ferrari pits their driver one or two laps before the rival. The "
            "driver on fresh tyres is faster and closes the gap while the rival is still on old "
            "rubber. If the gap is small enough, Ferrari's driver exits the pit lane ahead. "
            "Undercut works best on circuits where the pit lane exit is favourable and fresh tyres "
            "give a large lap time advantage. The critical variable is the pit stop time loss — "
            "typically 20–25 seconds — versus the tyre performance delta."
        ),
        "race": "StrategyPattern",
        "year": 2026,
        "outcome": "Undercut: pit early, gain time on fresh tyres, exit ahead of rival",
    },
    {
        "text": (
            "Overcut strategy: Ferrari keeps their driver out when the rival pits. The driver on "
            "track can push harder on now-clear track and extend their stint while rivals are in "
            "the pit lane. Ferrari then pits later and hopes the track position advantage outweighs "
            "the tyre delta. Overcut works when Safety Cars are likely, when traffic is heavy in "
            "the pit lane, or when the current tyre compound still has significant life remaining."
        ),
        "race": "StrategyPattern",
        "year": 2026,
        "outcome": "Overcut: stay out, gain track position, pit later when traffic clears",
    },
    {
        "text": (
            "DRS (Drag Reduction System) opens a flap in the rear wing to reduce drag on designated "
            "DRS zones. In 2026, DRS is permitted but the active aero rules interact with it — teams "
            "must balance DRS with their X-Mode/Z-Mode settings. A driver 'in DRS range' means they "
            "are within one second of the car ahead at the DRS detection point, allowing them to open "
            "DRS on the following straight for an overtake attempt."
        ),
        "race": "TerminologyGuide",
        "year": 2026,
        "outcome": "DRS: rear wing opens within 1 second of car ahead, reduces drag for overtake",
    },
    {
        "text": (
            "Tyre delta or delta time refers to the lap time difference between tyre compounds. "
            "In 2026, Pirelli supplies three compounds per race weekend — soft, medium, and hard. "
            "The soft tyre is fastest but degrades quickly. The hard tyre lasts longer but is "
            "slower. Strategy engineers calculate the delta — how many seconds per lap the softer "
            "compound gains — to decide whether an undercut or overcut is viable. If the tyre delta "
            "is large and the pit loss is small, an undercut is likely. A typical soft-to-medium "
            "delta is 0.3–0.6 seconds per lap at Bahrain."
        ),
        "race": "TerminologyGuide",
        "year": 2026,
        "outcome": "Tyre delta: per-lap time advantage of softer over harder compound, drives pit strategy",
    },
]
