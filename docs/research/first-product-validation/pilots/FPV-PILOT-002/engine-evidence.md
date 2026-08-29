# FPV-PILOT-002 revealed chess evidence

Status: Revealed only after P01 pre-engine evidence was frozen.

Research instrument: Stockfish 18, official Windows x86-64 build, depth 16, 2 threads, 256 MB hash. Binary SHA-256: `9BDE420202717CE083412027FBFB8C5C935B537591D712BE8A8A8BAE92F6E8D6`.

Scores are centipawns from the side-to-move perspective before the played move. After-move scores use the same perspective. They are instrument outputs, not claims about P01's thought process.

## P002-01

FEN: `6k1/1b1q1p1p/2p3p1/ppQ1B3/3p4/6PP/PPP1r1BK/R7 b - - 1 28`  
Played move: `28...Rxc2`  
Pre-move score: `-57`  
After-move score: `-609`

Top candidates:

1. `28...Qf5` — `-57` — `28...Qf5 29.Bxd4 Qxc5 30.Bxc5 Rxc2 31.Be7 c5 32.Rg1`
2. `28...Bc8` — `-285`
3. `28...h5` — `-302`
4. `28...d3` — `-308`
5. `28...b4` — `-325`

The played move permits a large evaluation swing toward White. The board context shows Black's rook activity is not sufficient to justify the immediate capture, while the queen move addresses the tactical and positional demands of the position.

## P002-02

FEN: `r1bqk2r/p4ppp/n1pb1n2/1p1p4/4PB2/2N4P/PPPQ1PP1/3RKBNR w Kkq - 1 11`  
Played move: `11.Bxd6`  
Pre-move score: `+238`  
After-move score: `+46`

Top candidates:

1. `11.e5` — `+238` — `11.e5 b4 12.Nb5 Bxe5 13.Bxe5 Ne4 14.Qd4 O-O`
2. `11.exd5` — `+90`
3. `11.Bxb5` — `+66`
4. `11.Bxd6` — `+51`
5. `11.Nf3` — `+41`

P01's `e5` observation is legal and identifies the strongest engine choice. The played move is playable but gives up a substantial part of White's advantage. The response demonstrates recognition of the decisive pawn-fork idea, although the supplied response does not establish whether alternatives were considered.

## P002-03

FEN: `rnbqkb1r/4npp1/p2pp2p/1ppP4/4P1PP/2N2N2/PPP2P2/R1BQKB1R w KQkq - 0 10`  
Played move: `10.a3`  
Pre-move score: `+93`  
After-move score: `-16`

Top candidates:

1. `10.g5` — `+93` — `10.g5 h5 11.dxe6 Bxe6 12.Bf4 b4 13.Nd5 Bxd5`
2. `10.Bh3` — `+64`
3. `10.dxe6` — `+49`
4. `10.Qd3` — `+42`
5. `10.Rg1` — `+36`

The central tension noted by P01 is present, but the engine favors an immediate kingside move that gains space and addresses the position's dynamic requirements. `10.a3` changes the evaluation from a small White edge to approximately equal at this search depth. The response does not specify whether `a3` was considered or whether the participant had a concrete alternative.

## P002-04

FEN: `N1bk1b1r/pp3ppp/6n1/8/5P2/4n3/PPP1R1PP/2K2BNR w - - 2 15`  
Played move: `15.Rxe3`  
Pre-move score: `+402`  
After-move score: `+409`

Top candidates:

1. `15.Rxe3` — `+402` — `15.Rxe3 Bd6 16.g3 Nxf4 17.Ne2 Ng6 18.Bg2 Be5`
2. `15.Rd2+` — `+384`
3. `15.Nb6` — `+274`
4. `15.Nf3` — `+257`
5. `15.Nh3` — `+255`

P01 correctly identified the hanging knight and selected the engine-preferred rook capture. This is a successful control example. The response does not establish the participant's calculation of Black's reply or whether the tactical resource was fully verified.

## P002-05

FEN: `r1bq1rk1/p1p2p2/1p2p2p/1Q1p4/1PnP1P2/P3P1PN/2P3BP/R4RK1 w - - 1 17`  
Played move: `17.g4`  
Pre-move score: `0`  
After-move score: `-208`

Top candidates:

1. `17.f5` — `0` — `17.f5 Bd7 18.Qa6 Qe8 19.Qb7 Nxe3 20.Rf2 Rc8`
2. `17.e4` — `-56`
3. `17.Qa4` — `-57`
4. `17.Nf2` — `-91`
5. `17.Rfe1` — `-176`

P01 recognized a kingside structural target and uncertainty about implementation. The board context confirms a missing black g-pawn, but the engine's top move is the immediate central break `f5`, not the played `g4`. The response identifies a real strategic feature while leaving the urgent candidate-generation question unresolved.

## P002-06

FEN: `r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22`  
Played move: `22...g6`  
Pre-move score: `+220`  
After-move score: `-369`

Top candidates:

1. `22...Qe7` — `+220` — `22...Qe7 23.Bf4 Bb6 24.Bd6 Qd7 25.Bc5 g6 26.Qg5`
2. `22...d3` — `-84`
3. `22...f6` — `-201`
4. `22...Qb6` — `-219`
5. `22...f5` — `-230`

This position was previously exposed to P01 and is therefore excluded from clean C3 inference. It is retained for C1/C2 context-comprehension analysis only.
