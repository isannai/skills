#!/usr/bin/env python3
"""csv-analyzer / analyze.py

skill run 계약:
  입력  = argv[1] : 분석할 CSV 파일의 절대경로 (skill run 의 args[0])
  출력  = stdout  : 사람이 읽는 요약 표 (이 문자열이 곧 툴 결과값)
  실패  = exit!=0 : stderr 에 사유, 비정상 종료코드

sandbox: skill 폴더는 cwd(RW), 폴더 밖은 grant 로 연 경로만 접근 가능.
CSV 경로는 SKILL.md 의 grant_args.ro=["args"] 로 부모 폴더가 RO 로 열린다.
"""

import csv
import sys


def die(msg: str, code: int = 1) -> None:
    """에러를 stderr 로 내고 비정상 종료 — runtime 이 실패로 처리한다."""
    print(msg, file=sys.stderr)
    sys.exit(code)


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


def main() -> None:
    if len(sys.argv) < 2:
        die("usage: analyze.py <csv-path>")

    path = sys.argv[1]

    # sandbox 밖 경로는 grant 없으면 여기서 PermissionError 로 막힌다.
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                die(f"empty file: {path}")
            rows = list(reader)
    except FileNotFoundError:
        die(f"file not found: {path}")
    except PermissionError:
        die(f"access denied (sandbox): {path} — grant 로 열어줘야 합니다")
    except OSError as e:
        die(f"read error: {e}")

    if not rows:
        print(f"file : {path}")
        print("rows : 0 (header only)")
        return

    ncol = len(header)

    # 컬럼별로 값을 모으고, 전부 숫자인 컬럼만 통계 계산.
    cols = {i: [] for i in range(ncol)}
    for r in rows:
        for i in range(min(len(r), ncol)):
            cols[i].append(r[i])

    lines = []
    lines.append(f"file : {path}")
    lines.append(f"rows : {len(rows)}")
    lines.append(f"cols : {ncol}")
    lines.append("")
    lines.append(f"{'column':<20} {'count':>7} {'mean':>12} {'min':>12} {'max':>12}")
    lines.append("-" * 65)

    for i in range(ncol):
        name = header[i] if i < len(header) else f"col{i}"
        vals = cols[i]
        nums = [float(v) for v in vals if is_number(v)]
        if nums and len(nums) == len([v for v in vals if v != ""]):
            mean = sum(nums) / len(nums)
            lines.append(
                f"{name:<20} {len(nums):>7} {mean:>12.3f} {min(nums):>12.3f} {max(nums):>12.3f}"
            )
        else:
            # 숫자 컬럼이 아니면 고유값 개수만.
            uniq = len(set(v for v in vals if v != ""))
            lines.append(f"{name:<20} {len(vals):>7} {'(text, ' + str(uniq) + ' uniq)':>38}")

    # stdout 전체가 툴 결과값이 된다.
    print("\n".join(lines))


if __name__ == "__main__":
    main()
