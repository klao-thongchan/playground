#!/usr/bin/env python3
"""
Rate story synopses (col A → col B) with OpenAI.

Changes vs. previous version
─────────────────────────────
• Interactive filename prompt when no CLI arg is given
• Auto-completion of files in current folder (*.xlsx / *.csv)
• Clearer logging + graceful KeyboardInterrupt exit
• Minor refactors (type hints, f-strings, stricter error handling)
"""

import sys, readline, glob, pathlib, os, pandas as pd
from tqdm import tqdm
import openai

# ── CONFIGURABLE ────────────────────────────────────────────────────────────────
MODEL       = "gpt-4o-mini"   # cheaper? -> "gpt-3.5-turbo"
TEMP        = 0.2
PROMPT_SYS  = (
    "You are a film & TV development analyst. "
    "Given a story synopsis, score each dimension from 1-5 and return "
    "exactly this template (no extra text):\n\n"
    "Rating: <avg>\n\n"
    "Thematic Relevance: <score>\n"
    "Character Appeal: <score>\n"
    "Plot Engagement: <score>\n"
    "Production Strength: <score>\n"
    "Emotional Impact: <score>"
)
RETRIES     = 3
# ────────────────────────────────────────────────────────────────────────────────


def _prompt_for_file() -> pathlib.Path:
    """Interactive prompt + simple tab completion for *.xlsx/csv in cwd."""
    files = glob.glob("*.xlsx") + glob.glob("*.csv")
    print("\n📄 Available files:", ", ".join(files) or "(none found)")
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims("")
    readline.set_completer(lambda text, state, f=files: [s for s in f if s.startswith(text)][state] if state < len([s for s in f if s.startswith(text)]) else None)
    while True:
        fname = input("Enter Excel/CSV filename: ").strip()
        path  = pathlib.Path(fname)
        if path.exists():
            return path
        print(f"❌ '{fname}' not found – try again.")


def get_rating_block(synopsis: str) -> str:
    """One OpenAI call → six-line ratings block."""
    for attempt in range(1, RETRIES + 1):
        try:
            resp = openai.chat.completions.create(
                model=MODEL,
                temperature=TEMP,
                messages=[
                    {"role": "system", "content": PROMPT_SYS},
                    {"role": "user",   "content": synopsis.strip()},
                ],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt == RETRIES:
                raise
            print(f"[Retry {attempt}/{RETRIES}] {e}")


def load_df(path: pathlib.Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, header=None)
    return pd.read_excel(path, header=None)


def ensure_two_columns(df: pd.DataFrame) -> None:
    while df.shape[1] < 2:
        df[df.shape[1]] = ""


def main() -> None:
    try:
        # 1. Resolve input path
        path_in = pathlib.Path(sys.argv[1]) if len(sys.argv) >= 2 else _prompt_for_file()

        # 2. Load + prepare
        df = load_df(path_in)
        ensure_two_columns(df)

        # 3. Rate all synopses
        tqdm.pandas()
        df[1] = df[0].progress_apply(get_rating_block)

        # 4. Save next to original
        out_path = path_in.with_stem(path_in.stem + "_with_ratings").with_suffix(".xlsx")
        df.to_excel(out_path, index=False, header=False)
        print(f"\n✅ Done – ratings saved to “{out_path}”")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Bye!")
    except Exception as err:
        print(f"\n❌ Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
