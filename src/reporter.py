"""
출력 리포터
===========
CybORG 의 의존성(pygame)이 임포트 중 표준출력(fd 1)을 닫아버려 print 결과가
사라지는 문제가 있다. 이를 회피하기 위해 모든 출력을 두 경로로 보낸다.
  1) results.txt 파일에 기록 (UTF-8, 언제나 남는다)
  2) 표준에러(sys.stderr)에 기록 (콘솔 실시간 표시)

[한글 깨짐 방지] 콘솔 출력은 반드시 sys.stderr(파이썬 텍스트 스트림)로 보낸다.
Windows 에서 파이썬은 콘솔에 유니코드를 WriteConsoleW 로 출력하므로 한글이
정상 표시된다. (os.write 로 UTF-8 바이트를 직접 쓰면 cp949 로 오인되어 깨진다.)
"""

import sys

# pygame 임포트 이전의 원본 stderr 를 보관해 둔다.
_ERR = sys.stderr
_fpath = None


def init(path="results.txt"):
    """결과 파일을 초기화한다."""
    global _fpath
    _fpath = path
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
    except Exception:
        pass


def log(msg=""):
    """한 줄을 results.txt(UTF-8) 와 콘솔(stderr) 양쪽에 기록한다."""
    s = str(msg)
    if _fpath:
        try:
            with open(_fpath, "a", encoding="utf-8") as f:
                f.write(s + "\n")
        except Exception:
            pass
    for stream in (_ERR, sys.stderr):
        try:
            stream.write(s + "\n")
            stream.flush()
            break
        except Exception:
            continue
