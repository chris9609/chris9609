"""パックマンのSVGの最後に「GAME CLEAR / HIGH SCORE」を足す。

元のSVGは全アニメーションが durationMs の1周で回っている。
1周を HOLD_MS だけ延ばし、元の動きは前半に縮めて最後のコマで止め、
延ばした部分で文字を出す。同じ時計に乗るのでパックマンとずれない。

使い方: python3 scripts/game_over.py <score> dist/*.svg
"""
import re
import sys

HOLD_MS = 6000


def stretch(anim: str, dur: int, total: int) -> str:
    ratio = dur / total
    key_times = re.search(r'keyTimes="([^"]*)"', anim).group(1).split(";")
    values = re.search(r'values="([^"]*)"', anim, re.S).group(1).split(";")
    key_times = [f"{float(k) * ratio:.6f}" for k in key_times] + ["1"]
    values = values + [values[-1]]
    anim = anim.replace(f'dur="{dur}ms"', f'dur="{total}ms"')
    anim = re.sub(r'keyTimes="[^"]*"', f'keyTimes="{";".join(key_times)}"', anim)
    return re.sub(r'values="[^"]*"', lambda _: f'values="{";".join(values)}"', anim, flags=re.S)


def overlay(score: int, dur: int, total: int, width: int, height: int) -> str:
    start = f"{dur / total:.6f}"
    show = f'<animate attributeName="opacity" dur="{total}ms" repeatCount="indefinite" calcMode="discrete" values="0;1" keyTimes="0;{start}"/>'
    # 点滅は表示中ずっと続く。消えている間は親が0なので見えない
    blink = '<animate attributeName="opacity" dur="0.8s" repeatCount="indefinite" calcMode="discrete" values="1;0" keyTimes="0;0.6"/>'
    font = "font-family=\"'Press Start 2P', 'Courier New', monospace\" font-weight=\"bold\" text-anchor=\"middle\""
    cx, cy = width / 2, height / 2
    return f"""<g opacity="0">{show}
<rect width="100%" height="100%" fill="#000000" opacity="0.75"/>
<text x="{cx}" y="{cy - 6}" {font} font-size="40" fill="#4ade80" letter-spacing="6">GAME CLEAR{blink}</text>
<text x="{cx}" y="{cy + 34}" {font} font-size="20" fill="#ffd700" letter-spacing="3">HIGH SCORE  {score}</text>
</g>"""


def main() -> None:
    score = int(sys.argv[1])
    for path in sys.argv[2:]:
        svg = open(path, encoding="utf-8").read()
        dur = int(re.search(r"<durationMs>(\d+)</durationMs>", svg).group(1))
        total = dur + HOLD_MS
        width, height = map(int, re.search(r'<svg width="(\d+)" height="(\d+)"', svg).groups())
        svg = re.sub(
            rf'<animate(?:Transform)?\b[^>]*dur="{dur}ms"[^>]*>',
            lambda m: stretch(m.group(0), dur, total),
            svg,
        )
        svg = svg.replace("</svg>", overlay(score, dur, total, width, height) + "</svg>")
        open(path, "w", encoding="utf-8").write(svg)
        print(f"{path}: {dur}ms -> {total}ms, score {score}")


if __name__ == "__main__":
    main()
