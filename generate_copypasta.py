import dataclasses
import json
import os

import yaml


@dataclasses.dataclass(kw_only=True)
class CopypastaInput:
    name: str
    description: str | None = None


@dataclasses.dataclass(kw_only=True)
class CopypastaStringInput(CopypastaInput):
    default: str = ""


@dataclasses.dataclass(kw_only=True)
class CopypastaChoiceInput(CopypastaInput):
    choice: list[str]
    default: int = 1


@dataclasses.dataclass(kw_only=True)
class CopypastaData:
    id: str
    name: str
    inputs: list[CopypastaInput]
    text: str


def slugify(name: str):
    return "".join(filter(lambda x: x == "_" or x.isalnum(), name.replace(" ", "_")))


def main():
    copypastas: list[CopypastaData] = []
    id_checker: dict[str, str] = {}

    for copypasta in os.scandir("copypasta"):
        name, ext = os.path.splitext(copypasta.name)
        if ext == ".yaml" or ext == ".yml":
            # Duplicate check
            copypasta_id = slugify(name)
            if copypasta_id in id_checker:
                raise RuntimeError(
                    f"ID conflict of \"{copypasta_id}\", originally defined for {id_checker['copypasta_id']}"
                )
            id_checker[copypasta_id] = copypasta.path

            # YAMLize
            with open(copypasta.path, "r", encoding="UTF-8", newline="\n") as f:
                yamldata = yaml.load(f, Loader=yaml.Loader)

            copypasta_input: list[CopypastaInput] = []
            for input_data in yamldata["inputs"]:
                if "choice" in input_data:
                    copypasta_input.append(
                        CopypastaChoiceInput(
                            name=input_data["name"],
                            description=input_data.get("description", input_data["name"]),
                            choice=input_data["choice"],
                            default=input_data.get("default", 1),
                        )
                    )
                else:
                    copypasta_input.append(
                        CopypastaStringInput(
                            name=input_data["name"],
                            description=input_data.get("description", input_data["name"]),
                            default=input_data.get("default", ""),
                        )
                    )

            copypastas.append(
                CopypastaData(
                    id=copypasta_id,
                    name=yamldata["name"],
                    inputs=copypasta_input,
                    text=yamldata["text"],
                )
            )

    copypastas.sort(key=lambda k: k.id)
    # JSONizie
    with open("copypasta.json", "w", encoding="UTF-8", newline="") as f:
        json.dump(list(map(dataclasses.asdict, copypastas)), f)


if __name__ == "__main__":
    main()
