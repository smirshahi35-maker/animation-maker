# Map the user's transcript tokens onto the 134 script tokens the composition and mix are keyed to.
# Differences in the user's read: «حقیقتو» (script: حقیقت رو), «هزار و چهارصد و پنج» (script token: 1405).
import json
u = json.load(open("audio/vo/narration.words.json"))["words"]
assert len(u) == 137, len(u)
S = lambda i: [u[i]["start"], u[i]["end"]]
c = [S(i) for i in range(10)]                                   # تو … تا
c += [[u[10]["start"], u[10]["end"] - 0.08], [u[10]["end"] - 0.08, u[10]["end"]]]   # حقیقت | رو  ← حقیقتو
c += [S(i) for i in range(11, 49)]                              # بدونی … آبان
c += [[u[49]["start"], u[53]["end"]]]                           # 1405 ← هزار و چهارصد و پنج
c += [S(i) for i in range(54, 137)]                             # ثبت شرکت … بگیرن
assert len(c) == 134, len(c)
json.dump(c, open("audio/vo/narration.canonical.json", "w"))
open("comp/vo_words.js", "w").write("window.VO_WORDS = " + json.dumps(c) + ";\n")
print("canonical tokens:", len(c), "last end", c[-1][1])
