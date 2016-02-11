## Chess With Friends to PGN Exporter

Ever played Zynga's Chess With Friends and wanted to export your games to PGN 
to be able to analyze them on http://lichess.org (and other websites supporting 
PGN game import) and learn from your mistakes?

Well, here you go.
First, install the needed requirements:<br>
`pip install -r requirements.txt`

Now you can retrieve your games in PGN by running:<br>
`./cwf_to_pgn_exporter.py --username <<YOUR CWF USERNAME>> --password <<YOUR CWF PASSWORD>>`


Sample PGN output:

```
[Event "CWF Game between oliver006 and Player 2"]
[Site "Chess With Friends"]
[Date "2016.01.25"]
[Round "-"]
[White "oliver006"]
[Black "Player 2"]
[Result "1-0"]
1. e4 d5 2. e4xd5 Qxd5 3. Nc3 Qe6 4. Qe2 Qxe2 5. Bf1xe2 Nc6 6. d3 Nf6 7. Bf4 e5 8. Be3 Nd4 9. Be3xd4 e5xd4 10. Ne4 Nd5 11. c3 d4xc3 12. Ne4xc3 c6 13. Bf3 Nb4 14. O-O-O Bf5 15. d4 Nd3 16. Kc2 Nd3xf2 17. Kd2 Nf2xh1 18. Re1 Be6 19. Bg4 Kd7 20. Bg4xe6 f7xe6 21. Ke2 Bd6 22. Nf3 Rf8 23. Re1xh1 h6 24. Ne5 Bd6xe5 25. d4xe5 Rf7 26. Rd1 Ke7 27. Ne4 Rf8 28. Rd2 Rf5 29. Nd6 Rf5xe5 30. Kd1 Rf1 31. Kc2 b5 32. Nc8 Kf6 33. Nc8xa7 Rc5 34. Kd3 Rd5 35. Ke2 Rd5xd2 36. Kxd2 Rf2 37. Kc3 e5 38. Na7xc6 e4 39. Kd4 Re2 40. Kc3 e3 41. Nd4 Re2xg2 42. Kd3 Rg2xh2 43. Kxe3 Rh3 44. Ke2 g5 45. Nd4xb5 g4 46. Kf2 h5 47. Kg2 Kf5 48. Nd4 Ke4 49. Ne2 Re3 50. Ng3 Kf4 51. Ng3xh5 Ke5 52. Ng3 Kf4 53. Nh5 Kg5 54. Ng3 Kh4 55. Nf5 {black resigned}
```

A few things are still missing/incomplete, in particular
- pawn promotion only supports promotion to queen right now
- en passant is not marked with an `x` (eg. looks like a regular pawn move)
- possibly more

Please open a Github issue if you have suggestions, comments, additions, etc

