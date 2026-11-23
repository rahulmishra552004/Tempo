# Tempo: Agentic AI Chess Coach

An AI chess coach that gives hints, rates your moves, answers your questions, reviews full games,
scouts your opponents, lets you practice against a bot that plays like them, studies your own games
to show you how to improve, and builds and teaches you an opening repertoire.

## Roadmap

Features, in build order:

| # | Feature | What you get | Status |
|---|---|---|---|
| 1 | **Hints** | Enter a position → 3 hints, each more obvious | Planned |
| 2 | **Move rating** | Enter a move → Brilliant / Best / … / Blunder, with an explanation | Planned |
| 3 | **Chat** | Ask anything about the move; answers are checked with the engine | Planned |
| 4 | **Game analyzer** | Full game report: accuracy, labels, key moments, summary, lessons | Planned |
| 5 | **Opponent Scout** | Enter a profile → their playstyle + opening prep against them | Planned |
| 6 | **Sparring bot** | Practice against a bot that plays like that opponent | Planned |
| 7 | **Your improvement report** | Your playstyle, weaknesses and a training plan that adapts as you improve | Planned |
| 8 | **Opening Lab** | Your personal repertoire, opening courses, drills, a bot that plays openings against you, and checks that you follow your repertoire in your games | Planned |

Each feature builds on the ones before it:

```
Engine wrapper + facts detector
 ├─ Hints ─────────────────────────────────────────┐
 ├─ Move rating (labels, refutation) ──────────────┤
 │                                                 ▼
 │                     Chat agent + answer checker (uses hints + rating as tools)
 │                                                 │
 └─ Game analyzer = move rating on every move + stats + AI report
        ├─ Opponent Scout = game analyzer on THEIR games + style stats + prep
        │      └─ Sparring bot = Scout's style profile turned into a playing bot
        └─ Your improvement report = game analyzer on YOUR games + specialists + plan
               └─ Opening Lab = your style + opening explorer + RAG → repertoire, courses, drills
```
