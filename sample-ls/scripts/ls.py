#!/usr/bin/env python3
r"""sample-ls / ls.py

skill run 계약:
  입력  = argv[1] : 나열할 폴더의 절대경로 (필수)
  출력  = stdout  : JSON {path, count, entries[]}
  실패  = exit!=0 : stderr 에 사유, 비정상 종료코드

sandbox: SKILL.md 의 grant_args.ro=["args"] 로 argv 의 경로가 RO 로 열린다.
그 한 번의 호출 동안 그 폴더만 열리고 다른 곳은 여전히 막혀 있다.

왜 이 스크립트가 존재하나: cmd 의 `dir` 은 목록 앞에 볼륨 이름/일련번호를 찍으려
디스크 장치(\\.\C:)를 여는데, AppContainer 가 그것을 막는다. `dir /b` 도 표시만
생략할 뿐 조회는 그대로라 같이 실패한다(`vol` 이 단독으로도 실패하는 것이 그 증거).
파이썬은 디렉토리만 열고 볼륨은 보지 않으므로 정상 동작한다.
"""

import json
import os
import sys
from datetime import datetime


def die(msg: str, code: int = 1) -> None:
    """에러를 stderr 로 내고 비정상 종료 — runtime 이 실패로 처리한다."""
    print(msg, file=sys.stderr)
    sys.exit(code)


def main() -> None:
    # 인자가 없으면 실패한다. 예전엔 현재 폴더(= 스킬 폴더)를 나열했는데, 그것이
    # 최악의 실패 방식이었다: 호출자가 `args: []` 로 부르면 **성공적으로** 엉뚱한
    # 폴더의 진짜 목록이 돌아온다. 실측 런에서 모델은 그 결과에 "C:\var 의 내용"
    # 이라는 라벨을 붙였다 — 데이터는 진짜였고 문장만 거짓이었다. 조용한 기본값이
    # 없었다면 그 자리에서 고칠 수 있었을 오류다.
    #
    # 빈 목록이나 빈 JSON 이 아니라 exit!=0 인 이유: 부분적으로 맞아 보이는 답보다
    # 명확한 실패가 낫다. 무엇을 안 줬는지 말해야 다음 턴에 고친다.
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        die('no folder given. Pass the folder to list as the first argument, '
            'e.g. args: ["C:\\\\var"] (an absolute path). This script takes no '
            'options and does not run a shell.')
    path = sys.argv[1]

    try:
        with os.scandir(path) as it:
            items = list(it)
    except FileNotFoundError:
        die("folder not found: %s" % path)
    except NotADirectoryError:
        die("not a folder: %s" % path)
    except PermissionError:
        # grant 를 안 받은 경로. 바닥의 "Access is denied" 만 나가면 호출자는
        # 무엇을 고쳐야 할지 모른다 — 무엇이 막혔고 왜인지까지 말한다.
        die("access denied (sandbox): %s — pass it as the argument so the "
            "sandbox opens that folder for this call" % path)
    except OSError as e:
        die("read error: %s" % e)

    entries = []
    for e in items:
        try:
            st = e.stat()
            size = 0 if e.is_dir() else st.st_size
            mtime = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
        except OSError:
            # 나열은 됐는데 개별 항목의 stat 이 막힌 경우: 이름은 살리고 나머지는
            # 비운다. 항목 하나 때문에 목록 전체를 잃는 것이 더 나쁘다.
            size, mtime = 0, ""
        entries.append({
            "name": e.name,
            "dir": e.is_dir(),
            "size": size,
            "modified": mtime,
        })

    # 폴더 먼저, 그 다음 이름순 — 호출마다 순서가 흔들리지 않게.
    entries.sort(key=lambda x: (not x["dir"], x["name"].lower()))

    out = {"path": os.path.abspath(path), "count": len(entries), "entries": entries}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
