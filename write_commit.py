import argparse

import subprocess


def get_commit(path: str):
    p = subprocess.run(
        ("git", "log", "--pretty=format:%H", "-n", "1", path), encoding="utf-8", check=True, stdout=subprocess.PIPE
    )
    return p.stdout


def main():
    class Args:
        input: str
        ghrepo: str
        output: str

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", help="index.html input")
    parser.add_argument("ghrepo", help="${{ github.server_url }}/${{ github.repository }}")
    parser.add_argument("output", help="index.html output")
    args = parser.parse_args(namespace=Args())

    with open(args.input, "r", encoding="utf-8", newline="") as f:
        indexhtml = f.read()

    indexcommit = get_commit("index.html")
    copypastacommit = get_commit("copypasta")
    newindex = (
        indexhtml.replace("PAGE_COMMIT_LINK", f"{args.ghrepo}/commit/{indexcommit}")
        .replace("PAGE_COMMIT_SHA", indexcommit[:7])
        .replace("COPYPASTA_COMMIT_LINK", f"{args.ghrepo}/commit/{copypastacommit}")
        .replace("COPYPASTA_COMMIT_SHA", copypastacommit[:7])
    )

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        f.write(newindex)


if __name__ == "__main__":
    main()
